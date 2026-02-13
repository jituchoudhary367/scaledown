import os
import json
from typing import List, Dict, Any, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Default to a capable free/cheap model on OpenRouter if not specified
MODEL_NAME = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-001")
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

def get_llm(json_mode: bool = False, temperature: float = 0.7, max_tokens: int = 16384):
    """
    Returns a configured ChatOpenAI instance pointing to OpenRouter.
    """
    if not API_KEY:
        # Avoid hard error if importing without env vars, but warn on usage
        print("Warning: API Key not found context usually.")

    model_kwargs = {}
    if json_mode:
        model_kwargs["response_format"] = {"type": "json_object"}

    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=API_KEY,
        openai_api_base=BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
        model_kwargs=model_kwargs
    )

def call_llm(messages: List[Dict[str, str]], system_prompt: str, json_mode: bool = False, temperature: float = 0.7, max_tokens: int = 16384) -> Union[str, Dict[str, Any]]:
    """
    Helper to call the LLM with a system prompt and a list of messages.
    """
    if not API_KEY:
         raise ValueError("API Key not found. Please set OPENROUTER_API_KEY in .env")

    llm = get_llm(json_mode=json_mode, temperature=temperature, max_tokens=max_tokens)
    
    formatted_messages = [SystemMessage(content=system_prompt)]
    for msg in messages:
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        # Add other roles if needed

    try:
        response = llm.invoke(formatted_messages)
        content = response.content
    except Exception as e:
        error_str = str(e)
        # Check for OpenRouter 402, insufficient_quota, or credit issues
        if "402" in error_str or "insufficient_quota" in error_str.lower() or "credits" in error_str.lower():
            print(f"LLM Quota Error: {e}")
            
            # STAGE 1: Aggressive Token Reduction (fit within ~3000 limit)
            print("FALLBACK STAGE 1: Retrying with 2048 tokens...")
            try:
                fallback_llm = get_llm(json_mode=json_mode, temperature=temperature, max_tokens=2048)
                response = fallback_llm.invoke(formatted_messages)
                content = response.content
            except Exception as e2:
                print(f"Stage 1 failed: {e2}")
                
                # STAGE 2: Try SCALEDOWN_API_KEY as requested
                # We assume this key might allow access via a different quota or provider
                scaledown_key = os.getenv("SCALEDOWN_API_KEY")
                if scaledown_key:
                    print("FALLBACK STAGE 2: Using SCALEDOWN_API_KEY...")
                    try:
                        # Temporarily swap key for this call
                        original_key = API_KEY
                        # We use a trick here: instantiate ChatOpenAI manually or hack get_llm
                        # simpler to just instantiate manually to avoid global var issues
                        fallback_llm_2 = ChatOpenAI(
                            model=MODEL_NAME,
                            openai_api_key=scaledown_key,
                            openai_api_base=BASE_URL,
                            temperature=temperature,
                            max_tokens=4000, # Try moderate tokens with this key
                            model_kwargs={"response_format": {"type": "json_object"}} if json_mode else {}
                        )
                        response = fallback_llm_2.invoke(formatted_messages)
                        content = response.content
                    except Exception as e3:
                        print(f"Stage 2 failed: {e3}")
                        error_msg = f"LLM Quota Exceeded. All fallbacks failed. Last error: {str(e3)}"
                        if json_mode: return {"error": error_msg}
                        return error_msg
                else:
                    error_msg = f"LLM Quota Exceeded. Stage 1 failed and no SCALEDOWN_API_KEY. Last error: {str(e2)}"
                    if json_mode: return {"error": error_msg}
                    return error_msg
        else:
            print(f"LLM Call Failed: {e}")
            if json_mode:
                 return {"error": f"LLM Call Failed: {str(e)}"}
            return f"LLM Error: {str(e)}"

    if json_mode:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("Error decoding JSON from LLM response. Returning raw text.")
            return {"raw_output": content, "error": "JSONDecodeError"}
            
    return content
