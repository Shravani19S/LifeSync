import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from joblib import dump, load  # For saving and loading ML models

# ✅ Define all possible questions for consistent training
all_questions = [
    "How often do you eat vegetables?", "How many hours do you sleep?", "Do you play outdoor games?",
    "How much water do you drink daily?", "Do you eat junk food?", "How often do you brush your teeth?",
    "Do you watch TV or use screens before bed?", "Do you have a regular bedtime?", "Do you drink milk daily?",
    "How often do you wash your hands before meals?", "How often do you exercise?", "Do you eat fast food?",
    "How often do you feel stressed?", "How many hours do you spend on screens daily?", "Do you eat breakfast regularly?",
    "How often do you consume sugary drinks?", "Do you smoke or drink alcohol?", "How often do you engage in hobbies?",
    "Do you follow a balanced diet?", "How many hours do you work per day?", "Do you take breaks while working?",
    "Do you drink coffee?", "Do you have a regular workout routine?", "Do you have a work-life balance?",
    "How often do you socialize?", "Do you go for regular health checkups?", "Do you have digestive issues?",
    "Do you spend time with family and friends?", "How often do you meditate or relax?",
    "How often do you feel lonely?", "Do you maintain a healthy weight?"
]

# ✅ Sample dataset (Train ML Model with All Features)
data = [
    {q: "Sometimes" for q in all_questions} | {"Lifestyle Score": 70},
    {q: "Always" for q in all_questions} | {"Lifestyle Score": 90},
    {q: "Rarely" for q in all_questions} | {"Lifestyle Score": 40},
    {q: "Often" for q in all_questions} | {"Lifestyle Score": 60},
]

# ✅ Convert dataset to DataFrame
df = pd.DataFrame(data)

# ✅ Separate Features (X) and Target Variable (y)
X = df.drop(columns=["Lifestyle Score"])
y = df["Lifestyle Score"]

# ✅ One-Hot Encoding for categorical features
encoder = OneHotEncoder(handle_unknown="ignore")  # ✅ Ignore unknown categories
X_encoded = encoder.fit_transform(X).toarray()

# ✅ Split data into training & testing
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# ✅ Train Decision Tree Model
model = DecisionTreeRegressor()
model.fit(X_train, y_train)

# ✅ Save trained model & encoder
dump(model, 'lifestyle_model.joblib')
dump(encoder, 'encoder.joblib')

print("✅ Model trained and saved!")


# ✅ Predict Lifestyle Score Function
def calculate_lifestyle_score(responses):
    """
    Predicts the lifestyle score based on user responses using ML.
    """
    model = load('lifestyle_model.joblib')
    encoder = load('encoder.joblib')

    # ✅ Fill missing responses with default "Sometimes"
    complete_responses = {q: responses.get(q, "Sometimes") for q in all_questions}

    # Convert user responses into DataFrame
    df = pd.DataFrame([complete_responses])
    X_encoded = encoder.transform(df).toarray()

    # Predict lifestyle score using ML model
    score = model.predict(X_encoded)[0]
    
    return round(score)


# ✅ AI-Based Recommendation System
def get_recommendations(responses):
    """
    Generates AI-driven recommendations based on ML-predicted lifestyle score.
    """
    score = calculate_lifestyle_score(responses)

    general_recommendation = ""
    recommendations_list = []

    # ✅ AI-Based General Recommendations
    if score >= 80:
        general_recommendation = "🏆 Excellent lifestyle! Keep up your healthy habits!"
    elif score >= 60:
        general_recommendation = "✅ Good lifestyle! Consider adding more healthy routines."
    elif score >= 40:
        general_recommendation = "⚠️ Moderate lifestyle. Try improving your diet and activity level."
    else:
        general_recommendation = "🚨 Unhealthy lifestyle! Consider significant changes to improve your well-being."

    # ✅ AI-Based Specific Recommendations
    for question, answer in responses.items():
        if "sleep" in question.lower() and answer in ["Less than 6", "More than 10"]:
            recommendations_list.append("💤 Aim for 7-9 hours of sleep to improve energy levels.")

        if "water" in question.lower() and answer in ["Less than 1L", "1-2L"]:
            recommendations_list.append("💧 Increase your water intake to at least 2-3 liters daily.")

        if "exercise" in question.lower() and answer in ["Never", "Rarely"]:
            recommendations_list.append("🏃 Incorporate at least 30 minutes of physical activity daily.")

        if ("fruits" in question.lower() or "vegetables" in question.lower()) and answer in ["Rarely", "Never"]:
            recommendations_list.append("🍎 Increase your intake of fresh fruits and vegetables.")

        if "screen time" in question.lower() and answer == "More than 6":
            recommendations_list.append("📵 Reduce screen time and take breaks to avoid eye strain.")

        if "caffeine" in question.lower() and answer == "More than 3 cups":
            recommendations_list.append("☕ Limit caffeine intake to avoid sleep disruption.")

        if "sugar" in question.lower() and answer == "High sugar intake":
            recommendations_list.append("🚫 Reduce sugar intake to lower the risk of diabetes.")

        if "work-life balance" in question.lower() and answer == "Poor work-life balance":
            recommendations_list.append("⚖️ Set boundaries to improve work-life balance.")

        if "stress" in question.lower() and answer == "Frequent stress":
            recommendations_list.append("🧘 Try relaxation techniques like meditation or deep breathing.")

    return {
        "score": score,
        "general_recommendation": general_recommendation,
        "specific_recommendations": recommendations_list
    }


# ✅ Example Usage
if __name__ == "__main__":
    user_responses = {
        "How often do you eat vegetables?": "Sometimes",
        "How many hours do you sleep?": "7-9",
    }

    result = get_recommendations(user_responses)

    print("🔹 Lifestyle Score:", result["score"])
    print("🔹 General Recommendation:", result["general_recommendation"])
    print("🔹 Specific Recommendations:")
    for rec in result["specific_recommendations"]:
        print(f"✅ {rec}")
