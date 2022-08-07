# ****************************************************************************
# ****************************************************************************

import difflib

import cv2
import logging
import os
import pyautogui
import pytesseract
import time
import asyncio
import numpy

from typing import Optional, Tuple, Any
from ctypes import windll, create_unicode_buffer

from help import debounce

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
WINDOW_NAME = "ELDEN RING™"

# ----------------------------------------------------------------------------

DIR_NAME_SCREENSHOT_CACHE = "screenshot_cache"
DIR_NAME_DEATH = "death"
DIR_NAME_WTF = "wtf"

# ----------------------------------------------------------------------------

DIR_CRNT = os.path.dirname(__file__)
DIR_SCREENSHOT_CACHE = os.path.join(
    DIR_CRNT,
    DIR_NAME_SCREENSHOT_CACHE
)
DIR_DEATH = os.path.join(
    DIR_CRNT,
    DIR_NAME_DEATH
)
DIR_WTF = os.path.join(
    DIR_CRNT, DIR_NAME_WTF
)

# ----------------------------------------------------------------------------

COLOR_CUT_LOWER_RED = numpy.array([160, 100, 50])
COLOR_CUT_HIGHER_RED = numpy.array([180, 255, 255])

# ----------------------------------------------------------------------------

OCR_DETECTION_LANG = "deu"
PICK_RATIO = 0.75


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def is_elden_ring_active_window() -> bool:
    return get_foreground_window_title() == WINDOW_NAME


# ----------------------------------------------------------------------------
def get_foreground_window_title() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)

    return buf.value if buf.value else None


# ----------------------------------------------------------------------------
@debounce(5)
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
def get_center_crop(image):
    return image[480:600, 300: 1600]


# ----------------------------------------------------------------------------
def get_red_screen_text(path: str) -> Tuple[Any, Any, Any, str]:
    img = cv2.imread(path)
    img = get_center_crop(img)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, COLOR_CUT_LOWER_RED, COLOR_CUT_HIGHER_RED)
    mask_inv = cv2.bitwise_not(mask)

    text = pytesseract.image_to_string(
        mask_inv,
        lang=OCR_DETECTION_LANG
    )

    return img, mask, mask_inv, text


# ----------------------------------------------------------------------------
def make_screenshot() -> str:
    name = time.time()
    img = pyautogui.screenshot()
    sh_path = get_screenshot_path(name)
    img.save(sh_path)

    log.debug(f"Saved screen-image: {sh_path}")

    return sh_path


# ----------------------------------------------------------------------------
def delete_next_few(path: str) -> bool:
    dirname = os.path.dirname(path)
    files = os.listdir(dirname)
    files = sorted(
        [os.path.join(dirname, x) for x in files],
        key=os.path.getctime
    )

    pick_count = round(5 / PICK_RATIO)
    log.info(f"Will remove the next {pick_count}")

    for i in range(pick_count):
        if files[i]:
            os.remove(files[i])
            log.info(f"Removed additional file: [{files[i]}]")
        else:
            return True

    return True


# ----------------------------------------------------------------------------
def save_into_death(name: str, cv_image: Any) -> bool:
    death_path = os.path.join(
        DIR_DEATH,
        f"{name}.jpg"
    )

    cv2.imwrite(death_path, cv_image)

    log.info(f"Saved into deaths: {name}")

    return True, death_path


# ----------------------------------------------------------------------------
def save_results_into_wtf(
        name: str,
        original,
        mask,
        mask_inv,
        ocr_text: str
) -> bool:
    dir_path = os.path.join(DIR_WTF, name)

    os.mkdir(dir_path)

    original_path = os.path.join(dir_path, "original.jpg")
    mask_path = os.path.join(dir_path, "mask.jpg")
    mask_inv_path = os.path.join(dir_path, "mask_inv.jpg")
    ocr_result_path = os.path.join(dir_path, "ocr_result_text.txt")

    cv2.imwrite(original_path, original)
    cv2.imwrite(mask_path, mask)
    cv2.imwrite(mask_inv_path, mask_inv)

    with open(ocr_result_path, 'w') as f:
        f.write(ocr_text)

    log.info(f"Weird results [{ocr_text}]: saving [{name}] into wtf")

    return True, dir_path


# ----------------------------------------------------------------------------
def get_screenshot_path(name: str):
    return os.path.join(DIR_NAME_SCREENSHOT_CACHE, f"{name}.jpg")


# ----------------------------------------------------------------------------
def remove_cached_screenshot(screenshot_path: str) -> bool:
    os.remove(screenshot_path)

    log.debug(f"Removed cached screenshot: {screenshot_path}")

    return True


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
def get_oldest_file_from(path: str):
    files = os.listdir(path)

    if len(files) > 0:
        return sorted(
            [os.path.join(path, x) for x in files],
            key=os.path.getctime
        )[0]

    return None


# ----------------------------------------------------------------------------
def get_next_screenshot():
    return get_oldest_file_from(DIR_NAME_SCREENSHOT_CACHE)


# ----------------------------------------------------------------------------
async def loop_detection():
    while True:
        next_path = get_next_screenshot()

        if next_path is None:
            if not is_elden_ring_active_window():
                log.info("Elden Ring is not active. "
                         "Pausing detection for 5 seconds...")

                await asyncio.sleep(5)

            await asyncio.sleep(0.1)
        else:
            name = os.path.basename(next_path).split(".")[0]

            img_original, img_mask, img_mask_inv, ocr_text = \
                get_red_screen_text(next_path)

            log.debug(f"GOT: {ocr_text}")
            ratio = get_ocr_diff_ratio(ocr_text, MATCH_DIED_DE)
            log.debug(f"RATIO: {ratio}")

            if ratio > 0.75:
                log.info("YOYOYO: heee/sheee dead... hehe")
                save_into_death(name, img_original)
                iter_counter_file()
                # delete_next_few(next_path)
            # elif ratio > 0.35:
            #     save_results_into_wtf(
            #         name,
            #         img_original,
            #         img_mask,
            #         img_mask_inv,
            #         ocr_text
            #     )
            else:
                log.debug("Nothing found...")

            remove_cached_screenshot(next_path)

            await asyncio.sleep(0.01)


# ----------------------------------------------------------------------------
async def loop_screenshot(sleep_time: float = PICK_RATIO):
    while True:
        if is_elden_ring_active_window():
            make_screenshot()
            await asyncio.sleep(sleep_time)
        else:
            log.info("Elden Ring is not active. Sleeping 5 seconds...")
            await asyncio.sleep(5)


# ----------------------------------------------------------------------------
async def main():
    f1 = loop.create_task(loop_screenshot())
    f2 = loop.create_task(loop_detection())

    await asyncio.wait([f1, f2])


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()

    # while True:
    #     print(get_foreground_window_title())

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(loop_screenshot())
    asyncio.ensure_future(loop_detection())
    loop.run_forever()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# toast = ToastNotifier()
# toast.show_toast("Elden Ring Dying Message", "Du bist gesterbiet!")


# i = 0
# while True:
#     log.debug(f"--------------------------------------------------------  {i}")
#
#     text = get_center_screen_text(screenshot())
#     ratio = get_ocr_diff_ratio(text, MATCH_DIED_DE)
#
#     if ratio >= 0.5:
#         print(f"MÄH: {text} - {ratio}")
#
#         log.info("-- GESTORBEN --")
#         iter_counter_file()
#         time.sleep(5)
#     else:
#         time.sleep(300 / 1000)
#
#     i += 1


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
