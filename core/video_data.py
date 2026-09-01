# ============================================================
# ANIMATED VIDEOS & STORIES — CONTENT CONFIG
# ============================================================
#
# This is the ONE file you need to edit to add, remove or update
# a video/story on the "Animated Videos & Stories" page.
#
# HOW TO ADD A NEW VIDEO
# -----------------------------------------------------------
# 1. Copy one of the dictionaries below and paste it at the end
#    of the VIDEOS list.
# 2. Give it a new unique "id" (just the next number).
# 3. Set "category" to one of the values in CATEGORIES below
#    (the value must match exactly, e.g. "Stories").
# 4. Drop your thumbnail image here:
#       static/images/videos/<your-file>.jpg
#    and your video file here:
#       static/videos/<your-file>.mp4
#    then point "thumbnail" / "video" at those filenames.
# 5. That's it — no other file needs to change. The page reads
#    this list automatically.
#
# NOTE ON VIDEO/THUMBNAIL FILES
# -----------------------------------------------------------
# The filenames referenced below are placeholders. Until you add
# the real .mp4 / .jpg files in the folders above, the thumbnail
# will show a generated placeholder and the video player will
# show a friendly "video coming soon" message instead of failing.
# ============================================================


# Categories shown as filter tabs at the top of the page.
# "slug" is used internally for filtering, "label" is shown to the user.
CATEGORIES = [
    {"slug": "all", "label": "All", "icon": "🟣"},
    {"slug": "learning", "label": "Learning", "icon": "🎓"},
    {"slug": "stories", "label": "Stories", "icon": "📖"},
    {"slug": "moral-stories", "label": "Moral Stories", "icon": "💛"},
    {"slug": "nature", "label": "Nature", "icon": "🌿"},
    {"slug": "life-skills", "label": "Life Skills", "icon": "⭐"},
]


# ------------------------------------------------------------
# VIDEO / STORY LIBRARY
# Add new entries below this line — keep the same shape.
# ------------------------------------------------------------
VIDEOS = [
    {
        "id": 1,
        "title": "Animal Stories",
        "description": "Fun animal adventures",
        "category": "stories",
        "duration": "06:15",
        "thumbnail": "images/videos/animal-stories.jpg",
        "video": "videos/animal-stories.mp4",
    },
    {
        "id": 2,
        "title": "Colors for Kids",
        "description": "Learn colors with fun",
        "category": "learning",
        "duration": "05:20",
        "thumbnail": "images/videos/colors-for-kids.jpg",
        "video": "videos/colors-for-kids.mp4",
    },
    {
        "id": 3,
        "title": "Numbers 1-10",
        "description": "Count and learn",
        "category": "learning",
        "duration": "04:30",
        "thumbnail": "images/videos/numbers-1-10.jpg",
        "video": "videos/numbers-1-10.mp4",
    },
    {
        "id": 4,
        "title": "ABC Learning",
        "description": "Learn alphabets easily",
        "category": "learning",
        "duration": "05:10",
        "thumbnail": "images/videos/abc-learning.jpg",
        "video": "videos/abc-learning.mp4",
    },
    {
        "id": 5,
        "title": "Good Habits",
        "description": "Healthy habits for kids",
        "category": "life-skills",
        "duration": "05:10",
        "thumbnail": "images/videos/good-habits.jpg",
        "video": "videos/good-habits.mp4",
    },
    {
        "id": 6,
        "title": "Nature & Environment",
        "description": "Love and protect nature",
        "category": "nature",
        "duration": "05:35",
        "thumbnail": "images/videos/nature-environment.jpg",
        "video": "videos/nature-environment.mp4",
    },
    {
        "id": 7,
        "title": "The Tortoise and the Hare",
        "description": "Slow and steady wins the race",
        "category": "moral-stories",
        "duration": "07:30",
        "thumbnail": "images/videos/tortoise-and-hare.jpg",
        "video": "videos/tortoise-and-hare.mp4",
    },
    {
        "id": 8,
        "title": "The Ant and the Grasshopper",
        "description": "Hard work pays off",
        "category": "moral-stories",
        "duration": "06:20",
        "thumbnail": "images/videos/ant-and-grasshopper.jpg",
        "video": "videos/ant-and-grasshopper.mp4",
    },
    {
        "id": 9,
        "title": "The Thirsty Crow",
        "description": "Cleverness solves problems",
        "category": "moral-stories",
        "duration": "05:50",
        "thumbnail": "images/videos/thirsty-crow.jpg",
        "video": "videos/thirsty-crow.mp4",
    },
    {
        "id": 10,
        "title": "The Three Little Goats",
        "description": "Bravery over the bridge",
        "category": "moral-stories",
        "duration": "07:05",
        "thumbnail": "images/videos/three-little-goats.jpg",
        "video": "videos/three-little-goats.mp4",
    },
    # ---- add new videos above this line -----------------------
]