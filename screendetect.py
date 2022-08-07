# import the libraries
import difflib

import cv2 as cv
import numpy as np
import pytesseract
import time
import pyautogui
import os


# ----------------------------------------------------------------------------
def screenshot(timestr: str) -> str:
    img = pyautogui.screenshot()
    path = os.path.join(os.path.dirname(__file__), "images", f"{timestr}.jpg")
    img.save(path)

    # print(f"Took screenshot: {path}")
    # log.debug(f"Saved screen-image: {path}")

    return path


# ----------------------------------------------------------------------------
def get_red_screen_text(path: str):
    # custom_config = r'--psm 13 --oem 2'

    img = cv.imread(path)
    # img = img[515:580, 300: 1600]

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    lower_red = np.array([160, 100, 50])
    upper_red = np.array([180, 255, 255])

    mask = cv.inRange(hsv, lower_red, upper_red)
    mask_inv = cv.bitwise_not(mask)

    # cv.namedWindow("mask_inv", cv.WINDOW_NORMAL)
    # cv.imshow("mask_inv", mask_inv)

    return pytesseract.image_to_string(mask_inv, lang='deu')


# ----------------------------------------------------------------------------
def get_ocr_diff_ratio(text_rec: str, match: str) -> float:
    a = text_rec.casefold()
    b = match.casefold()
    diff_ratio = difflib.SequenceMatcher(a=a, b=b).ratio()

    # log.debug(f"TEXT GET: {a}")
    # log.debug(f"TEXT MATCH: {b}")
    # log.debug(f"RATIO: {diff_ratio}")

    return diff_ratio


# ----------------------------------------------------------------------------
def save_death_file(name: str, tmp_path: str):
    image = cv.imread(tmp_path)

    death_path = os.path.join(
        os.path.dirname(__file__),
        "death",
        f"{name}.jpg"
    )

    cv.imwrite(death_path, image)
    print(f"Saved death file: {death_path}")


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
MATCH_DIED_DE = "ihr seid gestorben"

while True:
    print("--------------------------------------------")
    start = time.time()

    path = screenshot(start)
    text = get_red_screen_text(path)
    ratio = get_ocr_diff_ratio(text, MATCH_DIED_DE)

    end = time.time()

    print(f"GOT: {text}")
    print(f"RATIO: {ratio}")
    print(f"TIME: {end - start}")

    if ratio > 0.5:
        print("CHECK - saving file")
        save_death_file(start, path)

    time.sleep(1)
