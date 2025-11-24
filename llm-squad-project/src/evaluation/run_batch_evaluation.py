#!/usr/bin/env python3
"""
Batch Evaluation Script

Runs comprehensive evaluations across multiple:
- Models (mock + real)
- Datasets (SQuAD, Wikipedia Clean, Wikipedia Noisy)
- Prompt templates

Generates comparison tables and visualizations.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import subprocess
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class BatchEvaluator:
    """Run batch evaluations across models and datasets."""

    def __init__(self, project_root: Path, use_real_models: bool = False, max_questions: int = None, skip_confirm: bool = False):
        """
        Initialize batch evaluator.

        Args:
            project_root: Root directory of the project
            use_real_models: Whether to use real API models
            max_questions: Max questions per evaluation (for testing)
            skip_confirm: Skip confirmation prompt
        """
        self.project_root = project_root
        self.use_real_models = use_real_models
        self.max_questions = max_questions
        self.skip_confirm = skip_confirm
        self.eval_script = project_root / 'src' / 'evaluation' / 'evaluate_llm.py'
        self.results_dir = project_root / 'results'

    def define_evaluation_matrix(self):
        """
        Define which combinations to evaluate.

        Returns mixed mock + real model approach.
        """
        # Datasets to evaluate
        datasets = ['squad', 'wikipedia_clean', 'wikipedia_noisy']

        # Mock models (free, fast)
        mock_configs = [
            {'provider': 'mock', 'model': 'mock-gpt-4', 'name': 'Mock-GPT-4'},
            {'provider': 'mock', 'model': 'mock-claude-sonnet', 'name': 'Mock-Claude-Sonnet'},
        ]

        # Real models (costs money, but gives actual performance)
        real_configs = [
            {'provider': 'anthropic', 'model': 'claude-3-5-haiku-20241022', 'name': 'Claude-Haiku-3.5'},
            {'provider': 'openai', 'model': 'gpt-3.5-turbo', 'name': 'GPT-3.5-Turbo'},
        ]

        # Prompt templates to test
        prompts = ['zero_shot', 'robust']  # Focus on most important prompts

        # Build evaluation matrix
        evaluations = []

        # Add mock model evaluations (all datasets, all prompts)
        for model_config in mock_configs:
            for dataset in datasets:
                for prompt in prompts:
                    evaluations.append({
                        'provider': model_config['provider'],
                        'model': model_config['model'],
                        'name': model_config['name'],
                        'dataset': dataset,
                        'prompt': prompt,
                        'type': 'mock'
                    })

        # Add real model evaluations (all datasets, zero_shot only to save cost)
        if self.use_real_models:
            for model_config in real_configs:
                for dataset in datasets:
                    evaluations.append({
                        'provider': model_config['provider'],
                        'model': model_config['model'],
                        'name': model_config['name'],
                        'dataset': dataset,
                        'prompt': 'zero_shot',  # Use zero_shot to save costs
                        'type': 'real'
                    })

        return evaluations

    def run_single_evaluation(self, config: dict) -> bool:
        """
        Run a single evaluation.

        Args:
            config: Evaluation configuration

        Returns:
            True if successful, False otherwise
        """
        cmd = [
            'python', str(self.eval_script),
            '--provider', config['provider'],
            '--model', config['model'],
            '--dataset', config['dataset'],
            '--prompt', config['prompt']
        ]

        if self.max_questions:
            cmd.extend(['--max-questions', str(self.max_questions)])

        print(f"\n{'='*70}")
        print(f"Running: {config['name']} on {config['dataset']} ({config['prompt']})")
        print(f"Type: {config['type'].upper()}")
        print(f"{'='*70}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=False, text=True)
            print(f"✅ Completed: {config['name']} - {config['dataset']}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {config['name']} - {config['dataset']}")
            print(f"   Error: {e}")
            return False

    def run_batch(self):
        """Run all evaluations in batch."""
        print("\n" + "="*70)
        print("BATCH EVALUATION STARTING")
        print("="*70)
        print(f"Project: {self.project_root}")
        print(f"Real Models: {'Yes' if self.use_real_models else 'No'}")
        print(f"Max Questions: {self.max_questions if self.max_questions else 'All'}")
        print("="*70)

        # Get evaluation matrix
        evaluations = self.define_evaluation_matrix()

        print(f"\nTotal evaluations to run: {len(evaluations)}")

        # Count by type
        mock_count = sum(1 for e in evaluations if e['type'] == 'mock')
        real_count = sum(1 for e in evaluations if e['type'] == 'real')
        print(f"  - Mock evaluations: {mock_count}")
        print(f"  - Real evaluations: {real_count}")

        # Estimate time
        if self.max_questions:
            est_time_mock = mock_count * 0.5  # ~0.5 min per mock eval with limited questions
            est_time_real = real_count * 2     # ~2 min per real eval with limited questions
        else:
            est_time_mock = mock_count * 2     # ~2 min per mock eval
            est_time_real = real_count * 10    # ~10 min per real eval

        total_est_time = est_time_mock + est_time_real
        print(f"\nEstimated time: {total_est_time:.0f} minutes")

        if not self.skip_confirm:
            input("\nPress ENTER to start batch evaluation (or Ctrl+C to cancel)...")

        # Run evaluations
        start_time = time.time()
        results = []

        for i, config in enumerate(evaluations, 1):
            print(f"\n[{i}/{len(evaluations)}]")
            success = self.run_single_evaluation(config)
            results.append({'config': config, 'success': success})

            # Small delay between evaluations
            if i < len(evaluations):
                time.sleep(1)

        # Summary
        elapsed_time = time.time() - start_time
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        print("\n" + "="*70)
        print("BATCH EVALUATION COMPLETE")
        print("="*70)
        print(f"Total time: {elapsed_time/60:.1f} minutes")
        print(f"Successful: {successful}/{len(results)}")
        print(f"Failed: {failed}/{len(results)}")
        print("="*70)

        return results

    def generate_comparison_table(self):
        """Generate comparison tables from all results."""
        print("\n" + "="*70)
        print("GENERATING COMPARISON VISUALIZATIONS")
        print("="*70)

        # Generate visualizations for each dataset
        for dataset in ['squad', 'wikipedia_clean', 'wikipedia_noisy']:
            results_dir = self.results_dir / dataset

            if not results_dir.exists() or not list(results_dir.glob('*.json')):
                print(f"\nSkipping {dataset} - no results found")
                continue

            print(f"\nGenerating visualizations for: {dataset}")

            viz_cmd = [
                'python',
                str(self.project_root / 'src' / 'evaluation' / 'visualize_results.py'),
                '--results-dir', str(results_dir)
            ]

            try:
                subprocess.run(viz_cmd, check=True)
                print(f"✅ Visualizations created for {dataset}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create visualizations for {dataset}: {e}")

        print("\n" + "="*70)
        print("VISUALIZATIONS COMPLETE")
        print("="*70)
        print(f"\nResults saved in: {self.results_dir}")
        print("Check each dataset folder for:")
        print("  - comparison_table.csv (importable to Excel)")
        print("  - comparison_table.png (visual table)")
        print("  - performance_comparison.png (charts)")
        print("  - answerability_confusion_matrix.png")
        print("="*70)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Run batch evaluations across models and datasets'
    )

    parser.add_argument('--real-models', action='store_true',
                       help='Include real API models (costs money)')
    parser.add_argument('--max-questions', type=int, default=50,
                       help='Max questions per evaluation (default: 50 for testing)')
    parser.add_argument('--full', action='store_true',
                       help='Run on full datasets (overrides --max-questions)')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')

    args = parser.parse_args()

    # Determine max questions
    max_questions = None if args.full else args.max_questions

    # Initialize batch evaluator
    project_root = Path(__file__).parent.parent.parent
    evaluator = BatchEvaluator(
        project_root=project_root,
        use_real_models=args.real_models,
        max_questions=max_questions,
        skip_confirm=args.yes
    )

    # Show configuration
    print("\n" + "="*70)
    print("BATCH EVALUATION CONFIGURATION")
    print("="*70)
    if args.real_models:
        print("⚠️  WARNING: Real models enabled - this will cost money!")
        print("   Estimated cost: $2-5 for limited questions")
        print("   Estimated cost: $10-20 for full datasets")
    else:
        print("ℹ️  Using mock models only (FREE)")
        print("   To include real models, add --real-models flag")

    print(f"\nQuestions per evaluation: {max_questions if max_questions else 'All'}")
    print("="*70)

    # Run batch evaluation
    evaluator.run_batch()

    # Generate visualizations
    evaluator.generate_comparison_table()

    print("\n✨ All done! Check the results directories for outputs.")


if __name__ == "__main__":
    main()
