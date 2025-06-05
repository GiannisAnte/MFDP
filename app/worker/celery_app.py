import os
from celery import Celery

celery_app = Celery(
    'ml_tasks',
    broker=os.getenv("CELERY_BROKER_URL"),
    backend='rpc://',
    include=["worker.tasks"],
)


celery_app.conf.update(
    task_always_eager=False)
# celery_app.conf.update(
#     task_always_eager=True,#False
#     task_eager_propagates=True,
# ) 

celery_app.conf.task_default_queue = 'celery'

celery_app.conf.task_routes = {
    "worker.tasks.process_cnn_data_task": {"queue": "cnn"},
    "worker.tasks.process_weather_task": {"queue": "weather"},
    "worker.tasks.process_ensemble_task": {"queue": "ensemble"},
}


celery_app.autodiscover_tasks(['worker'])