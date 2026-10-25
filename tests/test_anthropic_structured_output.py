"""Structured output on Claude models that reject forced tool use."""

import warnings

import pytest
from langchain_core.messages import HumanMessage

from tradingagents.agents.schemas import TraderProposal
from tradingagents.llm_clients.anthropic_client import AnthropicClient


def _payload(model: str, **structured_kwargs) -> dict:
    llm = AnthropicClient(model=model, effort="low", api_key="x").get_llm()
    bound = llm.with_structured_output(TraderProposal, **structured_kwargs).first
    return bound.bound._get_request_payload([HumanMessage("x")], **bound.kwargs)


@pytest.mark.unit
@pytest.mark.parametrize("model", ["claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1"])
def test_models_without_forced_tools_use_native_structured_output(model):
    with warnings.catch_warnings():
        # The function-calling path warns that the tool call cannot be forced.
        warnings.simplefilter("error")
        payload = _payload(model)
    assert payload["output_config"]["format"]["type"] == "json_schema"
    assert payload["output_config"]["effort"] == "low"
    assert "tools" not in payload
    assert "tool_choice" not in payload


@pytest.mark.unit
def test_models_with_forced_tools_keep_function_calling():
    payload = _payload("claude-sonnet-5")
    assert payload["tool_choice"] == {"type": "tool", "name": "TraderProposal"}
    assert "format" not in payload.get("output_config", {})


@pytest.mark.unit
def test_an_explicit_method_is_respected():
    payload = _payload("claude-opus-5-5", method="function_calling")
    assert [tool["name"] for tool in payload["tools"]] == ["TraderProposal"]
