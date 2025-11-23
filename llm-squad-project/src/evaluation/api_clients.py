"""
API Clients for LLM Evaluation

Wrappers for different LLM providers:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude Sonnet, Opus)
- HuggingFace (Llama-2, Mistral via Inference API)

Includes rate limiting, error handling, and token tracking.
"""

import os
import time
import re
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseLLMClient:
    """Base class for LLM clients."""

    def __init__(self, model_name: str, rate_limit_delay: float = 1.0):
        """
        Initialize LLM client.

        Args:
            model_name: Name of the model
            rate_limit_delay: Minimum delay between API calls (seconds)
        """
        self.model_name = model_name
        self.rate_limit_delay = rate_limit_delay
        self.last_call_time = 0
        self.total_calls = 0
        self.total_tokens = 0

    def _rate_limit(self):
        """Implement rate limiting."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_call_time = time.time()

    def _extract_answer(self, response: str) -> Tuple[str, bool]:
        """
        Extract answer from model response.

        Returns:
            Tuple of (answer, is_impossible)
        """
        response = response.strip()

        # Check if marked as unanswerable
        if response.upper() == "UNANSWERABLE" or "cannot be answered" in response.lower():
            return "UNANSWERABLE", True

        # For chain-of-thought or verbose responses, try to extract final answer
        if "Answer:" in response:
            parts = response.split("Answer:")
            answer = parts[-1].strip()
        elif "answer is" in response.lower():
            # Extract after "answer is"
            match = re.search(r'answer is[:\s]+(.+?)(?:\.|$)', response, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
            else:
                answer = response
        else:
            answer = response

        # Clean up the answer
        answer = answer.strip('."\'')

        # Check again after extraction
        is_impossible = answer.upper() == "UNANSWERABLE"

        return answer, is_impossible

    def query(self, prompt: str) -> Dict:
        """
        Query the LLM with a prompt.

        Returns:
            Dictionary with 'answer', 'is_impossible', 'tokens_used', 'response_time'
        """
        raise NotImplementedError

class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""

    def __init__(self, model_name: str = "gpt-4", **kwargs):
        """Initialize OpenAI client."""
        super().__init__(model_name, **kwargs)

        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

    def query(self, prompt: str) -> Dict:
        """Query OpenAI API."""
        self._rate_limit()

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for evaluation
                max_tokens=200
            )

            response_time = time.time() - start_time
            tokens_used = response.usage.total_tokens

            self.total_calls += 1
            self.total_tokens += tokens_used

            answer_text = response.choices[0].message.content
            answer, is_impossible = self._extract_answer(answer_text)

            return {
                'answer': answer,
                'is_impossible': is_impossible,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'raw_response': answer_text
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                'answer': '',
                'is_impossible': False,
                'tokens_used': 0,
                'response_time': time.time() - start_time,
                'error': str(e)
            }

class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client."""

    def __init__(self, model_name: str = "claude-sonnet-4-5-20250929", **kwargs):
        """Initialize Anthropic client."""
        super().__init__(model_name, **kwargs)

        try:
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")

    def query(self, prompt: str) -> Dict:
        """Query Anthropic API."""
        self._rate_limit()

        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=200,
                temperature=0.0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_time = time.time() - start_time

            # Anthropic tokens
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            self.total_calls += 1
            self.total_tokens += tokens_used

            answer_text = response.content[0].text
            answer, is_impossible = self._extract_answer(answer_text)

            return {
                'answer': answer,
                'is_impossible': is_impossible,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'raw_response': answer_text
            }

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return {
                'answer': '',
                'is_impossible': False,
                'tokens_used': 0,
                'response_time': time.time() - start_time,
                'error': str(e)
            }

class HuggingFaceClient(BaseLLMClient):
    """HuggingFace Inference API client."""

    def __init__(self, model_name: str = "meta-llama/Llama-2-70b-chat-hf", **kwargs):
        """Initialize HuggingFace client."""
        super().__init__(model_name, **kwargs)

        try:
            import requests
            self.requests = requests
            api_key = os.getenv('HUGGINGFACE_API_KEY')
            if not api_key:
                raise ValueError("HUGGINGFACE_API_KEY not found in environment")
            self.api_key = api_key
            self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        except ImportError:
            raise ImportError("requests library not installed")

    def query(self, prompt: str) -> Dict:
        """Query HuggingFace Inference API."""
        self._rate_limit()

        start_time = time.time()

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }

            response = self.requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            response_time = time.time() - start_time

            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")

            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                answer_text = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                answer_text = result.get('generated_text', result.get('text', ''))
            else:
                answer_text = str(result)

            # Estimate tokens (rough approximation)
            tokens_used = len(prompt.split()) + len(answer_text.split())

            self.total_calls += 1
            self.total_tokens += tokens_used

            answer, is_impossible = self._extract_answer(answer_text)

            return {
                'answer': answer,
                'is_impossible': is_impossible,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'raw_response': answer_text
            }

        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            return {
                'answer': '',
                'is_impossible': False,
                'tokens_used': 0,
                'response_time': time.time() - start_time,
                'error': str(e)
            }

class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing without API calls."""

    def __init__(self, model_name: str = "mock-gpt-4", **kwargs):
        """Initialize mock client."""
        super().__init__(model_name, **kwargs)

    def query(self, prompt: str) -> Dict:
        """Generate mock response."""
        self._rate_limit()

        start_time = time.time()
        time.sleep(0.1)  # Simulate API latency

        # Simple rule-based mock response
        if "unanswerable" in prompt.lower() or "when" in prompt.lower():
            # Randomly mark some as unanswerable
            import random
            if random.random() < 0.3:
                answer = "UNANSWERABLE"
                is_impossible = True
            else:
                answer = "1991"  # Mock answer
                is_impossible = False
        else:
            answer = "This is a mock answer based on the context."
            is_impossible = False

        response_time = time.time() - start_time
        tokens_used = 50  # Mock token count

        self.total_calls += 1
        self.total_tokens += tokens_used

        return {
            'answer': answer,
            'is_impossible': is_impossible,
            'tokens_used': tokens_used,
            'response_time': response_time,
            'raw_response': answer
        }

def get_client(provider: str, model: str, **kwargs) -> BaseLLMClient:
    """
    Factory function to get appropriate LLM client.

    Args:
        provider: 'openai', 'anthropic', 'huggingface', or 'mock'
        model: Model name
        **kwargs: Additional arguments

    Returns:
        LLM client instance
    """
    clients = {
        'openai': OpenAIClient,
        'anthropic': AnthropicClient,
        'huggingface': HuggingFaceClient,
        'mock': MockLLMClient
    }

    if provider not in clients:
        available = ', '.join(clients.keys())
        raise ValueError(f"Unknown provider '{provider}'. Available: {available}")

    return clients[provider](model_name=model, **kwargs)

if __name__ == "__main__":
    # Test with mock client
    print("Testing LLM Clients")
    print("="*60)

    client = get_client('mock', 'mock-gpt-4')

    test_prompt = """Text: Python was created by Guido van Rossum in 1991.
Question: When was Python created?
Answer:"""

    print("Querying mock client...")
    result = client.query(test_prompt)

    print(f"\nAnswer: {result['answer']}")
    print(f"Is impossible: {result['is_impossible']}")
    print(f"Tokens used: {result['tokens_used']}")
    print(f"Response time: {result['response_time']:.3f}s")

    print(f"\nTotal calls: {client.total_calls}")
    print(f"Total tokens: {client.total_tokens}")

    print("\n" + "="*60)
    print("Client test successful!")
