# pomodoro_timer.py
import os
import platform
import time

try:
    import RPi.GPIO as GPIO
    from sense_hat import SenseHat
    SENSE_HAT_AVAILABLE = True
    sense = SenseHat()
except (ImportError, RuntimeError):
    SENSE_HAT_AVAILABLE = False
    GPIO = None

WORK_DURATION = 25 * 60  # 25 minutes
BREAK_DURATION = 5 * 60  # 5 minutes
LONG_BREAK = 15 * 60     # Optional long break
SESSIONS_BEFORE_LONG_BREAK = 4

LED_PIN = 18  # Use GPIO18
if GPIO:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

def beep():
    if platform.system() == "Darwin":  # macOS
        os.system("say 'Time is up!'")
    elif platform.system() == "Linux":  # Raspberry Pi
        os.system("aplay /usr/share/sounds/alsa/Front_Center.wav")

    if GPIO:
        for _ in range(5):
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.3)

    if SENSE_HAT_AVAILABLE:
        sense.show_message("Time's Up!", text_colour=[0, 255, 0])
        sense.clear()

def countdown(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02}:{secs:02}"
        print(f"\r\033[92m⏳ Timer: {timer}\033[0m", end="")
        time.sleep(1)
        seconds -= 1
    print("\n\033[92m🔔 Time's up!\033[0m")
    beep()

def pomodoro():
    session_count = 0
    try:
        while True:
            print(f"\n\033[92m🍅 Pomodoro session #{session_count + 1} starting!\033[0m")
            countdown(WORK_DURATION)

            session_count += 1

            if session_count % SESSIONS_BEFORE_LONG_BREAK == 0:
                print("\n\033[92m🌴 Time for a long break!\033[0m")
                countdown(LONG_BREAK)
            else:
                print("\n\033[92m☕ Time for a short break!\033[0m")
                countdown(BREAK_DURATION)
    except KeyboardInterrupt:
        print("\n\033[92m⏹️ Timer stopped. Good work!\033[0m")
        if GPIO:
            GPIO.cleanup()

if __name__ == "__main__":
    pomodoro()