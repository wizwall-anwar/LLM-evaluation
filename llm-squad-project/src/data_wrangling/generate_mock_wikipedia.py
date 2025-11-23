"""
Generate Mock Wikipedia HTML Data
Creates realistic mock Wikipedia articles with intentional messiness for demonstration.
In production, you would use the actual wikipedia_scraper.py.
"""

import json
from pathlib import Path
from datetime import datetime
import random

class MockWikipediaGenerator:
    """Generate mock Wikipedia HTML with realistic messiness."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.output_dir.parent.parent.parent / 'logs' / 'scraping_log.txt'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        """Log message to file and console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\\n')

    def create_messy_html(self, title, topic, content):
        """Create HTML with intentional messiness."""

        # Add random messiness
        messiness_types = []

        # 1. Add citations [1], [2], etc.
        if random.random() > 0.3:
            content = self.add_citations(content)
            messiness_types.append("citations")

        # 2. Add special characters and encoding issues
        if random.random() > 0.4:
            content = self.add_special_chars(content)
            messiness_types.append("special_characters")

        # 3. Add extra whitespace
        if random.random() > 0.5:
            content = self.add_whitespace_issues(content)
            messiness_types.append("whitespace_issues")

        # Create full HTML structure
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} - Wikipedia</title>
</head>
<body>
    <div id="mw-content-text">
        <div class="mw-parser-output">
            <table class="infobox">
                <tbody>
                    <tr><th colspan="2" class="infobox-above">{title}</th></tr>
                    <tr><td colspan="2">Random Info: Data here</td></tr>
                </tbody>
            </table>

            <p>{content}</p>

            <table class="wikitable">
                <tbody>
                    <tr><th>Category</th><th>Details</th></tr>
                    <tr><td>Type</td><td>{topic}</td></tr>
                </tbody>
            </table>

            <div class="references">
                <h2>References</h2>
                <ol>
                    <li id="cite_note-1"><span class="reference-text">Reference 1</span></li>
                    <li id="cite_note-2"><span class="reference-text">Reference 2</span></li>
                </ol>
            </div>
        </div>
    </div>
</body>
</html>"""

        return html, messiness_types

    def add_citations(self, text):
        """Add citation markers like [1], [2]."""
        words = text.split('.')
        cited_words = []
        citation_num = 1

        for word in words:
            if word.strip() and random.random() > 0.6:
                cited_words.append(word + f'<sup class="reference">[{citation_num}]</sup>')
                citation_num += 1
            else:
                cited_words.append(word)

        return '.'.join(cited_words)

    def add_special_chars(self, text):
        """Add special characters and encoding issues."""
        replacements = {
            'and': 'and', # Keep some normal
            'a': 'Ã¡' if random.random() > 0.95 else 'a',  # Encoding error
            'e': 'Ã©' if random.random() > 0.95 else 'e',
            'smart quote': '"smart quote"',  # Smart quotes
            'dash': '—',  # Em dash
            'degrees': '°',  # Degree symbol
        }

        # Randomly insert some special Unicode characters
        unicode_chars = ['é', 'ñ', 'ü', '–', '—', '"', '"', ''', ''']
        if random.random() > 0.5:
            insert_pos = random.randint(0, len(text) - 1)
            char = random.choice(unicode_chars)
            text = text[:insert_pos] + char + text[insert_pos:]

        return text

    def add_whitespace_issues(self, text):
        """Add extra whitespace and formatting issues."""
        # Random double spaces
        text = text.replace('. ', '.  ' if random.random() > 0.7 else '. ')
        # Random tabs
        if random.random() > 0.8:
            text = text.replace(' ', '\t', 1)
        # Random line breaks
        if random.random() > 0.7:
            words = text.split()
            insert_pos = random.randint(0, len(words) - 1)
            words.insert(insert_pos, '\n')
            text = ' '.join(words)

        return text

    def generate_content(self, title, topic):
        """Generate realistic content for the topic."""
        content_templates = {
            'Technology': f"{title} is a technology that has revolutionized modern computing. It involves complex algorithms and data processing techniques. The field has seen rapid advancement in recent years, with applications in artificial intelligence, machine learning, and data science. Researchers continue to explore new possibilities and applications.",

            'History': f"{title} was a significant period in human history. The events during this time shaped the modern world in profound ways. Political, social, and economic changes occurred that continue to influence society today. Historians study this era to understand the development of modern civilization.",

            'Science': f"{title} is an important concept in scientific understanding. The phenomenon was first observed in the early scientific investigations and has been studied extensively since then. Modern research uses advanced technology to explore the underlying mechanisms. Scientists continue to make discoveries in this field.",

            'Sports': f"{title} is a popular sport enjoyed by millions worldwide. The game requires skill, strategy, and physical fitness. Professional athletes train extensively to compete at the highest levels. Major tournaments and championships attract global audiences and media coverage.",

            'Politics': f"{title} is a political concept that influences governance and policy-making. The system has evolved over centuries of political thought and practice. Different countries implement variations based on their cultural and historical context. Political scientists analyze its effectiveness and impact.",

            'Arts': f"{title} represents an important artistic movement or work. The creative expression reflects cultural values and aesthetic principles of its time. Artists working in this style or period made significant contributions to cultural heritage. Critics and scholars continue to study and interpret the significance.",

            'Geography': f"{title} is a notable geographical feature with unique characteristics. The location plays an important role in regional climate and ecology. Human civilizations have been influenced by this geographic feature throughout history. Modern environmental studies examine its ongoing significance.",
        }

        return content_templates.get(topic, f"{title} is an important topic in {topic}. It has multiple dimensions and significant impact.")

    def generate_articles(self, article_lists):
        """Generate mock Wikipedia articles."""
        all_metadata = []

        for topic, articles in article_lists.items():
            self.log(f"\\nGenerating {topic} articles...")

            for article_title in articles[:15]:  # 15 per topic
                # Generate content
                content = self.generate_content(article_title, topic)

                # Create messy HTML
                html, messiness = self.create_messy_html(article_title, topic, content)

                # Save HTML file
                filename = f"{topic}_{article_title.replace(' ', '_')}"
                html_file = self.output_dir / f"{filename}.html"

                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)

                # Create metadata
                metadata = {
                    'title': article_title,
                    'topic': topic,
                    'html_file': str(html_file),
                    'scraped_at': datetime.now().isoformat(),
                    'issues_found': [
                        "Contains 1 infobox",
                        "Contains 1 table",
                        "Contains 2 citations"
                    ] + [f"Has {m}" for m in messiness],
                    'status': 'success'
                }

                all_metadata.append(metadata)
                self.log(f"  ✓ Generated: {article_title}")

        return all_metadata

def main():
    """Main generation function."""
    print("="*60)
    print("MOCK WIKIPEDIA DATA GENERATOR")
    print("="*60)
    print("NOTE: This generates mock data for offline demonstration.")
    print("In production, use wikipedia_scraper.py for real data.")
    print("="*60)

    # Setup
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'data' / 'raw' / 'wikipedia_raw'

    generator = MockWikipediaGenerator(output_dir)
    generator.log("\\nStarting mock Wikipedia data generation")

    # Article lists (same as real scraper)
    article_lists = {
        'Technology': ['Artificial Intelligence', 'Machine Learning', 'Deep Learning', 'Neural Network', 'Natural Language Processing', 'Computer Vision', 'Quantum Computing', 'Blockchain', 'Internet of Things', 'Cloud Computing', 'Cybersecurity', 'Data Science', 'Big Data', 'Python', 'JavaScript'],
        'History': ['World War II', 'Renaissance', 'Industrial Revolution', 'Ancient Egypt', 'Roman Empire', 'French Revolution', 'Cold War', 'American Civil War', 'Age of Enlightenment', 'Ancient Greece', 'Viking Age', 'Byzantine Empire', 'Ottoman Empire', 'Mongol Empire', 'British Empire'],
        'Science': ['Photosynthesis', 'Evolution', 'DNA', 'Quantum Mechanics', 'General Relativity', 'Climate Change', 'Plate Tectonics', 'Periodic Table', 'Cell Biology', 'Ecosystem', 'Black Hole', 'Big Bang', 'Genetics', 'Neuroscience', 'Thermodynamics'],
        'Sports': ['Football', 'Basketball', 'Cricket', 'Tennis', 'Baseball', 'American Football', 'Olympics', 'FIFA World Cup', 'UEFA Champions League', 'Super Bowl', 'Wimbledon', 'Rugby', 'Golf', 'Boxing', 'Formula One'],
        'Politics': ['Democracy', 'Communism', 'Capitalism', 'Socialism', 'United Nations', 'European Union', 'NATO', 'Constitution', 'Human Rights', 'Monarchy', 'Republic', 'Federalism', 'Diplomacy', 'International Law', 'Political Party'],
        'Arts': ['Renaissance Art', 'Impressionism', 'Baroque', 'Modernism', 'Abstract Art', 'Leonardo da Vinci', 'Vincent van Gogh', 'Pablo Picasso', 'Classical Music', 'Jazz', 'Rock Music', 'Hip Hop', 'Opera', 'Theatre', 'Literature'],
        'Geography': ['Mount Everest', 'Amazon Rainforest', 'Sahara', 'Pacific Ocean', 'Atlantic Ocean', 'Nile', 'Antarctica', 'Arctic', 'Great Barrier Reef', 'Himalayas', 'Andes', 'Mediterranean Sea', 'Great Lakes', 'Mariana Trench', 'Grand Canyon'],
    }

    # Generate articles
    all_metadata = generator.generate_articles(article_lists)

    # Save metadata
    metadata_file = output_dir.parent.parent / 'processed' / 'wikipedia_metadata.json'
    metadata_file.parent.mkdir(parents=True, exist_ok=True)

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)

    # Summary
    total = len(all_metadata)
    generator.log("\\n" + "="*60)
    generator.log("GENERATION COMPLETE")
    generator.log("="*60)
    generator.log(f"Total articles generated: {total}")
    generator.log(f"Raw HTML saved to: {output_dir}")
    generator.log(f"Metadata saved to: {metadata_file}")

    print("\\n" + "="*60)
    print(f"Successfully generated {total} mock Wikipedia articles!")
    print("="*60)

if __name__ == "__main__":
    main()
