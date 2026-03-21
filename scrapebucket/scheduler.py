import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler(standalone=True)


@sched.scheduled_job('interval', seconds=1)  # weeks, days, hours, minutes
def timed_job():
    print('This job is run every second.')


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=5, minute=0, timezone=pytz.timezone('Asia/Manila'))
def hello():
    print('This job is run mon-sun, 5pm.')


# another way NOT using decorator
def job_every_second():
    print("Hello World in every second")


sched.add_job(job_every_second, 'interval', seconds=1)


def job_sked():
    print("Hello World for this schedule")


sched.add_job(job_sked, 'cron', day_of_week='mon-sun', hour=5, minute=0, timezone=pytz.timezone('Asia/Manila'))


try:
    sched.start()
except (KeyboardInterrupt, SystemExit):
    sched.shutdown(wait=False)


# https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
