# Smart Learning Through Tunes & Cartoons

A complete Django web application for the **Smart Learning Through Tunes & Cartoons** project described in the supplied PPT and abstract.

The platform is designed for early-childhood nursery-rhyme learning and implements the documented modules:

- User Interface
- User Authentication
- Learning Management
- Gamified Quizzes
- Progress Tracking
- Database / Storage
- Parent progress monitoring
- Django administration for content and user management

The current project scope does **not** require AI/ML. The supplied PPT lists AI-based personalization and voice recognition under **Future Enhancement**, so no external AI API or API key is required for the current implementation.

---

## 1. Project Overview

The learner can:

1. Create an account or sign in.
2. Browse nursery rhymes by category, search term and difficulty.
3. Watch an uploaded cartoon video, use an embeddable video URL, or listen to uploaded audio.
4. Use Smart Repeat to restart a local video/audio lesson and record practice.
5. Use built-in browser voice mode when a lesson has no uploaded media yet.
6. Mark a lesson as learned.
7. Take a simple gamified quiz.
8. Receive instant answer feedback.
9. Earn stars and rule-based badges.
10. View detailed learning progress.

A parent account can:

1. Create learner profiles.
2. View learner completion counts.
3. View Smart Repeat activity.
4. View quiz scores and stars.
5. View badges and recent assessment activity.

An administrator can use Django Admin to:

- Manage users and parent/learner relationships.
- Create and publish categories.
- Add/edit/delete rhymes.
- Upload video, audio and thumbnail media.
- Add quizzes and questions.
- Configure visual/audio quiz prompts.
- Review quiz attempts and answers.
- Manage badges.

---

## 2. Features

### Learning
- Child-friendly nursery-rhyme library
- Category filtering
- Search
- Difficulty filtering
- Animated CSS fallback lesson scene
- Video player
- Audio player
- External embeddable video support
- Lyrics display
- Browser speech fallback when no media is uploaded
- Smart Repeat tracking
- Completion tracking

### Quiz
- One quiz per rhyme
- Multiple-choice questions
- Emoji/image/text choices
- Optional audio question prompts
- Optional question images
- Instant AJAX feedback
- Correct-answer highlighting
- Score calculation
- Passing threshold
- 0–3 star rating
- Retry flow
- Incomplete-attempt protection

### Progress
- Completed rhymes
- Smart Repeat count
- Quizzes taken
- Average quiz score
- Perfect quiz count
- Stars
- Badges
- Rhyme-by-rhyme activity
- Quiz history

### Parent dashboard
- Parent authentication
- Add learner profiles
- Learner switcher
- Per-learner progress summary
- Quiz history
- Badge monitoring

### UI / UX
- Responsive desktop/tablet/mobile layout
- Glass-style cards
- Dark futuristic visual system
- 3D-style orbit elements
- Animated learning scenes
- Micro-interactions
- Toast notifications
- Loading/disabled states
- Empty/error states
- Accessible labels and semantic controls
- No external advertising or tracking scripts

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Django 5 |
| Frontend | Django Templates + HTML5 + CSS3 + Vanilla JavaScript |
| Database | SQLite by default |
| Optional database | MySQL |
| Image uploads | Pillow |
| Configuration | python-dotenv |
| Optional MySQL driver | PyMySQL |
| Authentication | Django authentication/session framework |
| Admin | Django Admin |
| API style | JSON endpoints used by frontend JavaScript |

The existing Django/server-rendered architecture has been preserved instead of replacing it with an unrelated frontend framework.

---

## 4. Folder Structure

```text
smart_learning/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
│
├── smart_learning/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── decorators.py
│   ├── admin.py
│   ├── urls.py
│   └── migrations/
│
├── core/
│   ├── views.py
│   ├── urls.py
│   ├── parent_urls.py
│   └── migrations/
│
├── rhymes/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── management/commands/seed_data.py
│   └── migrations/
│
├── quizzes/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── progress/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── templates/
│   ├── base.html
│   ├── 404.html
│   ├── 500.html
│   ├── accounts/
│   ├── core/
│   ├── rhymes/
│   ├── quizzes/
│   └── progress/
│
├── static/
│   ├── css/style.css
│   └── js/
│       ├── app.js
│       ├── player.js
│       └── quiz.js
│
└── media/
    ├── rhymes/
    └── quiz/
```

---

## 5. Prerequisites

Recommended:

- Python 3.10+
- pip
- A modern browser: Chrome, Edge, Firefox or Safari
- Git (optional)

For the default SQLite setup, **MySQL is not required**.

---

# 6. Windows PowerShell — Fresh Setup

Open **Terminal 1**.

### Step 1 — Enter the project

```powershell
cd "smart_learning"
```

Use the folder containing `manage.py`.

### Step 2 — Create a virtual environment

```powershell
py -m venv venv
```

### Step 3 — Activate it

```powershell
.env\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.env\Scripts\Activate.ps1
```

### Step 4 — Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5 — Create environment file

```powershell
Copy-Item .env.example .env
```

For local development the supplied SQLite configuration can remain unchanged.

### Step 6 — Apply migrations

```powershell
python manage.py migrate
```

### Step 7 — Seed the learning content

```powershell
python manage.py seed_data
```

This creates:

- Categories
- Four sample nursery rhymes
- Quiz questions and choices
- Gamification badges

### Step 8 — Create the administrator

```powershell
python manage.py createsuperuser
```

Follow Django's prompts.

### Step 9 — Start the backend/web server

```powershell
python manage.py runserver
```

Keep this terminal running.

Open:

**http://127.0.0.1:8000/**

Admin:

**http://127.0.0.1:8000/admin/**

---

# 7. Terminal 2 — Frontend

This project uses Django templates, so there is **no separate Vite/npm frontend server**.

Do not run `npm run dev`.

The frontend is served by Django from the same server:

```text
Frontend URL:
http://127.0.0.1:8000/

Backend/API URL:
http://127.0.0.1:8000/
```

Therefore:

- **Terminal 1:** Django server
- **Terminal 2:** optional for logs/testing/browser tools; no separate frontend process is required.

This preserves the original server-rendered architecture.

---

# 8. macOS / Linux

```bash
cd smart_learning
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 9. Environment Variables

Copy `.env.example` to `.env`.

### Required

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### SQLite

```env
DB_ENGINE=sqlite
```

No database username/password is required.

### MySQL

If deploying with MySQL:

```env
DB_ENGINE=mysql
DB_NAME=smart_learning_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Production security

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Upload size

```env
MAX_UPLOAD_SIZE=52428800
```

The default is approximately 50 MB.

### API keys

**None are required for the current project.**

The PPT identifies AI personalization and voice recognition as future enhancements, not current required functionality.

---

# 10. Database Setup

## SQLite

SQLite is the default and requires no separate database service.

```bash
python manage.py migrate
```

The database is created as:

```text
db.sqlite3
```

## MySQL

Create a database:

```sql
CREATE DATABASE smart_learning_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Set:

```env
DB_ENGINE=mysql
DB_NAME=smart_learning_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Then:

```bash
python manage.py migrate
python manage.py seed_data
```

PyMySQL is included so the project does not require the native `mysqlclient` build on Windows.

---

# 11. Media / Learning Content

The supplied project ZIP did not contain real nursery-rhyme video/audio files.

The application therefore has three supported lesson modes:

1. Uploaded video — preferred for animated rhyme lessons.
2. Uploaded audio — useful for sing-along audio lessons.
3. External embeddable video URL.
4. Built-in browser voice fallback when no media exists.

To add real project media:

1. Open `/admin/`.
2. Sign in with the superuser.
3. Open **Rhymes**.
4. Create or edit a rhyme.
5. Upload:
   - Video
   - Audio
   - Thumbnail
6. Publish the rhyme.
7. Add/configure the quiz.

For the strongest final demonstration, upload the actual project nursery-rhyme videos/audio supplied by the project team.

---

# 12. Authentication

There are two normal account types:

### Learner

A learner can:

- Browse lessons
- Watch/listen
- Repeat
- Complete lessons
- Take quizzes
- Earn badges
- View progress

### Parent / Guardian

A parent can:

- Add learner accounts
- Select a learner
- Monitor progress
- Review quiz results
- Review badges

### Administrator

A Django staff/superuser can access:

```text
/admin/
```

and manage platform content and users.

---

# 13. API Endpoints

All learner APIs require an authenticated Django session and POST APIs require CSRF protection.

### Rhyme APIs

```text
POST /rhymes/<slug>/log-play/
POST /rhymes/<slug>/log-repeat/
POST /rhymes/<slug>/mark-complete/
```

### Quiz API

```text
POST /quiz/<slug>/answer/
```

Example request:

```json
{
  "question_id": 1,
  "choice_id": 2
}
```

Example response:

```json
{
  "ok": true,
  "correct": true,
  "correct_choice_id": 2,
  "running_score": 1,
  "answered": 1,
  "total": 2
}
```

### Progress API

```text
GET /progress/api/summary/
```

Example response:

```json
{
  "ok": true,
  "completed_count": 2,
  "total_repeats": 5,
  "quizzes_taken": 1,
  "perfect_scores": 1,
  "total_stars": 3,
  "avg_score_pct": 100,
  "badge_count": 2
}
```

---

# 14. Important URLs

```text
Landing
/

Learner home
/home/

Learner registration
/accounts/register/

Login
/accounts/login/

Rhyme library
/rhymes/

Progress
/progress/

Parent dashboard
/parent/

Add learner
/parent/add-child/

Django admin
/admin/
```

---

# 15. Testing Instructions

Run:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Then start:

```bash
python manage.py runserver
```

### Manual workflow test

#### Learner authentication

1. Open `/accounts/register/`.
2. Create a learner.
3. Confirm redirect to learner home.
4. Logout.
5. Login again.

#### Rhyme workflow

1. Open **Rhymes**.
2. Search/filter a rhyme.
3. Open a lesson.
4. If media is uploaded, play it.
5. If no media exists, use **Listen to rhyme**.
6. Click **Smart Repeat**.
7. Confirm the repeat counter changes.
8. Mark the lesson complete.
9. Open **My Progress**.
10. Confirm completion/repeat statistics.

#### Quiz workflow

1. Open a rhyme with a configured quiz.
2. Click **Take the quiz**.
3. Select an answer.
4. Confirm instant feedback.
5. Confirm correct answer highlighting.
6. Continue through all questions.
7. Confirm score and stars.
8. Try again.

#### Parent workflow

1. Create a parent account.
2. Open `/parent/`.
3. Click **Add learner**.
4. Create a learner.
5. Select the learner.
6. Confirm progress and quiz history are displayed.

#### Admin workflow

1. Open `/admin/`.
2. Log in with the superuser.
3. Add/edit a category.
4. Add/edit a rhyme.
5. Upload a thumbnail/video/audio.
6. Add a quiz and questions.
7. Confirm the learner UI displays the content.

---

# 16. Common Errors

## `ModuleNotFoundError: No module named 'django'`

Activate the virtual environment:

```powershell
.env\Scripts\Activate.ps1
```

Then:

```powershell
pip install -r requirements.txt
```

## `python` is not recognized on Windows

Try:

```powershell
py --version
```

Then create the environment with:

```powershell
py -m venv venv
```

## Port 8000 is already in use

Run:

```powershell
python manage.py runserver 8001
```

Then open:

```text
http://127.0.0.1:8001/
```

## PowerShell activation is blocked

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.env\Scripts\Activate.ps1
```

## MySQL connection error

Check:

- MySQL service is running.
- Database exists.
- `DB_NAME` is correct.
- Username/password are correct.
- Host/port are correct.

## Uploaded media does not appear

During local development make sure:

```env
DEBUG=True
```

and confirm the file exists inside:

```text
media/
```

## Quiz gives a CSRF error

Use the application page normally instead of manually calling the API. The frontend includes the Django CSRF token and sends it with AJAX requests.

---

# 17. Production Deployment

For production:

1. Set a strong `SECRET_KEY`.
2. Set `DEBUG=False`.
3. Configure `ALLOWED_HOSTS`.
4. Configure `CSRF_TRUSTED_ORIGINS`.
5. Enable HTTPS.
6. Set secure cookies.
7. Use MySQL or another production database.
8. Run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

9. Use Gunicorn or another WSGI/ASGI server.
10. Put Nginx or a managed reverse proxy in front.
11. Store uploaded media on durable storage.
12. Configure backups for the database and media.
13. Monitor Django logs.

Example Gunicorn command:

```bash
gunicorn smart_learning.wsgi:application --bind 0.0.0.0:8000
```

For ASGI deployments:

```bash
uvicorn smart_learning.asgi:application --host 0.0.0.0 --port 8000
```

---

# 18. Architecture

```text
                    ┌───────────────────────┐
                    │       Learner         │
                    │  Browser / Mobile Web │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Django Templates    │
                    │ HTML + CSS + JS        │
                    └───────────┬───────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
               ▼                ▼                ▼
        Authentication      Learning         Quiz Module
        / Accounts          / Rhymes         / Scoring
               │                │                │
               └────────────────┼────────────────┘
                                ▼
                       Progress Tracking
                                │
                                ▼
                         Database / Media
                                ▲
                                │
                    ┌───────────┴───────────┐
                    │   Parent Dashboard   │
                    │   Django Admin       │
                    └───────────────────────┘
```

---

# 19. Project-to-PPT Mapping

| PPT requirement | Implementation |
|---|---|
| User Interface Module | Responsive Django templates + polished CSS/JS |
| User Authentication Module | Custom Django User + learner/parent authentication |
| Learning Management Module | Categories, rhyme library, video/audio/external media, lyrics, Smart Repeat |
| Quiz Module | Questions, choices, instant AJAX grading, scores, stars |
| Progress Tracking Module | Rhyme progress, quiz history, statistics, badges |
| Database/Storage Module | Django ORM + SQLite/MySQL + media storage |
| Child-friendly interface | Large controls, visual cards, minimal navigation |
| Independent learning | Learner account + direct lesson/quiz workflow |
| Parent monitoring | Parent dashboard + learner profiles |
| Admin content management | Django Admin |
| AI personalization | Not part of current scope; listed as future enhancement in PPT |
| Voice recognition | Not part of current scope; listed as future enhancement in PPT |

---

# 20. Final Run Order

### Terminal 1 — Backend + complete web application

Windows:

```powershell
cd "smart_learning"
.env\Scripts\Activate.ps1
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Linux/macOS:

```bash
cd smart_learning
source venv/bin/activate
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Browser

Open:

```text
http://127.0.0.1:8000/
```

### Admin

Open:

```text
http://127.0.0.1:8000/admin/
```

### Separate frontend terminal?

**Not required.**

The frontend is the Django-rendered application and is served by the same Django process.

---

## Project status

The supplied Django architecture has been preserved and completed around the requirements in the supplied PPT and abstract. The current source package contains no real nursery-rhyme media files, so the application includes a working browser-voice fallback and is ready for administrators to upload the actual project video/audio assets.
