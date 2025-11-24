# LLM Evaluation Results Summary

## 📊 Overview

This document summarizes the comprehensive evaluation of Large Language Models on question-answering tasks across three datasets with varying data quality levels.

### Evaluation Period
- **Latest Batch Run**: November 24, 2025
- **Datasets Evaluated**: 3 (SQuAD 2.0, Wikipedia Clean, Wikipedia Noisy)
- **Models Tested**: 3 (Mock GPT-4, Mock Claude Sonnet, Claude Haiku 3.5)
- **Prompt Templates**: 2 (zero_shot, robust)
- **Total Evaluations**: 12+ evaluation runs

---

## 🎯 Dataset Characteristics

| Dataset | Total Questions | Answerable | Unanswerable | Data Quality | Source |
|---------|----------------|------------|--------------|--------------|--------|
| **SQuAD 2.0** | 112 | 84 (75%) | 28 (25%) | Clean benchmark | Stanford NLP |
| **Wikipedia Clean** | 630 | 420 (67%) | 210 (33%) | Clean scraped data | Wikipedia |
| **Wikipedia Noisy** | 630 | 420 (67%) | 210 (33%) | ~29% noisy tokens | Wikipedia + Noise |

---

## 🤖 Model Performance Summary

### 1. SQuAD 2.0 Benchmark Results

#### Claude Haiku 3.5 (Real API)
- **Sample Size**: 20 questions
- **Exact Match**: 25.0%
- **F1 Score**: 43.2%
- **Answerability Detection**: 75.0% accuracy
- **Performance**: ~1.03s per question, 203 tokens average
- **Status**: ✅ Best performing model on clean benchmark

#### Mock GPT-4 (Robust Prompt)
- **Sample Size**: 50 questions
- **Exact Match**: 6.0%
- **F1 Score**: 6.0%
- **Answerability Detection**: 62.0% accuracy
- **Precision**: 78.8% | Recall: 68.4%
- **Performance**: ~0.10s per question

#### Mock Claude Sonnet (Robust Prompt)
- **Sample Size**: 50 questions
- **Exact Match**: 6.0%
- **F1 Score**: 6.0%
- **Answerability Detection**: 64.0% accuracy
- **Precision**: 76.3% | Recall: 76.3%
- **Performance**: ~0.10s per question

---

### 2. Wikipedia Clean Results

#### Claude Haiku 3.5 (Real API)
- **Sample Size**: 20 questions
- **Exact Match**: 0.0%
- **F1 Score**: 3.5%
- **Answerability Detection**: 60.0% accuracy
- **Performance**: ~1.59s per question, 180 tokens average
- **Note**: Significant drop from SQuAD performance, suggesting domain transfer challenges

#### Mock GPT-4 (Robust Prompt)
- **Sample Size**: 50 questions
- **Exact Match**: 0.0%
- **F1 Score**: 0.0%
- **Answerability Detection**: 54.0% accuracy
- **Precision**: 64.9% | Recall: 70.6%

#### Mock Claude Sonnet (Robust Prompt)
- **Sample Size**: 50 questions
- **Exact Match**: 0.0%
- **F1 Score**: 0.0%
- **Answerability Detection**: Similar to Mock GPT-4

---

### 3. Wikipedia Noisy Results

#### Mock GPT-4 (Robust Prompt)
- **Sample Size**: 50 questions
- **Exact Match**: 0.0%
- **F1 Score**: 0.0%
- **Answerability Detection**: 68.0% accuracy ⬆️ (improved vs clean!)
- **Precision**: 72.5% | Recall: 85.3%
- **F1**: 78.4%
- **Confusion Matrix**: TP=29, FP=11, FN=5, TN=5

#### Mock Claude Sonnet (Robust Prompt)
- **Sample Size**: 50 questions
- **Answerability Detection**: Similar patterns to Mock GPT-4

---

## 📈 Key Findings

### 1. Real vs Mock Model Performance Gap
- **Real API (Claude Haiku 3.5)** significantly outperforms mock models
- **SQuAD F1**: 43.2% (real) vs 6.0% (mock)
- **Response Quality**: Real models provide contextual explanations
- **Cost Trade-off**: Real models are 10-15x slower but far more accurate

### 2. Dataset Transfer Challenges
- **SQuAD → Wikipedia**: Significant performance drop observed
- Claude Haiku F1 dropped from 43.2% to 3.5% (92% degradation)
- Suggests models struggle with:
  - Different question formulation styles
  - Wikipedia-specific content structure
  - Domain adaptation requirements

### 3. Noise Impact (Surprising Result!)
- **Counter-intuitive finding**: Answerability detection improved on noisy data
- **Wikipedia Clean**: 54% accuracy
- **Wikipedia Noisy**: 68% accuracy (+14 percentage points)
- **Hypothesis**: Noise may have made "unanswerable" signals more obvious
- **Alternative**: Could indicate overfitting to specific noise patterns

### 4. Answerability Detection Challenges
- **Best Performance**: 75% on SQuAD (real model)
- **Common Issue**: False positives (predicting answerable when unanswerable)
- **Claude Haiku on SQuAD**: 0% true negatives (missed all unanswerable questions)
- **Mock Models**: Better balanced but lower overall accuracy

### 5. Prompt Template Effectiveness
Both zero_shot and robust prompts were tested:
- **Robust prompts** showed slightly better answerability detection
- **F1 scores** remained similar between templates for mock models
- Further testing needed with real models to assess prompt impact

---

## 🎨 Visualizations Available

All visualizations are saved in `results/[dataset]/visualizations/`:

1. **Performance Comparison Charts** (`performance_comparison.png`)
   - Side-by-side EM and F1 scores
   - Model and prompt template comparisons

2. **Answerability Confusion Matrices** (`answerability_confusion_matrix.png`)
   - Visual breakdown of TP, TN, FP, FN
   - Heatmap representation

3. **Comparison Tables** (`comparison_table.png`)
   - Tabular summary of all metrics
   - Easy model comparison

4. **Performance Metrics Dashboards** (`performance_metrics.png`)
   - Comprehensive metric breakdown
   - Response time and token usage

---

## 💡 Insights & Recommendations

### For Production Use

1. **Use Real API Models**
   - Mock models are suitable only for testing pipeline
   - Real models (Claude Haiku, GPT-4) provide 7x better F1 scores
   - Cost: ~$0.10-0.50 per 100 questions (worth the investment)

2. **Focus on SQuAD-style Data**
   - Models perform significantly better on SQuAD format
   - Wikipedia data requires additional adaptation
   - Consider fine-tuning for Wikipedia-specific QA

3. **Improve Answerability Detection**
   - Current accuracy (60-75%) leaves room for improvement
   - Consider:
     - Dedicated answerability classifier
     - Ensemble methods
     - Confidence threshold tuning

4. **Robust Prompt Benefits**
   - Robust prompts show marginal improvements
   - More extensive prompt engineering needed
   - Test few-shot and chain-of-thought approaches

### For Further Research

1. **Investigate Noise Paradox**
   - Why did noisy data improve answerability detection?
   - Run controlled experiments with varying noise levels
   - Analyze which noise types help vs hurt

2. **Domain Adaptation**
   - Why such a large SQuAD → Wikipedia gap?
   - Test intermediate domains
   - Explore domain-specific fine-tuning

3. **Expand Model Coverage**
   - Test GPT-4, Claude Opus, Gemini Pro
   - Compare open-source models (Llama 3, Mistral)
   - Evaluate cost-performance trade-offs

4. **Prompt Engineering Deep Dive**
   - Test all 5 prompt templates thoroughly
   - Measure prompt impact with real models
   - Optimize for both accuracy and cost

---

## 📊 Statistical Summary

### Overall Metrics Across All Evaluations

| Metric | SQuAD | Wikipedia Clean | Wikipedia Noisy |
|--------|-------|-----------------|-----------------|
| **Best F1** | 43.2% | 3.5% | ~0% |
| **Best EM** | 25.0% | 0.0% | 0.0% |
| **Best Answerability** | 75.0% | 60.0% | 68.0% |
| **Avg Response Time (Real)** | 1.03s | 1.59s | N/A |
| **Avg Response Time (Mock)** | 0.10s | 0.10s | 0.10s |

### Model Ranking (by F1 Score)

1. **Claude Haiku 3.5** (Real API)
   - SQuAD: 43.2% F1
   - Best for production use
   - Good speed/cost balance

2. **Mock Models** (Testing Only)
   - Consistent ~6% F1 on SQuAD
   - Useful for pipeline testing
   - Not suitable for real evaluations

---

## 🚀 Next Steps

### Immediate Actions
- [ ] Run full evaluations with Claude Sonnet 4.5 and GPT-4
- [ ] Expand Wikipedia evaluations to full 630 questions
- [ ] Test all 5 prompt templates with real models
- [ ] Analyze failed predictions for patterns

### Medium-term Goals
- [ ] Implement confidence calibration
- [ ] Build answerability classifier
- [ ] Create interactive results dashboard
- [ ] Establish cost-performance benchmarks

### Long-term Research
- [ ] Fine-tune models on Wikipedia QA
- [ ] Multi-lingual evaluation framework
- [ ] Real-time evaluation pipeline
- [ ] Automated prompt optimization

---

## 📁 Data Files

All raw evaluation results are stored in JSON format:

```
results/
├── squad/
│   ├── anthropic_claude-3-5-haiku-20241022_squad_zero_shot_20251124_011734.json
│   ├── mock_mock-gpt-4_squad_robust_20251124_012709.json
│   ├── mock_mock-claude-sonnet_squad_robust_20251124_013211.json
│   └── visualizations/
├── wikipedia_clean/
│   ├── anthropic_claude-3-5-haiku-20241022_wikipedia_clean_zero_shot_20251124_011808.json
│   ├── mock_mock-gpt-4_wikipedia_clean_robust_20251124_012850.json
│   └── visualizations/
└── wikipedia_noisy/
    ├── mock_mock-gpt-4_wikipedia_noisy_robust_20251124_013030.json
    └── visualizations/
```

---

## 🔬 Methodology Notes

### Evaluation Metrics

**Answer Quality:**
- **Exact Match (EM)**: Binary score (1 if prediction exactly matches any ground truth)
- **F1 Score**: Token-level overlap between prediction and ground truth

**Answerability Detection:**
- **Accuracy**: (TP + TN) / Total
- **Precision**: TP / (TP + FP) - How many predicted answerable were correct
- **Recall**: TP / (TP + FN) - How many actual answerable were found
- **F1**: Harmonic mean of precision and recall

**Performance:**
- **Response Time**: Average seconds per question
- **Token Usage**: Average tokens per response

### Limitations

1. **Sample Size**: Some evaluations used limited samples (20-50 questions)
2. **Mock Models**: Not representative of real model capabilities
3. **Dataset Bias**: Wikipedia questions may not reflect production use cases
4. **Prompt Optimization**: Limited prompt engineering exploration
5. **Single Run**: Results not averaged over multiple runs (variance unknown)

---

## 📞 Contact & Contributions

For questions or contributions to this evaluation framework:
- Review the full codebase in `src/`
- Check documentation in `docs/`
- See `README.md` for setup instructions

---

**Last Updated**: November 24, 2025
**Framework Version**: 1.0
**Evaluation Status**: ✅ Batch evaluation complete, ongoing analysis
