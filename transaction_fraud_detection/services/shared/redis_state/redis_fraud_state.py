import redis
from shared.config import REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisState:

    def __init__(
        self
    ):
         self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    def record_transaction(
        self,
        customer_id: str,
        transaction_id: str
    ):
        key = f"customer:{customer_id}:transactions"

        self.redis.zadd(
            key,
            {
                transaction_id: self.redis.time()[0]
            }
        )

        self.redis.expire(key, 3600)

    def get_transaction_count(
        self,
        customer_id: str,
        window_seconds: int = 60
    ) -> int:

        key = f"customer:{customer_id}:transactions"

        current_time = self.redis.time()[0]

        minimum_time = current_time - window_seconds

        return self.redis.zcount(
            key,
            minimum_time,
            current_time
        )

    def get_customer_countries(self, customer_id):

      key = f"customer:{customer_id}:countries"

      return self.redis.smembers(key)


    def add_customer_country(self, customer_id, country):

      key = f"customer:{customer_id}:countries"

      self.redis.sadd(key, country)

      self.redis.expire(key, 86400 * 30)