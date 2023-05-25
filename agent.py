import psutil
import yaml

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "movie_logs"
path = "config.yaml"

with open(path) as file:
    config = yaml.load(file, Loader=yaml.Loader)
    influxDb_measurement_name = config["config"]["monitored_server"] + "_system_monitoring"

client = InfluxDBClient(url="http://192.168.64.12:8086", token="5akShSOR813MQmv7ZehBxLF97KbvDPFOWL-R15TrTCcnUVOhtYQ_w6OAiVkfcRilWY07m1iMa5XHqpUWlYZIMw==", org="coding")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()


def write(metric : str, value, subset : str):
    if not subset:
        subset = "None"

    p = Point(influxDb_measurement_name).tag("subset", subset).field(metric, value)

    write_api.write(bucket=bucket, record=p)


def getter(metric: str, args : dict, subset : str | None = None):
    getter = getattr(psutil, metric)
    value = getter(**args)
    if subset :
        value = getattr(value, subset)

    write(metric, str(value), subset)

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

def main():
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


main()