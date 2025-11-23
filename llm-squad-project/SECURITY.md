# Security Policy

## 🔒 Secure API Key Management

This project implements industry-standard security practices for handling sensitive API keys.

### ✅ What We Do Right

1. **Environment Variables**: API keys are stored in `.env` file, never hardcoded
2. **Git Exclusion**: `.env` is in `.gitignore` - keys never committed to repository
3. **Automatic Loading**: `python-dotenv` loads keys at runtime
4. **Safe for Public Repos**: Your keys remain private even if repo is public

### 🚫 What We Don't Do

- ❌ Never hardcode API keys in source code
- ❌ Never commit `.env` files to git
- ❌ Never log or print API keys
- ❌ Never share keys in documentation or examples

## 📁 File Structure

```
llm-squad-project/
├── .env                  # ← YOUR API KEYS (gitignored, NEVER commit)
├── .gitignore           # ← Contains .env exclusion
├── src/
│   └── evaluation/
│       └── api_clients.py  # ← Loads keys from environment
└── docs/
    └── API_KEYS_GUIDE.md   # ← Instructions for getting keys
```

## 🔐 API Key Storage

### Current `.env` Format

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxx...

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxx...

# Hugging Face API Key
HUGGINGFACE_API_KEY=hf_xxxxx...
```

### How Keys Are Loaded

```python
# In src/evaluation/api_clients.py
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Access keys securely
api_key = os.getenv('OPENAI_API_KEY')
```

## 🛡️ Security Checklist

Before sharing or deploying:

- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in source code
- [ ] No API keys in commit history (`git log | grep -i "key"`)
- [ ] `.env.example` provided (without real keys)
- [ ] Documentation explains how to get keys
- [ ] Spending limits set in provider dashboards

## 🚨 If Keys Are Compromised

If you accidentally commit API keys:

### Immediate Actions

1. **Revoke the exposed keys immediately** in provider dashboards:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys
   - Hugging Face: https://huggingface.co/settings/tokens

2. **Generate new keys** from the same dashboards

3. **Update your `.env` file** with the new keys

4. **Remove from git history** (if already committed):
   ```bash
   # WARNING: This rewrites history - coordinate with team first
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (use with caution!)
   git push origin --force --all
   ```

5. **Monitor usage** for any unauthorized access

### Prevention

- Use git hooks to prevent commits with keys
- Enable branch protection rules
- Use secret scanning tools (GitHub has this built-in)
- Regular key rotation (every 90 days)

## 🔍 Verification

### Check if `.env` is Protected

```bash
# Should return .env in the list
cat .gitignore | grep "\.env"

# Should NOT show .env (if keys are safe)
git status

# Should NOT contain .env
git ls-files | grep "\.env"
```

### Check for Leaked Keys

```bash
# Search for common key patterns in git history
git log --all --full-history --source --pretty=format: -S "sk-" --name-only
git log --all --full-history --source --pretty=format: -S "OPENAI_API_KEY" --name-only
```

## 🎯 Best Practices

### For Development

1. **Never use production keys in development**
2. **Use separate keys per environment** (dev, staging, prod)
3. **Set rate limits** in provider settings
4. **Monitor costs daily** during active development

### For Deployment

1. **Use environment variables** in deployment platform
2. **Rotate keys regularly** (automated if possible)
3. **Use key management services** (AWS Secrets Manager, etc.)
4. **Implement least privilege** (separate keys for different services)

### For Collaboration

1. **Share `.env.example`** (template without real values):
   ```env
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   HUGGINGFACE_API_KEY=your_huggingface_key_here
   ```

2. **Document in README** how to get keys
3. **Use team key management** (1Password, Vault, etc.)
4. **Don't share keys via Slack/email** - use secure channels

## 📊 Current Status

✅ **This project is secure:**
- `.env` file created and excluded from git
- All keys loaded from environment variables
- No hardcoded credentials in source
- Comprehensive documentation provided
- Safe to push to public GitHub

⚠️ **Note**: The API keys initially provided were invalid. Follow the [API Keys Guide](docs/API_KEYS_GUIDE.md) to obtain valid credentials.

## 📚 Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/production-best-practices)
- [Anthropic Security Guidelines](https://docs.anthropic.com/claude/docs/security)

## 🐛 Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT open a public issue**
2. Email the repository owner privately
3. Include detailed reproduction steps
4. Allow time for fix before public disclosure

## 📝 Version History

- **v1.0** (2025-11-23): Initial security implementation
  - Environment variable support added
  - `.env` file gitignored
  - API key documentation created
  - Secure loading mechanism implemented

---

**Remember**: Security is not a one-time task but an ongoing practice! 🔐
