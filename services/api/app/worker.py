from redis import Redis
from rq import Queue, Worker

from app.db import init_db
from app.settings import settings


def main() -> None:
    init_db()
    redis = Redis.from_url(settings.redis_url)
    worker = Worker([Queue("default", connection=redis)], connection=redis)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
