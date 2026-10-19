
import json
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler

from app.schemas import FraudAssessment, FraudReviewEvent
from app.guardrails import (
    validate_review_event,
    validate_assessment,
    safe_fallback,
)
from app.agent import build_agent

import shared.config as CONFIG


class FraudGraphState(TypedDict, total=False):
    event: dict
    validated_event: dict
    assessment: dict
    status: str
    error: str
    result: dict


agent = build_agent()


def validate_input(state: FraudGraphState):
    event = validate_review_event(state["event"])
    return {"validated_event": event.model_dump(), "status": "VALID"}


def investigate(state: FraudGraphState):
    event = state["validated_event"]

    prompt = f"""
    Assess this payment review case.

    Transaction and rule evidence:
    {json.dumps(event, ensure_ascii=True)}

    Retrieve additional context when useful.
    Return a structured assessment based only on available evidence.
    """

    try:
        callbacks = [CallbackHandler()] if (
            CONFIG.LANGFUSE_PUBLIC_KEY
            and CONFIG.LANGFUSE_SECRET_KEY
        ) else []

        response = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={
                "callbacks": callbacks,
                "recursion_limit": CONFIG.MAX_AGENT_STEPS,
                "metadata": {
                    "service": "llm-fraud-service",
                    "workflow_version": "v1",
                },
            },
        )

        # Requires response_format=FraudAssessment on the agent.
        assessment = response.get("structured_response")

        if assessment is None:
            raise ValueError("Agent did not return structured output")

        if isinstance(assessment, FraudAssessment):
            assessment = assessment.model_dump()

        return {
            "assessment": assessment,
            "status": "ASSESSED",
        }

    except Exception as exc:
        # Avoid logging raw transaction data or provider responses.
        return {
            "status": "AGENT_ERROR",
            "error": type(exc).__name__,
        }


def validate_output(state: FraudGraphState):
    try:
        assessment = validate_assessment(state["assessment"])
        return {
            "assessment": assessment.model_dump(),
            "status": "VALIDATED",
        }
    except Exception as exc:
        return {
            "status": "VALIDATION_ERROR",
            "error": type(exc).__name__,
        }


def route_after_input(state: FraudGraphState):
    return "investigate" if state.get("status") == "VALID" else "fallback"


def route_after_investigation(state: FraudGraphState):
    return (
        "validate_output"
        if state.get("status") == "ASSESSED"
        else "fallback"
    )


def route_after_validation(state: FraudGraphState):
    return (
        "finish"
        if state.get("status") == "VALIDATED"
        else "fallback"
    )


def fallback_node(state: FraudGraphState):
    return {
        "result": safe_fallback(),
        "status": "FALLBACK_REVIEW",
    }


def finish_node(state: FraudGraphState):
    return {
        "result": {
            "assessment": state["assessment"],
            "status": "VALIDATED",
        }
    }


def build_graph():
    graph = StateGraph(FraudGraphState)

    graph.add_node("validate_input", validate_input)
    graph.add_node("investigate", investigate)
    graph.add_node("validate_output", validate_output)
    graph.add_node("fallback", fallback_node)
    graph.add_node("finish", finish_node)

    graph.add_edge(START, "validate_input")

    graph.add_conditional_edges(
        "validate_input",
        route_after_input,
        {
            "investigate": "investigate",
            "fallback": "fallback",
        },
    )

    graph.add_conditional_edges(
        "investigate",
        route_after_investigation,
        {
            "validate_output": "validate_output",
            "fallback": "fallback",
        },
    )

    graph.add_conditional_edges(
        "validate_output",
        route_after_validation,
        {
            "finish": "finish",
            "fallback": "fallback",
        },
    )

    graph.add_edge("finish", END)
    graph.add_edge("fallback", END)

    return graph.compile()


fraud_graph = build_graph()
