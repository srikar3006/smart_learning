# ============================================================
# RHYMES — CONTENT CONFIG
# ============================================================
#
# This is the ONE file you need to edit to add, remove or update
# a rhyme on the "Rhymes" page. It works exactly the same way as
# core/video_data.py does for the "Animated Videos & Stories" page.
#
# HOW TO ADD A NEW RHYME
# -----------------------------------------------------------
# 1. Copy one of the dictionaries below and paste it at the end
#    of the RHYMES list.
# 2. Give it a new unique "id" (just the next number).
# 3. Set "category" to one of the values in CATEGORIES below
#    (the value must match exactly, e.g. "Animals").
# 4. Drop your audio file and thumbnail image here:
#
#       PUT RHYME AUDIO FILES HERE:      static/audio/rhymes/<your-file>.mp3
#       PUT RHYME THUMBNAILS HERE:       static/images/rhymes/<your-file>.jpg
#
#    then point "audio" / "thumbnail" at those filenames.
# 5. That's it — no other file needs to change. The Rhymes page
#    reads this list automatically.
#
# NOTE ON AUDIO/THUMBNAIL FILES
# -----------------------------------------------------------
# Each rhyme currently points at a simple hand-drawn .svg
# thumbnail (already included in static/images/rhymes/) so the
# page looks complete out of the box. Swap any of them out for
# your own .jpg/.png photo any time — just replace the file and
# update the "thumbnail" value below to match your filename.
#
# There are no placeholder audio files (only you can legally
# supply the rhyme recordings). Until a real .mp3 is added in
# static/audio/rhymes/, the bottom player will show a friendly
# "audio coming soon" message instead of failing.
#
# ONLY LOCAL FILES ARE USED ON THIS PAGE.
# No YouTube, Spotify or any other external service is used for
# rhyme audio or thumbnails — everything is served from this
# project's own /static/ folder.
# ============================================================


# Categories shown as filter pills at the top of the page.
# "slug" is used internally for filtering, "label" is shown to the user.
CATEGORIES = [
    {"slug": "all", "label": "All Rhymes", "icon": "🎵"},
    {"slug": "Animals", "label": "Animals", "icon": "🐾"},
    {"slug": "Nursery", "label": "Nursery", "icon": "🧸"},
    {"slug": "Action", "label": "Action", "icon": "🏃"},
    {"slug": "Nature", "label": "Nature", "icon": "🌿"},
    {"slug": "Festival", "label": "Festival", "icon": "🎁"},
]


# ------------------------------------------------------------
# RHYME LIBRARY
# ADD NEW RHYMES HERE — add new entries below this line, keep
# the same shape (id, title, description, category, duration,
# rating, thumbnail, audio).
# ------------------------------------------------------------
RHYMES = [
    {
        "id": 1,
        "title": "Humpty Dumpty",
        "description": "A classic nursery rhyme",
        "category": "Nursery",
        "duration": "02:15",
        "rating": 4.8,
        "thumbnail": "images/reference/humpty.png",
        "audio": "audio/rhymes/humpty-dumpty.mp3",
    },
    {
        "id": 2,
        "title": "Twinkle Twinkle Little Star",
        "description": "Lullaby rhyme",
        "category": "Nature",
        "duration": "01:45",
        "rating": 4.9,
        "thumbnail": "images/reference/twinkle.png",
        "audio": "audio/rhymes/twinkle-twinkle.mp4",
    },
    {
        "id": 3,
        "title": "Baa Baa Black Sheep",
        "description": "Farmyard rhyme",
        "category": "Animals",
        "duration": "01:30",
        "rating": 4.7,
        "thumbnail": "images/reference/baa-baa.png",
        "audio": "audio/rhymes/baa-baa-black-sheep.mp3",
    },
    {
        "id": 4,
        "title": "Wheels on the Bus",
        "description": "Fun ride rhyme",
        "category": "Action",
        "duration": "02:05",
        "rating": 4.6,
        "thumbnail": "images/rhymes/wheels-on-the-bus.svg",
        "audio": "audio/rhymes/wheels-on-the-bus.mp3",
    },
    {
        "id": 5,
        "title": "Mary Had a Little Lamb",
        "description": "Animal rhyme",
        "category": "Animals",
        "duration": "01:50",
        "rating": 4.7,
        "thumbnail": "images/rhymes/mary-had-a-little-lamb.svg",
        "audio": "audio/rhymes/mary-had-a-little-lamb.mp3",
    },
    {
        "id": 6,
        "title": "Rain Rain Go Away",
        "description": "Rainy day rhyme",
        "category": "Nature",
        "duration": "01:40",
        "rating": 4.5,
        "thumbnail": "images/rhymes/rain-rain-go-away.svg",
        "audio": "audio/rhymes/rain-rain-go-away.mp3",
    },
    {
        "id": 7,
        "title": "If You're Happy and You Know It",
        "description": "Action rhyme",
        "category": "Action",
        "duration": "01:55",
        "rating": 4.8,
        "thumbnail": "images/rhymes/if-youre-happy.svg",
        "audio": "audio/rhymes/if-youre-happy.mp3",
    },
    {
        "id": 8,
        "title": "Jingle Bells",
        "description": "Festival rhyme",
        "category": "Festival",
        "duration": "02:10",
        "rating": 4.9,
        "thumbnail": "images/rhymes/jingle-bells.svg",
        "audio": "audio/rhymes/jingle-bells.mp3",
    },
    # ---- add new rhymes above this line -----------------------
]
