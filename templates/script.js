document.addEventListener("DOMContentLoaded", function () {
    let age = localStorage.getItem("selectedAge");
    let gender = localStorage.getItem("selectedGender");

    if (!age || !gender) {
        alert("Age and gender not selected. Redirecting...");
        window.location.href = "age-gender.html";
        return;
    }

    fetch("http://127.0.0.1:5000/get_questions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ age: age, gender: gender }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        let questionsDiv = document.getElementById("questions");
        questionsDiv.innerHTML = "";

        data.questions.forEach((question, index) => {
            questionsDiv.innerHTML += `
                <div class="question">
                    <p>${index + 1}. ${question}</p>
                    <select id="q${index}">
                        <option value="">Select an option</option>
                        <option value="Always">Always</option>
                        <option value="Often">Often</option>
                        <option value="Sometimes">Sometimes</option>
                        <option value="Rarely">Rarely</option>
                        <option value="Never">Never</option>
                    </select>
                </div>
            `;
        });
    })
    .catch(error => console.error("Error fetching questions:", error));
});

function submitAnswers() {
    let responses = {};
    let totalQuestions = document.querySelectorAll(".question").length;

    for (let i = 0; i < totalQuestions; i++) {
        let answer = document.getElementById(`q${i}`).value;
        if (!answer) {
            alert("Please answer all questions before submitting.");
            return;
        }
        responses[`Q${i + 1}`] = answer;
    }

    console.log("User Responses:", responses);
    alert("Answers submitted successfully!");
    window.location.href = "results.html"; // Redirect to results page
}
