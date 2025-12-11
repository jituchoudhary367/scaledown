import pytest
import os
from scaledown.compressor.config import get_api_url, default_scaledown_api

def test_get_api_url_default(monkeypatch):
    """test that default url is returned when env var is missing"""
    monkeypatch.delenv("SCALEDOWN_API_URL", raising=False)
    assert get_api_url() == default_scaledown_api

def test_get_api_url_env_var(monkeypatch):
    """test that env var overrides the default url"""
    test_url = "https://custom.api.com"
    monkeypatch.setenv("SCALEDOWN_API_URL", test_url)
    assert get_api_url() == test_url    

