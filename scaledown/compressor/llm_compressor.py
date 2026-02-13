from typing import Union, List, Optional
import time
from .base import BaseCompressor
from ..types import CompressedPrompt
from ..llm import call_llm
SCALE_DOWN_CONTEXT_PROMPT = """Used before passing messages.

Compress the following information for inter-agent sharing.

Requirements:
- preserve facts
- remove redundancy
- use dense bullet style
- <= 200 tokens
- no filler language

Return only compressed content."""
from ..types.metrics import count_tokens

class LLMCompressor(BaseCompressor):
    """
    Compressor that uses a local/configured LLM to compress context.
    Uses the agent system's LLM configuration.
    """
    def __init__(self, rate='auto', api_key=None, temperature=0.2):
        super().__init__(rate=rate, api_key=api_key)
        self.temperature = temperature

    def compress(self, context: Union[str, List[str]], prompt: Union[str, List[str]] = "", 
                 max_tokens: int = None, **kwargs) -> Union[CompressedPrompt, List[CompressedPrompt]]:
        """
        Compress context using the configured LLM.
        Note: 'prompt' argument is kept for signature compatibility but mostly unused 
        if we rely strictly on SCALE_DOWN_CONTEXT_PROMPT, 
        or it can be appended to the context.
        """
        if isinstance(context, str):
            return self._compress_single(context, prompt, max_tokens=max_tokens, **kwargs)
        elif isinstance(context, list):
            # For simplicity in this implementation, strictly sequential
            return [self._compress_single(c, prompt, max_tokens, **kwargs) for c in context]
        else:
            raise ValueError("Invalid context type.")

    def _compress_single(self, context: str, prompt: str = "", max_tokens=None, **kwargs) -> CompressedPrompt:
        start_time = time.time()
        
        # The goal is to compress the CONTEXT.
        # The prompt is the instruction for compression.
        
        original_tokens = count_tokens(context)
        
        # We use the specific system prompt for compression
        compressed_text = call_llm(
            messages=[{"role": "user", "content": context}],
            system_prompt=SCALE_DOWN_CONTEXT_PROMPT,
            json_mode=False,
            temperature=self.temperature
        )
        
        if isinstance(compressed_text, dict):
            compressed_text = str(compressed_text)
            
        latency = (time.time() - start_time) * 1000
        compressed_tokens = count_tokens(compressed_text)
        
        metrics = {
            "original_prompt_tokens": original_tokens,
            "compressed_prompt_tokens": compressed_tokens,
            "latency_ms": latency,
            "model_used": "llm-custom", # Metadata
            "timestamp": time.time()
        }
        
        return CompressedPrompt.from_api_response(
            content=compressed_text,
            raw_response=metrics
        )
