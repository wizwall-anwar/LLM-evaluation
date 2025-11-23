"""
Visualization Module for LLM Evaluation Results

Creates visual dashboards and charts from evaluation results:
- Model comparison charts
- Prompt strategy comparison
- Clean vs Noisy performance
- Time/Cost analysis
- Confusion matrices
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

class ResultsVisualizer:
    """Visualize LLM evaluation results."""

    def __init__(self, results_dir: Path, output_dir: Path = None):
        """
        Initialize visualizer.

        Args:
            results_dir: Directory containing JSON result files
            output_dir: Directory to save visualizations (default: results_dir/visualizations)
        """
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir) if output_dir else self.results_dir / 'visualizations'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_results(self, pattern: str = '*.json') -> List[Dict]:
        """Load all result files matching pattern."""
        result_files = list(self.results_dir.glob(pattern))

        results = []
        for file in result_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    results.append(data)
            except Exception as e:
                print(f"Error loading {file}: {e}")

        return results

    def create_performance_comparison(self, results: List[Dict], save: bool = True):
        """Create bar chart comparing EM and F1 scores."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Extract data
        labels = []
        em_scores = []
        f1_scores = []

        for result in results:
            meta = result.get('metadata', {})
            metrics = result.get('aggregate_metrics', {}).get('overall', {})

            label = f"{meta.get('model', 'Unknown')}\n{meta.get('prompt_template', '')}"
            labels.append(label)
            em_scores.append(metrics.get('em', 0) * 100)
            f1_scores.append(metrics.get('f1', 0) * 100)

        x = np.arange(len(labels))
        width = 0.35

        # EM scores
        axes[0].bar(x, em_scores, width, label='Exact Match', color='steelblue', alpha=0.8)
        axes[0].set_ylabel('Score (%)', fontsize=12)
        axes[0].set_title('Exact Match Scores', fontsize=14, fontweight='bold')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(labels, rotation=45, ha='right')
        axes[0].set_ylim([0, 100])
        axes[0].grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for i, v in enumerate(em_scores):
            axes[0].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')

        # F1 scores
        axes[1].bar(x, f1_scores, width, label='F1 Score', color='coral', alpha=0.8)
        axes[1].set_ylabel('Score (%)', fontsize=12)
        axes[1].set_title('F1 Scores', fontsize=14, fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(labels, rotation=45, ha='right')
        axes[1].set_ylim([0, 100])
        axes[1].grid(axis='y', alpha=0.3)

        for i, v in enumerate(f1_scores):
            axes[1].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')

        plt.tight_layout()

        if save:
            output_file = self.output_dir / 'performance_comparison.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")

        plt.show()
        return fig

    def create_answerability_matrix(self, results: List[Dict], save: bool = True):
        """Create confusion matrix for answerability detection."""
        fig, axes = plt.subplots(1, len(results), figsize=(6*len(results), 5))

        if len(results) == 1:
            axes = [axes]

        for idx, result in enumerate(results):
            meta = result.get('metadata', {})
            ans_metrics = result.get('aggregate_metrics', {}).get('answerability_detection', {})
            cm = ans_metrics.get('confusion_matrix', {})

            # Create confusion matrix
            matrix = np.array([
                [cm.get('tn', 0), cm.get('fp', 0)],
                [cm.get('fn', 0), cm.get('tp', 0)]
            ])

            # Plot heatmap
            sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues',
                       xticklabels=['Pred Unanswerable', 'Pred Answerable'],
                       yticklabels=['True Unanswerable', 'True Answerable'],
                       cbar_kws={'label': 'Count'},
                       ax=axes[idx])

            title = f"{meta.get('model', 'Unknown')} - {meta.get('prompt_template', '')}"
            axes[idx].set_title(title, fontsize=12, fontweight='bold')

            # Add metrics text
            acc = ans_metrics.get('accuracy', 0)
            prec = ans_metrics.get('precision', 0)
            rec = ans_metrics.get('recall', 0)
            f1 = ans_metrics.get('f1', 0)

            text = f"Accuracy: {acc:.3f}\nPrecision: {prec:.3f}\nRecall: {rec:.3f}\nF1: {f1:.3f}"
            axes[idx].text(1.5, -0.5, text, fontsize=10,
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save:
            output_file = self.output_dir / 'answerability_confusion_matrix.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")

        plt.show()
        return fig

    def create_performance_metrics(self, results: List[Dict], save: bool = True):
        """Create performance metrics visualization (time, tokens)."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        labels = []
        avg_times = []
        total_tokens = []

        for result in results:
            meta = result.get('metadata', {})
            perf = result.get('aggregate_metrics', {}).get('performance', {})

            label = f"{meta.get('model', 'Unknown')}\n{meta.get('prompt_template', '')}"
            labels.append(label)
            avg_times.append(perf.get('avg_response_time', 0))
            total_tokens.append(perf.get('total_tokens', 0))

        x = np.arange(len(labels))

        # Response time
        axes[0].bar(x, avg_times, color='mediumseagreen', alpha=0.8)
        axes[0].set_ylabel('Time (seconds)', fontsize=12)
        axes[0].set_title('Average Response Time per Question', fontsize=14, fontweight='bold')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(labels, rotation=45, ha='right')
        axes[0].grid(axis='y', alpha=0.3)

        for i, v in enumerate(avg_times):
            axes[0].text(i, v + 0.02, f'{v:.3f}s', ha='center', fontweight='bold')

        # Token usage
        axes[1].bar(x, total_tokens, color='mediumpurple', alpha=0.8)
        axes[1].set_ylabel('Tokens', fontsize=12)
        axes[1].set_title('Total Token Usage', fontsize=14, fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(labels, rotation=45, ha='right')
        axes[1].grid(axis='y', alpha=0.3)

        for i, v in enumerate(total_tokens):
            axes[1].text(i, v + (max(total_tokens)*0.02), f'{v:,}', ha='center', fontweight='bold')

        plt.tight_layout()

        if save:
            output_file = self.output_dir / 'performance_metrics.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")

        plt.show()
        return fig

    def create_metric_comparison_table(self, results: List[Dict], save: bool = True):
        """Create comprehensive comparison table."""
        data = []

        for result in results:
            meta = result.get('metadata', {})
            overall = result.get('aggregate_metrics', {}).get('overall', {})
            answerable = result.get('aggregate_metrics', {}).get('answerable', {})
            ans_det = result.get('aggregate_metrics', {}).get('answerability_detection', {})
            perf = result.get('aggregate_metrics', {}).get('performance', {})

            row = {
                'Model': meta.get('model', 'Unknown'),
                'Prompt': meta.get('prompt_template', ''),
                'Dataset': meta.get('dataset', ''),
                'EM (Overall)': f"{overall.get('em', 0):.3f}",
                'F1 (Overall)': f"{overall.get('f1', 0):.3f}",
                'EM (Answerable)': f"{answerable.get('em', 0):.3f}",
                'F1 (Answerable)': f"{answerable.get('f1', 0):.3f}",
                'Ans. Accuracy': f"{ans_det.get('accuracy', 0):.3f}",
                'Avg Time (s)': f"{perf.get('avg_response_time', 0):.3f}",
                'Total Tokens': f"{perf.get('total_tokens', 0):,}"
            }
            data.append(row)

        df = pd.DataFrame(data)

        # Create figure
        fig, ax = plt.subplots(figsize=(16, len(data) * 0.5 + 1))
        ax.axis('tight')
        ax.axis('off')

        table = ax.table(cellText=df.values,
                        colLabels=df.columns,
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.12] * len(df.columns))

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Style header
        for i in range(len(df.columns)):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Alternate row colors
        for i in range(1, len(df) + 1):
            color = '#f1f1f2' if i % 2 == 0 else 'white'
            for j in range(len(df.columns)):
                table[(i, j)].set_facecolor(color)

        plt.title('Comprehensive Evaluation Results', fontsize=16, fontweight='bold', pad=20)

        if save:
            output_file = self.output_dir / 'comparison_table.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")

        plt.show()

        # Also save as CSV
        csv_file = self.output_dir / 'comparison_table.csv'
        df.to_csv(csv_file, index=False)
        print(f"✓ Saved CSV: {csv_file}")

        return df

    def create_dashboard(self, results: List[Dict]):
        """Create comprehensive dashboard with all visualizations."""
        print("="*60)
        print("CREATING VISUALIZATION DASHBOARD")
        print("="*60)
        print(f"Results loaded: {len(results)}")
        print(f"Output directory: {self.output_dir}")
        print("="*60)

        # Generate all visualizations
        print("\n1. Performance Comparison...")
        self.create_performance_comparison(results)

        print("\n2. Answerability Analysis...")
        self.create_answerability_matrix(results)

        print("\n3. Performance Metrics...")
        self.create_performance_metrics(results)

        print("\n4. Comparison Table...")
        self.create_metric_comparison_table(results)

        print("\n" + "="*60)
        print("DASHBOARD COMPLETE")
        print("="*60)
        print(f"All visualizations saved to: {self.output_dir}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Visualize LLM evaluation results')

    parser.add_argument('--results-dir', type=str, required=True,
                       help='Directory containing result JSON files')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory for visualizations')
    parser.add_argument('--pattern', type=str, default='*.json',
                       help='File pattern to match (default: *.json)')

    args = parser.parse_args()

    # Initialize visualizer
    visualizer = ResultsVisualizer(
        results_dir=Path(args.results_dir),
        output_dir=Path(args.output_dir) if args.output_dir else None
    )

    # Load results
    results = visualizer.load_results(args.pattern)

    if not results:
        print(f"No results found in {args.results_dir}")
        return

    print(f"Loaded {len(results)} result files")

    # Create dashboard
    visualizer.create_dashboard(results)

if __name__ == "__main__":
    main()
