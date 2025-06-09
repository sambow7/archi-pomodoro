# pomodoro_timer_v3.py
import os
import platform
import time
import threading

try:
    import RPi.GPIO as GPIO
    from sense_hat import SenseHat, ACTION_PRESSED
    SENSE_HAT_AVAILABLE = True
    sense = SenseHat()
except (ImportError, RuntimeError):
    SENSE_HAT_AVAILABLE = False
    GPIO = None

WORK_DURATION = 25 * 60
BREAK_DURATION = 5 * 60
LONG_BREAK = 15 * 60
SESSIONS_BEFORE_LONG_BREAK = 4

LED_PIN = 18
if GPIO:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

# Global control flags
is_paused = False
should_exit = False
session_active = False

def beep():
    if platform.system() == "Darwin":
        os.system("say 'Time is up!'")
    elif platform.system() == "Linux":
        os.system("aplay /usr/share/sounds/alsa/Front_Center.wav")

    if GPIO:
        for _ in range(5):
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.3)

    if SENSE_HAT_AVAILABLE:
        alert_colors = [
            [0, 255, 0],
            [255, 255, 0],
            [255, 165, 0],
            [0, 0, 0]
        ]
        for _ in range(3):
            for color in alert_colors:
                sense.set_pixels([color] * 64)
                time.sleep(0.15)
        sense.show_message("Time's Up!", text_colour=[0, 255, 0])
        sense.clear()

def update_led_progress(elapsed, total, color):
    if not SENSE_HAT_AVAILABLE:
        return
    progress = int((elapsed / total) * 64)
    pixels = [color if i < progress else [0, 0, 0] for i in range(64)]
    sense.set_pixels(pixels)

def pulse_pause_animation():
    while is_paused and not should_exit:
        if SENSE_HAT_AVAILABLE:
            sense.set_pixels([[0, 255, 0]] * 64)
            time.sleep(0.5)
            sense.clear()
            time.sleep(0.5)

def joystick_listener():
    if not SENSE_HAT_AVAILABLE:
        return

    def handle_event(event):
        global is_paused, should_exit, session_active

        if event.action != ACTION_PRESSED:
            return

        if event.direction == "up" and not session_active:
            print("\n🎮 Joystick UP: Starting session")
            session_active = True

        elif event.direction == "down":
            print("\n🎮 Joystick DOWN: Stopping session")
            should_exit = True

        elif event.direction == "right" and session_active and not is_paused:
            print("\n🎮 Joystick RIGHT: Paused")
            is_paused = True

        elif event.direction == "left" and session_active and is_paused:
            print("\n🎮 Joystick LEFT: Resumed")
            is_paused = False

    sense.stick.direction_any = handle_event

def countdown(seconds, session_type):
    global is_paused, should_exit
    total = seconds
    color = [0, 255, 0] if session_type == "work" else [0, 0, 255]

    elapsed = 0
    while seconds:
        if should_exit:
            break
        if is_paused:
            pulse_pause_animation()
            continue

        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02}:{secs:02}"
        print(f"\r⏳ Timer: {timer}", end="")
        update_led_progress(elapsed, total, color)
        time.sleep(1)
        seconds -= 1
        elapsed += 1

    print("\n🔔 Time's up!")
    beep()

def pomodoro():
    global session_active, should_exit, is_paused
    session_count = 0
    print("🎮 Use joystick to start (UP), pause (RIGHT), resume (LEFT), or stop (DOWN).")
    joystick_thread = threading.Thread(target=joystick_listener, daemon=True)
    joystick_thread.start()

    try:
        while True:
            if should_exit:
                break
            if not session_active:
                time.sleep(0.1)
                continue

            print(f"\n🍅 Pomodoro session #{session_count + 1} starting!")
            countdown(WORK_DURATION, "work")
            if should_exit:
                break

            session_count += 1

            if session_count % SESSIONS_BEFORE_LONG_BREAK == 0:
                print("\n🌴 Long break starting...")
                countdown(LONG_BREAK, "break")
            else:
                print("\n☕ Short break starting...")
                countdown(BREAK_DURATION, "break")

            if should_exit:
                break
            session_active = False  # Reset after session

    except KeyboardInterrupt:
        print("\n⏹️ Timer manually stopped.")
    finally:
        if GPIO:
            GPIO.cleanup()
        if SENSE_HAT_AVAILABLE:
            sense.clear()

if __name__ == "__main__":
    pomodoro()