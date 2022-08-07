# ****************************************************************************
# ****************************************************************************

import difflib

import cv2
import logging
import os
import pyautogui
import pytesseract
import re
import time

import numpy

# ****************************************************************************
# ****************************************************************************

debug = False

# ----------------------------------------------------------------------------
logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log = logging.getLogger()

fileHandler = logging.FileHandler(f"log/main.log")
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

log.setLevel(logging.DEBUG if debug else logging.INFO)

# ----------------------------------------------------------------------------
PATH_COUNTER_FILE = os.path.join(
    "C:\\", "Users", "ratze", "Desktop", "Twitch", "current",
    "eldenring_death_counter.txt"
)

MATCH_DIED_DE = "ihr seid gestorben"


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

def iter_counter_file():
    with open(PATH_COUNTER_FILE, "r+") as f:
        content = f.read()
        f.seek(0)

        print(f"Current counter file content: {content}")

        f.write(str(int(content) + 1))
        f.truncate()


# ----------------------------------------------------------------------------
def show(cv2img, name: str = "image"):
    cv2.imshow(name, cv2img)
    cv2.waitKey(0)


# ----------------------------------------------------------------------------
def get_center_screen_text(img_path: str):
    image = cv2.imread(img_path)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # lukas von der treppe schubsen # cluster algorythmus - falls mir langweilig ist
    # gradiant, kontrast hoch, threshhold

    part_middle_crop = image[515:580, 450: 1500]
    # part_middle_crop = image[:, :, 2] # ONLY RED

    show(part_middle_crop)

    hsv = cv2.cvtColor(part_middle_crop, cv2.COLOR_BGR2HSV)
    lower = numpy.array([155, 25, 0])
    upper = numpy.array([179, 255, 255])
    mask = cv2.inRange(part_middle_crop, lower, upper)
    result = cv2.bitwise_and(hsv, hsv, mask=mask)

    show(result)
    show(mask)



    # slowing thinks down
    # part_middle_crop = cv2.fastNlMeansDenoisingColored(part_middle_crop,None,10,10,7,21)
    # show(part_middle_crop)

    custom_config = r'--psm 13 --oem 2'
    text = pytesseract.image_to_string(part_middle_crop, lang='deu',
                                       config=custom_config)

    text = re.sub('[^0-9a-zA-Z ]+', '', text)
    text = text.strip()

    return text


# ----------------------------------------------------------------------------
def screenshot() -> str:
    filename = str(i) if debug else "tmp"

    img = pyautogui.screenshot()
    path = os.path.join(os.path.dirname(__file__), "images", f"{filename}.jpg")
    img.save(path)

    log.debug(f"Saved screen-image: {path}")

    return path


# ----------------------------------------------------------------------------
def get_ocr_diff_ratio(text_rec: str, match: str) -> float:
    a = text_rec.casefold()
    b = match.casefold()
    diff_ratio = difflib.SequenceMatcher(a=a, b=b).ratio()

    log.debug(f"TEXT GET: {a}")
    log.debug(f"TEXT MATCH: {b}")
    log.debug(f"RATIO: {diff_ratio}")

    return diff_ratio


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# toast = ToastNotifier()
# toast.show_toast("Elden Ring Dying Message", "Du bist gesterbiet!")


i = 0
while True:
    log.debug(f"--------------------------------------------------------  {i}")

    text = get_center_screen_text(screenshot())
    ratio = get_ocr_diff_ratio(text, MATCH_DIED_DE)

    if ratio >= 0.5:
        print(f"MÄH: {text} - {ratio}")

        log.info("-- GESTORBEN --")
        iter_counter_file()
        time.sleep(5)
    else:
        time.sleep(300 / 1000)

    i += 1

# text = get_center_screen_text(screenshot())

# # ----------------------------------------------------------------------------
# def is_died_screen(imgpath: str):
#     image = cv2.imread(imgpath)
#     # image = cv2.cvtColor(image, cv2.IMREAD_UNCHANGED)
#     # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#
#     # cv2.imshow("name", image)
#     # cv2.waitKey(0)
#     # 0:500 1920:500
#     # 0:580 1920:580
#
#     # part_middle_crop = image[500:580, 520: 1400] # perfect for normal died
#     part_middle_crop = image[500:580, 300: 1600]
#
#     # steps = 1
#     # height = 540
#     # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     # color pxl check
#     # for i in range(round(1920 - steps)):
#     #     pxl = image[height, i * steps]
#     #     b, g, r = pxl
#     #     print(f"Colors: {r} {g} {b} - [{height}:{i}]")
#
#     # image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     custom_config = r'--psm 13 --oem 1'
#     text = pytesseract.image_to_string(part_middle_crop, lang='deu',
#                                        config=custom_config)
#
#     MATCH_DIED_DE = "ihr seid gestorben"
#
#     if text.strip().lower() == MATCH_DIED_DE:
#         print(">>> YOYOYOYO <<<")
#     else:
#         print(f"nothing interesting...")
#
#     # # 0:500 1920:500
#     # # 0:580 1920:580
