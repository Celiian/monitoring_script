from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "movie_logs"

client = InfluxDBClient(url="http://192.168.64.12:8086", token="5akShSOR813MQmv7ZehBxLF97KbvDPFOWL-R15TrTCcnUVOhtYQ_w6OAiVkfcRilWY07m1iMa5XHqpUWlYZIMw==", org="coding")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

p = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)

write_api.write(bucket=bucket, record=p)