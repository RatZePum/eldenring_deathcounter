# import the libraries
import difflib

import cv2 as cv
import numpy as np
import pytesseract
import time
import pyautogui
import os

debug = False


# ----------------------------------------------------------------------------
def screenshot(name: str) -> str:
    img = pyautogui.screenshot()
    sh_path = os.path.join(os.path.dirname(__file__), "images", f"{name}.jpg")

    img.save(sh_path)

    return sh_path


# ----------------------------------------------------------------------------
def show(cv2img, name: str = "image"):
    if not debug:
        return None

    cv.imshow(name, cv2img)
    cv.waitKey(0)


# ----------------------------------------------------------------------------
def get_red_screen_text(sh_path: str):
    img = cv.imread(sh_path)
    img = img[480:600, 300: 1600]
    show(img, "croped")

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_red = np.array([160, 100, 50])
    upper_red = np.array([180, 255, 255])

    mask = cv.inRange(hsv, lower_red, upper_red)
    mask_inv = cv.bitwise_not(mask)

    show(mask, "mask")
    show(mask_inv, "mask_inv")

    return pytesseract.image_to_string(mask_inv, lang='deu')


# ----------------------------------------------------------------------------
def get_ocr_diff_ratio(text_rec: str, match: str) -> float:
    a = text_rec.casefold()
    b = match.casefold()
    diff_ratio = difflib.SequenceMatcher(a=a, b=b).ratio()

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
def get_example_path():
    return os.path.join(os.path.dirname(__file__), "example", f"example.png")


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
MATCH_DIED_DE = "ihr seid gestorben"

while True:
    print("--------------------------------------------")
    start = time.time()

    # path = screenshot(start)
    path = get_example_path()
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
