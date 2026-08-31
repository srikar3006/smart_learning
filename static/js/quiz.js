(() => {
    const config = window.QUIZ_CONFIG;
    const grid = document.getElementById("choices-grid");
    const feedback = document.getElementById("feedback-banner");
    const nextBtn = document.getElementById("next-btn");
    if (!config || !grid || !nextBtn) return;

    let answered = false;

    const setFeedback = (text, kind) => {
        feedback.textContent = text;
        feedback.className = `feedback-banner ${kind}`;
    };

    grid.querySelectorAll(".choice-btn").forEach((button) => {
        button.addEventListener("click", async () => {
            if (answered) return;
            answered = true;
            button.classList.add("loading-choice");

            try {
                const data = await window.postJSON(config.answerUrl, {
                    question_id: config.questionId,
                    choice_id: Number(button.dataset.choiceId),
                });

                grid.querySelectorAll(".choice-btn").forEach((item) => {
                    item.disabled = true;
                    if (data.correct_choice_id && Number(item.dataset.choiceId) === data.correct_choice_id) {
                        item.classList.add("correct");
                    }
                });

                if (data.correct) {
                    button.classList.add("correct");
                    setFeedback("🎉 Correct! You got it!", "correct");
                } else {
                    button.classList.add("wrong");
                    setFeedback("Keep going — the correct answer is highlighted.", "wrong");
                }
                nextBtn.disabled = false;
            } catch (error) {
                answered = false;
                button.classList.remove("loading-choice");
                setFeedback(error.message || "Could not save your answer. Please try again.", "wrong");
            }
        });
    });

    nextBtn.addEventListener("click", () => {
        nextBtn.disabled = true;
        window.location.assign(config.nextUrl);
    });

    const audio = document.getElementById("question-audio");
    const promptButton = document.getElementById("prompt-audio-btn");
    if (audio && promptButton) {
        promptButton.addEventListener("click", async () => {
            if (audio.paused) {
                await audio.play();
                promptButton.textContent = "■ Stop question";
            } else {
                audio.pause();
                promptButton.textContent = "▶ Hear the question";
            }
        });
        audio.addEventListener("ended", () => {
            promptButton.textContent = "▶ Hear the question";
        });
    }
})();

