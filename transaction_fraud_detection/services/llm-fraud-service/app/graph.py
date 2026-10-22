
import json
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler 

from schemas import FraudAssessment
from guardrails import (
    validate_review_event,
    validate_assessment,
    safe_fallback,
)
from agent import build_agent

import shared.config as CONFIG
import traceback

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
        # 1. Initialize the global Langfuse client once safely 
        if CONFIG.LANGFUSE_PUBLIC_KEY and CONFIG.LANGFUSE_SECRET_KEY:
            Langfuse(
                public_key=CONFIG.LANGFUSE_PUBLIC_KEY,
                secret_key=CONFIG.LANGFUSE_SECRET_KEY,
                host=CONFIG.LANGFUSE_BASE_URL
            )
            # 2. Get the handler out of the configured global client singleton
            callbacks = [CallbackHandler()]
        else:
            callbacks = []
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config={
                    "callbacks": callbacks,
                    "recursion_limit": int(CONFIG.MAX_AGENT_STEPS),
                    "configurable": {
                        "response_format": FraudAssessment 
                    },
                    "metadata": {
                        "service": "llm-fraud-service",
                        "workflow_version": "v1"
                    },

                },
            )
        except Exception:
            traceback.print_exc() 
          
        # Requires response_format=FraudAssessment on the agent.
        if response and "messages" in response:
            final_message = response["messages"][-1]
            raw_content = final_message.content
            # 2. Parse the text contents into a dictionary
            try:
                # If wrapped under a root class name key by the LLM
                parsed_json = json.loads(raw_content)
                if "FraudAssessment" in parsed_json:
                    assessment = parsed_json["FraudAssessment"]
                else:
                    assessment = parsed_json
            except (json.JSONDecodeError, TypeError):
                # Fallback in case of raw tool call representations
                assessment = getattr(final_message, "tool_calls", None)
        else:
            assessment = None
            print("Error: The agent state returned empty or missing 'messages'.")

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
