import RPi.GPIO as GPIO
import time

RelayPin = 18


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RelayPin, GPIO.OUT)
    GPIO.output(RelayPin, GPIO.LOW)


def play_metronome(bpm, time_signature):
    interval = 60.0 / bpm
    beats_per_measure, count_unit = map(int, time_signature.split('/'))

    if beats_per_measure in list({2,3,4}):
        meter = str("simple")
    elif beats_per_measure in list({6,9,12}):
        meter = str("compound")
    else:
        meter = str("complex")

    if beats_per_measure in list({2,6}):
        meter_name = str("duple")
    elif beats_per_measure in list({3,9}):
        meter_name = str("triple")
    elif beats_per_measure in list({4,12}):
        meter_name = str("quadruple")
    else:
        meter_name = str("complex")
    count = 0

    while True:
        if meter == "simple":
            if meter_name == "duple":
                if count % 2 == 0 or count / count_unit == 0:
                    print("Strong")
                else:
                    print(1+count % 2)

            elif meter_name == "triple":
                if count % 3 == 0 or count / count_unit == 0:
                    print("Strong")
                else:
                    print(1 + count % 3)

            else:
                if count % 4 == 0 or (count+2) % count_unit == 0:
                    if (count+2) % count_unit == 0:
                        print("Medium Strong")
                    else:
                        print("Strong")
                else:
                    print(1 + count % 4)

        elif meter == "compound":


            if meter_name == "duple":
                if count % 3 == 0:
                    if count % beats_per_measure == 0 or (count+2) % (beats_per_measure) == 0:
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
                if count % 3 ==0:
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
