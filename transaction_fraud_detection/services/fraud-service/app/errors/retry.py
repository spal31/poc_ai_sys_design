import time

from config import MAX_RETRIES
from errors.exceptions import TransientProcessingError


def execute_with_retry(process_function):

    retry_count = 0

    while True:

        try:
            result = process_function()

            return result, retry_count

        except TransientProcessingError:

            retry_count += 1

            if retry_count > MAX_RETRIES:
                raise

            sleep_seconds = 2 ** (retry_count - 1)

            print(
                f"Retry {retry_count}/{MAX_RETRIES} "
                f"after {sleep_seconds}s"
            )

            time.sleep(sleep_seconds)