from crontab import CronTab
import os
import pwd


def get_username():
    return pwd.getpwuid(os.getuid()).pw_name


def get_current_cron_config():
    cron, job = get_cron_job()
    config = {}

    if job:
        config['minutes'] = 1 if str(job.minutes) == '*' else str(job.minutes)[-1]
        config['hours'] = 1 if str(job.hours) == '*' else str(job.hours)[-1]
        config['days'] = 1 if str(job.day) == '*' else str(job.day)[-1]
    return config


def create_cron(minutes=None, hours=None, days=None):
    cron, job = get_cron_job()
    if not job:
        cron.new(command='python {0}/{1}'.format(os.getcwd(), 'load_data.py'), comment='cron_load_data')
        cron.write()
    update_cron(minutes, hours, days)


def update_cron(minutes=None, hours=None, days=None):
    cron, job = get_cron_job()
    if not job:
        create_cron(minutes, hours, days)
    else:
        print(minutes, hours, days)
        job.day.every(int(days))
        job.hour.every(int(hours))
        job.minute.every(int(minutes))
        cron.write()


def get_cron_job():
    cron = CronTab(user=get_username())
    jobs = cron.find_comment('cron_load_data')
    return cron, next(jobs, None)


if __name__ == '__main__':
    #update_cron(**{'minutes': 4, 'hours': '7', 'days': 4})
    #print(get_current_cron_config())
    pass