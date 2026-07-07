from redis import Redis
from rq import Queue, SimpleWorker

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url)
    SimpleWorker = SimpleWorker([Queue("paper-processing", connection=redis)], connection=redis)
    worker.work()


if __name__ == "__main__":
    main()
