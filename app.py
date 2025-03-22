from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db,bcrypt,Challenge, GroupChallenge, GroupChallengeParticipants, Group, GroupMember
from models import TestResult, User, QuestionnaireResult
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pymongo import MongoClient  # Corrected MongoDB Import
import lifestyle_model  # Import recommendation logic
from dotenv import load_dotenv
from datetime import datetime, timezone  # ✅ Import timezone
from flask_login import login_user
import json
from lifestyle_model import calculate_lifestyle_score, get_recommendations
# Initialize Flask App
app = Flask(__name__)
app.secret_key = "super123"
import os

basedir = os.path.abspath(os.path.dirname(__file__))  # Get base directory
db_path = os.path.join(basedir, 'instance', 'lifestyle_db.sqlite')  # Correct DB path

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Load environment variables
app.config['SECRET_KEY'] = "super123"


# Initialize SQLAlchemy & Bcrypt
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
from flask_session import Session  # ✅ Import Flask-Session

# Configure session to use filesystem storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)  # ✅ Initialize session


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    print(f"🔹 Loading user with ID: {user_id}")  # Debugging
    return User.query.get(int(user_id))  # Ensure it returns a user

# Ensure tables are created
with app.app_context():
    db.create_all()
    print("Database tables created!")

# Define questions and options for each age group
questions_data = {
    "0-12": [
        ("How often do you eat vegetables?", ["Rarely", "Sometimes", "Often", "Always"]),
        ("How many hours do you sleep?", ["Less than 6", "6-8", "8-10", "More than 10"]),
        ("Do you play outdoor games?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How much water do you drink daily?", ["Less than 1L", "1-2L", "2-3L", "More than 3L"]),
        ("Do you eat junk food?", ["Daily", "Few times a week", "Rarely", "Never"]),
        ("How often do you brush your teeth?", ["Once a day", "Twice a day", "Rarely", "Never"]),
        ("Do you watch TV or use screens before bed?", ["Always", "Often", "Sometimes", "Never"]),
        ("Do you have a regular bedtime?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you drink milk daily?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you wash your hands before meals?", ["Never", "Rarely", "Sometimes", "Always"])
    ],
    "12-20": [
        ("How often do you exercise?", ["Never", "1-2 times a week", "3-5 times a week", "Daily"]),
        ("How many hours do you sleep?", ["Less than 5", "5-7", "7-9", "More than 9"]),
        ("Do you eat fast food?", ["Daily", "Few times a week", "Rarely", "Never"]),
        ("How much water do you drink daily?", ["Less than 1L", "1-2L", "2-3L", "More than 3L"]),
        ("How often do you feel stressed?", ["Always", "Often", "Sometimes", "Rarely"]),
        ("How many hours do you spend on screens daily?", ["More than 6", "4-6", "2-4", "Less than 2"]),
        ("Do you eat breakfast regularly?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you consume sugary drinks?", ["Daily", "Few times a week", "Rarely", "Never"]),
        ("Do you smoke or drink alcohol?", ["Yes", "Occasionally", "Rarely", "Never"]),
        ("How often do you engage in hobbies?", ["Never", "Rarely", "Sometimes", "Often"])
    ],
    "20-35": [
        ("How often do you exercise?", ["Never", "1-2 times a week", "3-5 times a week", "Daily"]),
        ("Do you follow a balanced diet?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How many hours do you work per day?", ["Less than 4", "4-6", "6-8", "More than 8"]),
        ("Do you take breaks while working?", ["Never", "Rarely", "Sometimes", "Often"]),
        ("How often do you feel stressed?", ["Always", "Often", "Sometimes", "Rarely"]),
        ("Do you get enough sleep?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you drink coffee?", ["More than 3 cups", "2-3 cups", "1 cup", "Rarely"]),
        ("Do you have a regular workout routine?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you have a work-life balance?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you socialize?", ["Never", "Rarely", "Sometimes", "Often"])
    ],
    "35-50": [
        ("Do you go for regular health checkups?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you exercise?", ["Never", "1-2 times a week", "3-5 times a week", "Daily"]),
        ("Do you have a balanced diet?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you experience joint pain?", ["Always", "Often", "Sometimes", "Rarely"]),
        ("Do you get quality sleep?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you consume alcohol?", ["Daily", "Few times a week", "Rarely", "Never"]),
        ("How often do you meditate or relax?", ["Never", "Rarely", "Sometimes", "Often"]),
        ("Do you feel energetic throughout the day?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you have digestive issues?", ["Always", "Often", "Sometimes", "Rarely"]),
        ("Do you spend time with family and friends?", ["Never", "Rarely", "Sometimes", "Often"])
    ],
    "50+": [
        ("Do you go for regular health checkups?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you walk or exercise?", ["Never", "Rarely", "Sometimes", "Daily"]),
        ("Do you consume a high-fiber diet?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you take prescribed medications regularly?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you experience joint pain?", ["Always", "Often", "Sometimes", "Rarely"]),
        ("Do you engage in mental activities like reading?", ["Never", "Rarely", "Sometimes", "Often"]),
        ("How often do you feel lonely?", ["Always", "Often", "Sometimes", "Rarely"]),
        ("Do you get quality sleep?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("Do you maintain a healthy weight?", ["Never", "Rarely", "Sometimes", "Always"]),
        ("How often do you meet friends or family?", ["Never", "Rarely", "Sometimes", "Often"])
    ]
}

# Homepage Route
@app.route('/')
def index():
    return render_template('index.html')


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user:
            print(f"🔹 Found user: {user.email}")
        else:
            print("❌ User not found")
            flash('User does not exist.', 'danger')
            return redirect(url_for('login'))

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)  # Ensure `remember=True`
            print(f"✅ Logged in user: {user.email}, ID: {user.id}")  
            print(f"Session user: {current_user.is_authenticated}")  # Check if session is updated
            return redirect(url_for('gender_age'))
        else:
            print("❌ Incorrect password")
            flash('Invalid email or password. Try again.', 'danger')

    return render_template('login.html')

# User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Gender & Age Selection
@app.route('/gender-age', methods=['GET', 'POST'])
def gender_age():
    if request.method == 'POST':
        gender = request.form.get('gender')
        age_group = request.form.get("age_group")


        if not gender or not age_group:
            flash("Please select both gender and age.", "danger")
            return redirect(url_for('gender_age'))

        # Store in session
        session['gender'] = gender
        session['age_group'] = age_group

        print(f"✅ Gender: {gender}, Age: {age_group}")  # Debugging
        session["age_group"] = age_group
        return redirect(url_for("questionnaire", age_group=age_group))


    return render_template('gender_age.html')


# Questionnaire Route
@app.route("/questionnaire/<age_group>", methods=["GET", "POST"])
def questionnaire(age_group):
    questions = questions_data.get(age_group, [])  # Fetch age-specific questions

    if request.method == "POST":
        responses = {q: request.form[q] for q, _ in questions}  # Collect user responses

        # Store responses in session for result page
        session["last_test"] = responses  

        # Get recommendations and lifestyle score from the model
        result = lifestyle_model.get_recommendations(responses)

        # Store result in session to display on the result page
        session["result"] = result  

        return redirect(url_for("result"))  # Redirect to result page

    return render_template("question_form.html", age_group=age_group, questions=questions)

@app.route('/test-session')
def test_session():
    print("🔍 Session Data:", session)  # Debugging
    return jsonify(session)


# Display Recommendations
@app.route("/recommendations")
def recommendations():
    responses = session.get("responses", {})
    age_group = session.get("age_group", "")

    # Process responses using lifestyle_model
    recommendations = lifestyle_model.get_recommendations(age_group, responses)

    return render_template("recommendations.html", recommendations=recommendations)

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    print("🔍 Session Data Before Rendering Profile:", session)  # Debugging

    # ✅ Get test history
    test_history = session.get("test_history", [])
    completed_group_challenges = GroupChallengeParticipants.query.filter_by(user_id=current_user.id, completed=True).all()

    return render_template(
        'profile.html', 
        user=current_user, 
        test_history=test_history, 
        completed_group_challenges=completed_group_challenges
    )


@app.route('/result')
def result():
    past_test = session.get('last_test', {})
    result = session.get('result', None)

    print("Session data:", session)  # Debugging

    if not past_test or not result:
        flash("Please complete the questionnaire first.", "warning")
        return redirect(url_for("index"))  
    if "test_history" not in session:
        session["test_history"] = []

    # ✅ Append new test result to history
    session["test_history"].append({
        "score": result["score"],
        "recommendations": "\n".join(result["specific_recommendations"]),
        "date_taken": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    session.modified = True  # ✅ Ensure session updates

    print("✅ Test History Updated:", session["test_history"])  # Debugging
    return render_template('result.html', past_test=past_test, result=result)

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    data = request.json
    responses = data.get("responses")
    age_group = data.get("age_group")

    if not responses or not age_group:
        return jsonify({"error": "Missing data"}), 400

    # Process responses and calculate score
    result_data = lifestyle_model.get_recommendations(responses)
    score = result_data.get("score", 0)  
    recommendations = "\n".join(result_data.get("specific_recommendations", ["No recommendations available"]))

    # ✅ Debugging: Print before updating session
    print("🔹 Storing Test Result:", {"score": score, "recommendations": recommendations})

    # ✅ Store test results in session
    if "test_history" not in session:
        session["test_history"] = []  

    session["test_history"].append({
        "score": score,
        "recommendations": recommendations,
        "date_taken": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    session.modified = True  # ✅ Ensure session updates

    print("✅ Test History Updated in Session:", session["test_history"])  

    return jsonify({
        "message": "Quiz submitted successfully!",
        "score": score,
        "recommendations": recommendations
    })
def add_default_challenges(user_id):
    """Assigns default challenges to a newly registered user if none exist."""
    
    existing_challenges = Challenge.query.filter_by(user_id=user_id).count()
    if existing_challenges > 0:
        print(f"🔹 User {user_id} already has challenges assigned!")
        return  # ✅ Avoid duplicate assignments

    default_challenges = [
        "Drink 2L water today!",
        "Avoid junk food for a day!",
        "Walk 5000 steps today!",
        "Sleep for at least 7 hours!",
        "Do 15 minutes of meditation!",
        "Eat a home-cooked meal today!",
        "Limit screen time to 2 hours!",
        "Read a book for 30 minutes!",
        "Spend 30 minutes exercising!",
        "Avoid sugary drinks today!"
    ]

    for challenge_text in default_challenges:
        challenge = Challenge(user_id=user_id, challenge_text=challenge_text, completed=False)
        db.session.add(challenge)

    db.session.commit()
    print(f"✅ Default challenges assigned successfully for user {user_id}!")



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        add_default_challenges(new_user.id)
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ✅ Route: Fetch Personal Challenge
@app.route('/challenges', methods=['GET'])
@login_required
def challenges():
    # ✅ Fetch **only the first incomplete challenge**
    active_challenge = Challenge.query.filter_by(user_id=current_user.id, completed=False).first()

    if active_challenge:
        print("🔍 Active Challenge Found:", active_challenge.challenge_text)  # Debugging
    else:
        print("⚠️ No active challenges available!")  # Debugging

    return render_template("challenges.html", challenge=active_challenge)
@app.route('/complete_challenge/<int:challenge_id>')
@login_required
def complete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)

    if challenge.user_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for('challenges'))

    # ✅ Mark current challenge as completed
    challenge.completed = True
    db.session.commit()

    # ✅ Fetch next challenge
    next_challenge = Challenge.query.filter_by(user_id=current_user.id, completed=False).first()

    if not next_challenge:
        # ✅ If no more challenges, reset them
        flash("🎉 You've completed all challenges! Restarting challenges... 🔄", "success")
        reset_user_challenges(current_user.id)

    return redirect(url_for('challenges'))


def reset_user_challenges(user_id):
    """Resets all challenges for a user after they complete them all."""
    default_challenges = [
        "Drink 2L water today!",
        "Avoid junk food for a day!",
        "Walk 5000 steps today!",
        "Sleep for at least 7 hours!",
        "Do 15 minutes of meditation!",
        "Eat a home-cooked meal today!",
        "Limit screen time to 2 hours!",
        "Read a book for 30 minutes!",
        "Spend 30 minutes exercising!",
        "Avoid sugary drinks today!"
    ]

    # ✅ Remove old challenges
    Challenge.query.filter_by(user_id=user_id).delete()

    # ✅ Assign new challenges
    for challenge_text in default_challenges:
        new_challenge = Challenge(user_id=user_id, challenge_text=challenge_text, completed=False)
        db.session.add(new_challenge)

    db.session.commit()
    print("✅ Challenges reset successfully for user:", user_id)


@app.route('/create_group_challenge', methods=['POST'])
@login_required
def create_group_challenge():
    """Allows a user to create a new group challenge"""
    challenge_text = request.form.get('challenge_text')

    if not challenge_text:
        flash("Challenge text cannot be empty!", "danger")
        return redirect(url_for('group_challenges'))

    new_challenge = GroupChallenge(
        challenge_text=challenge_text, created_by=current_user.id
    )
    db.session.add(new_challenge)
    db.session.commit()
    
    flash("🎯 Group Challenge Created!", "success")
    return redirect(url_for('group_challenges'))



@app.route('/join_group_challenge/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
def join_group_challenge(challenge_id):
    challenge = GroupChallenge.query.get_or_404(challenge_id)

    # Check if the user is already in the challenge
    existing_member = GroupChallengeParticipants.query.filter_by(
        group_challenge_id=challenge_id, user_id=current_user.id
    ).first()

    if existing_member:
        flash("You're already in this challenge!", "warning")
    else:
        new_member = GroupChallengeParticipants(group_challenge_id=challenge_id, user_id=current_user.id)
        db.session.add(new_member)
        db.session.commit()
        flash("Successfully joined the group challenge!", "success")

    return redirect(url_for('group_challenges'))



@app.route('/complete_group_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_group_challenge(challenge_id):
    """Allows a user to mark a group challenge as completed."""
    participation = GroupChallengeParticipants.query.filter_by(
        group_challenge_id=challenge_id, user_id=current_user.id
    ).first()

    if participation:
        if not participation.completed:
            participation.completed = True
            db.session.commit()
            flash("🎉 Challenge Completed! You earned a badge!", "success")
        else:
            flash("You have already completed this challenge!", "warning")
    else:
        flash("You haven't joined this challenge yet!", "danger")

    return redirect(url_for('group_challenges'))




@app.route('/group_challenges', methods=['GET'])
@login_required
def group_challenges():
    challenges = GroupChallenge.query.all()
    
    # Fetch user's joined challenges
    joined_challenges = GroupChallengeParticipants.query.filter_by(user_id=current_user.id).all()
    joined_ids = {jc.group_challenge_id for jc in joined_challenges}

    print("🔍 Debug: Challenges Fetched:", challenges)  # Debugging

    return render_template(
        "group_challenges.html", 
        challenges=challenges, 
        joined_ids=joined_ids
    )



@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    group_name = request.form.get('group_name')

    if not group_name:
        flash("Group name cannot be empty!", "danger")
        return redirect(url_for('groups'))

    new_group = Group(name=group_name, created_by=current_user.id)
    db.session.add(new_group)
    db.session.commit()

    # Automatically add creator as the first member
    group_member = GroupMember(group_id=new_group.id, user_id=current_user.id)
    db.session.add(group_member)
    db.session.commit()

    flash("🎯 Group Created Successfully!", "success")
    return redirect(url_for('groups'))




@app.route('/invite_to_group/<int:group_id>', methods=['POST'])
@login_required
def invite_to_group(group_id):
    invited_user_id = request.form.get('user_id')

    if not invited_user_id:
        flash("User ID is required!", "danger")
        return redirect(url_for('groups'))

    existing_member = GroupMember.query.filter_by(group_id=group_id, user_id=invited_user_id).first()
    if existing_member:
        flash("User is already a member of this group!", "warning")
    else:
        new_member = GroupMember(group_id=group_id, user_id=invited_user_id)
        db.session.add(new_member)
        db.session.commit()
        flash("✅ User added to the group!", "success")

    return redirect(url_for('groups'))



@app.route('/groups', methods=['GET'])
@login_required
def groups():
    """Displays all user groups"""
    all_groups = Group.query.all()
    user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.id).all()

    return render_template("groups.html", all_groups=all_groups, user_groups=user_groups)



# ✅ Route: View a Specific Group
@app.route('/group/<int:group_id>')
@login_required
def group_details(group_id):
    group = Group.query.get_or_404(group_id)
    members = GroupMember.query.filter_by(group_id=group.id).all()

    return render_template("group_details.html", group=group, members=members)


@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

if __name__ == '__main__':
    app.run(debug=True)




