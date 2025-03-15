LearnHub is a web-based educational platform designed to facilitate online learning. It provides users with access to courses, assignments, enrollment management, and more. The platform is built using Flask and MongoDB.

Features

User Authentication: Signup and login functionality for students and admins.

Course Management: View, add, edit, and delete courses.

Enrollment System: Users can enroll in courses and track their progress.

Assignments & Quizzes: Fetch assignments and quizzes based on courses.

PDF Certificate Generation: Generates a certificate when a course is successfully completed.

Payment System: Handles course payments and enrollment.


Technologies Used

Backend: Flask (Python)

Database: MongoDB

Frontend: HTML, CSS (Templates rendered using Flask)

Libraries: ReportLab (for PDF generation), PyMongo (MongoDB integration)


Installation

Prerequisites

Python 3.x installed

MongoDB installed and running locally

Setup Instructions

Clone the repository:

git clone https://github.com/RamidiSathwik/LearnHub.git
cd LearnHub

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Access the application in your browser at:

http://127.0.0.1:5000/
