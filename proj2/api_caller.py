import requests
import argparse
from dotenv import dotenv_values

config = dotenv_values(".env")
parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--count", help="(int) amount of rows to return from latest data",
    type=int, default=1)
parser.add_argument(
    "-i", "--id", help="(int) id of row to fetch",
    type=int, default=None)

args = parser.parse_args()
api_endpoint = "/sensordata"
api_url = config["API_ROOT"] + api_endpoint

print(f"GET {api_endpoint} with")
for arg, val in vars(args).items():
    print(f"\t{arg}: {val}")


response = requests.get(api_url, params={"count": args.count, "id": args.id})
response_json = response.json()
if response_json is not {}:
    for content in response_json:
        print("ID:", content.get("id"))
        print("\tDatetime:", content.get("datetime"))
        print(f"\tTemperature (degC): {content.get("temperature_degC"):.2f}")
        print(f"\tHumidity (%): {content.get("humidity_pcent"):.2f}")
else:
    print("Empty result")
