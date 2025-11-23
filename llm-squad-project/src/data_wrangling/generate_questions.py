"""
Generate Questions from Wikipedia Articles using LLMs

This script uses LLMs (GPT-4 or Claude) to generate SQuAD-style questions from cleaned Wikipedia text.
- Generates 3-5 answerable questions per article
- Generates 2-3 unanswerable questions per article
- Saves Q&A pairs in SQuAD format
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuestionGenerator:
    """Generate questions from text using LLMs."""

    def __init__(self, model='gpt-4', api_provider='openai'):
        """
        Initialize question generator.

        Args:
            model: Model to use ('gpt-4', 'gpt-3.5-turbo', 'claude-sonnet', etc.)
            api_provider: 'openai' or 'anthropic'
        """
        self.model = model
        self.api_provider = api_provider
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize API client based on provider."""
        if self.api_provider == 'openai':
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                return OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("OpenAI library not installed. Run: pip install openai")

        elif self.api_provider == 'anthropic':
            try:
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                return Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("Anthropic library not installed. Run: pip install anthropic")

        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")

    def create_answerable_prompt(self, context: str, num_questions: int = 4) -> str:
        """Create prompt for generating answerable questions."""
        return f"""Given the following text, generate {num_questions} questions that CAN be answered using information from the text.

For each question:
1. The answer MUST be explicitly stated in the text
2. Provide the exact answer text
3. Indicate where the answer starts in the text (character position)

Text:
{context}

Return your response as a JSON array with this format:
[
  {{
    "question": "What is...?",
    "answer": "exact text from context",
    "answer_start": 123
  }},
  ...
]

Only return the JSON array, no other text."""

    def create_unanswerable_prompt(self, context: str, num_questions: int = 2) -> str:
        """Create prompt for generating unanswerable questions."""
        return f"""Given the following text, generate {num_questions} plausible questions that CANNOT be answered using the information in the text.

The questions should:
1. Be related to the topic
2. Sound reasonable
3. NOT have answers in the provided text

Text:
{context}

Return your response as a JSON array with this format:
[
  {{
    "question": "What is...?"
  }},
  ...
]

Only return the JSON array, no other text."""

    def generate_questions(self, context: str, num_answerable: int = 4, num_unanswerable: int = 2) -> Dict:
        """Generate both answerable and unanswerable questions."""

        questions = {
            'answerable': [],
            'unanswerable': []
        }

        try:
            # Generate answerable questions
            answerable_prompt = self.create_answerable_prompt(context, num_answerable)
            answerable_response = self._call_api(answerable_prompt)
            questions['answerable'] = self._parse_json_response(answerable_response)

            # Generate unanswerable questions
            unanswerable_prompt = self.create_unanswerable_prompt(context, num_unanswerable)
            unanswerable_response = self._call_api(unanswerable_prompt)
            questions['unanswerable'] = self._parse_json_response(unanswerable_response)

        except Exception as e:
            print(f"Error generating questions: {e}")
            questions['error'] = str(e)

        return questions

    def _call_api(self, prompt: str) -> str:
        """Call the appropriate API."""
        if self.api_provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates high-quality reading comprehension questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content

        elif self.api_provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

    def _parse_json_response(self, response: str) -> List[Dict]:
        """Parse JSON response from API."""
        try:
            # Try to extract JSON from markdown code blocks if present
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response was: {response[:200]}...")
            return []

def process_wikipedia_articles(
    input_dir: Path,
    output_file: Path,
    metadata_file: Path,
    generator: QuestionGenerator,
    max_articles: int = None
):
    """Process all Wikipedia articles and generate questions."""

    print("="*60)
    print("QUESTION GENERATION FROM WIKIPEDIA")
    print("="*60)
    print(f"Using model: {generator.model}")
    print(f"API provider: {generator.api_provider}")
    print()

    # Load metadata to get article info
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Process articles
    all_qa_data = {'version': 'v2.0', 'data': []}
    processed_count = 0
    error_count = 0

    articles_to_process = metadata[:max_articles] if max_articles else metadata

    for i, article_meta in enumerate(articles_to_process, 1):
        try:
            title = article_meta['title']
            topic = article_meta['topic']

            # Read cleaned text
            txt_file = Path(article_meta['html_file'].replace('.html', '.txt').replace('wikipedia_raw', 'wikipedia_clean'))

            if not txt_file.exists():
                print(f"Skipping {title}: cleaned file not found")
                continue

            with open(txt_file, 'r', encoding='utf-8') as f:
                context = f.read().strip()

            if len(context) < 100:  # Skip very short articles
                print(f"Skipping {title}: context too short")
                continue

            print(f"[{i}/{len(articles_to_process)}] Generating questions for: {title}")

            # Generate questions
            questions = generator.generate_questions(context, num_answerable=4, num_unanswerable=2)

            # Format as SQuAD-style data
            article_data = {
                'title': title,
                'topic': topic,
                'paragraphs': [{
                    'context': context,
                    'qas': []
                }]
            }

            # Add answerable questions
            for j, q in enumerate(questions.get('answerable', [])):
                qa_entry = {
                    'id': f"{title.replace(' ', '_')}_q{j}_answerable",
                    'question': q['question'],
                    'is_impossible': False,
                    'answers': [{
                        'text': q['answer'],
                        'answer_start': q.get('answer_start', context.find(q['answer']))
                    }]
                }
                article_data['paragraphs'][0]['qas'].append(qa_entry)

            # Add unanswerable questions
            for j, q in enumerate(questions.get('unanswerable', [])):
                qa_entry = {
                    'id': f"{title.replace(' ', '_')}_q{j}_unanswerable",
                    'question': q['question'],
                    'is_impossible': True,
                    'answers': []
                }
                article_data['paragraphs'][0]['qas'].append(qa_entry)

            all_qa_data['data'].append(article_data)
            processed_count += 1

            # Rate limiting
            time.sleep(1)  # Avoid API rate limits

        except Exception as e:
            print(f"Error processing {title}: {e}")
            error_count += 1
            continue

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_data, f, indent=2, ensure_ascii=False)

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Processed: {processed_count} articles")
    print(f"Errors: {error_count}")
    print(f"Output saved to: {output_file}")
    print("="*60)

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / 'data' / 'processed' / 'wikipedia_clean'
    metadata_file = project_root / 'data' / 'processed' / 'wikipedia_metadata.json'
    output_file = project_root / 'data' / 'processed' / 'wikipedia_qa.json'

    # Check for API keys
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: No API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("\nFor demonstration purposes, use generate_mock_questions.py instead.")
        return

    # Initialize generator (prefer GPT-4, fall back to others)
    if os.getenv('OPENAI_API_KEY'):
        generator = QuestionGenerator(model='gpt-4', api_provider='openai')
    else:
        generator = QuestionGenerator(model='claude-sonnet-4-5-20250929', api_provider='anthropic')

    # Process articles (limit to 20 for cost control in demo)
    process_wikipedia_articles(
        input_dir=input_dir,
        output_file=output_file,
        metadata_file=metadata_file,
        generator=generator,
        max_articles=20  # Limit for cost control
    )

if __name__ == "__main__":
    main()
