from .celery import app
from db import check_payment
from datetime import timedelta
from timeloop import Timeloop


tl = Timeloop()


@tl.job(interval=timedelta(seconds=2))
def job_every_20sec():
    res = check_payment()


@app.task
def get_transaction():
    tl.start(block=True)
