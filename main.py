import time
import math
import keyboard
import ctypes
import tkinter
from tkinter.filedialog import askopenfilename
import osu_parser
import pyautogui as pag
import random

pag.PAUSE = 0.000000001


def get_new_resolution():  # 1
    while True:
        try:
            x = int(input("\nX: "))
            y = int(input("Y: "))
        except ValueError:
            print("Insert an valid number.")
        else:
            if x >= 640 and y >= 480:
                dif = (0.6 / 19) * y
                return x, y, dif

            print("Lowest possible resolution is 640x480. Please insert a valid one.")


def get_new_offset():  # 2
    while True:
        try:
            offset = int(input("\nOffset (in ms): "))
        except ValueError:
            print("Insert an valid number.")
        else:
            if offset >= 0:
                return offset / 1000

            print("Offset must be greater than 0.")


def busy_wait(duration):  # 3
    start = time.perf_counter()
    while time.perf_counter() < start + duration:
        pass


def slider_move(path, duration, repeat, start, next_tracker):  # 4
    pag.mouseDown()
    skip = duration / len(path) / 1000
    index = -1
    direction = -1
    for i in range(repeat):
        direction *= -1
        index += direction
        for point in path:
            ctypes.windll.user32.SetCursorPos(path[index][0], path[index][1])
            index += direction
            busy_wait(skip)

            if keyboard.is_pressed("s") or time.perf_counter() >= start + next_tracker:
                return
    pag.mouseUp()


def spin(duration, screen_x, screen_y, screen_dif):
    pag.mouseDown()
    angle = 0
    a = 0.1
    end = time.perf_counter() + duration / 1000
    while end > time.perf_counter() and not keyboard.is_pressed("s"):
        x = int(math.cos(angle) * (screen_x * a) + (screen_x / 2))
        y = int(math.sin(angle) * (screen_x * a) + (screen_y + screen_dif) / 2)
        ctypes.windll.user32.SetCursorPos(x, y)
        angle += a/25
    pag.mouseUp()


def adjust_offsets(HOs):
    first = HOs[0].offset

    for count, ho in enumerate(HOs):
        HOs[count].offset = (HOs[count].offset - first) / 1000


def main():
    # 1
    tkinter.Tk().withdraw()
    offset = 0.005
    DT, HT, HR = False, False, False
    LOADED = False
    HOs = None

    screen_x = ctypes.windll.user32.GetSystemMetrics(0)
    screen_y = ctypes.windll.user32.GetSystemMetrics(1)
    screen_dif = (0.6 / 19) * screen_y
    # 2
    print(f'''
Press L to load a map.
Press P to start the map.
Press S to stop the map.
Press D to toggle DT, H to toggle HT.
Press R to toggle Hard Rock.
Press Q to change resolution manually.
Press O to change start offset.
Press PauseBreak to stop the bot from taking inputs, 
Press again to bring it back to life.

Offset: {offset * 1000} ms
DT: {DT}   
HT: {HT}   
HR: {HR}
{screen_x}x{screen_y}.
    '''

          )

    # 3
    while True:
        # 4
        if keyboard.is_pressed("l"):
            beatmap = askopenfilename(filetypes=[("Osu files", "*.osu")])

            try:
                f = open(file=beatmap, mode="r", encoding="utf8")
            except FileNotFoundError:
                continue

            try:
                HOs = osu_parser.parse_HOs(f, DT, HT, HR)
                osu_parser.convert_coordinates(HOs, screen_x, screen_y)
                adjust_offsets(HOs)

            except Exception as e:
                print(f"Something went wrong... error: {e}")
            else:
                print("Loaded successfully")
                LOADED = True
        # 5
        elif keyboard.is_pressed("p") and LOADED:
            tracker = 0
            busy_wait(offset)
            start = time.perf_counter()

            while len(HOs) > tracker and not keyboard.is_pressed("s"):
                if time.perf_counter() >= HOs[tracker].offset + start:
                    if HOs[tracker].obj == 1:  # 6
                        ctypes.windll.user32.SetCursorPos(HOs[tracker].x, HOs[tracker].y)
                        pag.click()
                    elif HOs[tracker].obj == 2:
                        try:
                            next_tracker = HOs[tracker + 1].offset
                        except IndexError:
                            next_tracker = math.inf
                        slider_move(HOs[tracker].path, HOs[tracker].duration, HOs[tracker].repeat, start, next_tracker)

                    else:
                        spin(HOs[tracker].duration, screen_x, screen_y, screen_dif)

                    tracker += 1
        # 7
        elif keyboard.is_pressed("d") or keyboard.is_pressed("h") or keyboard.is_pressed("r"):
            if keyboard.is_pressed("d"):
                DT = not DT
                if HT: HT = False
            elif keyboard.is_pressed("h"):
                HT = not HT
                if DT: DT = False
            elif keyboard.is_pressed("r"):
                HR = not HR

            if HOs is not None:
                HOs = osu_parser.parse_HOs(f, DT, HT, HR)
                osu_parser.convert_coordinates(HOs, screen_x, screen_y)
                adjust_offsets(HOs)

            print(f"DT: {DT}   HT: {HT}   HR: {HR}")
            time.sleep(0.1)
        # 8
        elif keyboard.is_pressed("q"):
            screen_x, screen_y, screen_dif = get_new_resolution()
            print(f"New resolution set to {screen_x}x{screen_y}")
        # 9
        elif keyboard.is_pressed("o"):
            offset = get_new_offset()
            print(f"New offset set to {offset * 1000} ms")
        # 10
        elif keyboard.is_pressed("pause"):
            time.sleep(0.15)

            while not keyboard.is_pressed("pause"):
                time.sleep(0.05)
            time.sleep(0.15)


if __name__ == "__main__":
    main()
