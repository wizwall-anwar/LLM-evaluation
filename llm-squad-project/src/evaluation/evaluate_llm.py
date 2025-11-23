"""
Main LLM Evaluation Script

Evaluates LLMs on Q&A datasets:
- SQuAD 2.0 (baseline)
- Wikipedia Clean
- Wikipedia Noisy

Supports multiple models, prompt strategies, and evaluation metrics.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.api_clients import get_client
from evaluation.metrics import EvaluationResults, QAMetrics
from prompts.prompt_templates import get_prompt

class LLMEvaluator:
    """Evaluate LLMs on Q&A tasks."""

    def __init__(
        self,
        provider: str,
        model: str,
        prompt_template: str = 'zero_shot',
        max_questions: int = None
    ):
        """
        Initialize evaluator.

        Args:
            provider: LLM provider ('openai', 'anthropic', 'huggingface', 'mock')
            model: Model name
            prompt_template: Prompt template to use
            max_questions: Maximum number of questions to evaluate (for testing)
        """
        self.provider = provider
        self.model = model
        self.prompt_template = prompt_template
        self.max_questions = max_questions
        self.client = get_client(provider, model)
        self.results = EvaluationResults()

    def load_dataset(self, dataset_path: Path) -> List[Dict]:
        """Load Q&A dataset."""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = []
        for article in data['data']:
            for paragraph in article['paragraphs']:
                context = paragraph['context']
                for qa in paragraph['qas']:
                    questions.append({
                        'id': qa['id'],
                        'question': qa['question'],
                        'context': context,
                        'answers': qa.get('answers', []),
                        'is_impossible': qa.get('is_impossible', False)
                    })

        return questions

    def evaluate_question(self, qa: Dict) -> Dict:
        """Evaluate a single question."""
        # Format prompt
        prompt = get_prompt(
            self.prompt_template,
            qa['context'],
            qa['question']
        )

        # Query LLM
        response = self.client.query(prompt)

        # Extract answer
        prediction = response['answer']
        predicted_impossible = response['is_impossible']

        # Compute metrics
        ground_truths = [a['text'] for a in qa['answers']]
        if ground_truths:
            metrics = QAMetrics.compute_metrics_for_qa(prediction, ground_truths)
        else:
            metrics = {'em': 0.0, 'f1': 0.0}

        # Store result
        self.results.add_result(
            question_id=qa['id'],
            question=qa['question'],
            prediction=prediction,
            ground_truths=ground_truths,
            is_impossible=qa['is_impossible'],
            predicted_impossible=predicted_impossible,
            em=metrics['em'],
            f1=metrics['f1'],
            response_time=response.get('response_time', 0.0),
            tokens_used=response.get('tokens_used', 0)
        )

        return response

    def evaluate(self, dataset_path: Path) -> Dict:
        """
        Evaluate on a dataset.

        Args:
            dataset_path: Path to Q&A dataset

        Returns:
            Dictionary with evaluation results
        """
        print("="*60)
        print("LLM EVALUATION")
        print("="*60)
        print(f"Provider: {self.provider}")
        print(f"Model: {self.model}")
        print(f"Prompt Template: {self.prompt_template}")
        print(f"Dataset: {dataset_path.name}")
        print("="*60)

        # Load dataset
        questions = self.load_dataset(dataset_path)

        if self.max_questions:
            questions = questions[:self.max_questions]
            print(f"\nEvaluating on {len(questions)} questions (limited for testing)")
        else:
            print(f"\nEvaluating on {len(questions)} questions")

        # Evaluate each question
        for i, qa in enumerate(questions, 1):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(questions)} questions evaluated...")

            try:
                self.evaluate_question(qa)
            except Exception as e:
                print(f"Error on question {qa['id']}: {e}")
                continue

        # Compute aggregate metrics
        metrics = self.results.compute_aggregate_metrics()

        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print("="*60)
        print(f"\nOverall Performance:")
        print(f"  Exact Match: {metrics['overall']['em']:.3f}")
        print(f"  F1 Score: {metrics['overall']['f1']:.3f}")

        print(f"\nAnswerable Questions ({metrics['answerable']['count']}):")
        print(f"  Exact Match: {metrics['answerable']['em']:.3f}")
        print(f"  F1 Score: {metrics['answerable']['f1']:.3f}")

        print(f"\nAnswerability Detection:")
        ans_det = metrics['answerability_detection']
        print(f"  Accuracy: {ans_det['accuracy']:.3f}")
        print(f"  Precision: {ans_det['precision']:.3f}")
        print(f"  Recall: {ans_det['recall']:.3f}")
        print(f"  F1: {ans_det['f1']:.3f}")

        print(f"\nPerformance:")
        perf = metrics['performance']
        print(f"  Avg Response Time: {perf['avg_response_time']:.3f}s")
        print(f"  Total Time: {perf['total_time']:.1f}s")
        print(f"  Avg Tokens: {perf['avg_tokens']:.0f}")
        print(f"  Total Tokens: {perf['total_tokens']}")

        return metrics

    def save_results(self, output_dir: Path, dataset_name: str):
        """Save evaluation results."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.provider}_{self.model}_{dataset_name}_{self.prompt_template}_{timestamp}.json"
        output_file = output_dir / filename

        # Prepare results
        results_data = {
            'metadata': {
                'provider': self.provider,
                'model': self.model,
                'prompt_template': self.prompt_template,
                'dataset': dataset_name,
                'timestamp': timestamp,
                'num_questions': len(self.results.results)
            },
            'aggregate_metrics': self.results.compute_aggregate_metrics(),
            'detailed_results': self.results.get_detailed_results()
        }

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results saved to: {output_file}")

        return output_file

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Evaluate LLMs on Q&A datasets')

    parser.add_argument('--provider', type=str, default='mock',
                       choices=['openai', 'anthropic', 'huggingface', 'mock'],
                       help='LLM provider')
    parser.add_argument('--model', type=str, default='mock-gpt-4',
                       help='Model name')
    parser.add_argument('--dataset', type=str, required=True,
                       choices=['squad', 'wikipedia_clean', 'wikipedia_noisy'],
                       help='Dataset to evaluate on')
    parser.add_argument('--prompt', type=str, default='zero_shot',
                       choices=['zero_shot', 'few_shot', 'chain_of_thought', 'instruction', 'robust'],
                       help='Prompt template to use')
    parser.add_argument('--max-questions', type=int, default=None,
                       help='Maximum number of questions to evaluate (for testing)')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory for results')

    args = parser.parse_args()

    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data'

    # Get dataset path
    dataset_paths = {
        'squad': data_dir / 'squad' / 'dev-v2.0.json',
        'wikipedia_clean': data_dir / 'processed' / 'wikipedia_qa.json',
        'wikipedia_noisy': data_dir / 'processed' / 'wikipedia_qa_noisy.json'
    }

    dataset_path = dataset_paths[args.dataset]

    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}")
        return

    # Set output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / 'results' / args.dataset

    # Create evaluator
    evaluator = LLMEvaluator(
        provider=args.provider,
        model=args.model,
        prompt_template=args.prompt,
        max_questions=args.max_questions
    )

    # Run evaluation
    try:
        metrics = evaluator.evaluate(dataset_path)

        # Save results
        evaluator.save_results(output_dir, args.dataset)

        print("\n" + "="*60)
        print("Evaluation completed successfully!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
        print("Partial results saved.")
        evaluator.save_results(output_dir, args.dataset)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
