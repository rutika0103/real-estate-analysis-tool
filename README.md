** Real Estate Analysis Tool **

SigmaValue — Full Stack Assignment (React + Flask)

>> Project Overview

The Real Estate Analysis Tool is a full-stack web application designed to analyze residential locality data from Excel files.
It allows users to upload datasets, view detailed summaries, explore price trends, and compare multiple locations.
This project is developed as part of the SigmaValue Full Stack Developer Assignment using React (frontend) and Flask (backend).

The goal of this project is to provide a simple yet powerful tool for real estate data insights with a clean UI and robust backend.

>> Features
🔹 Frontend (React + Bootstrap)

Upload Excel dataset

Search locality (Wakad, Baner, Hinjewadi, etc.)

Auto-generated summary in simple language

Dynamic charts with 5-year price trends

Compare multiple locations visually

Responsive UI for mobile & desktop

🔹 Backend (Flask + Pandas)

Reads Excel (.xlsx) files

Cleans & preprocesses data

Year-wise price trend creation

Computes mean, median & recommendations

Multi-location comparison support

CORS enabled for frontend communication

🛠 Technologies Used

* Frontend

React.js

Axios

Bootstrap

* Backend

Python

Flask

Pandas

Flask-CORS

>> Project Structure

interview project/
│── frontend/
│    ├── src/
│    └── React UI (upload, chart, summary)
│
│── backend/
│    ├── app.py (Main API)
│    ├── analysis.py
│    ├── requirements.txt

>> How to Run
1. Start Backend
cd backend
python app.py


Backend runs at:
--> http://127.0.0.1:8000

>> Start Frontend
cd frontend
npm install
npm start


Frontend runs at:
--> http://localhost:3000

>> API Endpoints
POST /upload

Uploads and processes Excel dataset.

GET /analyze?area=Wakad

Fetches price trends + summary for selected area.

POST /compare

Compares multiple locations and returns their trends + insights.

>> Deployment Guide
Deploy Backend (Flask) on Render

Go to https://render.com

Create Web Service

Connect GitHub repo

Add:

Build Command: pip install -r requirements.txt

Start Command: python app.py

Deploy

Deploy Frontend (React) on Netlify

Go to https://netlify.com

Upload the React project

Set:

Build Command: npm run build

Publish Directory: build/

Deploy

>> Assignment Checklist (Completed ✔)

✔ React Frontend
✔ Flask Backend
✔ Excel Upload
✔ Locality Summary
✔ Trends Chart
✔ Multi-Location Comparison
✔ Clean Code
✔ No Errors
✔ Professional README
✔ Company-ready Submission

>> Developer

Rutika Sarje
Full Stack Developer
GitHub: https://github.com/rutika0103

>> Footer

Developed as part of SigmaValue Full Stack Developer Assignment.
