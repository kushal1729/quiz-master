Quiz Master - V1

Quiz Master is a multi-user quiz management web application designed to provide an interactive and efficient platform for exam preparation. It enables users to take quizzes across various subjects and chapters while providing administrators with tools to manage content and monitor performance visually.

> 🔗 [Watch Demo Video](https://youtu.be/fy7Ieh8HvII)

---

Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Database Design](#database-design)
- [API Endpoints](#api-endpoints)
- [Challenges Faced](#challenges-faced)
- [How to Run Locally](#how-to-run-locally)
- [Demo](#demo)
- [License](#license)

---

Overview

Objective

The goal of Quiz Master - V1 is to create a lightweight, interactive system for quiz-based learning and performance monitoring. It is intended for both academic and professional users who want to assess their knowledge in a structured, subject-wise manner.

Problem Solved

Conventional quiz systems lack interactivity, are difficult to administer, and don’t track performance effectively. This project solves these limitations by enabling:
- Easy quiz creation and management
- Time-bound tests
- Automated performance visualization
- Multi-role access for users and admins

---

Key Features

Admin Dashboard
- Add/edit/delete subjects, chapters, quizzes, and questions
- View user performance through interactive charts
- Search functionality for users, quizzes, and topics

User Dashboard
- Register and login as a user
- Attempt quizzes by subject/chapter
- Track and review personal performance

Quiz Timer
- Each quiz has a countdown timer
- Auto-submit functionality when time runs out

Performance Monitoring
- User performance stored in the database
- Bar charts rendered using Chart.js for visual insights

---

Tech Stack

| Layer        | Technology                      |
|--------------|----------------------------------|
| **Backend**  | Python (Flask), SQLAlchemy       |
| **Frontend** | HTML5, CSS3, Bootstrap, Jinja2   |
| **Database** | SQLite                           |
| **Charts**   | Chart.js                         |

---

Database Design

The database uses the following schema:

- `users`: Stores user info like name, credentials, and profile
- `subjects`: List of subjects and descriptions
- `chapters`: Chapters linked to subjects
- `quizzes`: Quiz metadata (date, time, chapter)
- `questions`: Quiz questions and options
- `scores`: Stores individual quiz performance

---

API Endpoints

| Endpoint         | Description                  |
|------------------|------------------------------|
| `GET /api/subjects` | Returns list of subjects       |
| `GET /api/chapters` | Returns list of chapters       |
| `GET /api/quizzes`  | Returns all quizzes           |
| `GET /api/questions`| Returns questions for a quiz |
| `GET /api/scores`   | Returns user scores           |

---

Challenges Faced

Timer Integration
- Creating a reliable countdown timer that auto-submits the quiz
- Solved using client-side JavaScript

Database Relationships
- Linking subjects → chapters → quizzes → questions
- Solved with SQLAlchemy ORM relationships

Performance Graphs
- Dynamic and readable user score charts
- Solved with Chart.js bar graphs

---

How to Run Locally

```bash
# Clone the repo
git clone https://github.com/your-username/quiz-master-v1.git
cd quiz-master-v1

# Setup virtual environment
python -m venv venv
source venv/bin/activate     # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
