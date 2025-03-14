from flask import Flask, jsonify, make_response, render_template, request, redirect, url_for, session, make_response
from pymongo import MongoClient

from decimal import Decimal
from bson import ObjectId
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from bson import json_util
from datetime import datetime
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.learnhubdb
user_collection = db['user']
admin_collection = db['admin']
instructors_collection = db['instructors']
courses_collection = db['courses']
enrollment_collection = db['enrollment']
assignment_collection = db['assignment']

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
@app.route('/')
def main():
    return render_template('login.html')
@app.route('/enrolled')
def enrolled():
    return render_template('enrolled.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/home')
def cards():
    return render_template('main.html')
@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/admin_user')
def adminuser():
    return render_template('admin_user.html')
@app.route('/admin_instructor')
def admin_instructor():
    return render_template('instructor.html')
@app.route('/enrollment')
def enrollment():
    enrollments = list(enrollment_collection.find())
    return render_template('admin_enrollment.html', enrollments=enrollments)
# @app.route('/profile')
# def profile():
#     return render_template('profile.html')
# Routes for user authentication
@app.route('/all_courses')
def all_courses():
    # Fetch all products from the database
    courses = courses_collection.find()
    # Convert the cursor to a list of dictionaries
    courses = list(courses)
    # Render the all_products.html template with the products data
    return render_template('all_courses.html', courses=courses)

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = list(user_collection.find())
        return json_util.dumps(users)
    elif request.method == 'POST':
        user_data = request.json
        user_collection.insert_one(user_data)
        return jsonify({'message': 'User added successfully'})
@app.route('/instructors', methods=['GET', 'POST'])
def instructors():
    if request.method == 'GET':
        instructors = list(instructors_collection.find())
        return json_util.dumps(instructors)
    elif request.method == 'POST':
        instructors_data = request.json
        instructors_collection.insert_one(instructors_data)
        return jsonify({'message': 'instructors added successfully'})
@app.route('/users/<username>', methods=['PUT'])
def update_user(username):
    user_data = request.json
    user_collection.update_one({"username": username}, {"$set": user_data})
    return jsonify({"message": "User updated successfully"})
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        # Fetch user information from the database
        user_info = user_collection.find_one({'username': username})

        # Pass user information to the profile.html template
        return render_template('profile.html', user_info=user_info)
    else:
        return 'You are not logged in!'


@app.route('/generate_pdf/<username>/<course_title>')
def generate_pdf(username, course_title):
    # Fetch user information from the database
    user_info = user_collection.find_one({'username': username})

    # Generate PDF if grade is more than 60%
    for course in user_info['courses']:
        if course['title'] == course_title and course['grade'] > 60:
            pdf_filename = f"{username}_Congratulations.pdf"
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, f"Congratulations {username}!")
            c.drawString(100, 730, f"You have completed {course_title} with a grade of {course['grade']}%.")
            c.save()
            buffer.seek(0)
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response

    return "PDF not generated."
@app.route('/quiz/<int:course_id>')
def get_quiz(course_id):
    # Fetch quiz questions from MongoDB based on course ID
    quiz_questions = assignment_collection.find_one({'course_id': str(course_id)})
    if quiz_questions:
        del quiz_questions["_id"]
        return jsonify(quiz_questions.get("quiz_questions", []))
    else:
        return jsonify([])
@app.route('/assignment/<int:course_id>', methods=['GET'])
def get_assignment(course_id):
    print("Fetching assignment for course_id:", course_id)  # Print course_id for debugging
    # Fetch assignment details from MongoDB based on course ID
    course = assignment_collection.find_one({"course_id": str(course_id)})
    if course:
        assignment = course.get("assignment", None)
        if assignment:
            return jsonify({
                "title": assignment["title"],
                "description": assignment["description"],
                "due_date": assignment["due_date"]
            })
        else:
            return jsonify({"error": "Assignment not found for this course"})
    else:
        return jsonify({"error": "Course not found"})




@app.route('/assignment/<int:course_id>/upload', methods=['POST'])
def upload_assignment(course_id):
    # Save uploaded assignment file
    # This is just a placeholder, you need to implement the file upload logic here
    uploaded_file = request.files['assignment']
    if uploaded_file:
        # Save the file
        # Example: uploaded_file.save(uploaded_file.filename)
        return jsonify({"message": "Assignment uploaded successfully"})
    else:
        return jsonify({"error": "No file uploaded"})
# Route to add grade to user's session
@app.route('/user/add_grade', methods=['POST'])
def add_grade_to_user():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    data = request.json
    course_id = data.get('course_id')
    grade = data.get('grade')
    course_title = data.get('course_title')

    # Update user_collection
    user_collection.update_one(
        {"username": session['username']},
        {"$push": {"courses": {"course_id": course_id, "grade": grade, "title": course_title}}}
    )

    return jsonify({'success': True, 'message': 'Grade added to user'})
@app.route('/get_courses', methods=['GET'])
def get_courses():
    courses = courses_collection.find()
    courses_list = []
    for course in courses:
        courses_list.append({
            'title': course['title'],
            'description': course['description'],
            'instructor': course['instructor'],
            'video_url': course['video_url'],
            'price': course['price'],
            'start_date': course['start_date'],
            'end_date': course['end_date'],
            'status': course['status'],
            'image': course['image']  # Add image path to the response
        })
    return jsonify(courses_list)
@app.route('/courses')
def courses():
    courses = courses_collection.find()
    if 'username' in session:
        username = session['username']
        return render_template('home.html', courses=courses, username=username)
    else:
        return render_template('home.html', courses=courses, username=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Check if the user is an admin
    admin = admin_collection.find_one({'username': username, 'password': password})
    if admin:
        # Store the admin username in the session
        session['username'] = username
        # Redirect admin to all_products.html
        return redirect('/all_courses')
    
    # If the user is not an admin, check if it's a regular user
    user = user_collection.find_one({'username': username, 'password': password})
    if user:
        # Store the regular user username in the session
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login successful', 'username': username})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})
@app.route('/courses/<category>')
def get_products(category):
    courses = list(courses_collection.find({"category": category}))
    for course in courses:
        course['_id'] = str(course['_id'])
    return render_template('courses.html', courses=courses)

@app.route('/add_course', methods=['POST'])
def add_product():
    # Convert ImmutableMultiDict to dictionary
    course_data = request.form.to_dict()
    
    # Insert the product into the database
    courses_collection.insert_one(course_data)
    
    # Return a JSON response indicating success
    return jsonify({'message': 'Course added successfully'})


@app.route('/delete_course/<course_id>', methods=['GET'])
def delete_course(course_id):
    # Delete the product from the database based on the product ID
    result = courses_collection.delete_one({'course_id': course_id})
    if result.deleted_count == 1:
        return redirect(url_for('all_courses'))
    else:
        return "Course not found", 404

@app.route('/get_course/<course_id>', methods=['GET'])
def get_course(course_id):
    # Retrieve the product from the database based on the product ID
    course = courses_collection.find_one({'course_id': course_id})
    if course:
      
        course['_id'] = str(course['_id'])
        return jsonify(course), 200
    else:
        return 'course not found', 404
 
@app.route('/edit_course/<course_id>', methods=['POST'])
def edit_product(course_id):
    # Get updated product data from the request
    updated_course_data = request.form.to_dict()
    print(updated_course_data)
    # Update the product in the database based on the product ID
    result = courses_collection.update_one({'course_id': course_id}, {'$set': updated_course_data})
    if result.modified_count == 1:
        return 'Course updated successfully', 200
    else:
        return 'Course not found', 404
# @app.route('/enroll', methods=['POST'])
# def enroll():
#     if 'username' not in session:
#         return jsonify({'success': False, 'message': 'User not logged in'})

#     username = session['username']
#     data = request.json
#     data['username'] = username

#     enrollment_collection.insert_one(data)
    
#     return jsonify({'success': True, 'message': 'Course enrolled successfully'})
@app.route('/enroll', methods=['POST'])
def enroll():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    username = session['username']
    data = request.json
    data['username'] = username
    data['payment'] = "paid"
    data['status'] = "enrolled"
    data['date'] = datetime.now().strftime("%Y-%m-%d")

    enrollment_collection.insert_one(data)
    
    return jsonify({'success': True, 'message': 'Course enrolled successfully'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        contactno = request.form['contactno']
        address = request.form['address']
        city = request.form['city']
        zip_code = request.form['zip']
        dob = request.form['dob']
        
        user = user_collection.find_one({'username': username})
        if user:
            return jsonify({'success': False, 'message': 'Username already exists'})
        else:
            new_user = {
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'password': password,
                'contactno': contactno,
                'address': address,
                'city': city,
                'zip': zip_code,
                'dob': dob
            }
            user_collection.insert_one(new_user)
            return jsonify({'success': True, 'message': 'User created successfully'})
    return render_template('signup.html')
# @app.route('/get_courses', methods=['GET'])
# def get_courses():
#     courses = courses_collection.find()
#     courses_list = []
#     for course in courses:
#         courses_list.append({
#             'title': course['title'],
#             'description': course['description'],
#             'instructor': course['instructor'],
#             'video_url': course['video_url'],
#             'price': course['price'],
#             'start_date': course['start_date'],
#             'end_date': course['end_date'],
#             'status': course['status']
#         })
#     return jsonify(courses_list)

# Routes for course management

@app.route('/create_course', methods=['POST'])
def create_course():
    # Your course creation logic here
    pass

@app.route('/enrolled_courses', methods=['GET'])
def get_enrolled_courses():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    username = session['username']
    courses = enrollment_collection.find({'username': username})
    enrolled_courses = []
    for course in courses:
        enrolled_courses.append({
            'id':course['id'],
            'title': course['title'],
            'description': course['description'],
            'instructor': course['instructor'],
            'video_url': course['video_url']

        })
    return jsonify(enrolled_courses)



@app.route('/get_enrollments', methods=['GET'])
def get_enrollments():
    # Your logic to fetch enrollments here
    pass

# Routes for assignments

@app.route('/create_assignment', methods=['POST'])
def create_assignment():
    # Your assignment creation logic here
    pass

@app.route('/get_assignments', methods=['GET'])
def get_assignments():
    # Your logic to fetch assignments here
    pass

# Routes for payments

@app.route('/make_payment', methods=['POST'])
def make_payment():
    # Your payment logic here
    pass

@app.route('/get_payments', methods=['GET'])
def get_payments():
    # Your logic to fetch payments here
    pass

if __name__ == '__main__':
    app.run(debug=True)
