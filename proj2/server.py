import paho.mqtt.client as paho
import json
import ssl
import time
import datetime
from dotenv import dotenv_values
import pseudoSensor

config = dotenv_values(".env")
connflag = False
run = True


# http://www.steves-internet-guide.com/python-mqtt-client-changes/
# MQTT version five is used, the above guide helps understand the code changes
# Needed to get this to work with the latest libraries
def on_connect(client, userdata, flags, reason_code, properties=None):
    global connflag
    connflag = True
    print("Connection returned result ->", str(reason_code))


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    print("Message received on topic ->", msg.topic)
    for key, value in payload.items():
        print(key, "->", value)

    # Handle the commands
    match msg.topic:
        case "control/commands":
            handle_command(payload)


def handle_command(payload: dict):
    """
    handle_command takes in the message payload and specifically looks
    for a "command" key to parse and handle from the "control/commands" topic

    Args:
        payload (dict): command payload from topic "control/commands"
    """
    global run
    global connflag
    match payload["command"]:
        case "stop":
            run = False
        case "pause":
            connflag = False
        case "resume":
            connflag = True
        case _:
            print("Error: unknown command", payload["command"])


def on_subscribe(client, obj, mid, reason_code_list, properties):
    print("Suscribed:" + str(mid) + " " + str(reason_code_list))


mqtt_client = paho.Client(
    paho.CallbackAPIVersion.VERSION2)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

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

# Subscribe to the contorl/commands topic which sends the stop command
# To end the MQTT loop
mqtt_client.subscribe("control/commands")

mqtt_client.loop_start()

while run:
    time.sleep(3)
    if connflag:
        hum, temp = ps.generate_value()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {"humidity": hum, "temperature": temp, "datetime": now}

        mqtt_client.publish("sensor/data", json.dumps(data), qos=1)
        print("msg sent -> ")
        print("\thumidity:", hum)
        print("\ttemperature:", temp)
        print("\tdatetime:", now)
    else:
        print("Publishing data paused...")

# Thing has sent the command to stop, the above while loop is stopped
# So the MQTT client loop is stopped.
print("|-------")
print("Message received to stop loop...\n\n")
print("Ending loop, please restart script to send data")
print("|-------")
mqtt_client.loop_stop()
