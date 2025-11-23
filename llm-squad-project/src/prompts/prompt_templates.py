"""
Prompt Templates for LLM Evaluation

Provides different prompting strategies:
- Zero-shot: Direct question answering
- Few-shot: With examples
- Chain-of-Thought: Step-by-step reasoning
- Custom: For specific model requirements
"""

from typing import List, Dict, Optional

class PromptTemplate:
    """Base class for prompt templates."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def format(self, context: str, question: str, **kwargs) -> str:
        """Format the prompt with context and question."""
        raise NotImplementedError

class ZeroShotPrompt(PromptTemplate):
    """Simple zero-shot prompt template."""

    def __init__(self):
        super().__init__(
            name="zero_shot",
            description="Direct question answering without examples"
        )

    def format(self, context: str, question: str, **kwargs) -> str:
        """Format zero-shot prompt."""
        return f"""Read the following text and answer the question. If the answer cannot be found in the text, respond with "UNANSWERABLE".

Text:
{context}

Question: {question}

Answer:"""

class FewShotPrompt(PromptTemplate):
    """Few-shot prompt with examples."""

    def __init__(self, examples: Optional[List[Dict]] = None):
        super().__init__(
            name="few_shot",
            description="Question answering with example demonstrations"
        )
        self.examples = examples or self._get_default_examples()

    def _get_default_examples(self) -> List[Dict]:
        """Get default few-shot examples."""
        return [
            {
                "context": "The Eiffel Tower is located in Paris, France. It was built in 1889 and stands 330 meters tall.",
                "question": "Where is the Eiffel Tower located?",
                "answer": "Paris, France"
            },
            {
                "context": "Python is a high-level programming language created by Guido van Rossum in 1991.",
                "question": "When was Python created?",
                "answer": "1991"
            },
            {
                "context": "The human heart has four chambers: two atria and two ventricles.",
                "question": "How many lungs does the human heart have?",
                "answer": "UNANSWERABLE"
            }
        ]

    def format(self, context: str, question: str, **kwargs) -> str:
        """Format few-shot prompt with examples."""
        examples_text = "\n\n".join([
            f"Text: {ex['context']}\nQuestion: {ex['question']}\nAnswer: {ex['answer']}"
            for ex in self.examples
        ])

        return f"""Answer questions based on the provided text. If the answer cannot be found in the text, respond with "UNANSWERABLE".

Examples:

{examples_text}

Now answer this question:

Text: {context}
Question: {question}
Answer:"""

class ChainOfThoughtPrompt(PromptTemplate):
    """Chain-of-thought prompting for step-by-step reasoning."""

    def __init__(self):
        super().__init__(
            name="chain_of_thought",
            description="Step-by-step reasoning before answering"
        )

    def format(self, context: str, question: str, **kwargs) -> str:
        """Format chain-of-thought prompt."""
        return f"""Read the text and answer the question. Think step-by-step:
1. First, identify what information the question is asking for
2. Search the text for relevant information
3. If found, extract the answer
4. If not found, respond with "UNANSWERABLE"

Text:
{context}

Question: {question}

Let's think step-by-step:"""

class InstructionPrompt(PromptTemplate):
    """Detailed instruction-based prompt."""

    def __init__(self):
        super().__init__(
            name="instruction",
            description="Detailed instructions for answer extraction"
        )

    def format(self, context: str, question: str, **kwargs) -> str:
        """Format instruction prompt."""
        return f"""You are a helpful reading comprehension assistant. Your task is to answer questions based ONLY on the information provided in the given text.

Instructions:
- Read the text carefully
- Find the specific information that answers the question
- Extract only the relevant answer from the text
- Keep your answer concise and accurate
- If the answer is not in the text, respond with exactly "UNANSWERABLE"
- Do not use external knowledge
- Do not make assumptions

Text:
{context}

Question: {question}

Answer (keep it brief and extract directly from the text):"""

class RobustPrompt(PromptTemplate):
    """Prompt designed for noisy/messy data."""

    def __init__(self):
        super().__init__(
            name="robust",
            description="Handles messy data with typos and formatting issues"
        )

    def format(self, context: str, question: str, **kwargs) -> str:
        """Format robust prompt for messy data."""
        return f"""Read the text below and answer the question. Note: The text may contain typos, formatting issues, or encoding errors. Try to understand the meaning despite any errors.

If you can find the answer despite errors in the text, provide it. If the information is genuinely not present (not just hard to read), respond with "UNANSWERABLE".

Text:
{context}

Question: {question}

Answer:"""

class PromptRegistry:
    """Registry of available prompt templates."""

    def __init__(self):
        self.templates = {
            'zero_shot': ZeroShotPrompt(),
            'few_shot': FewShotPrompt(),
            'chain_of_thought': ChainOfThoughtPrompt(),
            'instruction': InstructionPrompt(),
            'robust': RobustPrompt()
        }

    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self.templates:
            available = ', '.join(self.templates.keys())
            raise ValueError(f"Unknown template '{name}'. Available: {available}")
        return self.templates[name]

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {'name': name, 'description': template.description}
            for name, template in self.templates.items()
        ]

    def add_template(self, name: str, template: PromptTemplate):
        """Add a custom template to the registry."""
        self.templates[name] = template

# Global registry instance
prompt_registry = PromptRegistry()

def get_prompt(template_name: str, context: str, question: str, **kwargs) -> str:
    """
    Convenience function to get formatted prompt.

    Args:
        template_name: Name of the template to use
        context: Context text
        question: Question to answer
        **kwargs: Additional arguments for the template

    Returns:
        Formatted prompt string
    """
    template = prompt_registry.get_template(template_name)
    return template.format(context, question, **kwargs)

if __name__ == "__main__":
    # Test the prompt templates
    print("Testing Prompt Templates")
    print("="*60)

    context = "Artificial intelligence (AI) is intelligence demonstrated by machines. The field was founded in 1956."
    question = "When was AI founded?"

    registry = PromptRegistry()

    print("\nAvailable templates:")
    for t in registry.list_templates():
        print(f"  - {t['name']}: {t['description']}")

    print("\n" + "="*60)
    print("ZERO-SHOT TEMPLATE:")
    print("="*60)
    print(get_prompt('zero_shot', context, question))

    print("\n" + "="*60)
    print("FEW-SHOT TEMPLATE:")
    print("="*60)
    print(get_prompt('few_shot', context, question)[:500] + "...")

    print("\n" + "="*60)
    print("CHAIN-OF-THOUGHT TEMPLATE:")
    print("="*60)
    print(get_prompt('chain_of_thought', context, question))

    print("\n" + "="*60)
    print("All templates tested successfully!")
