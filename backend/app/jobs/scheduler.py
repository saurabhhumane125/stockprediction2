from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler(
    job_defaults={
        "coalesce": True,
        "max_instances": 1,
    },
    timezone="Asia/Kolkata",
)