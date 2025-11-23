"""
Evaluation Metrics for Question Answering

Implements standard QA evaluation metrics:
- Exact Match (EM)
- F1 Score (token-level overlap)
- Precision/Recall for answerability detection
- Response time tracking
- Token usage tracking
"""

import re
import string
from collections import Counter
from typing import List, Dict, Tuple, Optional

class QAMetrics:
    """Question Answering evaluation metrics."""

    @staticmethod
    def normalize_answer(text: str) -> str:
        """
        Normalize answer text for comparison.

        - Lowercase
        - Remove punctuation
        - Remove articles (a, an, the)
        - Remove extra whitespace
        """
        # Lowercase
        text = text.lower()

        # Remove punctuation
        text = ''.join(ch if ch not in string.punctuation else ' ' for ch in text)

        # Remove articles
        text = re.sub(r'\b(a|an|the)\b', ' ', text)

        # Normalize whitespace
        text = ' '.join(text.split())

        return text

    @staticmethod
    def exact_match(prediction: str, ground_truth: str) -> float:
        """
        Calculate Exact Match score (0 or 1).

        Args:
            prediction: Predicted answer
            ground_truth: Correct answer

        Returns:
            1.0 if normalized strings match exactly, 0.0 otherwise
        """
        return float(QAMetrics.normalize_answer(prediction) ==
                    QAMetrics.normalize_answer(ground_truth))

    @staticmethod
    def f1_score(prediction: str, ground_truth: str) -> float:
        """
        Calculate token-level F1 score.

        Args:
            prediction: Predicted answer
            ground_truth: Correct answer

        Returns:
            F1 score (0.0 to 1.0)
        """
        pred_tokens = QAMetrics.normalize_answer(prediction).split()
        truth_tokens = QAMetrics.normalize_answer(ground_truth).split()

        # Handle empty predictions or ground truths
        if len(pred_tokens) == 0 or len(truth_tokens) == 0:
            return float(pred_tokens == truth_tokens)

        # Calculate token overlap
        common = Counter(pred_tokens) & Counter(truth_tokens)
        num_common = sum(common.values())

        if num_common == 0:
            return 0.0

        precision = num_common / len(pred_tokens)
        recall = num_common / len(truth_tokens)
        f1 = (2 * precision * recall) / (precision + recall)

        return f1

    @staticmethod
    def compute_metrics_for_qa(
        prediction: str,
        ground_truths: List[str]
    ) -> Dict[str, float]:
        """
        Compute metrics for a single QA pair.
        Takes max over multiple ground truths (SQuAD style).

        Args:
            prediction: Predicted answer
            ground_truths: List of acceptable answers

        Returns:
            Dictionary with 'em' and 'f1' scores
        """
        if not ground_truths:
            return {'em': 0.0, 'f1': 0.0}

        em_scores = [QAMetrics.exact_match(prediction, gt) for gt in ground_truths]
        f1_scores = [QAMetrics.f1_score(prediction, gt) for gt in ground_truths]

        return {
            'em': max(em_scores),
            'f1': max(f1_scores)
        }

    @staticmethod
    def answerability_metrics(
        predictions: List[bool],
        ground_truths: List[bool]
    ) -> Dict[str, float]:
        """
        Calculate precision, recall, and F1 for answerability detection.

        Args:
            predictions: List of predicted answerability (True = answerable)
            ground_truths: List of true answerability

        Returns:
            Dictionary with precision, recall, f1, and accuracy
        """
        if len(predictions) != len(ground_truths):
            raise ValueError("Predictions and ground truths must have same length")

        if len(predictions) == 0:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0, 'accuracy': 0.0}

        # Calculate confusion matrix
        true_positives = sum(p and g for p, g in zip(predictions, ground_truths))
        false_positives = sum(p and not g for p, g in zip(predictions, ground_truths))
        false_negatives = sum(not p and g for p, g in zip(predictions, ground_truths))
        true_negatives = sum(not p and not g for p, g in zip(predictions, ground_truths))

        # Calculate metrics
        precision = (true_positives / (true_positives + false_positives)
                    if (true_positives + false_positives) > 0 else 0.0)
        recall = (true_positives / (true_positives + false_negatives)
                 if (true_positives + false_negatives) > 0 else 0.0)
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0.0)
        accuracy = ((true_positives + true_negatives) / len(predictions)
                   if len(predictions) > 0 else 0.0)

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'accuracy': accuracy,
            'confusion_matrix': {
                'tp': true_positives,
                'fp': false_positives,
                'fn': false_negatives,
                'tn': true_negatives
            }
        }

class EvaluationResults:
    """Container for evaluation results."""

    def __init__(self):
        self.results = []
        self.total_time = 0.0
        self.total_tokens = 0

    def add_result(
        self,
        question_id: str,
        question: str,
        prediction: str,
        ground_truths: List[str],
        is_impossible: bool,
        predicted_impossible: bool,
        em: float,
        f1: float,
        response_time: float = 0.0,
        tokens_used: int = 0
    ):
        """Add a single evaluation result."""
        self.results.append({
            'question_id': question_id,
            'question': question,
            'prediction': prediction,
            'ground_truths': ground_truths,
            'is_impossible': is_impossible,
            'predicted_impossible': predicted_impossible,
            'em': em,
            'f1': f1,
            'response_time': response_time,
            'tokens_used': tokens_used
        })
        self.total_time += response_time
        self.total_tokens += tokens_used

    def compute_aggregate_metrics(self) -> Dict:
        """Compute aggregate metrics across all results."""
        if not self.results:
            return {}

        # Overall EM and F1
        avg_em = sum(r['em'] for r in self.results) / len(self.results)
        avg_f1 = sum(r['f1'] for r in self.results) / len(self.results)

        # Separate metrics for answerable vs unanswerable
        answerable = [r for r in self.results if not r['is_impossible']]
        unanswerable = [r for r in self.results if r['is_impossible']]

        answerable_em = (sum(r['em'] for r in answerable) / len(answerable)
                        if answerable else 0.0)
        answerable_f1 = (sum(r['f1'] for r in answerable) / len(answerable)
                        if answerable else 0.0)

        # Answerability detection metrics
        predictions = [not r['predicted_impossible'] for r in self.results]
        ground_truths = [not r['is_impossible'] for r in self.results]
        answerability = QAMetrics.answerability_metrics(predictions, ground_truths)

        # Timing and token metrics
        avg_time = self.total_time / len(self.results) if self.results else 0.0
        avg_tokens = self.total_tokens / len(self.results) if self.results else 0.0

        return {
            'overall': {
                'em': avg_em,
                'f1': avg_f1,
                'total_questions': len(self.results)
            },
            'answerable': {
                'em': answerable_em,
                'f1': answerable_f1,
                'count': len(answerable)
            },
            'unanswerable': {
                'count': len(unanswerable)
            },
            'answerability_detection': answerability,
            'performance': {
                'avg_response_time': avg_time,
                'total_time': self.total_time,
                'avg_tokens': avg_tokens,
                'total_tokens': self.total_tokens
            }
        }

    def get_detailed_results(self) -> List[Dict]:
        """Get all individual results."""
        return self.results

def evaluate_predictions(
    predictions: List[Dict],
    ground_truths: List[Dict]
) -> Dict:
    """
    Evaluate predictions against ground truths.

    Args:
        predictions: List of prediction dicts with 'id', 'answer', 'is_impossible'
        ground_truths: List of ground truth dicts with 'id', 'answers', 'is_impossible'

    Returns:
        Dictionary with aggregate metrics
    """
    results = EvaluationResults()

    # Create lookup for ground truths
    gt_lookup = {gt['id']: gt for gt in ground_truths}

    for pred in predictions:
        pred_id = pred['id']

        if pred_id not in gt_lookup:
            continue

        gt = gt_lookup[pred_id]

        # Get ground truth answers
        gt_answers = [a['text'] for a in gt.get('answers', [])]

        # Compute metrics
        if gt_answers:
            metrics = QAMetrics.compute_metrics_for_qa(pred['answer'], gt_answers)
        else:
            metrics = {'em': 0.0, 'f1': 0.0}

        results.add_result(
            question_id=pred_id,
            question=gt.get('question', ''),
            prediction=pred['answer'],
            ground_truths=gt_answers,
            is_impossible=gt['is_impossible'],
            predicted_impossible=pred.get('is_impossible', False),
            em=metrics['em'],
            f1=metrics['f1'],
            response_time=pred.get('response_time', 0.0),
            tokens_used=pred.get('tokens_used', 0)
        )

    return results.compute_aggregate_metrics()

if __name__ == "__main__":
    # Test the metrics
    print("Testing QA Metrics...")
    print("="*60)

    # Test Exact Match
    em = QAMetrics.exact_match("The capital of France", "the capital of france")
    print(f"Exact Match (case insensitive): {em}")

    # Test F1 Score
    f1 = QAMetrics.f1_score("The quick brown fox", "quick brown fox jumps")
    print(f"F1 Score: {f1:.3f}")

    # Test with multiple ground truths
    metrics = QAMetrics.compute_metrics_for_qa(
        "Paris",
        ["Paris", "paris", "Paris, France"]
    )
    print(f"\nMetrics with multiple ground truths: {metrics}")

    # Test answerability metrics
    preds = [True, True, False, False, True]
    truths = [True, False, False, True, True]
    ans_metrics = QAMetrics.answerability_metrics(preds, truths)
    print(f"\nAnswerability metrics: {ans_metrics}")

    print("\n" + "="*60)
    print("All tests passed!")
