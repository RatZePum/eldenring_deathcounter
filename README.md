IDEAS:
    - Invader detection?!
    - STATES
        - in fight possible?
    - BOSS STUFF
        - BOSS TRY COUNT
        - BOSS FIGHT STATE
        - BOSS NAME DETECTION

DETECTION DIFF WITH AND WITHOUT CROP
    # average full detection time without cropping: ~ 500ms
    # average full detection time with cropping: ~ 400ms

NOTE:
    the crop have to be with a border of a view px like 20+
    without a border the image recognition fails nearly every time

    now i use >> [480:600, 300: 1600] <<

    before there was no border on top or bottom [515:575, ...]
    => no recognition happened
