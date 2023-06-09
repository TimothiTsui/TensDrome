import RPi.GPIO as GPIO
import time
import subprocess
import LCD1602
StrongPin = 23
MediumPin = 24


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(StrongPin, GPIO.OUT)
    GPIO.setup(MediumPin, GPIO.OUT)
    LCD1602.init(0x27, 1)

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
        GPIO.output(StrongPin, GPIO.LOW)
        GPIO.output(MediumPin, GPIO.LOW)
        if meter == "simple":
            if meter_name == "duple":
                if count % 2 == 0 or count / count_unit == 0:
                    print("Strong")
                    GPIO.output(StrongPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(StrongPin, GPIO.LOW)
                    time.sleep(interval / 2)
                else:
                    print(1+count % 2)
                    GPIO.output(MediumPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(MediumPin, GPIO.LOW)
                    time.sleep(interval / 2)

            elif meter_name == "triple":
                if count % 3 == 0 or count / count_unit == 0:
                    print("Strong")
                    GPIO.output(StrongPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(StrongPin, GPIO.LOW)
                    time.sleep(interval / 2)
                else:
                    print(1 + count % 3)
                    GPIO.output(MediumPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(MediumPin, GPIO.LOW)
                    time.sleep(interval / 2)

            else:
                if count % 4 == 0 or (count+2) % count_unit == 0:
                    if (count+2) % count_unit == 0:
                        print("Medium Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                    else:
                        print("Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                else:
                    print(1 + count % 4)
                    GPIO.output(MediumPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(MediumPin, GPIO.LOW)
                    time.sleep(interval / 2)

        elif meter == "compound":


            if meter_name == "duple":
                if count % 3 == 0:
                    if count % beats_per_measure == 0 or (count+2) % (beats_per_measure) == 0:
                        print("Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                    else:
                        print("Medium Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                else:
                    print(1 + count % beats_per_measure)
                    GPIO.output(MediumPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(MediumPin, GPIO.LOW)
                    time.sleep(interval / 2)

            elif meter_name == "triple":
                if count % 3 == 0:
                    if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                        print("Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                    else:
                        print("Medium Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                else:
                    print(1 + count % beats_per_measure)
                    GPIO.output(MediumPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(MediumPin, GPIO.LOW)
                    time.sleep(interval / 2)
            else:
                if count % 3 ==0:
                    if count % beats_per_measure == 0 or (count + 2) % (beats_per_measure) == 0:
                        print("Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                    else:
                        print("Medium Strong")
                        GPIO.output(StrongPin, GPIO.HIGH)
                        time.sleep(interval / 2)
                        GPIO.output(StrongPin, GPIO.LOW)
                        time.sleep(interval / 2)
                else:
                    print(1 + count % beats_per_measure)
                    GPIO.output(MediumPin, GPIO.HIGH)
                    time.sleep(interval / 2)
                    GPIO.output(MediumPin, GPIO.LOW)
                    time.sleep(interval / 2)




        line_1 = "BPM: " + str(bpm)
        line_2 = "Time Sig: " + time_signature
        LCD1602.write(0, 0, line_1)
        LCD1602.write(0, 1, line_2)

        count += 1

def destroy():
    GPIO.output(StrongPin, GPIO.LOW)
    GPIO.output(MediumPin, GPIO.LOW)
    GPIO.cleanup()
    LCD1602.clear()


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
