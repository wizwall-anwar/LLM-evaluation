"""
Add Noise to Wikipedia Q&A Data

This script introduces realistic errors to simulate messy real-world data:
- Typos (simulate OCR errors)
- Random capitalization issues
- Missing punctuation
- Extra whitespace
- Encoding errors (simulate UTF-8 issues)

Target: Add noise to ~30% of contexts to test LLM robustness
"""

import json
import random
from pathlib import Path
import copy

class NoiseInjector:
    """Inject realistic noise into text data."""

    def __init__(self, noise_probability=0.3):
        """
        Initialize noise injector.

        Args:
            noise_probability: Probability that a context will have noise added (0-1)
        """
        self.noise_probability = noise_probability

        # Common OCR/typo errors
        self.char_substitutions = {
            'a': ['@', 'а'],  # @ symbol, Cyrillic a
            'e': ['3', 'е'],  # 3, Cyrillic e
            'i': ['l', '1', 'і'],  # lowercase L, 1, Cyrillic i
            'o': ['0', 'о'],  # zero, Cyrillic o
            's': ['$', '5'],
            't': ['7', '+'],
            'l': ['1', 'I'],
            'O': ['0', 'О'],  # Zero, Cyrillic O
            'I': ['l', '1', 'І'],
        }

        # Common words to occasionally misspell
        self.common_typos = {
            'the': ['teh', 'hte'],
            'and': ['adn', 'nad'],
            'that': ['taht', 'thta'],
            'with': ['wiht', 'iwth'],
            'have': ['ahve', 'hvae'],
            'this': ['htis', 'tihs'],
            'from': ['form', 'fro'],
            'they': ['htey', 'tehy'],
        }

        self.noise_types_applied = {
            'typos': 0,
            'capitalization': 0,
            'missing_punctuation': 0,
            'extra_whitespace': 0,
            'encoding_errors': 0,
            'total_contexts_noised': 0
        }

    def add_typos(self, text: str, typo_rate: float = 0.01) -> str:
        """Add random typos (character substitutions)."""
        words = text.split()
        noised_words = []

        for word in words:
            if random.random() < typo_rate:
                # Character substitution
                if len(word) > 2 and random.random() < 0.7:
                    char_pos = random.randint(0, len(word) - 1)
                    char = word[char_pos]

                    if char in self.char_substitutions:
                        replacement = random.choice(self.char_substitutions[char])
                        word = word[:char_pos] + replacement + word[char_pos + 1:]
                        self.noise_types_applied['typos'] += 1

                # Common word misspelling
                elif word.lower() in self.common_typos and random.random() < 0.5:
                    typo = random.choice(self.common_typos[word.lower()])
                    word = typo if word.islower() else typo.capitalize()
                    self.noise_types_applied['typos'] += 1

            noised_words.append(word)

        return ' '.join(noised_words)

    def add_capitalization_errors(self, text: str) -> str:
        """Add random capitalization issues."""
        words = text.split()
        noised_words = []

        for i, word in enumerate(words):
            if random.random() < 0.02:  # 2% chance
                if word[0].isupper() and i != 0:  # Not start of sentence
                    word = word.lower()
                    self.noise_types_applied['capitalization'] += 1
                elif word[0].islower() and i == 0:  # Start of sentence
                    word = word.capitalize()
                    self.noise_types_applied['capitalization'] += 1

            noised_words.append(word)

        return ' '.join(noised_words)

    def remove_punctuation(self, text: str) -> str:
        """Randomly remove some punctuation."""
        result = []
        for char in text:
            if char in '.,;:' and random.random() < 0.05:  # 5% chance to remove
                self.noise_types_applied['missing_punctuation'] += 1
                continue  # Skip this punctuation
            result.append(char)

        return ''.join(result)

    def add_extra_whitespace(self, text: str) -> str:
        """Add extra spaces randomly."""
        words = text.split()
        result = []

        for word in words:
            result.append(word)
            if random.random() < 0.03:  # 3% chance to add extra space
                result.append('')  # This will create double space when joined
                self.noise_types_applied['extra_whitespace'] += 1

        return ' '.join(result)

    def add_encoding_errors(self, text: str) -> str:
        """Simulate encoding errors."""
        encoding_errors = {
            'é': 'Ã©',
            'á': 'Ã¡',
            'ñ': 'Ã±',
            'ü': 'Ã¼',
            '"': 'â€œ',
            '"': 'â€',
            '—': 'â€"',
        }

        for correct, wrong in encoding_errors.items():
            if correct in text and random.random() < 0.3:  # 30% chance
                text = text.replace(correct, wrong, 1)  # Replace only first occurrence
                self.noise_types_applied['encoding_errors'] += 1

        return text

    def inject_noise(self, text: str, noise_level: str = 'medium') -> str:
        """
        Inject multiple types of noise into text.

        Args:
            text: Original text
            noise_level: 'light', 'medium', or 'heavy'

        Returns:
            Noised text
        """
        # Determine noise parameters based on level
        params = {
            'light': {'typo_rate': 0.005, 'apply_all': False},
            'medium': {'typo_rate': 0.01, 'apply_all': False},
            'heavy': {'typo_rate': 0.02, 'apply_all': True}
        }

        typo_rate = params[noise_level]['typo_rate']
        apply_all = params[noise_level]['apply_all']

        # Apply noise types
        if apply_all or random.random() < 0.5:
            text = self.add_typos(text, typo_rate)

        if apply_all or random.random() < 0.4:
            text = self.add_capitalization_errors(text)

        if apply_all or random.random() < 0.3:
            text = self.remove_punctuation(text)

        if apply_all or random.random() < 0.3:
            text = self.add_extra_whitespace(text)

        if apply_all or random.random() < 0.2:
            text = self.add_encoding_errors(text)

        return text

    def process_qa_dataset(self, input_file: Path, output_file: Path, noise_level: str = 'medium'):
        """Process Q&A dataset and add noise to contexts."""

        print("="*60)
        print("NOISE INJECTION")
        print("="*60)
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Noise level: {noise_level}")
        print(f"Target contexts with noise: ~{self.noise_probability*100:.0f}%")
        print("="*60)

        # Load data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Deep copy to avoid modifying original
        noised_data = copy.deepcopy(data)

        total_contexts = 0
        noised_contexts = 0

        # Process each article
        for article in noised_data['data']:
            for paragraph in article['paragraphs']:
                total_contexts += 1

                # Decide whether to add noise to this context
                if random.random() < self.noise_probability:
                    original_context = paragraph['context']
                    noised_context = self.inject_noise(original_context, noise_level)
                    paragraph['context'] = noised_context
                    noised_contexts += 1
                    self.noise_types_applied['total_contexts_noised'] += 1

        # Save noised data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(noised_data, f, indent=2, ensure_ascii=False)

        # Print statistics
        print("\n" + "="*60)
        print("NOISE INJECTION COMPLETE")
        print("="*60)
        print(f"Total contexts: {total_contexts}")
        print(f"Contexts with noise: {noised_contexts} ({noised_contexts/total_contexts*100:.1f}%)")
        print("\nNoise types applied:")
        for noise_type, count in self.noise_types_applied.items():
            if noise_type != 'total_contexts_noised':
                print(f"  {noise_type.replace('_', ' ').title()}: {count}")

        print(f"\nNoised dataset saved to: {output_file}")
        print("="*60)

        return {
            'total_contexts': total_contexts,
            'noised_contexts': noised_contexts,
            'noise_percentage': noised_contexts / total_contexts * 100,
            'noise_types': self.noise_types_applied
        }

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / 'data' / 'processed' / 'wikipedia_qa.json'
    output_file = project_root / 'data' / 'processed' / 'wikipedia_qa_noisy.json'

    # Check if input exists
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        print("Run generate_mock_questions.py first to create the Q&A dataset.")
        return

    # Create noise injector (30% of contexts will get noise)
    injector = NoiseInjector(noise_probability=0.3)

    # Process dataset
    stats = injector.process_qa_dataset(
        input_file=input_file,
        output_file=output_file,
        noise_level='medium'
    )

    # Save statistics
    stats_file = output_file.parent / 'noise_injection_stats.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    print(f"\nStatistics saved to: {stats_file}")

if __name__ == "__main__":
    main()
