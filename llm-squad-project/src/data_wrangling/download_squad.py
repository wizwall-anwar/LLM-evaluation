"""
Download SQuAD 2.0 Dataset
This script downloads the SQuAD 2.0 dataset and saves it locally.
"""

import os
import json
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url, filepath):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    with open(filepath, 'wb') as f, tqdm(
        desc=filepath.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            size = f.write(chunk)
            pbar.update(size)

def analyze_squad_data(data):
    """Analyze SQuAD dataset and return statistics."""
    stats = {
        'total_articles': len(data['data']),
        'total_paragraphs': 0,
        'total_questions': 0,
        'answerable': 0,
        'unanswerable': 0,
        'context_lengths': [],
        'question_lengths': [],
        'answer_lengths': []
    }

    for article in data['data']:
        for paragraph in article['paragraphs']:
            stats['total_paragraphs'] += 1
            context = paragraph['context']
            stats['context_lengths'].append(len(context))

            for qa in paragraph['qas']:
                stats['total_questions'] += 1
                stats['question_lengths'].append(len(qa['question']))

                if qa['is_impossible']:
                    stats['unanswerable'] += 1
                else:
                    stats['answerable'] += 1
                    if qa['answers']:
                        stats['answer_lengths'].append(len(qa['answers'][0]['text']))

    return stats

def download_squad():
    """Download SQuAD 2.0 dataset and save to data/squad/ directory."""

    # Define paths
    project_root = Path(__file__).parent.parent.parent
    squad_dir = project_root / "data" / "squad"
    squad_dir.mkdir(parents=True, exist_ok=True)

    # SQuAD 2.0 URLs (from official Stanford NLP repo)
    urls = {
        'train': 'https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json',
        'dev': 'https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json'
    }

    print("Downloading SQuAD 2.0 dataset...")
    print("="*60)

    downloaded_files = {}

    for split, url in urls.items():
        filepath = squad_dir / f"{split}-v2.0.json"

        if filepath.exists():
            print(f"✓ {split} set already exists: {filepath}")
        else:
            print(f"\nDownloading {split} set from {url}")
            try:
                download_file(url, filepath)
                print(f"✓ Downloaded to: {filepath}")
            except Exception as e:
                print(f"✗ Error downloading {split} set: {e}")
                continue

        downloaded_files[split] = filepath

    # Load and analyze the validation/dev set
    if 'dev' in downloaded_files:
        print("\n" + "="*60)
        print("ANALYZING VALIDATION SET")
        print("="*60)

        with open(downloaded_files['dev'], 'r', encoding='utf-8') as f:
            dev_data = json.load(f)

        stats = analyze_squad_data(dev_data)

        print(f"\nValidation Set Statistics:")
        print(f"  Articles: {stats['total_articles']}")
        print(f"  Paragraphs: {stats['total_paragraphs']}")
        print(f"  Total questions: {stats['total_questions']}")
        print(f"  Answerable: {stats['answerable']} ({stats['answerable']/stats['total_questions']*100:.1f}%)")
        print(f"  Unanswerable: {stats['unanswerable']} ({stats['unanswerable']/stats['total_questions']*100:.1f}%)")

        if stats['context_lengths']:
            avg_context = sum(stats['context_lengths']) / len(stats['context_lengths'])
            print(f"\n  Average context length: {avg_context:.1f} characters")

        if stats['question_lengths']:
            avg_question = sum(stats['question_lengths']) / len(stats['question_lengths'])
            print(f"  Average question length: {avg_question:.1f} characters")

        if stats['answer_lengths']:
            avg_answer = sum(stats['answer_lengths']) / len(stats['answer_lengths'])
            print(f"  Average answer length: {avg_answer:.1f} characters")

        # Create a sample file (500 questions)
        print(f"\nCreating sample file (500 questions)...")
        sample_data = {'data': [], 'version': dev_data['version']}
        question_count = 0
        target_questions = 500

        for article in dev_data['data']:
            if question_count >= target_questions:
                break

            sample_article = {
                'title': article['title'],
                'paragraphs': []
            }

            for paragraph in article['paragraphs']:
                if question_count >= target_questions:
                    break

                sample_paragraph = {
                    'context': paragraph['context'],
                    'qas': []
                }

                for qa in paragraph['qas']:
                    if question_count >= target_questions:
                        break
                    sample_paragraph['qas'].append(qa)
                    question_count += 1

                if sample_paragraph['qas']:
                    sample_article['paragraphs'].append(sample_paragraph)

            if sample_article['paragraphs']:
                sample_data['data'].append(sample_article)

        sample_file = squad_dir / "dev-v2.0-sample-500.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Sample saved to: {sample_file}")

    print("\n" + "="*60)
    print("Download complete! Dataset ready for exploration.")
    print("="*60)

    return downloaded_files

if __name__ == "__main__":
    download_squad()
