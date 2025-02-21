def calculate_lifestyle_score(responses):
    """
    Calculates a lifestyle score based on user responses.
    Each option has a weight (higher for healthier choices).
    """
    score = 0
    total_questions = len(responses)

    # Define scoring system for responses (higher score for healthier habits)
    scoring = {
        "Always": 10, "Daily": 10, "Often": 7, "3-5 times a week": 7,
        "Sometimes": 5, "Few times a week": 5, "Neutral": 5,  
        "Rarely": 2, "1-2 times a week": 2, "Never": 0,
        "Less than 1L": 2, "1-2L": 5, "2-3L": 7, "More than 3L": 10,
        "Less than 6": 2, "6-8": 7, "8-10": 10, "More than 10": 10,
        "Less than 5": 2, "5-7": 5, "7-9": 7, "More than 9": 10,
        "More than 6": 0, "4-6": 2, "2-4": 5, "Less than 2": 10,
        "More than 8": 2, "6-8": 5, "4-6": 7, "Less than 4": 10,
        "More than 3 cups": 2, "2-3 cups": 5, "1 cup": 7, "Rarely": 10,
        "High sugar intake": 2, "Moderate sugar intake": 5, "Low sugar intake": 10,
        "Poor work-life balance": 2, "Moderate balance": 5, "Good balance": 10,
        "Frequent stress": 2, "Occasional stress": 5, "Rarely stressed": 10
    }

    # Calculate total score
    for response in responses.values():
        score += scoring.get(response, 5)  # Default score is 5 if not found

    # Normalize the score to a scale of 100
    max_possible_score = total_questions * 10  # Max score per question is 10
    lifestyle_score = (score / max_possible_score) * 100 if total_questions > 0 else 0

    return round(lifestyle_score)

def get_recommendations(responses):
    """
    Generates recommendations based on the user's lifestyle score and responses.
    """
    score = calculate_lifestyle_score(responses)

    general_recommendation = ""
    recommendations_list = []  # Stores all recommendations correctly

    # General lifestyle score-based feedback
    if score >= 80:
        general_recommendation = "Excellent lifestyle! Keep maintaining your healthy habits."
    elif score >= 60:
        general_recommendation = "Good lifestyle, but consider adding more healthy routines like exercise and a balanced diet."
    elif score >= 40:
        general_recommendation = "Moderate lifestyle. Try to improve your habits by eating healthy and staying active."
    else:
        general_recommendation = "Unhealthy lifestyle. Consider making significant changes such as exercising daily and eating nutritious food."

    # DEBUG: Print responses to check keys
    print("\n🔍 DEBUG: User Responses:", responses)

    # Generate specific recommendations
    for question, answer in responses.items():
        question_lower = question.lower()

        if "sleep" in question_lower and answer in ["Less than 6", "More than 10"]:
            recommendations_list.append("Try to get 7-9 hours of sleep for better health.")

        if "water" in question_lower and answer in ["Less than 1L", "1-2L"]:
            recommendations_list.append("Increase your water intake to at least 2-3 liters daily.")

        if "exercise" in question_lower and answer in ["Never", "Rarely"]:
            recommendations_list.append("Incorporate regular physical activity, at least 30 minutes a day.")

        if "fruits" in question_lower or "vegetables" in question_lower and answer in ["Rarely", "Never"]:
            recommendations_list.append("Increase your intake of fresh vegetables and fruits for a balanced diet.")

        if "screen time" in question_lower and answer == "More than 6":
            recommendations_list.append("Reduce screen time and take regular breaks to avoid eye strain and mental fatigue.")

        if "caffeine" in question_lower and answer == "More than 3 cups":
            recommendations_list.append("Limit caffeine intake to avoid sleep disruption and anxiety.")

        if "sugar" in question_lower and answer == "High sugar intake":
            recommendations_list.append("Reduce sugar intake to lower the risk of diabetes and weight gain.")

        if "work-life balance" in question_lower and answer == "Poor work-life balance":
            recommendations_list.append("Ensure a better balance by setting boundaries and taking breaks.")

        if "stress" in question_lower and answer == "Frequent stress":
            recommendations_list.append("Try relaxation techniques like meditation, deep breathing, or yoga.")

    # Print only recommendations
    print("\n📌 **Personalized Recommendations:**")

    if general_recommendation:
        print(f"👉 {general_recommendation}\n")

    if recommendations_list:
        for rec in recommendations_list:
            print(f"✅ {rec}")
    else:
        print("✅ Keep up the good work! No major improvements needed.")

    return {
        "score": score,
        "general_recommendation": general_recommendation,
        "specific_recommendations": recommendations_list
    }
