
from langchain_core.tools import tool
from shared.redis_state.redis_llm_state import RedisCustomerContext

def get_redis_context_object(customer_id) -> RedisCustomerContext:
     if not customer_id or len(customer_id) > 128:
            raise ValueError("Invalid customer ID")     
     return RedisCustomerContext()

@tool
def get_transaction_context(customer_id: str) -> dict:
    """Fetch last 5 trasactions of the customer with given customer id
    """
    customer_context = get_redis_context_object(customer_id)
    transaction_history = customer_context.get_transaction_history(customer_id)
    return transaction_history


@tool
def get_customer_profile(customer_id: str) -> dict:
    """Fetch the customer profile with given customer id."""
    customer_context = get_redis_context_object(customer_id)
    customer_profile = customer_context.get_customer_profile(customer_id)
    return customer_profile