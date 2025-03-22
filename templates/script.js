document.addEventListener("DOMContentLoaded", function () {
    // Animate Hero Section
    const hero = document.querySelector(".hero");
    setTimeout(() => {
        hero.style.transform = "scale(1.05)";
    }, 500);

    // Dark Mode Toggle
    const toggleBtn = document.createElement("button");
    toggleBtn.innerText = "Toggle Dark Mode";
    toggleBtn.classList.add("btn");
    toggleBtn.style.margin = "10px";
    document.body.insertBefore(toggleBtn, document.body.firstChild);

    toggleBtn.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");
    });

    // Form Validation
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            let valid = true;
            document.querySelectorAll("input[required]").forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.border = "2px solid red";
                } else {
                    input.style.border = "1px solid #ccc";
                }
            });

            if (!valid) {
                e.preventDefault();
                alert("Please fill in all required fields.");
            }
        });
    }
});
