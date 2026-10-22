import json
from langchain_core.tools import tool
from shared.redis_state.redis_llm_state import RedisCustomerContext

def get_redis_context_object(customer_id: str) -> RedisCustomerContext:
    if not customer_id or len(customer_id) > 128:
        raise ValueError("Invalid customer ID")     
    return RedisCustomerContext()

@tool
def get_transaction_context(customer_id: str) -> str:
    """Fetch last 5 transactions of the customer with given customer id."""
    try:
        # Keep instantiation strictly scoped locally
        customer_context = get_redis_context_object(customer_id)
        transaction_history = customer_context.get_transaction_history(customer_id)
        # Explicitly serialize to a string to prevent LangChain serialization loops
        return json.dumps(transaction_history, default=str)
    except Exception as e:
        return f"Error fetching transaction history: {str(e)}"


@tool
def get_customer_profile(customer_id: str) -> str:
    """Fetch the customer profile with given customer id."""
    try:
        # Keep instantiation strictly scoped locally
        customer_context = get_redis_context_object(customer_id)
        customer_profile = customer_context.get_customer_profile(customer_id)
        # Explicitly serialize to a string to prevent LangChain serialization loops
        return json.dumps(customer_profile, default=str)
    except Exception as e:
        return f"Error fetching customer profile: {str(e)}"
