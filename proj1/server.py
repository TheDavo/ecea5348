import paho.mqtt.client as paho
import json
import ssl
import time
import datetime
from dotenv import dotenv_values
import pseudoSensor

config = dotenv_values(".env")
connflag = False

print(config)

# http://www.steves-internet-guide.com/python-mqtt-client-changes/


def on_connect(client, userdata, flags, reasonCode, properties=None):
    global connflag
    connflag = True
    print("Connection returned result: " + str(reasonCode))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


mqtt_client = paho.Client(
    paho.CallbackAPIVersion.VERSION2)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.tls_set(
    ca_certs=config["CA_CERT"],
    certfile=config["CERT_FILE"],
    keyfile=config["PRIV_KEY"],
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2,
    ciphers=None
)

mqtt_client.connect(
    host=config["AWSHOST"],
    port=int(config["AWSPORT"]),
    keepalive=60
)

ps = pseudoSensor.PseudoSensor()

mqtt_client.loop_start()

while True:
    time.sleep(1)
    if connflag:
        hum, temp = ps.generate_value()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {"humidity": hum, "temperature": temp, "datetime": now}
        mqtt_client.publish("sensor/data", json.dumps(data), qos=1)
        print("msg sent: ", data)

    else:
        print("waiting for connection...")
