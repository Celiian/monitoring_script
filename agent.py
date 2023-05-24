import psutil
import yaml

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


def getter(metric: str, args : dict, subset : str | None = None):
    getter = getattr(psutil, metric)
    value = getter(**args)
    if subset :
        value = getattr(value, subset)

    res = datetime.now().isoformat() + ";" + metric + ";" + str(value) + '\n'
    with open("logs.txt", 'a') as logs:
        logs.write(res)

def create_job(metric: str, args: dict):
    def job():
        return splitter(metric, args)
    return job

def splitter(metric: str, args : dict):
    if split := args.get("split", {}) :
        args.pop("split", None)
        for subset, display in split.items():
            if(display):
                getter(metric, args, subset)
    else :
        getter(metric, args)

def main(path):
    scheduler = BlockingScheduler()

    with open(path) as file:
        config = yaml.load(file, Loader=yaml.Loader)

    metrics = config["metrics"]
    for metric_name in metrics:
        args = metrics[metric_name]
        display = args.get("display", False)
        if(display):
            interval = args.get("time", 5)
            args.pop("time", None)
            args.pop("display", None)
            job = create_job(metric_name, args)
            scheduler.add_job(job, 'interval', seconds=interval)

    scheduler.start()


main("config.yaml")