"""
Clean Wikipedia HTML Data

This script cleans the messy Wikipedia HTML data:
- Removes HTML tags
- Removes citations [1], [2], etc.
- Handles special characters and encoding
- Removes tables and infoboxes
- Fixes whitespace issues
- Documents cleaning process

This demonstrates data wrangling skills on real-world messy data.
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata

class WikipediaDataCleaner:
    """Clean messy Wikipedia HTML data."""

    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'total_chars_removed': 0,
            'issues_fixed': {
                'html_tags': 0,
                'citations': 0,
                'tables': 0,
                'infoboxes': 0,
                'special_chars': 0,
                'whitespace': 0,
                'encoding_errors': 0
            }
        }

    def remove_html_tags(self, html_content):
        """Remove HTML tags and extract text."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unwanted elements
        for element in soup.find_all(['table', 'script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
            if element.name == 'table':
                if 'infobox' in element.get('class', []):
                    self.stats['issues_fixed']['infoboxes'] += 1
                else:
                    self.stats['issues_fixed']['tables'] += 1

        # Get text
        text = soup.get_text()
        self.stats['issues_fixed']['html_tags'] += html_content.count('<')

        return text

    def remove_citations(self, text):
        """Remove citation markers like [1], [2], [citation needed], etc."""
        original_len = len(text)

        # Remove numbered citations
        text = re.sub(r'\[\d+\]', '', text)

        # Remove citation templates
        text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[clarification needed\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[verification needed\]', '', text, flags=re.IGNORECASE)

        # Remove reference markers
        text = re.sub(r'\^', '', text)

        chars_removed = original_len - len(text)
        if chars_removed > 0:
            self.stats['issues_fixed']['citations'] += chars_removed
            self.stats['total_chars_removed'] += chars_removed

        return text

    def fix_encoding(self, text):
        """Fix encoding issues and normalize Unicode."""
        original_text = text

        # Normalize Unicode (NFD -> NFC)
        text = unicodedata.normalize('NFC', text)

        # Fix common encoding errors
        replacements = {
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã±': 'ñ',
            'Ã¼': 'ü',
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '—',
            'â€"': '–',
        }

        for wrong, correct in replacements.items():
            if wrong in text:
                text = text.replace(wrong, correct)
                self.stats['issues_fixed']['encoding_errors'] += text.count(wrong)

        # Remove or replace problematic characters
        # Keep standard punctuation and letters
        text = ''.join(char for char in text
                      if char.isprintable() or char in '\n\t ')

        return text

    def fix_whitespace(self, text):
        """Fix whitespace issues."""
        original_len = len(text)

        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Replace multiple newlines with double newline
        text = re.sub(r'\n\n+', '\n\n', text)

        # Replace tabs with spaces
        text = text.replace('\t', ' ')

        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # Remove empty lines at start and end
        text = text.strip()

        chars_removed = original_len - len(text)
        if chars_removed > 0:
            self.stats['issues_fixed']['whitespace'] += chars_removed
            self.stats['total_chars_removed'] += chars_removed

        return text

    def handle_special_characters(self, text):
        """Handle special characters appropriately."""
        # Keep useful special characters but normalize them
        replacements = {
            '"': '"',  # Smart quotes to regular
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',  # En dash to hyphen
            '—': '-',  # Em dash to hyphen
            '…': '...',  # Ellipsis
        }

        for special, regular in replacements.items():
            if special in text:
                count = text.count(special)
                text = text.replace(special, regular)
                self.stats['issues_fixed']['special_chars'] += count

        return text

    def clean_text(self, html_content):
        """Apply all cleaning steps."""
        # Step 1: Remove HTML
        text = self.remove_html_tags(html_content)

        # Step 2: Remove citations
        text = self.remove_citations(text)

        # Step 3: Fix encoding
        text = self.fix_encoding(text)

        # Step 4: Handle special characters
        text = self.handle_special_characters(text)

        # Step 5: Fix whitespace
        text = self.fix_whitespace(text)

        return text

    def clean_file(self, html_file):
        """Clean a single HTML file."""
        try:
            # Read HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Clean
            cleaned_text = self.clean_text(html_content)

            # Save cleaned text
            output_file = self.output_dir / html_file.name.replace('.html', '.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)

            return {
                'input_file': str(html_file),
                'output_file': str(output_file),
                'original_size': len(html_content),
                'cleaned_size': len(cleaned_text),
                'reduction': len(html_content) - len(cleaned_text),
                'status': 'success'
            }

        except Exception as e:
            return {
                'input_file': str(html_file),
                'error': str(e),
                'status': 'failed'
            }

    def clean_all(self):
        """Clean all HTML files."""
        print("="*60)
        print("WIKIPEDIA DATA CLEANING")
        print("="*60)

        # Get all HTML files
        html_files = list(self.input_dir.glob('*.html'))
        self.stats['total_files'] = len(html_files)

        print(f"\nFound {len(html_files)} HTML files to clean")
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print("\nCleaning in progress...")

        # Clean each file
        cleaning_reports = []

        for i, html_file in enumerate(html_files, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(html_files)} files...")

            report = self.clean_file(html_file)
            cleaning_reports.append(report)

            if report['status'] == 'success':
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1

        # Save cleaning report
        report_file = self.output_dir / 'cleaning_report.json'
        full_report = {
            'summary': self.stats,
            'files': cleaning_reports,
            'cleaned_at': datetime.now().isoformat()
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2)

        return full_report

    def print_summary(self):
        """Print cleaning summary."""
        print("\n" + "="*60)
        print("CLEANING SUMMARY")
        print("="*60)
        print(f"\nTotal files: {self.stats['total_files']}")
        print(f"Successfully cleaned: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success rate: {self.stats['successful']/self.stats['total_files']*100:.1f}%")

        print(f"\nTotal characters removed: {self.stats['total_chars_removed']:,}")

        print("\nIssues fixed:")
        for issue, count in self.stats['issues_fixed'].items():
            print(f"  {issue.replace('_', ' ').title()}: {count:,}")

        print("\n" + "="*60)

def create_before_after_examples(input_dir, output_dir, num_examples=3):
    """Create before/after examples for documentation."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    html_files = list(input_dir.glob('*.html'))[:num_examples]
    examples = []

    for html_file in html_files:
        txt_file = output_dir / html_file.name.replace('.html', '.txt')

        if txt_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                before = f.read()[:500]  # First 500 chars

            with open(txt_file, 'r', encoding='utf-8') as f:
                after = f.read()[:500]

            examples.append({
                'file': html_file.name,
                'before': before,
                'after': after
            })

    return examples

def main():
    """Main cleaning function."""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / 'data' / 'raw' / 'wikipedia_raw'
    output_dir = project_root / 'data' / 'processed' / 'wikipedia_clean'

    # Clean data
    cleaner = WikipediaDataCleaner(input_dir, output_dir)
    report = cleaner.clean_all()

    # Print summary
    cleaner.print_summary()

    # Create examples
    print("\nCreating before/after examples...")
    examples = create_before_after_examples(input_dir, output_dir, num_examples=3)

    examples_file = output_dir / 'cleaning_examples.json'
    with open(examples_file, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"✓ Examples saved to: {examples_file}")
    print(f"✓ Full report saved to: {output_dir / 'cleaning_report.json'}")
    print(f"✓ Cleaned files saved to: {output_dir}")

    print("\n" + "="*60)
    print("Data cleaning complete!")
    print("="*60)

if __name__ == "__main__":
    main()
