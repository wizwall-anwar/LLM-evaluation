# API Keys Setup and Troubleshooting Guide

## 🔐 Security First

Your API keys are now stored securely in `.env` file which is:
- ✅ Excluded from git via `.gitignore`
- ✅ Never committed to the repository
- ✅ Loaded automatically by the application
- ✅ Safe for public repositories

## ⚠️ Current Status

The API keys you provided returned authentication errors:

| Provider | Error | Status Code |
|----------|-------|-------------|
| OpenAI | "Access denied" | 403 Forbidden |
| Anthropic | "invalid x-api-key" | 401 Unauthorized |
| Hugging Face | "Access denied" | 403 Forbidden |

## 🔑 How to Get Valid API Keys

### OpenAI (GPT-4, GPT-3.5-turbo)

1. **Sign up**: https://platform.openai.com/signup
2. **Add payment method**: https://platform.openai.com/account/billing
3. **Create API key**: https://platform.openai.com/api-keys
4. **Key format**: `sk-proj-...` (starts with `sk-`)
5. **Pricing**: https://openai.com/api/pricing/

**Important Notes:**
- Free trial credits are limited ($5)
- Requires valid credit card after trial
- GPT-4: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- GPT-3.5-turbo: Much cheaper alternative (~$0.0015 per 1K tokens)

### Anthropic (Claude Sonnet, Opus)

1. **Sign up**: https://console.anthropic.com/
2. **Request access**: Fill out the API access form
3. **Create API key**: Console → API Keys
4. **Key format**: `sk-ant-...` (starts with `sk-ant-`)
5. **Pricing**: https://www.anthropic.com/api

**Important Notes:**
- Requires approval process (can take 1-2 days)
- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`): ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- Claude Haiku 3.5 (`claude-3-5-haiku-20241022`): Faster and cheaper option

### Hugging Face (Llama-2, Mistral, etc.)

1. **Sign up**: https://huggingface.co/join
2. **Create token**: Settings → Access Tokens → New Token
3. **Select permissions**: Read access is sufficient
4. **Key format**: `hf_...` (starts with `hf_`)
5. **Pricing**: FREE for many models!

**Important Notes:**
- Many models are free to use
- Some models require accepting terms (visit model page first)
- Rate limits apply (slower than paid APIs)
- Popular models: `meta-llama/Llama-2-7b-chat-hf`, `mistralai/Mistral-7B-Instruct-v0.2`

## 📝 Updating Your `.env` File

Once you have valid keys, update the `.env` file:

```bash
# Edit the .env file
nano .env  # or use your preferred editor

# Update the keys:
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY_HERE
HUGGINGFACE_API_KEY=hf_YOUR_ACTUAL_KEY_HERE
```

**NEVER commit the .env file to git!** It's already in `.gitignore`.

## ✅ Testing Your Keys

Test each provider individually:

```bash
# Test OpenAI
python src/evaluation/evaluate_llm.py --provider openai --model gpt-3.5-turbo --dataset squad --prompt zero_shot --max-questions 5

# Test Anthropic
python src/evaluation/evaluate_llm.py --provider anthropic --model claude-sonnet-4-5-20250929 --dataset squad --prompt zero_shot --max-questions 5

# Test Hugging Face
python src/evaluation/evaluate_llm.py --provider huggingface --model meta-llama/Llama-2-7b-chat-hf --dataset squad --prompt zero_shot --max-questions 5
```

Start with small samples (5-10 questions) to verify everything works before running full evaluations.

## 💰 Cost Estimation

For a full evaluation (630 questions across 3 datasets = 1,890 questions):

| Provider | Model | Est. Cost | Speed |
|----------|-------|-----------|-------|
| OpenAI | GPT-4 | $5-10 | Fast |
| OpenAI | GPT-3.5-turbo | $0.50-1 | Fast |
| Anthropic | Claude Sonnet | $3-6 | Fast |
| Anthropic | Claude Haiku | $0.50-1 | Very Fast |
| Hugging Face | Llama-2-7b | FREE | Slow |

**Recommendation**: Start with Hugging Face (free) or GPT-3.5-turbo (cheap) to validate the system.

## 🔒 Security Best Practices

1. **Never share your .env file**
2. **Rotate keys regularly** (every 90 days)
3. **Use environment-specific keys** (dev vs. production)
4. **Monitor usage** in provider dashboards
5. **Set spending limits** in provider settings
6. **Revoke keys immediately** if compromised

## 🚀 Running Without Real APIs

The mock client provides full functionality without API costs:

```bash
# Run comprehensive evaluation with mock client
python src/evaluation/evaluate_llm.py --provider mock --model mock-gpt-4 --dataset squad --prompt zero_shot --max-questions 100
```

This is perfect for:
- Testing the pipeline
- Developing visualizations
- Demonstrating the system
- Educational purposes

## 📊 Current Demo Results

The system has been tested with the mock client and is fully functional:

- ✅ 3 datasets evaluated (SQuAD, Wikipedia Clean, Wikipedia Noisy)
- ✅ Multiple prompt strategies tested
- ✅ Comprehensive visualizations generated
- ✅ All metrics calculated correctly
- ✅ Results saved and exportable

**When you get valid API keys, the system will work exactly the same way, but with real LLM responses!**

## 🆘 Troubleshooting

### Error: "OPENAI_API_KEY not found in environment"
- Check `.env` file exists in project root
- Verify key name is exactly `OPENAI_API_KEY`
- Restart terminal/IDE after updating `.env`

### Error: "Access denied" (403)
- Key is invalid or expired
- Key lacks necessary permissions
- Billing not set up (OpenAI)
- Daily/monthly quota exceeded

### Error: "invalid x-api-key" (401)
- Key format is incorrect
- Key was revoked
- Account not activated

### Error: "Rate limit exceeded" (429)
- Too many requests per minute
- Increase `rate_limit_delay` in code
- Wait and retry

## 📞 Support

- **OpenAI**: https://help.openai.com/
- **Anthropic**: support@anthropic.com
- **Hugging Face**: https://discuss.huggingface.co/

## 🎯 Next Steps

1. Get valid API keys from at least one provider
2. Update `.env` file with the new keys
3. Test with small sample (5-10 questions)
4. Run full evaluation if tests pass
5. Compare results across providers and prompts!

The infrastructure is ready - you just need valid credentials! 🚀
