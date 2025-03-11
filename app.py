from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set secret key for session management
app.secret_key = 'supersecretkey123!'  # Change this to a unique secret key

# Configuration
STATIC_FOLDER = 'static'
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
DATA_FILE = os.path.join(STATIC_FOLDER, 'data', 'papers.json')
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure necessary folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load existing papers data
def load_papers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save papers metadata
def save_papers(papers):
    with open(DATA_FILE, 'w') as f:
        json.dump(papers, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

app.secret_key = 'supersecretkey123!'  # Change this to a unique secret key

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  # 'admin' or 'student'

        # Simple login logic
        if username == 'admin' and password == 'admin123' and role == 'admin':
            session['role'] = 'admin'  # Set role in session
            return render_template('login.html', welcome_message="Welcome Admin")
        elif username == 'student' and password == 'student123' and role == 'student':
            session['role'] = 'student'  # Set role in session
            return render_template('login.html', welcome_message="Welcome Student")
        elif username == 'admin' and password == 'admin1234' and role == 'admin':
            session['role'] = 'admin'  # Set role in session
            return render_template('upload_images.html', welcome_message="Welcome admin")
        else:
            flash('Invalid credentials or role!', 'danger')
            return render_template('login.html')

    # If GET request or login fails, just show the login form
    return render_template('login.html')

@app.route('/<role>')
def dashboard(role):
    if 'role' not in session or session['role'] != role:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    if role == 'admin':
        return render_template('admin.html')  # Admin dashboard page
    elif role == 'student':
        return render_template('student.html')  # Student dashboard page

@app.route('/admin', methods=['GET', 'POST'])
def admin_upload():
    papers = load_papers()
    if request.method == 'POST':
        # Get form data
        course = request.form.get('course')
        branch = request.form.get('branch')
        year = request.form.get('year')
        semester = request.form.get('semester')
        subject = request.form.get('subject')
        paper_type = request.form.get('paper_type')
        paper_file = request.files.get('paper')

        # Validate file
        if not paper_file or paper_file.filename == '':
            flash('No file provided', 'danger')
            return redirect(url_for('admin_upload'))
        if not allowed_file(paper_file.filename):
            flash('Only PDF files are allowed', 'danger')
            return redirect(url_for('admin_upload'))

        # Save file
        filename = secure_filename(paper_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        paper_file.save(file_path)

        # Add paper metadata
        papers.append({
            'course': course,
            'branch': branch,
            'year': year,
            'semester': semester,
            'subject': subject,
            'paper_type': paper_type,
            'filename': filename,
            'file_path': file_path
        })
        save_papers(papers)

        flash('Paper uploaded successfully!', 'success')
        return redirect(url_for('admin_upload'))

    return render_template('admin.html')

@app.route('/student', methods=['GET', 'POST'])
def student_page():
    papers = load_papers()
    filtered_papers = []
    if request.method == 'POST':
        # Get search filters
        course = request.form.get('course')
        branch = request.form.get('branch')
        year = request.form.get('year')
        semester = request.form.get('semester')
        subject = request.form.get('subject')
        paper_type = request.form.get('paper_type')

        # Filter papers based on selected criteria
        filtered_papers = [
            paper for paper in papers
            if (course.lower() in paper['course'].lower() if course else True) and
               (branch.lower() in paper['branch'].lower() if branch else True) and
               (year == paper['year'] if year else True) and
               (semester.lower() in paper['semester'].lower() if semester else True) and
                (subject.lower() in paper['subject'].lower() if subject else True) and
               (paper_type.lower() in paper['paper_type'].lower() if paper_type else True)
        ]

    return render_template('student.html', papers=filtered_papers)
@app.route('/holidays')
def holidays():
    
    return render_template('holiday.html')

@app.route('/syllabus')
def syllabus():
    return render_template('syllabus.html')


@app.route('/semester_<branch>_<semester>')
def semester_page(branch, semester):
    return render_template(f"semester_{branch}_{semester}.html")

# Correct route for uploading syllabus



@app.route('/syllabus', methods=['GET', 'POST'])
def syllabus_options():
    if request.method == 'POST':
        # Handle form submission for upload or view action
        action = request.form.get('action')
        if action == 'upload':
            # Redirect to upload page
            return redirect(url_for('upload_syllabus'))
        elif action == 'view':
            # Redirect to view syllabus page
            return redirect(url_for('view_syllabus'))
    return render_template('syllabus_options.html')


@app.route('/upload_syllabus', methods=['GET', 'POST'])
def upload_syllabus():
    # Check if user is logged in and has the 'admin' role
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be logged in as an admin to upload syllabi.', 'error')
        return redirect(url_for('syllabus'))  # Redirect to login page if not authorized

    if request.method == 'POST':
        branch = request.form['branch']
        semester = request.form['semester']
        file = request.files['file']
        
        if file:
            # Define the upload folder structure (branch and semester-based)
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'syllabus', branch, semester)
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            flash("Syllabus uploaded successfully!", "success")
        else:
            flash("No file selected for upload.", "error")
    
    return render_template('upload_images.html', heading="Upload Syllabus")


@app.route('/view_syllabus')
def view_syllabus():
    # This route displays the syllabus files for students
    syllabus_files = {}
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'syllabus')

    # Loop through branches and semesters to find uploaded files
    for branch in os.listdir(upload_folder):
        branch_path = os.path.join(upload_folder, branch)
        if os.path.isdir(branch_path):
            syllabus_files[branch] = {}
            for semester in os.listdir(branch_path):
                semester_path = os.path.join(branch_path, semester)
                if os.path.isdir(semester_path):
                    syllabus_files[branch][semester] = [
                        f"/static/uploads/syllabus/{branch}/{semester}/{file}"
                        for file in os.listdir(semester_path)
                        if file.lower().endswith(('pdf', 'docx', 'jpg', 'png'))
                    ]

    return render_template('view_images.html', heading="View Syllabus", images=syllabus_files)




if __name__ == '__main__':
    app.run(debug=True)
