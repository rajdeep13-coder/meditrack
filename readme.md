# MediTrack

## Overview
**MediTrack** is a Flask-based web application that helps users manage medications and track daily adherence. It supports medication CRUD (create, read, update, delete), lets users mark medications as **taken today**, and calculates **adherence streaks** and **today’s progress** based on **active** medications.

---

## Key Features
- **Landing & Session-Aware Routing**
  - `/` landing page for guests
  - Redirects logged-in users to `/dashboard`
- **Dashboard (Adherence Analytics)**
  - Loads the user’s **active medications**
  - Determines whether each active medication was marked **taken today**
  - Computes:
    - **Adherence streak**: consecutive days where *all active meds* were taken
    - **Today’s progress**: percentage of active meds taken today
  - Renders `dashboard.html` with a time-based greeting
- **Medication Management (CRUD)**
  - `GET /medications`: list medications (active/inactive)
  - `GET/POST /medications/add`: add a medication (with form validation)
  - `GET/POST /medications/<med_id>/edit`: edit a medication (with form validation)
  - `POST /medications/<med_id>/delete`: delete a medication (associated logs removed via cascade if configured)
  - `POST /medications/<med_id>/toggle-active`: toggle active/inactive status for inclusion in adherence tracking
- **Daily Taken Toggle**
  - `POST /medications/<med_id>/toggle`
  - Creates or updates today’s `MedicationLog` entry by flipping the `taken` state
  - If called via **AJAX**, returns JSON including:
    - updated **streak**
    - updated **taken counts**
    - updated **progress percentage**
  - Otherwise redirects back to the dashboard
- **Streak Calculation Helper**
  - `_calculate_streak`: scans backwards day-by-day until a day is found where not all active medications were taken

---

## Tech Stack
- **Flask** (web framework)
- **Flask-SQLAlchemy** (ORM/database integration)
- **Flask-Login** (user authentication/session management)
- **Werkzeug** (WSGI/utilities used by Flask)
- **Flask-WTF** (forms and CSRF utilities)
- **python-dotenv** (loads environment variables from a `.env` file)

---

## Project Architecture
Based on the provided repository summaries, the core behavior is implemented through the Flask routing layer, specifically:

### `app/routes/main.py`
Defines the main Flask blueprint and user-facing routes:

- **`/`**: Landing page; redirects authenticated users to the dashboard.
- **`/dashboard`**: Main dashboard logic:
  - Loads **active medications**
  - Checks which are **taken today**
  - Computes **streak** and **progress**
  - Renders `dashboard.html`
- **Medication CRUD routes**:
  - `/medications`
  - `/medications/add`
  - `/medications/<med_id>/edit`
  - `/medications/<med_id>/delete`
  - `/medications/<med_id>/toggle-active`
- **Daily taken logging**:
  - `/medications/<med_id>/toggle`:
    - Updates today’s `MedicationLog`
    - Returns JSON when called via AJAX; redirects otherwise
- **Helper**:
  - `_calculate_streak`: computes the current consecutive-day streak by walking backwards in time until a failure day is encountered.

---

## Installation (Placeholder)
1. Clone the repository:
   bash
   git clone <repo-url>
   cd meditrack
   
2. Create a virtual environment (recommended).
3. Install dependencies:
   bash
   pip install -r requirements.txt
   
4. Add environment variables:
   - Create a `.env` file (used by `python-dotenv`) with the configuration your Flask app requires.

---

## Usage (Placeholder)
1. Start the Flask development server:
   bash
   flask run
   
2. Open the application in your browser.
3. Log in (implementation details not described in the provided summaries) and use:
   - **Dashboard** to view streak/progress
   - **Medication pages** to add, edit, delete, and toggle active status
   - **Toggle taken today** to update adherence calculations (optionally via AJAX)

---

## Notes for Developers
- Dashboard computations are driven by **active medications** only.
- The streak logic (`_calculate_streak`) relies on consecutive days where *all* active medications were taken.
- The `/toggle` endpoint updates today’s `MedicationLog` and supports both **AJAX (JSON response)** and **non-AJAX (redirect)** flows.

---
*This README was generated with [PresentMe](https://www.presentmeapp.xyz/). View the full presentation [here](https://www.presentmeapp.xyzhttp://localhost:5000/p/81777439-e9d9-4942-9156-ed02343873fd).*