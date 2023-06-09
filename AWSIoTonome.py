import RPi.GPIO as GPIO
import time
import threading
import json
import LCD1602
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

config = {
    "StrongPin": 23,
    "MediumPin": 24,
    "target_ep": "a2lfjupb1otf51-ats.iot.us-east-1.amazonaws.com",
    "thing_name": "RaspberryPi",
    "cert_filepath": "/home/pi/Desktop/AWSMetronome/certificate.pem.crt",
    "private_key_filepath": "/home/pi/Desktop/AWSMetronome/private.pem.key",
    "ca_filepath": "/home/pi/Desktop/AWSMetronome/AmazonRootCA1.pem",
    "client_id": "iotconsole-a12e0762-39fb-4fe7-b1ab-f1c8fa1abf50",
    "pub_topic": "connection_topic",
    "sub_topic": "status",
    "sub_topic2": "user/input",
}


class MetronomeGPIO:
    def __init__(self, RelayPin):
        self.RelayPin = RelayPin
        LCD1602.init(0x27, 1)
        LCD1602.write(0, 0, "Well,")
        LCD1602.write(0, 1, "Hello, there!")
        time.sleep(2)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RelayPin, GPIO.OUT)

    def output(self, value):
        GPIO.output(self.RelayPin, value)

    def cleanup(self):
        GPIO.cleanup()
        LCD1602.clear()


class AWSIoTClient:
    def __init__(self, config):
        self.client = AWSIoTMQTTClient(config["thing_name"])
        self.client.configureEndpoint(config["target_ep"], portNumber=8883)
        self.client.configureCredentials(
            CAFilePath=config["ca_filepath"],
            KeyPath=config["private_key_filepath"],
            CertificatePath=config["cert_filepath"],
        )
        # Infinite offline Publish queueing
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(20)  # 10 sec
        self.client.configureMQTTOperationTimeout(20)  # 5 sec

    def connect(self):
        self.client.connect()

    def publish(self, topic, payload, QoS):
        self.client.publish(topic=topic, payload=payload, QoS=QoS)

    def subscribe(self, topic, QoS, callback):
        self.client.subscribe(topic, QoS, callback)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def disconnect(self):
        self.client.disconnect()


class MetronomeController:
    def __init__(self, config):
        self.config = config
        self.shared_data = {"bpm": None, "time_signature": None}
        self.pause_event = threading.Event()
        self.strong_gpio = MetronomeGPIO(config["StrongPin"])
        self.medium_gpio = MetronomeGPIO(config["MediumPin"])
        self.aws_iot_client = AWSIoTClient(config)
        self.aws_iot_client.connect()

    def on_message_received(self, client, userdata, message):
        self.pause_event.clear()
        print("Received message from topic '{}': {}".format(
            message.topic, message.payload))
        recv_data = json.loads(message.payload)
        inputData = recv_data["inputDATA"]
        self.shared_data["bpm"] = inputData["bpm"]
        self.shared_data["time_signature"] = inputData["time_signature"]
        self.lcd_resume()

    def user_input_triggered(self, client, userdata, message):
        self.pause_event.set()
        print("User Input Detected: {}".format(message.payload))
        recv_data = json.loads(message.payload)
        inputData = recv_data["inputDATA"]
        self.lcd_flash_loop(inputData)

    def lcd_flash_loop(self, input_data):
        LCD1602.clear()
        LCD1602.write(0, 0, "Searching {}".format(input_data["title"]))
        LCD1602.write(0, 1, "Waiting AWS...")

    def lcd_resume(self):
        LCD1602.clear()
        LCD1602.write(0, 0, "BPM:{}".format(self.shared_data["bpm"]))
        LCD1602.write(0, 1, "Time Sig.:{}".format(self.shared_data["time_signature"]))

    def play_metronome(self):
        count = 0
        current_bpm = None
        current_time_signature = None
        interval = None
        beats_per_measure = None
        count_unit = None
        meter = None
        meter_name = None

        while True:
            if self.pause_event.is_set():
                self.pause_event.wait()

            if current_bpm != self.shared_data['bpm'] or current_time_signature != self.shared_data['time_signature']:
                current_bpm = self.shared_data['bpm']
                current_time_signature = self.shared_data['time_signature']
                interval = 60.0 / current_bpm
                beats_per_measure, count_unit = map(
                    int, current_time_signature.split('/'))

                self.lcd_resume()
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
                    if self.pause_event.is_set():
                        self.pause_event.wait()

                    if count % 2 == 0 or count / count_unit == 0:
                        self.strong_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.strong_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print("Strong")
                    else:
                        self.medium_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.medium_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print(1 + count % 2)

                elif meter_name == "triple":
                    if self.pause_event.is_set():
                        self.pause_event.wait()

                    if count % 3 == 0 or count / count_unit == 0:
                        self.strong_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.strong_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print("Strong")
                    else:
                        self.medium_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.medium_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print(1 + count % 3)

                else:
                    if self.pause_event.is_set():
                        self.pause_event.wait()

                    if count % 4 == 0 or (count + 2) % count_unit == 0:
                        if (count + 2) % count_unit == 0:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Medium Strong")
                        else:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Strong")
                    else:
                        print(1 + count % 4)
                        self.medium_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.medium_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)

            elif meter == "compound":

                if meter_name == "duple":
                    if self.pause_event.is_set():
                        self.pause_event.wait()
                    if count % 3 == 0:
                        if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Strong")
                        else:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Medium Strong")
                    else:
                        if self.pause_event.is_set():
                            self.pause_event.wait()

                        self.medium_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.medium_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print(1 + count % beats_per_measure)

                elif meter_name == "triple":
                    if self.pause_event.is_set():
                        self.pause_event.wait()

                    if count % 3 == 0:
                        if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Strong")
                        else:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)

                            print("Medium Strong")
                    else:
                        self.medium_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.medium_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print(1 + count % beats_per_measure)
                else:
                    if self.pause_event.is_set():
                        self.pause_event.wait()

                    if count % 3 == 0:
                        if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Strong")
                        else:
                            self.strong_gpio.output(value=GPIO.HIGH)
                            time.sleep(interval / 2)
                            self.strong_gpio.output(value=GPIO.LOW)
                            time.sleep(interval / 2)
                            print("Medium Strong")
                    else:

                        self.medium_gpio.output(value=GPIO.HIGH)
                        time.sleep(interval / 2)
                        self.medium_gpio.output(value=GPIO.LOW)
                        time.sleep(interval / 2)
                        print(1 + count % beats_per_measure)

            count += 1

    def run(self):
        payload = "Hello"
        self.aws_iot_client.publish(
            topic=self.config["pub_topic"], payload=payload, QoS=0)

        print("Subscribing to topic " + self.config["sub_topic"])
        self.aws_iot_client.subscribe(
            self.config["sub_topic2"], 0, callback=self.user_input_triggered)
        self.aws_iot_client.subscribe(
            self.config["sub_topic"], 0, callback=self.on_message_received)

        print("Subscribed!")
        threading.Thread(target=self.play_metronome).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            self.metronome_strong_gpio.cleanup()
            self.metronome_medium_gpio.cleanup()
            self.aws_iot_client.unsubscribe(self.config["sub_topic"])
            self.aws_iot_client.unsubscribe(self.config["sub_topic2"])
            self.aws_iot_client.disconnect()
        finally:
            GPIO.cleanup()


if __name__ == "__main__":
    metronome_controller = MetronomeController(config)
    metronome_controller.run()
