# ELDEN RING - OCR DETECTION
Program to detect a death in Elden Ring automatically via Screen-Grabbing,
Masking and OCR. Saves a number into a file.


## IDEAS:
- build detection via color part diff after masking to save calc time
    -> mask red => if red part more than x% try to detect something
    -> mask yellow => if yellow part more than x% try to detect something
- invader fight (could be cool, but a bit difficult)
- PvP fight
- Boss fight state
    - Boss death/try counter
    - Boss name in fight

## How it works [now]


2 async worker which
1. Makes a screenshot every 750ms and saves it into a tmp folder
2. Checks if an image exists in tmp folder, takes the latest
   and crops it down to the center area of the screen. 
   
   Mask the crop with lower and higher red numpy scale, inverts the 
   result and let tesseracts do the work. 
   
   If the recognition got a string content, and it matches the death 
   text to a 75%, it returns a True and iterates a number in a 
   specific file (currently static located).
   
### Language Detection
- DE
- EN (planed)


## TIMINGS
screenshot + ocr-tesseracts (image_to_string - default)

| Worker timings             | Time   |
| -------------              | ------ |
| detection without crop     | ~500ms |
| detection with crop        | ~400ms |
| image take every           |  750ms |

## NOTES:

#### DETECTION DETAILS
