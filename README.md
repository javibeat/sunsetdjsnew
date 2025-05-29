

# Sunset DJs

Sunset DJs is a web-based scheduling and shift management system designed specifically for DJs and event coordinators.

## Features

- DJ authentication and personalized dashboard
- Shift creation and editing with venue and time details
- Event highlighting and visual indicators
- FullCalendar integration for intuitive scheduling
- Admin panel and HR tools for shift coordination

## Tech Stack

- **Backend:** Django 5.2.1
- **Frontend:** HTML, CSS (custom + FullCalendar), JavaScript
- **Database:** SQLite (development)
- **Deployment Ready:** GitHub + production ready settings

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/javibeat/sunsetdjsnew.git
   cd sunsetdjsnew
   ```

2. Create and activate virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the server:
   ```
   python manage.py runserver
   ```

## Deployment

Use your preferred platform (e.g. Heroku, Render, or VPS) and set your `.env` with:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- Email credentials (if using email features)

## License

MIT License

---
Created with ❤️ by Javibeat