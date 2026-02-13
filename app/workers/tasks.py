from celery_worker import celery

@celery.task
def test_task(x: int, y: int) -> int:
    return x + y