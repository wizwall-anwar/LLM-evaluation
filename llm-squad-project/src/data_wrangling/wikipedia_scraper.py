"""
Wikipedia Scraper for Messy Data Collection

This script scrapes Wikipedia articles to create a MESSY dataset for LLM evaluation.
The goal is to capture real-world data challenges like:
- HTML formatting issues
- Special characters and encoding
- Tables and infoboxes
- Citations and references
- Mixed content types

Topics: Technology, History, Science, Sports, Politics, Arts, Geography
Target: 15-20 articles per topic (~100 total)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime
import random

class WikipediaScraper:
    """Scraper for Wikipedia articles."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Educational Research Project (Python/requests)'
        })
        self.log_file = self.output_dir.parent.parent.parent / 'logs' / 'scraping_log.txt'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        """Log message to file and console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\\n')

    def scrape_article(self, title, topic):
        """Scrape a single Wikipedia article."""
        try:
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            self.log(f"Scraping: {title} ({topic})")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Save raw HTML
            filename = f"{topic}_{title.replace(' ', '_').replace('/', '_')}"
            html_file = self.output_dir / f"{filename}.html"

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Extract some metadata
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', {'id': 'mw-content-text'})

            # Document issues found
            issues = []
            if content_div:
                # Check for tables
                tables = content_div.find_all('table')
                if tables:
                    issues.append(f"Contains {len(tables)} tables")

                # Check for citations
                citations = content_div.find_all('sup', {'class': 'reference'})
                if citations:
                    issues.append(f"Contains {len(citations)} citations")

                # Check for infoboxes
                infoboxes = content_div.find_all('table', {'class': 'infobox'})
                if infoboxes:
                    issues.append(f"Contains {len(infoboxes)} infoboxes")

                # Check for special characters
                text = content_div.get_text()
                special_chars = set([c for c in text if ord(c) > 127])
                if special_chars:
                    issues.append(f"Contains special characters: {len(special_chars)} unique")

            metadata = {
                'title': title,
                'topic': topic,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'html_file': str(html_file),
                'issues_found': issues,
                'status': 'success'
            }

            self.log(f"  ✓ Success: {title} - Issues: {', '.join(issues) if issues else 'None'}")
            return metadata

        except requests.exceptions.RequestException as e:
            self.log(f"  ✗ Error scraping {title}: {e}")
            return {
                'title': title,
                'topic': topic,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'error': str(e),
                'status': 'failed'
            }
        except Exception as e:
            self.log(f"  ✗ Unexpected error for {title}: {e}")
            return {
                'title': title,
                'topic': topic,
                'scraped_at': datetime.now().isoformat(),
                'error': str(e),
                'status': 'failed'
            }

    def scrape_topic(self, topic, articles, delay=1.0):
        """Scrape all articles for a given topic."""
        self.log(f"\\n{'='*60}")
        self.log(f"Starting topic: {topic} ({len(articles)} articles)")
        self.log(f"{'='*60}")

        metadata_list = []
        for article in articles:
            metadata = self.scrape_article(article, topic)
            metadata_list.append(metadata)
            time.sleep(delay + random.uniform(0, 0.5))  # Respectful crawling

        return metadata_list

def get_article_lists():
    """Define articles to scrape for each topic."""
    articles = {
        'Technology': [
            'Artificial_intelligence', 'Machine_learning', 'Deep_learning',
            'Neural_network', 'Natural_language_processing', 'Computer_vision',
            'Quantum_computing', 'Blockchain', 'Internet_of_things',
            'Cloud_computing', 'Cybersecurity', 'Data_science',
            'Big_data', 'Python_(programming_language)', 'JavaScript',
            'Robotics', '5G', 'Virtual_reality', 'Augmented_reality',
            'Cryptocurrency'
        ],
        'History': [
            'World_War_II', 'Renaissance', 'Industrial_Revolution',
            'Ancient_Egypt', 'Roman_Empire', 'French_Revolution',
            'Cold_War', 'American_Civil_War', 'Age_of_Enlightenment',
            'Ancient_Greece', 'Viking_Age', 'Byzantine_Empire',
            'Ottoman_Empire', 'Mongol_Empire', 'British_Empire',
            'Spanish_Empire', 'Crusades', 'Protestant_Reformation'
        ],
        'Science': [
            'Photosynthesis', 'Evolution', 'DNA', 'Quantum_mechanics',
            'General_relativity', 'Climate_change', 'Plate_tectonics',
            'Periodic_table', 'Cell_(biology)', 'Ecosystem',
            'Black_hole', 'Big_Bang', 'Genetics', 'Neuroscience',
            'Thermodynamics', 'Electromagnetic_radiation', 'Gravity',
            'Atomic_theory', 'Chemical_reaction', 'Cellular_respiration'
        ],
        'Sports': [
            'Association_football', 'Basketball', 'Cricket',
            'Tennis', 'Baseball', 'American_football', 'Olympics',
            'FIFA_World_Cup', 'UEFA_Champions_League', 'Super_Bowl',
            'Wimbledon_Championships', 'Rugby', 'Golf', 'Boxing',
            'Formula_One', 'Swimming_(sport)', 'Athletics_(sport)',
            'Ice_hockey', 'Volleyball', 'Table_tennis'
        ],
        'Politics': [
            'Democracy', 'Communism', 'Capitalism', 'Socialism',
            'United_Nations', 'European_Union', 'NATO',
            'Constitution', 'Human_rights', 'Monarchy',
            'Republic', 'Federalism', 'Diplomacy', 'International_law',
            'Political_party', 'Election', 'Referendum', 'Parliament'
        ],
        'Arts': [
            'Renaissance_art', 'Impressionism', 'Baroque', 'Modernism',
            'Abstract_art', 'Leonardo_da_Vinci', 'Vincent_van_Gogh',
            'Pablo_Picasso', 'Classical_music', 'Jazz', 'Rock_music',
            'Hip_hop', 'Opera', 'Theatre', 'Literature', 'Poetry',
            'Novel', 'Shakespeare'
        ],
        'Geography': [
            'Mount_Everest', 'Amazon_rainforest', 'Sahara',
            'Pacific_Ocean', 'Atlantic_Ocean', 'Nile', 'Antarctica',
            'Arctic', 'Great_Barrier_Reef', 'Himalayas',
            'Andes', 'Mediterranean_Sea', 'Great_Lakes', 'Mariana_Trench',
            'Grand_Canyon', 'Victoria_Falls', 'Yellowstone_National_Park'
        ]
    }
    return articles

def main():
    """Main scraping function."""
    print("="*60)
    print("WIKIPEDIA SCRAPER - MESSY DATA COLLECTION")
    print("="*60)

    # Setup
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'data' / 'raw' / 'wikipedia_raw'
    scraper = WikipediaScraper(output_dir)

    scraper.log("\\nStarting Wikipedia scraping session")
    scraper.log(f"Output directory: {output_dir}")

    # Get article lists
    article_lists = get_article_lists()

    # Select articles to scrape (15-20 per topic to get ~100 total)
    all_metadata = []
    total_articles = 0
    successful = 0
    failed = 0

    for topic, articles in article_lists.items():
        # Take first 15 articles from each topic
        selected = articles[:15]
        metadata = scraper.scrape_topic(topic, selected, delay=0.5)
        all_metadata.extend(metadata)

        topic_success = sum(1 for m in metadata if m['status'] == 'success')
        topic_failed = sum(1 for m in metadata if m['status'] == 'failed')

        total_articles += len(selected)
        successful += topic_success
        failed += topic_failed

        scraper.log(f"Topic {topic} complete: {topic_success} success, {topic_failed} failed")

    # Save metadata
    metadata_file = output_dir.parent.parent / 'processed' / 'wikipedia_metadata.json'
    metadata_file.parent.mkdir(parents=True, exist_ok=True)

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)

    # Final summary
    scraper.log("\\n" + "="*60)
    scraper.log("SCRAPING COMPLETE")
    scraper.log("="*60)
    scraper.log(f"Total articles attempted: {total_articles}")
    scraper.log(f"Successful: {successful}")
    scraper.log(f"Failed: {failed}")
    scraper.log(f"Success rate: {successful/total_articles*100:.1f}%")
    scraper.log(f"\\nRaw HTML saved to: {output_dir}")
    scraper.log(f"Metadata saved to: {metadata_file}")
    scraper.log(f"Log file: {scraper.log_file}")

    print("\\n" + "="*60)
    print("Scraping session complete! Check logs for details.")
    print("="*60)

if __name__ == "__main__":
    main()
