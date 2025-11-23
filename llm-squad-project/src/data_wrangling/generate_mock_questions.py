"""
Generate Mock Questions from Wikipedia Articles

This creates realistic mock questions for offline demonstration.
In production, use generate_questions.py with real LLM APIs.
"""

import json
import random
from pathlib import Path
import re

class MockQuestionGenerator:
    """Generate mock questions from cleaned text."""

    def __init__(self):
        # Question templates for different topics
        self.question_templates = {
            'what': [
                "What is {subject}?",
                "What does {subject} involve?",
                "What are the main features of {subject}?",
                "What is the purpose of {subject}?",
            ],
            'when': [
                "When did {subject} occur?",
                "When was {subject} first observed?",
                "When did {subject} become important?",
            ],
            'where': [
                "Where is {subject} located?",
                "Where does {subject} take place?",
                "Where can {subject} be found?",
            ],
            'who': [
                "Who discovered {subject}?",
                "Who developed {subject}?",
                "Who was involved in {subject}?",
            ],
            'how': [
                "How does {subject} work?",
                "How is {subject} used?",
                "How has {subject} evolved?",
            ],
            'why': [
                "Why is {subject} important?",
                "Why does {subject} occur?",
                "Why is {subject} studied?",
            ]
        }

        # Unanswerable question templates
        self.unanswerable_templates = [
            "What is the exact date when {subject} will end?",
            "Who invented the original {subject}?",
            "How many people have used {subject} in total?",
            "What percentage of experts agree on {subject}?",
            "When was the first instance of {subject} recorded?",
            "Which country spends the most on {subject}?",
        ]

    def extract_key_phrases(self, text: str, num_phrases: int = 5) -> list:
        """Extract key phrases from text."""
        # Simple extraction: get noun phrases and important terms
        # Clean text
        text = text.replace('\n', ' ')

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        key_phrases = []

        # Extract capitalized phrases (likely important terms)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        key_phrases.extend(capitalized[:num_phrases])

        # Extract multi-word phrases
        words = text.split()
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if len(phrase) > 10 and phrase.lower() not in key_phrases:
                key_phrases.append(phrase)

        return list(set(key_phrases))[:num_phrases]

    def find_answer_span(self, text: str, answer: str) -> int:
        """Find where answer appears in text."""
        # Try exact match first
        pos = text.find(answer)
        if pos != -1:
            return pos

        # Try case-insensitive
        pos = text.lower().find(answer.lower())
        return pos if pos != -1 else 0

    def generate_answerable_questions(self, title: str, context: str, num_questions: int = 4) -> list:
        """Generate answerable questions from context."""
        questions = []

        # Get sentences for extracting answers
        sentences = [s.strip() for s in re.split(r'[.!?]+', context) if len(s.strip()) > 20]

        if not sentences:
            return []

        # Extract key information
        key_phrases = self.extract_key_phrases(context, num_phrases=10)

        # Generate questions
        question_types = list(self.question_templates.keys())

        for i in range(min(num_questions, len(sentences))):
            # Pick a random question type
            q_type = random.choice(question_types)
            template = random.choice(self.question_templates[q_type])

            # Get answer from sentence
            sentence = sentences[min(i, len(sentences) - 1)]
            words = sentence.split()

            # Extract answer (3-8 words from sentence)
            if len(words) > 3:
                start_idx = random.randint(0, max(0, len(words) - 8))
                end_idx = min(start_idx + random.randint(3, 8), len(words))
                answer = ' '.join(words[start_idx:end_idx])
            else:
                answer = sentence

            # Clean answer
            answer = answer.strip(',.;:!?')

            # Generate question
            subject = title if random.random() > 0.5 else random.choice(key_phrases) if key_phrases else title
            question = template.format(subject=subject)

            # Find answer position
            answer_start = self.find_answer_span(context, answer)

            questions.append({
                'question': question,
                'answer': answer,
                'answer_start': answer_start
            })

        return questions

    def generate_unanswerable_questions(self, title: str, context: str, num_questions: int = 2) -> list:
        """Generate unanswerable questions."""
        questions = []

        for i in range(num_questions):
            template = random.choice(self.unanswerable_templates)
            question = template.format(subject=title)
            questions.append({'question': question})

        return questions

    def generate_questions(self, title: str, context: str, num_answerable: int = 4, num_unanswerable: int = 2) -> dict:
        """Generate both types of questions."""
        return {
            'answerable': self.generate_answerable_questions(title, context, num_answerable),
            'unanswerable': self.generate_unanswerable_questions(title, context, num_unanswerable)
        }

def process_wikipedia_articles(input_dir: Path, output_file: Path, metadata_file: Path):
    """Process all Wikipedia articles and generate mock questions."""

    print("="*60)
    print("MOCK QUESTION GENERATION FROM WIKIPEDIA")
    print("="*60)
    print("NOTE: This generates mock questions for offline demonstration.")
    print("In production, use generate_questions.py with real LLM APIs.")
    print("="*60)

    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    generator = MockQuestionGenerator()

    # Process articles
    all_qa_data = {'version': 'v2.0', 'data': []}
    processed_count = 0
    total_questions = 0

    for i, article_meta in enumerate(metadata, 1):
        try:
            title = article_meta['title']
            topic = article_meta['topic']

            # Read cleaned text
            # Construct filename: Topic_Title.txt
            filename = f"{topic}_{title.replace(' ', '_')}.txt"
            txt_file = input_dir / filename

            if not txt_file.exists():
                print(f"Skipping {title}: cleaned file not found")
                continue

            with open(txt_file, 'r', encoding='utf-8') as f:
                context = f.read().strip()

            if len(context) < 100:
                print(f"Skipping {title}: context too short")
                continue

            print(f"[{i}/{len(metadata)}] Generating questions for: {title}")

            # Generate questions
            questions = generator.generate_questions(title, context, num_answerable=4, num_unanswerable=2)

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
            for j, q in enumerate(questions['answerable']):
                qa_entry = {
                    'id': f"{title.replace(' ', '_')}_q{j}_answerable",
                    'question': q['question'],
                    'is_impossible': False,
                    'answers': [{
                        'text': q['answer'],
                        'answer_start': q['answer_start']
                    }]
                }
                article_data['paragraphs'][0]['qas'].append(qa_entry)
                total_questions += 1

            # Add unanswerable questions
            for j, q in enumerate(questions['unanswerable']):
                qa_entry = {
                    'id': f"{title.replace(' ', '_')}_q{j}_unanswerable",
                    'question': q['question'],
                    'is_impossible': True,
                    'answers': []
                }
                article_data['paragraphs'][0]['qas'].append(qa_entry)
                total_questions += 1

            all_qa_data['data'].append(article_data)
            processed_count += 1

        except Exception as e:
            print(f"Error processing {title}: {e}")
            continue

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_data, f, indent=2, ensure_ascii=False)

    # Calculate statistics
    answerable = sum(1 for article in all_qa_data['data']
                    for para in article['paragraphs']
                    for qa in para['qas']
                    if not qa['is_impossible'])
    unanswerable = total_questions - answerable

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Processed articles: {processed_count}")
    print(f"Total questions: {total_questions}")
    if total_questions > 0:
        print(f"  Answerable: {answerable} ({answerable/total_questions*100:.1f}%)")
        print(f"  Unanswerable: {unanswerable} ({unanswerable/total_questions*100:.1f}%)")
    print(f"\nOutput saved to: {output_file}")
    print("="*60)

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / 'data' / 'processed' / 'wikipedia_clean'
    metadata_file = project_root / 'data' / 'processed' / 'wikipedia_metadata.json'
    output_file = project_root / 'data' / 'processed' / 'wikipedia_qa.json'

    process_wikipedia_articles(input_dir, output_file, metadata_file)

if __name__ == "__main__":
    main()
