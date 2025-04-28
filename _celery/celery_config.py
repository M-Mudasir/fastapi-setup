
# TODO: uncomment this when we have a background task to run

# import ssl

# from celery import Celery
# from celery.schedules import crontab
# from app.core.config import settings

# celery = Celery(
#     "celery-app",
#     broker_url=f"azureservicebus://{settings.SERVICE_BUS_SAS_POLICY}:{settings.SERVICE_BUS_SAS_KEY}@{settings.SERVICE_BUS_NAMESPACE}",
# )

# broker_use_ssl = {
#     'ssl_cert_reqs': ssl.CERT_NONE
# }

# celery.conf.update(
#     task_serializer="json",
#     result_serializer="json",
#     accept_content=["json"],
#     broker_connection_retry_on_startup=True,
#     broker_use_ssl=broker_use_ssl
# )

# from . import tasks

# celery.conf.beat_schedule = {
#     "sample_job_every_5_mins": {
#         "task": "_celery.tasks.sample_job",
#         "schedule": crontab(minute="*/5"),
#     },
# }

