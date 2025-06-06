# pomodoro_timer_v2.py
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

WORK_DURATION = 10  # 10 seconds for testing
BREAK_DURATION = 5  # 5 seconds
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
        alert_colors = [
            [0, 255, 0],     # Green
            [255, 255, 0],   # Yellow
            [255, 165, 0],   # Orange
            [255, 0, 0],     # Red
            [0, 0, 0]        # Off (black)
    ]

    for _ in range(3):  # Repeat full sequence 3 times
        for color in alert_colors:
            sense.set_pixels([color] * 64)
            time.sleep(0.15)
    
    # Final glitchy red alert scroll
    sense.show_message("Time's Up!", text_colour=[255, 0, 0])
    sense.clear()
    
    
def update_led_progress(elapsed, total, color):
    if not SENSE_HAT_AVAILABLE:
        return
    progress = int((elapsed / total) * 64)
    pixels = [color if i < progress else [0, 0, 0] for i in range(64)]
    sense.set_pixels(pixels)

def countdown(seconds, session_type):
    total = seconds
    color = [0, 255, 0] if session_type == "work" else [0, 0, 255]
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02}:{secs:02}"
        print(f"\r\033[92m⏳ Timer: {timer}\033[0m", end="")
        update_led_progress(total - seconds, total, color)
        time.sleep(1)
        seconds -= 1
    print("\n\033[92m🔔 Time's up!\033[0m")
    beep()

def pomodoro():
    session_count = 0
    try:
        while True:
            print(f"\n\033[92m🍅 Pomodoro session #{session_count + 1} starting!\033[0m")
            countdown(WORK_DURATION, "work")

            session_count += 1

            if session_count % SESSIONS_BEFORE_LONG_BREAK == 0:
                print("\n\033[92m🌴 Time for a long break!\033[0m")
                countdown(LONG_BREAK, "break")
            else:
                print("\n\033[92m☕ Time for a short break!\033[0m")
                countdown(BREAK_DURATION, "break")
    except KeyboardInterrupt:
        print("\n\033[92m⏹️ Timer stopped. Good work!\033[0m")
        if GPIO:
            GPIO.cleanup()
        if SENSE_HAT_AVAILABLE:
            sense.clear()

if __name__ == "__main__":
    pomodoro()