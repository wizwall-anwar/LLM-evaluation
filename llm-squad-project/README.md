# LLM Evaluation on SQuAD 2.0 and Wikipedia Data

## Project Overview

This project evaluates Large Language Models (LLMs) on question-answering tasks using both clean benchmark datasets (SQuAD 2.0) and messy, real-world data scraped from Wikipedia. The goal is to understand how LLMs perform when faced with data wrangling challenges and noisy inputs, which more closely resembles real-world scenarios.

### Key Objectives

1. **Data Wrangling**: Scrape, clean, and structure messy Wikipedia data
2. **Question Generation**: Generate SQuAD-style questions from Wikipedia articles
3. **LLM Evaluation**: Compare multiple LLMs (GPT-4, Claude, Llama-2/Mistral) on:
   - Clean benchmark data (SQuAD 2.0)
   - Clean Wikipedia data
   - Noisy Wikipedia data
4. **AI Assistant Comparison**: Document and compare AI coding assistants (Cursor, Copilot, Claude/ChatGPT) throughout development
5. **Analysis**: Identify performance degradation patterns and effective prompting strategies

## Project Structure

```
llm-squad-project/
├── data/                          # Data storage
│   ├── raw/                       # Raw scraped data
│   ├── processed/                 # Cleaned and processed data
│   └── squad/                     # SQuAD 2.0 dataset
├── notebooks/                     # Jupyter notebooks for analysis
│   ├── 01_squad_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_squad_evaluation.ipynb
│   └── 04_final_analysis.ipynb
├── src/                           # Source code
│   ├── data_wrangling/           # Data collection and cleaning
│   │   ├── wikipedia_scraper.py
│   │   ├── clean_wikipedia.py
│   │   ├── generate_questions.py
│   │   └── add_noise.py
│   ├── evaluation/               # LLM evaluation framework
│   │   ├── evaluate_llm.py
│   │   └── api_clients.py
│   └── prompts/                  # Prompt templates
│       └── prompt_templates.py
├── results/                       # Evaluation results
│   ├── squad_baseline/
│   ├── wikipedia_clean/
│   ├── wikipedia_noisy/
│   └── prompt_experiments/
├── logs/                          # Logs and tracking
│   └── scraping_log.txt
├── docs/                          # Documentation
│   ├── ai_assistant_cursor.md
│   ├── ai_assistant_copilot.md
│   ├── ai_assistant_chatgpt.md
│   ├── ai_assistant_comparison.md
│   └── final_report.md
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd llm-squad-project
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here

# HuggingFace (optional, for inference API)
HUGGINGFACE_API_KEY=your_hf_key_here
```

**Important**: Never commit your `.env` file. It's already included in `.gitignore`.

### 5. Download NLTK Data (if needed)

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Usage

### Phase 1: Data Collection

1. **Download SQuAD 2.0**:
   ```bash
   python -c "from datasets import load_dataset; load_dataset('squad_v2')"
   ```

2. **Scrape Wikipedia**:
   ```bash
   python src/data_wrangling/wikipedia_scraper.py
   ```

3. **Clean Data**:
   ```bash
   python src/data_wrangling/clean_wikipedia.py
   ```

4. **Generate Questions**:
   ```bash
   python src/data_wrangling/generate_questions.py
   ```

### Phase 2: Evaluation

1. **Run Baseline Evaluation** (SQuAD 2.0):
   ```bash
   python src/evaluation/evaluate_llm.py --dataset squad --model gpt4
   ```

2. **Evaluate on Clean Wikipedia**:
   ```bash
   python src/evaluation/evaluate_llm.py --dataset wikipedia_clean --model gpt4
   ```

3. **Evaluate on Noisy Wikipedia**:
   ```bash
   python src/evaluation/evaluate_llm.py --dataset wikipedia_noisy --model gpt4
   ```

### Phase 3: Analysis

Open and run the Jupyter notebooks in `notebooks/` for exploratory data analysis and results visualization.

## Data Wrangling Challenges

This project intentionally includes messy data to simulate real-world scenarios:

- **HTML Parsing**: Inconsistent Wikipedia HTML structure
- **Text Cleaning**: Citations, special characters, encoding issues
- **Noise Injection**: Simulated OCR errors, typos, formatting issues
- **Quality Control**: Manual review and filtering of generated questions

## Evaluation Metrics

- **Exact Match (EM)**: Percentage of predictions matching ground truth exactly
- **F1 Score**: Token-level overlap between prediction and ground truth
- **Precision/Recall**: For answerability detection (SQuAD 2.0 includes unanswerable questions)
- **Response Time**: Latency per question
- **Token Usage**: Cost tracking per model

## Models Evaluated

1. **OpenAI**: GPT-4, GPT-3.5-turbo
2. **Anthropic**: Claude Sonnet, Claude Opus
3. **Open Source**: Llama-2 or Mistral (via HuggingFace Inference API)

## AI Assistant Comparison

Throughout this project, we document the usage of various AI coding assistants:

- **Cursor**: Code generation and refactoring
- **GitHub Copilot**: Autocomplete and suggestions
- **Claude/ChatGPT**: Architecture decisions and debugging

See `docs/ai_assistant_*.md` for detailed logs and comparisons.

## Contributing

This is a personal project for learning and demonstration purposes. However, suggestions and improvements are welcome!

## License

MIT License (or specify your preferred license)

## Contact

[Your Name/Email]

## Acknowledgments

- SQuAD 2.0 dataset by Stanford NLP
- HuggingFace for datasets and transformers libraries
- Wikipedia for the knowledge base

## Project Timeline

- **Phase 0**: Environment Setup ✓
- **Phase 1**: Data Collection and Wrangling (Tasks 1.1-2.2)
- **Phase 2**: Evaluation Framework (Tasks 3.1-3.2)
- **Phase 3**: LLM Evaluation (Tasks 4.1-4.4)
- **Phase 4**: AI Assistant Documentation (Tasks 5.1-5.4)
- **Phase 5**: Analysis and Reporting (Tasks 6.1-7.3)

## Notes

- All API keys must be kept secure and never committed to version control
- Large data files are excluded from git (see `.gitignore`)
- Estimated compute costs: ~$50-100 depending on evaluation scope
- Project designed to demonstrate both technical skills and real-world data handling

---

**Status**: Phase 0 Complete - Environment Setup ✓
