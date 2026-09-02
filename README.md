# 🏫 Schoolly Smart Backend

High-performance PostgreSQL relational database engine with automated risk analytics and RESTful API endpoints built in Python and FastAPI.

---

## 📌 Overview

**Schoolly Smart Backend** is a complete, scalable backend architecture for educational data management. It combines direct database engine operations with a modern REST API layer to log attendance in bulk, enforce classroom capacities, and analyze student drop-out risks in real time.

---

## ✨ Key Features

* **Relational Database Engine:** PostgreSQL schema modeling students, classes, enrollment, and daily attendance metrics.
* **Student Risk Analytics:** Custom SQL engine detecting students falling below attendance thresholds (e.g. < 75%).
* **Bulk Attendance Processing:** Fast, batch-inserted attendance logging with built-in validation.
* **RESTful FastAPI Service:** Async web server exposing clean JSON endpoints for frontend integration.
* **Interactive API Documentation:** Built-in Swagger UI testing playground served directly at `/docs`.

---

## 🛠️ Tech Stack

* **Language:** Python 3.13+
* **Framework:** FastAPI
* **Database:** PostgreSQL / `psycopg2-binary`
* **Data Validation:** Pydantic
* **Server:** Uvicorn

---

## 📂 Project Structure

```text
schoolly-smart-backend/
├── main.py                 # FastAPI application routes & API endpoints
├── analytics.py            # SQL-based student attendance risk engine
├── attendance_manager.py   # Bulk attendance logger & class summary logic
├── db_manager.py           # Database connection & schema setup
├── seed_data.py            # Synthetic mock data generator
└── test_pipeline.py        # End-to-end pipeline validation script