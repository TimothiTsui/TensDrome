import RPi.GPIO as GPIO
import time

RelayPin = 18

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RelayPin, GPIO.OUT)
    GPIO.output(RelayPin, GPIO.LOW)

def play_metronome(bpm):
    interval = 60.0 / bpm
    while True:
        print("Tick")
        GPIO.output(RelayPin, GPIO.HIGH)
        time.sleep(interval / 2)
        GPIO.output(RelayPin, GPIO.LOW)

        print("Tock")
        time.sleep(interval / 2)

def destroy():
    GPIO.output(RelayPin, GPIO.LOW)
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        bpm = int(input("Enter the BPM (Beats Per Minute): "))
        if bpm < 1:
            raise ValueError("BPM must be a positive integer.")
        play_metronome(bpm)
    except ValueError as ve:
        print(ve)
    except KeyboardInterrupt:
        print("\nMetronome stopped.")
        destroy()
