
from redis_llm_state import RedisCustomerContext

store = RedisCustomerContext()

store.save_customer_profile(
    "CUST-101",
    {
        "customer_id": "CUST-101",
        "last_login_before_days": 2,
        "home_country": "IN",
        "usual_average_transaction_amount": 2500,
        "occupation": "SALARIED",
        "profile_status": "ACTIVE"
    },
)

store.save_customer_profile(
    "CUST-102",
    {
        "customer_id": "CUST-102",
        "last_login_before_days": 2000,
        "home_country": "CA",
        "usual_average_transaction_amount": 500,
        "occupation": "SALARIED",
        "profile_status": "DEACTIVATED"
    },
)

store.save_customer_profile(
    "CUST-103",
    {
        "customer_id": "CUST-103",
        "last_login_before_days": 5,
        "home_country": "US",
        "usual_average_transaction_amount": 4000,
        "occupation": "BUSINESS",
        "profile_status": "ACTIVE"
    },
)

store.save_customer_profile(
    "CUST-104",
    {
        "customer_id": "CUST-104",
        "last_login_before_days": 7,
        "home_country": "UK",
        "usual_average_transaction_amount": 5000,
        "occupation": "SURGEON",
        "profile_status": "ACTIVE"
    },
)

store.save_customer_profile(
    "CUST-105",
    {
        "customer_id": "CUST-105",
        "last_login_before_days": 3,
        "home_country": "IN",
        "usual_average_transaction_amount": 6000,
        "occupation": "LAWYER",
        "profile_status": "ACTIVE"
    },
)

sample_transactions = [
    {
        "transaction_id": "TXN-1005",
        "amount": 3200,
        "currency": "INR",
        "country": "IN",
        "status": "APPROVED",
        "timestamp": "2026-10-18T14:20:00+05:30",
    },
    {
        "transaction_id": "TXN-1004",
        "amount": 1800,
        "currency": "INR",
        "country": "IN",
        "status": "APPROVED",
        "timestamp": "2026-10-18T13:10:00+05:30",
    },
    {
        "transaction_id": "TXN-1003",
        "amount": 2400,
        "currency": "INR",
        "country": "IN",
        "status": "APPROVED",
        "timestamp": "2026-10-17T19:15:00+05:30",
    },
    {
        "transaction_id": "TXN-1002",
        "amount": 2100,
        "currency": "INR",
        "country": "IN",
        "status": "APPROVED",
        "timestamp": "2026-10-17T12:30:00+05:30",
    },
    {
        "transaction_id": "TXN-1001",
        "amount": 2700,
        "currency": "INR",
        "country": "IN",
        "status": "APPROVED",
        "timestamp": "2026-10-16T18:00:00+05:30",
    },
]

# Add oldest first so the final list is newest first.
# for txn in reversed(sample_transactions):
#     store.add_transaction("CUST-101", txn)

# print("Redis health:", store.health_check())
# print("Profile:", store.get_customer_profile("CUST-101"))
# print("Last five:", store.get_last_transactions("CUST-101"))
