document.addEventListener("DOMContentLoaded", () => {
    // -----------------------------
    // Quiz Challenge UI interactions
    // -----------------------------

    const answerOptions = document.querySelectorAll(
        ".quiz-option, .answer-option, [data-answer]"
    );

    const nextButton = document.querySelector(
        "#next-question, .next-question, [data-next-question]"
    );

    const previousButton = document.querySelector(
        "#previous-question, .previous-question, [data-previous-question]"
    );

    let selectedAnswer = null;

    // -----------------------------
    // Answer selection
    // -----------------------------
    answerOptions.forEach((option) => {
        option.addEventListener("click", () => {
            // Remove previous selection
            answerOptions.forEach((item) => {
                item.classList.remove("selected");
                item.setAttribute("aria-selected", "false");
            });

            // Select current answer
            option.classList.add("selected");
            option.setAttribute("aria-selected", "true");

            selectedAnswer =
                option.dataset.answer ||
                option.dataset.value ||
                option.textContent.trim();

            // Enable next button
            if (nextButton) {
                nextButton.disabled = false;
                nextButton.classList.add("ready");
            }
        });

        // Keyboard accessibility
        option.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                option.click();
            }
        });
    });

    // -----------------------------
    // Next question
    // -----------------------------
    if (nextButton) {
        nextButton.addEventListener("click", () => {
            if (!selectedAnswer) {
                showQuizMessage("Please choose an answer first! 😊");
                return;
            }

            const form = nextButton.closest("form");

            if (form) {
                // If Django form exists, submit selected answer
                const input = form.querySelector(
                    'input[name="answer"]:checked, input[name="selected_answer"]'
                );

                if (input) {
                    input.value = selectedAnswer;
                }

                form.submit();
                return;
            }

            // JS-based quiz
            const nextUrl = nextButton.dataset.url;

            if (nextUrl) {
                window.location.href = nextUrl;
            }
        });
    }

    // -----------------------------
    // Previous question
    // -----------------------------
    if (previousButton) {
        previousButton.addEventListener("click", () => {
            const previousUrl = previousButton.dataset.url;

            if (previousUrl) {
                window.location.href = previousUrl;
                return;
            }

            window.history.back();
        });
    }

    // -----------------------------
    // Level card animations
    // -----------------------------
    const levelCards = document.querySelectorAll(
        ".level-card, .quiz-level-card"
    );

    levelCards.forEach((card) => {
        card.addEventListener("mouseenter", () => {
            if (!card.classList.contains("locked")) {
                card.classList.add("quiz-card-hover");
            }
        });

        card.addEventListener("mouseleave", () => {
            card.classList.remove("quiz-card-hover");
        });
    });

    // -----------------------------
    // Start Quiz buttons
    // -----------------------------
    const startButtons = document.querySelectorAll(
        ".start-quiz, .start-quiz-btn, [data-start-quiz]"
    );

    startButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const card = button.closest(
                ".level-card, .quiz-level-card"
            );

            if (card && card.classList.contains("locked")) {
                event.preventDefault();
                showQuizMessage(
                    "Complete the previous level to unlock this one! ⭐"
                );
                return;
            }

            button.classList.add("loading");

            setTimeout(() => {
                button.classList.remove("loading");
            }, 500);
        });
    });

    // -----------------------------
    // Star animation
    // -----------------------------
    const stars = document.querySelectorAll(
        ".star, .quiz-star, .earned-star"
    );

    stars.forEach((star, index) => {
        setTimeout(() => {
            star.classList.add("star-pop");
        }, index * 100);
    });

    // -----------------------------
    // Progress bar animation
    // -----------------------------
    const progressBars = document.querySelectorAll(
        ".progress-fill, .quiz-progress-fill"
    );

    progressBars.forEach((bar) => {
        const targetWidth =
            bar.dataset.progress ||
            bar.style.width ||
            "0%";

        bar.style.width = "0%";

        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 150);
    });

    // -----------------------------
    // Result page animation
    // -----------------------------
    const resultCard = document.querySelector(
        ".quiz-result, .result-card, .congratulations-card"
    );

    if (resultCard) {
        resultCard.classList.add("result-enter");

        const resultStars = resultCard.querySelectorAll(
            ".star, .result-star"
        );

        resultStars.forEach((star, index) => {
            setTimeout(() => {
                star.classList.add("star-pop");
            }, 300 + index * 180);
        });
    }

    // -----------------------------
    // Continue Quiz
    // -----------------------------
    const continueButton = document.querySelector(
        ".continue-quiz, [data-continue-quiz]"
    );

    if (continueButton) {
        continueButton.addEventListener("click", () => {
            const url = continueButton.dataset.url;

            if (url) {
                window.location.href = url;
            }
        });
    }

    // -----------------------------
    // Mobile navigation
    // -----------------------------
    const menuButton = document.querySelector(
        ".mobile-menu-btn, #mobile-menu-btn"
    );

    const navigation = document.querySelector(
        ".quiz-navigation, .main-navigation, nav"
    );

    if (menuButton && navigation) {
        menuButton.addEventListener("click", () => {
            navigation.classList.toggle("mobile-open");

            const isOpen =
                navigation.classList.contains("mobile-open");

            menuButton.setAttribute(
                "aria-expanded",
                String(isOpen)
            );
        });
    }

    // -----------------------------
    // Friendly message
    // -----------------------------
    function showQuizMessage(message) {
        let messageBox = document.querySelector(
            ".quiz-message"
        );

        if (!messageBox) {
            messageBox = document.createElement("div");
            messageBox.className = "quiz-message";

            document.body.appendChild(messageBox);
        }

        messageBox.textContent = message;
        messageBox.classList.add("show");

        setTimeout(() => {
            messageBox.classList.remove("show");
        }, 2500);
    }

    // -----------------------------
    // Prevent double submission
    // -----------------------------
    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const submitButtons = form.querySelectorAll(
                'button[type="submit"], input[type="submit"]'
            );

            submitButtons.forEach((button) => {
                button.disabled = true;
                button.classList.add("submitting");
            });
        });
    });
});