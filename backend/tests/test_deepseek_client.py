import pytest
from app.services.deepseek_client import DeepSeekClient
from app.config import settings

def test_cost_calculation():
    client = DeepSeekClient()
    # 1,000,000 prompt tokens (at $0.28) + 1,000,000 completion tokens (at $2.19) = $2.47
    cost = client.calculate_cost(1_000_000, 1_000_000)
    assert abs(cost - 2.47) < 0.001

    # 10,000 prompt tokens + 1,000 completion tokens
    small_cost = client.calculate_cost(10_000, 1_000)
    expected = (10_000 / 1e6 * 0.28) + (1_000 / 1e6 * 2.19)
    assert abs(small_cost - round(expected, 6)) < 1e-5

@pytest.mark.asyncio
async def test_offline_mock_completion_fallback(monkeypatch):
    monkeypatch.setattr(settings, "deepseek_api_key", "")
    client = DeepSeekClient()
    messages = [
        {"role": "system", "content": "You are a LinkedIn strategist."},
        {"role": "user", "content": "Generate six distinct drafts for dental practice workflow."}
    ]
    result = await client.call_completion(messages, endpoint_name="test_endpoint")
    assert result["is_mock"] is True
    assert result["prompt_tokens"] > 0
    assert result["completion_tokens"] > 0
    assert result["estimated_cost_usd"] > 0
    assert "concise" in result["content"].lower()
