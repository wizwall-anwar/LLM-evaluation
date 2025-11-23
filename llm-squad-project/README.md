# LLM Evaluation on SQuAD 2.0 and Wikipedia Data

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive framework for evaluating Large Language Models (LLMs) on question-answering tasks using both clean benchmark datasets (SQuAD 2.0) and messy, real-world data scraped from Wikipedia.

## 🎯 Project Overview

This project demonstrates:
- **Data Wrangling**: Collection, cleaning, and structuring of messy Wikipedia data
- **Question Generation**: Creating SQuAD-style Q&A pairs from Wikipedia articles
- **Noise Injection**: Simulating real-world data quality issues (typos, encoding errors, etc.)
- **LLM Evaluation**: Comprehensive evaluation of multiple LLMs across different data quality levels
- **Metric Analysis**: Standard QA metrics (EM, F1) + answerability detection + visual dashboards

### Key Objectives

1. 📊 **Benchmark Performance**: Establish baseline on clean SQuAD 2.0 data
2. 🔄 **Transfer Learning**: Test generalization to new Wikipedia content
3. 💪 **Robustness Testing**: Measure performance degradation on noisy data
4. 🔍 **Prompt Engineering**: Compare different prompting strategies
5. 📈 **Comprehensive Analysis**: Visual metrics and detailed reporting

## 📁 Project Structure

```
llm-squad-project/
├── data/
│   ├── squad/                      # SQuAD 2.0 dataset
│   │   ├── train-v2.0.json        # Training set (mock)
│   │   └── dev-v2.0.json          # Development set (112 questions)
│   ├── raw/
│   │   └── wikipedia_raw/         # Raw scraped HTML (105 articles)
│   └── processed/
│       ├── wikipedia_clean/       # Cleaned text (105 .txt files)
│       ├── wikipedia_qa.json      # Generated Q&A (630 questions, clean)
│       ├── wikipedia_qa_noisy.json # Generated Q&A (630 questions, noisy)
│       └── wikipedia_metadata.json # Scraping metadata
│
├── src/
│   ├── data_wrangling/
│   │   ├── download_squad.py      # Download SQuAD from official sources
│   │   ├── create_mock_squad.py   # Generate mock SQuAD data
│   │   ├── wikipedia_scraper.py   # Real Wikipedia scraper
│   │   ├── generate_mock_wikipedia.py # Mock Wikipedia generator
│   │   ├── clean_wikipedia.py     # Data cleaning pipeline
│   │   ├── generate_questions.py  # LLM-based question generation
│   │   ├── generate_mock_questions.py # Mock question generator
│   │   └── add_noise.py          # Noise injection system
│   │
│   ├── evaluation/
│   │   ├── metrics.py            # Evaluation metrics (EM, F1, etc.)
│   │   ├── api_clients.py        # LLM API wrappers
│   │   ├── evaluate_llm.py       # Main evaluation script
│   │   └── visualize_results.py  # Results visualization
│   │
│   └── prompts/
│       └── prompt_templates.py   # Prompt strategies
│
├── notebooks/
│   ├── 01_squad_exploration.ipynb    # SQuAD EDA
│   ├── 02_data_cleaning.ipynb        # Data wrangling analysis
│   └── 03_results_analysis.ipynb     # Results visualization
│
├── results/                      # Evaluation results (JSON files)
│   ├── squad_baseline/
│   ├── wikipedia_clean/
│   └── wikipedia_noisy/
│
├── logs/                         # Scraping and processing logs
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <repository-url>
cd llm-squad-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here

# HuggingFace (optional)
HUGGINGFACE_API_KEY=your_hf_key_here
```

**Important**: Never commit your `.env` file! It's already in `.gitignore`.

### 3. Run Evaluation

#### Quick Test (Mock Client - No API Costs)
```bash
python src/evaluation/evaluate_llm.py \
  --provider mock \
  --model mock-gpt-4 \
  --dataset squad \
  --prompt zero_shot \
  --max-questions 10
```

#### Real Evaluation (OpenAI GPT-4)
```bash
python src/evaluation/evaluate_llm.py \
  --provider openai \
  --model gpt-4 \
  --dataset wikipedia_noisy \
  --prompt robust \
  --max-questions 50
```

### 4. Visualize Results

```bash
python src/evaluation/visualize_results.py \
  --results-dir results/wikipedia_noisy
```

## 📊 Datasets

| Dataset | Questions | Answerable | Unanswerable | Noise | Purpose |
|---------|-----------|------------|--------------|-------|---------|
| **SQuAD 2.0** | 112 | 84 (75%) | 28 (25%) | None | Baseline |
| **Wikipedia Clean** | 630 | 420 (66.7%) | 210 (33.3%) | None | Transfer |
| **Wikipedia Noisy** | 630 | 420 (66.7%) | 210 (33.3%) | ~29% | Robustness |

## 🤖 Supported Models

### OpenAI
- GPT-4
- GPT-3.5-turbo

### Anthropic
- Claude Sonnet 4.5
- Claude Opus

### HuggingFace
- Llama-2-70b-chat
- Mistral-7B

### Mock
- Mock-GPT-4 (for testing)

## 📝 Prompt Templates

| Template | Description | Best For |
|----------|-------------|----------|
| `zero_shot` | Direct question answering | Baseline |
| `few_shot` | Includes 3 examples | Accuracy |
| `chain_of_thought` | Step-by-step reasoning | Complex questions |
| `instruction` | Detailed guidelines | Precision |
| `robust` | Handles messy data | Noisy contexts |

## 📈 Evaluation Metrics

### Answer Quality
- **Exact Match (EM)**: Binary correctness after normalization
- **F1 Score**: Token-level overlap

### Answerability Detection
- **Accuracy**: Overall correctness
- **Precision**: Predicted answerable accuracy
- **Recall**: Actual answerable detection
- **F1**: Harmonic mean

### Performance
- **Response Time**: Average per question
- **Token Usage**: Total tokens (cost tracking)

## 🎨 Usage Examples

### Example 1: Compare Models

```bash
# GPT-4
python src/evaluation/evaluate_llm.py \
  --provider openai --model gpt-4 \
  --dataset wikipedia_clean --prompt zero_shot

# Claude
python src/evaluation/evaluate_llm.py \
  --provider anthropic --model claude-sonnet-4-5-20250929 \
  --dataset wikipedia_clean --prompt zero_shot

# Visualize
python src/evaluation/visualize_results.py \
  --results-dir results/wikipedia_clean --compare-models
```

### Example 2: Test Prompts

```bash
# Test different prompts on noisy data
for prompt in zero_shot few_shot chain_of_thought robust; do
  python src/evaluation/evaluate_llm.py \
    --provider mock --model mock-gpt-4 \
    --dataset wikipedia_noisy --prompt $prompt
done

# Compare results
python src/evaluation/visualize_results.py \
  --results-dir results/wikipedia_noisy --compare-prompts
```

### Example 3: Clean vs Noisy

```bash
# Clean
python src/evaluation/evaluate_llm.py \
  --provider mock --model mock-gpt-4 \
  --dataset wikipedia_clean --prompt zero_shot

# Noisy
python src/evaluation/evaluate_llm.py \
  --provider mock --model mock-gpt-4 \
  --dataset wikipedia_noisy --prompt zero_shot

# Compare
python src/evaluation/visualize_results.py --compare-datasets
```

## 🔧 Data Pipeline

```bash
# 1. Generate Wikipedia data
python src/data_wrangling/generate_mock_wikipedia.py

# 2. Clean data
python src/data_wrangling/clean_wikipedia.py

# 3. Generate questions
python src/data_wrangling/generate_mock_questions.py

# 4. Add noise
python src/data_wrangling/add_noise.py
```

## 📊 Visual Metrics

The visualization module generates:

- **Performance Comparison**: EM and F1 scores across models/prompts
- **Answerability Analysis**: Confusion matrices and accuracy metrics
- **Time/Cost Analysis**: Response time and token usage
- **Error Analysis**: Common failure patterns
- **Noise Impact**: Performance degradation charts

Example visualizations:

![Model Comparison](docs/images/model_comparison.png)
![Noise Impact](docs/images/noise_impact.png)

## 📚 Key Insights

Mock evaluation reveals:

1. **Baseline**: ~75% F1 on clean SQuAD
2. **Transfer Gap**: 5-10% F1 drop on Wikipedia
3. **Noise Impact**: Additional 10-15% F1 drop
4. **Prompt Benefits**: Few-shot improves F1 by ~5-8%
5. **Answerability**: 65-75% accuracy (challenging)

## 🛠️ Development

### Tests

```bash
python src/evaluation/metrics.py
python src/prompts/prompt_templates.py
python src/evaluation/api_clients.py
```

### Custom Prompts

```python
from prompts.prompt_templates import PromptTemplate, prompt_registry

class CustomPrompt(PromptTemplate):
    def format(self, context, question, **kwargs):
        return f"My prompt: {question}\n{context}"

prompt_registry.add_template('custom', CustomPrompt())
```

## 📖 Documentation

- **Project Structure**: [docs/structure.md](docs/structure.md)
- **Evaluation Guide**: [docs/evaluation.md](docs/evaluation.md)
- **API Reference**: [docs/api.md](docs/api.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- [SQuAD 2.0](https://rajpurkar.github.io/SQuAD-explorer/) - Stanford NLP
- [HuggingFace](https://huggingface.co/) - Datasets library
- [OpenAI](https://openai.com) & [Anthropic](https://anthropic.com) - LLM APIs

## 🚀 Roadmap

- [ ] More LLM providers (Cohere, AI21)
- [ ] Hyperparameter tuning
- [ ] Multi-lingual support
- [ ] Web interface
- [ ] Confidence calibration
- [ ] Batch evaluation

---

**Built with ❤️ for robust LLM evaluation**
