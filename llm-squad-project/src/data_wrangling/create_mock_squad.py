"""
Create Mock SQuAD 2.0 Dataset
Since we're in an offline environment, this creates a realistic mock dataset for demonstration.
In a production environment, you would download the real dataset from HuggingFace or Stanford NLP.
"""

import json
from pathlib import Path
import random

def create_mock_squad_data():
    """Create a mock SQuAD 2.0 dataset with realistic examples."""

    # Sample contexts from various domains
    contexts = [
        {
            "title": "Artificial Intelligence",
            "context": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term 'artificial intelligence' is often used to describe machines that mimic 'cognitive' functions that humans associate with the human mind, such as 'learning' and 'problem solving'. Modern AI techniques include machine learning, deep learning, and natural language processing.",
            "questions": [
                ("What does AI stand for?", "Artificial intelligence", False),
                ("What is the goal of intelligent agents?", "maximize its chance of successfully achieving its goals", False),
                ("Who invented the term artificial intelligence?", None, True),  # Unanswerable
                ("What are modern AI techniques?", "machine learning, deep learning, and natural language processing", False),
            ]
        },
        {
            "title": "Climate Change",
            "context": "Climate change includes both global warming driven by human-induced emissions of greenhouse gases and the resulting large-scale shifts in weather patterns. Though there have been previous periods of climatic change, since the mid-20th century humans have had an unprecedented impact on Earth's climate system and caused change on a global scale. The largest driver of warming is the emission of greenhouse gases, of which more than 90% are carbon dioxide and methane. Fossil fuel burning for energy consumption is the main source of these emissions, with additional contributions from agriculture, deforestation, and manufacturing.",
            "questions": [
                ("What is the largest driver of climate warming?", "emission of greenhouse gases", False),
                ("What percentage of greenhouse gases are carbon dioxide and methane?", "more than 90%", False),
                ("When did climate change first begin?", None, True),  # Unanswerable
                ("What is the main source of greenhouse gas emissions?", "Fossil fuel burning for energy consumption", False),
            ]
        },
        {
            "title": "Python Programming",
            "context": "Python is a high-level, interpreted programming language created by Guido van Rossum and first released in 1991. Python's design philosophy emphasizes code readability with its notable use of significant indentation. Its language constructs as well as its object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects. Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured, object-oriented and functional programming.",
            "questions": [
                ("Who created Python?", "Guido van Rossum", False),
                ("When was Python first released?", "1991", False),
                ("What company sponsors Python development?", None, True),  # Unanswerable
                ("What does Python's design philosophy emphasize?", "code readability", False),
            ]
        },
        {
            "title": "The Roman Empire",
            "context": "The Roman Empire was the post-Republican period of ancient Rome. As a polity it included large territorial holdings around the Mediterranean Sea in Europe, Northern Africa, and Western Asia ruled by emperors. From the accession of Caesar Augustus to the military anarchy of the 3rd century, it was a principate with Italy as metropole of the provinces and the city of Rome as sole capital. The Roman Empire was one of the largest empires in world history. At its height under Trajan, it covered 5 million square kilometers and held sway over an estimated 70 million people, at that time 21% of the world's entire population.",
            "questions": [
                ("Who was the first Roman Emperor?", "Caesar Augustus", False),
                ("How many people lived in the Roman Empire at its height?", "70 million people", False),
                ("What year did the Roman Empire fall?", None, True),  # Unanswerable
                ("What percentage of world population did the Empire represent?", "21%", False),
            ]
        },
        {
            "title": "Photosynthesis",
            "context": "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water. In most cases, oxygen is also released as a waste product. Most plants, algae, and cyanobacteria perform photosynthesis; such organisms are called photoautotrophs. Photosynthesis is largely responsible for producing and maintaining the oxygen content of the Earth's atmosphere.",
            "questions": [
                ("What do plants convert light energy into?", "chemical energy", False),
                ("What is released as a waste product in photosynthesis?", "oxygen", False),
                ("How much oxygen does photosynthesis produce annually?", None, True),  # Unanswerable
                ("What are organisms that perform photosynthesis called?", "photoautotrophs", False),
            ]
        },
        {
            "title": "Machine Learning",
            "context": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves. The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future. The primary aim is to allow the computers to learn automatically without human intervention or assistance.",
            "questions": [
                ("What is machine learning a subset of?", "artificial intelligence", False),
                ("What does machine learning focus on?", "development of computer programs that can access data and use it to learn", False),
                ("Who invented machine learning?", None, True),  # Unanswerable
                ("What is the primary aim of machine learning?", "to allow the computers to learn automatically without human intervention", False),
            ]
        },
    ]

    # Generate more contexts by repeating with variations
    all_data = []
    question_id = 0

    for _ in range(15):  # Create 15 articles (will give us ~360 questions)
        for ctx_template in contexts:
            article_data = {
                "title": ctx_template["title"],
                "paragraphs": []
            }

            paragraph_data = {
                "context": ctx_template["context"],
                "qas": []
            }

            for q_text, answer_text, is_impossible in ctx_template["questions"]:
                qa_entry = {
                    "id": f"question_{question_id}",
                    "question": q_text,
                    "is_impossible": is_impossible,
                    "answers": []
                }

                if not is_impossible and answer_text:
                    # Find the answer in the context
                    start_idx = ctx_template["context"].find(answer_text)
                    if start_idx != -1:
                        qa_entry["answers"] = [{
                            "text": answer_text,
                            "answer_start": start_idx
                        }]

                paragraph_data["qas"].append(qa_entry)
                question_id += 1

            article_data["paragraphs"].append(paragraph_data)
            all_data.append(article_data)

    return all_data

def create_mock_datasets():
    """Create mock train and dev datasets."""

    project_root = Path(__file__).parent.parent.parent
    squad_dir = project_root / "data" / "squad"
    squad_dir.mkdir(parents=True, exist_ok=True)

    print("Creating mock SQuAD 2.0 dataset for demonstration...")
    print("="*60)
    print("NOTE: This is a mock dataset for offline demonstration.")
    print("In production, download the real dataset from HuggingFace.")
    print("="*60)

    # Create dataset
    all_data = create_mock_squad_data()

    # Split into train (70%) and dev (30%)
    split_point = int(len(all_data) * 0.7)
    train_data = all_data[:split_point]
    dev_data = all_data[split_point:]

    # Create train dataset
    train_dataset = {
        "version": "v2.0",
        "data": train_data
    }

    train_file = squad_dir / "train-v2.0.json"
    with open(train_file, 'w', encoding='utf-8') as f:
        json.dump(train_dataset, f, indent=2, ensure_ascii=False)
    print(f"✓ Created training set: {train_file}")

    # Create dev dataset
    dev_dataset = {
        "version": "v2.0",
        "data": dev_data
    }

    dev_file = squad_dir / "dev-v2.0.json"
    with open(dev_file, 'w', encoding='utf-8') as f:
        json.dump(dev_dataset, f, indent=2, ensure_ascii=False)
    print(f"✓ Created dev set: {dev_file}")

    # Analyze dev set
    stats = {
        'total_articles': len(dev_data),
        'total_questions': 0,
        'answerable': 0,
        'unanswerable': 0,
        'context_lengths': [],
        'question_lengths': [],
        'answer_lengths': []
    }

    for article in dev_data:
        for paragraph in article['paragraphs']:
            stats['context_lengths'].append(len(paragraph['context']))
            for qa in paragraph['qas']:
                stats['total_questions'] += 1
                stats['question_lengths'].append(len(qa['question']))
                if qa['is_impossible']:
                    stats['unanswerable'] += 1
                else:
                    stats['answerable'] += 1
                    if qa['answers']:
                        stats['answer_lengths'].append(len(qa['answers'][0]['text']))

    print("\n" + "="*60)
    print("DEV SET STATISTICS")
    print("="*60)
    print(f"\nArticles: {stats['total_articles']}")
    print(f"Total questions: {stats['total_questions']}")
    print(f"Answerable: {stats['answerable']} ({stats['answerable']/stats['total_questions']*100:.1f}%)")
    print(f"Unanswerable: {stats['unanswerable']} ({stats['unanswerable']/stats['total_questions']*100:.1f}%)")

    if stats['context_lengths']:
        print(f"\nAverage context length: {sum(stats['context_lengths'])/len(stats['context_lengths']):.1f} characters")
    if stats['question_lengths']:
        print(f"Average question length: {sum(stats['question_lengths'])/len(stats['question_lengths']):.1f} characters")
    if stats['answer_lengths']:
        print(f"Average answer length: {sum(stats['answer_lengths'])/len(stats['answer_lengths']):.1f} characters")

    # Create sample file (100 questions for quick testing)
    sample_size = min(100, stats['total_questions'])
    sample_articles = dev_data[:10]  # First 10 articles
    sample_dataset = {
        "version": "v2.0",
        "data": sample_articles
    }

    sample_file = squad_dir / "dev-v2.0-sample-500.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_dataset, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created sample file: {sample_file}")

    print("\n" + "="*60)
    print("Mock dataset creation complete!")
    print("="*60)

if __name__ == "__main__":
    create_mock_datasets()
