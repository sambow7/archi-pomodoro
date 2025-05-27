# pomodoro_timer.py

import time

WORK_DURATION = 25 * 60  # 25 minutes
BREAK_DURATION = 5 * 60  # 5 minutes
LONG_BREAK = 15 * 60     # Optional long break
SESSIONS_BEFORE_LONG_BREAK = 4

def countdown(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02}:{secs:02}"
        print(f"\r⏳ Timer: {timer}", end="")
        time.sleep(1)
        seconds -= 1
    print("\n🔔 Time's up!")

def pomodoro():
    session_count = 0
    try:
        while True:
            print(f"\n🍅 Pomodoro session #{session_count + 1} starting!")
            countdown(WORK_DURATION)

            session_count += 1

            if session_count % SESSIONS_BEFORE_LONG_BREAK == 0:
                print("\n🌴 Time for a long break!")
                countdown(LONG_BREAK)
            else:
                print("\n☕ Time for a short break!")
                countdown(BREAK_DURATION)
    except KeyboardInterrupt:
        print("\n⏹️ Timer stopped. Good work!")

if __name__ == "__main__":
    pomodoro()