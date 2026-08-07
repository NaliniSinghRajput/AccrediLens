from redis import Redis
from rq import Queue, SimpleWorker
from rq.timeouts import TimerDeathPenalty

from app.core.config import get_settings


class WindowsSimpleWorker(SimpleWorker):
    death_penalty_class = TimerDeathPenalty


def main() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url)
    worker = WindowsSimpleWorker([Queue("paper-processing", connection=redis)], connection=redis)
    worker.work()


if __name__ == "__main__":
    main()
