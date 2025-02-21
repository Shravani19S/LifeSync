from flask import Flask, render_template, request, redirect, url_for, session, flash
import lifestyle_model  # Import recommendation logic

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  

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
@app.route('/')
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    users = {"sonawaneshravani19@gmail.com": "sau"}
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("gender_age"))

        flash("Invalid credentials!", "danger")
    
    return render_template("login.html")

@app.route("/gender-age", methods=["GET", "POST"])
def gender_age():
    if request.method == "POST":
        print(request.form)  # Debugging: Print received form data
        if "gender" not in request.form or "age_group" not in request.form:
            return "Error: Missing form data", 400  # Handle missing data properly
        
        gender = request.form["gender"]
        age_group = request.form["age_group"]
        return redirect(url_for("questionnaire", age_group=age_group))

    return render_template("gender-age.html")


@app.route("/questionnaire/<age_group>", methods=["GET", "POST"])
def questionnaire(age_group):
    questions = questions_data.get(age_group, [])  # Fetch age-specific questions

    if request.method == "POST":
        responses = {q: request.form[q] for q, _ in questions}  # Collect user responses
        
        # Get recommendations and lifestyle score from the model
        result = lifestyle_model.get_recommendations(responses)

        return render_template("result.html", result=result)

    return render_template("question-form.html", age_group=age_group, questions=questions)
@app.route("/recommendations", methods=["GET"])
def recommendations():
    responses = session.get("responses")
    if not responses:
        flash("Please complete the questionnaire first.", "warning")
        return redirect(url_for("questionnaire"))

    recommendations = lifestyle_model.get_recommendations(responses)  
    return render_template("recommendations.html", recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)