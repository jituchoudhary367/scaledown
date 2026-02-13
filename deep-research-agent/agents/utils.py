import os
import traceback
from dotenv import load_dotenv
load_dotenv()

from scaledown.compressor import ScaleDownCompressor
from scaledown.pipeline import Pipeline
from scaledown.llm import call_llm, get_llm

def compress_context(text: str) -> str:
    """
    Compresses the context using a Scaledown Pipeline with ScaleDownCompressor.
    """
    api_key = os.environ.get("SCALEDOWN_API_KEY")
    if not api_key:
        print("WARNING: SCALEDOWN_API_KEY not found in environment variables.")

    # Create a pipeline with ScaleDownCompressor
    # Note: explicitly passing API key to ensure it's picked up
    pipe = Pipeline([
        ('compressor', ScaleDownCompressor(rate='auto', target_model='gpt-4o', api_key=api_key))
    ])
    
    try:
        # Run the pipeline
        result = pipe.run(context=text, prompt="Compress this context")
        return result.final_content
    except Exception as e:
        print(f"ScaleDown compression failed: {e}")
        traceback.print_exc() # Print full stack trace to logs
        print("Falling back to raw text.")
        return text
