
# app/redis_context.py

import json
import os
from typing import Any

import redis
from redis.exceptions import RedisError
from shared.config import REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisCustomerContext:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    @staticmethod
    def profile_key(customer_id: str) -> str:
        return f"customer:{customer_id}:profile"

    @staticmethod
    def transactions_key(customer_id: str) -> str:
        return f"customer:{customer_id}:transactions"

    def save_customer_profile(
        self,
        customer_id: str,
        profile: dict[str, Any],
    ) -> None:
        """Create or update the customer's profile."""
        key = self.profile_key(customer_id)

        # The Redis hash stores each profile field separately.
        serialized = {
            field: json.dumps(value)
            for field, value in profile.items()
        }

        try:
            pipe = self.client.pipeline(transaction=True)
            pipe.hset(key, mapping=serialized)

            ttl = int(
                os.getenv("CUSTOMER_PROFILE_TTL_SECONDS", "2592000")
            )
            if ttl > 0:
                pipe.expire(key, ttl)

            pipe.execute()
        except RedisError as exc:
            raise RuntimeError(
                f"Could not save profile for {customer_id}"
            ) from exc

    def get_customer_profile(
        self,
        customer_id: str,
    ) -> dict[str, Any] | None:
        """Return the profile, or None if it does not exist."""
        try:
            raw = self.client.hgetall(
                self.profile_key(customer_id)
            )
            if not raw:
                return None

            return {
                field: json.loads(value)
                for field, value in raw.items()
            }
        except (RedisError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Could not retrieve profile for {customer_id}"
            ) from exc

    def add_transaction(
        self,
        customer_id: str,
        transaction: dict[str, Any],
    ) -> None:
        """Add the newest transaction and retain only five entries."""
        key = self.transactions_key(customer_id)
        payload = json.dumps(transaction, separators=(",", ":"))

        try:
            # MULTI/EXEC makes LPUSH + LTRIM atomic.
            with self.client.pipeline(transaction=True) as pipe:
                pipe.lpush(key, payload)
                pipe.ltrim(key, 0, 4)
                pipe.execute()
        except RedisError as exc:
            raise RuntimeError(
                f"Could not save transaction for {customer_id}"
            ) from exc

    def get_last_transactions(
        self,
        customer_id: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Return newest first, capped at five transactions."""
        if not 1 <= limit <= 5:
            raise ValueError("limit must be between 1 and 5")

        try:
            records = self.client.lrange(
                self.transactions_key(customer_id),
                0,
                limit - 1,
            )
            return [json.loads(record) for record in records]
        except (RedisError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Could not retrieve transactions for {customer_id}"
            ) from exc

    def get_transaction_history(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        """Fetch trasnaction history required by the agent."""
        transactions = self.get_last_transactions(customer_id, limit=5)

        return {
            "recent_transactions": transactions,
            "history_available": bool(transactions)
        }

    def get_customer_profile(
                self,
                customer_id: str,
            ) -> dict[str, Any]:
                """Fetch customer required by the agent."""
                profile = self.get_customer_profile(customer_id)
        
                return {
                    "customer_profile": profile,
                    "profile_available": profile is not None,
                }
    

    def health_check(self) -> bool:
        return bool(self.client.ping())
