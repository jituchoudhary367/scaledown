import os
import pytest
from unittest.mock import patch
from scaledown.compressor.scaledown_compressor import ScaleDownCompressor
from scaledown.types.compressed_prompt import CompressedPrompt
from scaledown.exceptions import AuthenticationError


@pytest.fixture
def compressor():
    return ScaleDownCompressor(api_key="test_key", target_model="gpt-4o")

#this is an optional integration test that actually hits the network and uses api key
#for running with this:  SCALEDOWN_RUN_INTEGRATION=1 SCALEDOWN_API_KEY=... uv run python -m unittest discover tests
#else : uv run python -m unittest discover tests
@pytest.mark.skipif(not os.environ.get("SCALEDOWN_RUN_INTEGRATION"), reason="Skipping integration test: SCALEDOWN_RUN_INTEGRATION not set")
def test_live_api_call():
    api_key=os.environ.get("SCALEDOWN_API_KEY")
    if not api_key:
        pytest.skip("No API key found in environment")
    compressor=ScaleDownCompressor(api_key=api_key, target_model="gpt-4o")  
    context="ScaleDown integration test context."
    prompt="Shorten this."
    result=compressor.compress(context, prompt)
    assert isinstance(result, CompressedPrompt)
    assert len(result.content) > 0
    assert result.metrics.latency_ms > 0

@patch('requests.post')
def test_compress_single_success(mock_post, compressor):
    mock_response_data={
        "results": {
            "compressed_prompt": "Compressed content",
            "original_prompt_tokens": 100,
            "compressed_prompt_tokens": 50,
            "request_metadata": {"timestamp": "2023-01-01T00:00:00Z"}
        },
        "latency_ms": 123,
        "model_used": "gpt-4o"
    }      
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response_data
    result = compressor.compress("context", "prompt")
    args, kwargs = mock_post.call_args
    assert kwargs['headers']['x-api-key'] == 'test_key'
    assert kwargs['json']['model'] == 'gpt-4o'
    assert kwargs['json']['scaledown']['rate'] == 'auto'
    assert result.content == "Compressed content"
    assert result.metrics.original_prompt_tokens == 100
    assert result.metrics.latency_ms == 123

@patch('requests.post')
def test_compress_batch(mock_post, compressor):
    mock_response_data={
        "results": {"compressed_prompt": "Batch content"}
    }
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response_data
    contexts = ["ctx1", "ctx2"]
    prompts = ["p1", "p2"]
    results = compressor.compress(contexts, prompts)
    assert len(results) == 2
    assert mock_post.call_count == 2

def test_missing_api_key_raises_error(monkeypatch):
    """ensure missing api key raises error"""
    monkeypatch.delenv("SCALEDOWN_API_KEY", raising=False)
    with patch("scaledown.get_api_key", return_value=None):
        comp = ScaleDownCompressor(api_key=None)
        with pytest.raises(AuthenticationError):
            comp.compress("ctx", "prompt")    
