import RPi.GPIO as GPIO
import time

RelayPin = 18
from awscrt import io, mqtt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import threading
import json


shared_data = {
    'bpm': 60,
    'time_signature': "4/4"
}

is_playing = False

received_all_event = threading.Event()
target_ep = 'a2lfjupb1otf51-ats.iot.us-east-1.amazonaws.com'
thing_name = 'RaspberryPi'
cert_filepath = '/home/pi/Desktop/AWSMetronome/certificate.pem.crt'
private_key_filepath = '/home/pi/Desktop/AWSMetronome/private.pem.key'
ca_filepath = '/home/pi/Desktop/AWSMetronome/AmazonRootCA1.pem'
client_id = "iotconsole-e699be3c-0460-4c81-a5bb-60c21ebc18fa"
pub_topic = 'connection_topic'
sub_topic = 'status'
# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RelayPin, GPIO.OUT)
    GPIO.output(RelayPin, GPIO.LOW)


def on_message_received(client, userdata, message):
    global shared_data, is_playing
    print("Received message from topic '{}': {}".format(message.topic, message.payload))
    recv_data = json.loads(message.payload)
    inputData = recv_data['inputDATA']
    shared_data['bpm'] = inputData['bpm']
    shared_data['time_signature'] = inputData['time_signature']

    if not is_playing:
        is_playing = True
        threading.Thread(target=play_metronome).start()

def play_metronome():
    global shared_data
    count = 0
    current_bpm = None
    current_time_signature = None

    while True:
        # Check if bpm or time_signature has changed
        if current_bpm != shared_data['bpm'] or current_time_signature != shared_data['time_signature']:
            current_bpm = shared_data['bpm']
            current_time_signature = shared_data['time_signature']
            interval = 60.0 / current_bpm
            beats_per_measure, count_unit = map(int, current_time_signature.split('/'))

            if beats_per_measure in list({2, 3, 4}):
                meter = "simple"
            elif beats_per_measure in list({6, 9, 12}):
                meter = "compound"
            else:
                meter = "complex"

            if beats_per_measure in list({2, 6}):
                meter_name = "duple"
            elif beats_per_measure in list({3, 9}):
                meter_name = "triple"
            elif beats_per_measure in list({4, 12}):
                meter_name = "quadruple"
            else:
                meter_name = "complex"

        # ... (Rest of your play_metronome function) ...

        if meter == "simple":
            if meter_name == "duple":
                if count % 2 == 0 or count / count_unit == 0:
                    print("Strong")
                else:
                    print(1 + count % 2)

            elif meter_name == "triple":
                if count % 3 == 0 or count / count_unit == 0:
                    print("Strong")
                else:
                    print(1 + count % 3)

            else:
                if count % 4 == 0 or (count + 2) % count_unit == 0:
                    if (count + 2) % count_unit == 0:
                        print("Medium Strong")
                    else:
                        print("Strong")
                else:
                    print(1 + count % 4)

        elif meter == "compound":

            if meter_name == "duple":
                if count % 3 == 0:
                    if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                        print("Strong")
                    else:
                        print("Medium Strong")
                else:
                    print(1 + count % beats_per_measure)

            elif meter_name == "triple":
                if count % 3 == 0:
                    if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                        print("Strong")
                    else:
                        print("Medium Strong")
                else:
                    print(1 + count % beats_per_measure)
            else:
                if count % 3 == 0:
                    if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                        print("Strong")
                    else:
                        print("Medium Strong")
                else:
                    print(1 + count % beats_per_measure)

        GPIO.output(RelayPin, GPIO.HIGH)
        time.sleep(interval / 2)
        GPIO.output(RelayPin, GPIO.LOW)
        time.sleep(interval / 2)

        count += 1


def destroy():
    global is_playing
    is_playing = False
    GPIO.output(RelayPin, GPIO.LOW)
    GPIO.cleanup()


setup()

myMQTTClient = AWSIoTMQTTClient(thing_name)
myMQTTClient.configureEndpoint(target_ep, portNumber=8883)
myMQTTClient.configureCredentials(CAFilePath=ca_filepath, KeyPath=private_key_filepath, CertificatePath=cert_filepath)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(20)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(20)  # 5 sec

# connect and publish
myMQTTClient.connect()
payload = "Hello"

myMQTTClient.publish(topic=pub_topic, payload=payload, QoS=0)

print("Subscribing to topic " + sub_topic)

myMQTTClient.subscribe(sub_topic, 1, callback=on_message_received)
print("Subscribed!")
print("Received BPM: {}, Meter: {}".format(str(shared_data['bpm']), str(shared_data['time_signature'])))

if shared_data['bpm'] is not None and shared_data['time_signature'] is not None:
    print("Received BPM: {}, Meter: {}".format(str(shared_data['bpm']), str(shared_data['time_signature'])))
else:
    print("Waiting for BPM and Meter values...")

# Keep the program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    destroy()
    myMQTTClient.unsubscribe(sub_topic)
    myMQTTClient.disconnect()