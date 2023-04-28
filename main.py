import RPi.GPIO as GPIO
import time

RelayPin = 18

# Define Const
simple_meters = [
    "2/2",  # Cut time or Alla breve
    "2/4",
    "2/8",
    "3/2",
    "3/4",
    "3/8",
    "4/2",
    "4/4",  # Common time
    "4/8",
]

compound_meters = [
    "6/4",
    "6/8",
    "9/4",
    "9/8",
    "12/4",
    "12/8",
]


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RelayPin, GPIO.OUT)
    GPIO.output(RelayPin, GPIO.LOW)


def play_metronome(bpm, time_signature):
    interval = 60.0 / bpm
    beats_per_measure, beat_duration = map(int, time_signature.split('/'))
    beats = beats_per_measure * (beat_duration // 4)

    count = 1
    while True:
        if time_signature in simple_meters:
            if count % beats == 1:
                print("Downbeat")
            else:
                print(count % beats or beats)
        else:

            #Compound meters still doesn't print out correctly
            if count % beats == 1 or count % (beats // 2) == 1:
                print("Downbeat")
            else:
                print(count % beats or beats)

        GPIO.output(RelayPin, GPIO.HIGH)
        time.sleep(interval / 2)
        GPIO.output(RelayPin, GPIO.LOW)
        time.sleep(interval / 2)

        count += 1


def destroy():
    GPIO.output(RelayPin, GPIO.LOW)
    GPIO.cleanup()


if __name__ == "__main__":
    setup()
    try:
        bpm = int(input("Enter the BPM (Beats Per Minute): "))
        if bpm < 1:
            raise ValueError("BPM must be a positive integer.")

        time_signature = input("Enter the time signature (e.g., 4/4, 6/8, 3/4): ")
        if not time_signature or len(time_signature.split('/')) != 2:
            raise ValueError("Invalid time signature format.")

        play_metronome(bpm, time_signature)
    except ValueError as ve:
        print(ve)
    except KeyboardInterrupt:
        print("\nMetronome stopped.")
        destroy()
