(function () {
  "use strict";

  const STORAGE_PREFIX = "smartLearning.quizChallenge.v2";

  const getKey = (level) =>
    `${STORAGE_PREFIX}.level.${level}`;

  function safeJSON(value, fallback) {
    try {
      return JSON.parse(value);
    } catch (error) {
      return fallback;
    }
  }

  // ------------------------------------------------------------
  // SHUFFLE
  // ------------------------------------------------------------

  function shuffle(list) {
    const copy = list.slice();

    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));

      [copy[i], copy[j]] = [copy[j], copy[i]];
    }

    return copy;
  }

  // ------------------------------------------------------------
  // CSRF
  // ------------------------------------------------------------

  function csrfToken() {
    const input = document.querySelector("#csrf-token");

    if (input) {
      return input.value;
    }

    const match = document.cookie.match(
      /(?:^|; )csrftoken=([^;]+)/
    );

    return match
      ? decodeURIComponent(match[1])
      : "";
  }

  // ------------------------------------------------------------
  // MOBILE MENU
  // ------------------------------------------------------------

  function wireMobileMenu() {
    const button = document.getElementById("mobile-menu");
    const nav = document.getElementById("mobile-nav");

    if (!button || !nav || button.dataset.bound) {
      return;
    }

    button.dataset.bound = "1";

    button.addEventListener("click", function () {
      const open = nav.classList.toggle("open");

      button.setAttribute(
        "aria-expanded",
        String(open)
      );
    });
  }

  // ------------------------------------------------------------
  // TOAST
  // ------------------------------------------------------------

  function toast(message) {
    let node = document.querySelector(".quiz-toast");

    if (!node) {
      node = document.createElement("div");

      node.className = "quiz-toast";

      document.body.appendChild(node);
    }

    node.textContent = message;

    node.classList.add("show");

    window.clearTimeout(node._timer);

    node._timer = window.setTimeout(
      () => node.classList.remove("show"),
      2400
    );
  }

  // ============================================================
  // DASHBOARD
  // ============================================================

  function initDashboard() {
    if (!window.QUIZ_DASHBOARD) {
      return;
    }

    wireMobileMenu();

    const cards = Array.from(
      document.querySelectorAll(".category-card")
    );

    const levels = Array.from(
      document.querySelectorAll(".level-card")
    );

    const title =
      document.getElementById("levels-title");

    const description =
      document.getElementById("levels-description");

    const showAll =
      document.getElementById("show-all");

    // ----------------------------------------------------------
    // CATEGORY FILTER
    // ----------------------------------------------------------

    function setActive(category) {
      cards.forEach((card) => {
        const active =
          card.dataset.category === category;

        card.classList.toggle(
          "selected",
          active
        );

        card.setAttribute(
          "aria-pressed",
          String(active)
        );
      });

      let visible = 0;

      levels.forEach((card) => {
        const categories =
          card.dataset.categories || "";

        const matches =
          !category ||
          categories.includes(
            `|${category}|`
          );

        card.hidden = !matches;

        if (matches) {
          visible += 1;
        }
      });

      if (title) {
        title.textContent = category
          ? `${category} Levels`
          : "Level 1 — 10";
      }

      if (description) {
        description.textContent = category
          ? `${visible} level${visible === 1 ? "" : "s"} include ${category}.`
          : "Easy → Medium → Hard → Very Hard → Expert";
      }

      if (showAll) {
        showAll.hidden = !category;
      }
    }

    cards.forEach((card) => {
      card.addEventListener("click", () => {
        const category =
          card.dataset.category;

        setActive(category);

        localStorage.setItem(
          `${STORAGE_PREFIX}.category`,
          category
        );

        document
          .getElementById("quiz-levels-section")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
      });
    });

    showAll?.addEventListener(
      "click",
      () => {
        localStorage.removeItem(
          `${STORAGE_PREFIX}.category`
        );

        setActive("");
      }
    );

    const savedCategory =
      localStorage.getItem(
        `${STORAGE_PREFIX}.category`
      );

    if (
      savedCategory &&
      cards.some(
        (card) =>
          card.dataset.category ===
          savedCategory
      )
    ) {
      setActive(savedCategory);
    }

    // ----------------------------------------------------------
    // CONTINUE QUIZ
    // ----------------------------------------------------------

    const continueCard =
      document.getElementById(
        "continue-card"
      );

    const continueTitle =
      document.getElementById(
        "continue-title"
      );

    const continueDetail =
      document.getElementById(
        "continue-detail"
      );

    const continueLink =
      document.getElementById(
        "continue-link"
      );

    const restartContinue =
      document.getElementById(
        "restart-continue"
      );

    const unfinished = [];

    for (
      let level = 1;
      level <= 10;
      level += 1
    ) {
      const state = safeJSON(
        localStorage.getItem(
          getKey(level)
        ),
        null
      );

      if (
        state &&
        !state.completed &&
        Array.isArray(state.answers)
      ) {
        unfinished.push(state);
      }
    }

    unfinished.sort(
      (a, b) =>
        (b.updatedAt || 0) -
        (a.updatedAt || 0)
    );

    if (
      unfinished.length &&
      continueCard
    ) {
      const state = unfinished[0];

      const answered =
        Object.keys(
          state.answers || {}
        ).length;

      const url =
        window.QUIZ_DASHBOARD.levelUrlTemplate.replace(
          "/999/",
          `/${state.level}/`
        );

      continueCard.hidden = false;

      continueTitle.textContent =
        `Level ${state.level}`;

      continueDetail.textContent =
        `Question ${Math.min(
          (state.index || 0) + 1,
          state.total || 1
        )} of ${
          state.total || ""
        } · ${answered} answer${
          answered === 1 ? "" : "s"
        } saved`;

      continueLink.href = url;

      restartContinue?.addEventListener(
        "click",
        () => {
          localStorage.removeItem(
            getKey(state.level)
          );

          window.location.href =
            `${url}?restart=1`;
        }
      );
    }

    renderHistoryAndAchievements();
  }

  // ============================================================
  // HISTORY + ACHIEVEMENTS
  // ============================================================

  function renderHistoryAndAchievements() {
    const historyNode =
      document.getElementById(
        "quiz-history"
      );

    const achievementsNode =
      document.getElementById(
        "quiz-achievements"
      );

    if (
      !historyNode &&
      !achievementsNode
    ) {
      return;
    }

    const history = safeJSON(
      localStorage.getItem(
        `${STORAGE_PREFIX}.history`
      ),
      []
    );

    // ----------------------------------------------------------
    // HISTORY
    // ----------------------------------------------------------

    if (historyNode) {
      historyNode.innerHTML =
        history.length
          ? history
              .slice(0, 5)
              .map((item) => {
                const date =
                  item.completedAt
                    ? new Date(
                        item.completedAt
                      ).toLocaleDateString()
                    : "Recently";

                return `
                  <div class="history-item">

                    <span class="history-icon">
                      ${item.passed ? "✓" : "↻"}
                    </span>

                    <div>
                      <strong>
                        Level ${item.level}
                      </strong>

                      <small>
                        ${date} · ${item.percentage}%
                      </small>
                    </div>

                    <span class="history-score">
                      ${item.score}/${item.total}
                    </span>

                  </div>
                `;
              })
              .join("")
          :
          `
            <div class="empty-history">
              Complete a quiz to see your real scores here.
            </div>
          `;
    }

    // ----------------------------------------------------------
    // ACHIEVEMENTS
    // ----------------------------------------------------------

    if (achievementsNode) {
      const completed =
        Number(
          window.QUIZ_DASHBOARD
            ?.completedCount || 0
        );

      const categories =
        new Set(
          history.flatMap(
            (item) =>
              item.correctCategories ||
              []
          )
        );

      const defs = [
        [
          "🏆",
          "First Quiz",
          "Complete your first quiz",
          history.length >= 1
        ],

        [
          "⭐",
          "Perfect Score",
          "Get 100% on a quiz",
          history.some(
            (x) =>
              x.percentage === 100
          )
        ],

        [
          "🎯",
          "5 Levels",
          "Complete five levels",
          completed >= 5
        ],

        [
          "👑",
          "Quiz Master",
          "Complete all 10 levels",
          completed >= 10
        ],

        [
          "🧠",
          "Knowledge Star",
          "Answer correctly in all categories",

          [
            "ABC & Words",
            "Numbers",
            "Colors & Shapes",
            "Animals",
            "General Knowledge"
          ].every(
            (category) =>
              categories.has(category)
          )
        ]
      ];

      achievementsNode.innerHTML =
        defs
          .map(
            ([
              icon,
              name,
              text,
              unlocked
            ]) => `
              <div class="achievement ${
                unlocked ? "" : "locked"
              }">

                <div class="achievement-icon">
                  ${icon}
                </div>

                <strong>
                  ${name}
                </strong>

                <small>
                  ${
                    unlocked
                      ? "Unlocked!"
                      : text
                  }
                </small>

              </div>
            `
          )
          .join("");
    }
  }

  // ============================================================
  // QUIZ LEVEL
  // ============================================================

  function initLevel() {
    const config =
      window.QUIZ_LEVEL_CONFIG;

    if (!config) {
      return;
    }

    wireMobileMenu();

    const baseQuestions =
      Array.isArray(config.questions)
        ? config.questions
        : [];

    if (!baseQuestions.length) {
      return;
    }

    const storageKey =
      getKey(config.level);

    let saved =
      config.restart
        ? null
        : safeJSON(
            localStorage.getItem(
              storageKey
            ),
            null
          );

    if (
      saved &&
      saved.completed
    ) {
      saved = null;
    }

    // ----------------------------------------------------------
    // RANDOMIZE QUESTIONS
    // ----------------------------------------------------------

    let questions =
      shuffle(baseQuestions).map(
        (question) => ({
          ...question,
          options: shuffle(
            question.options
          )
        })
      );

    // ----------------------------------------------------------
    // RESTORE STATE
    // ----------------------------------------------------------

    let answers =
      saved?.answers || {};

    let index =
      Number.isInteger(saved?.index)
        ? saved.index
        : 0;

    index = Math.max(
      0,
      Math.min(
        index,
        questions.length - 1
      )
    );

    let score =
      Object.keys(answers).filter(
        (id) => {
          const question =
            baseQuestions.find(
              (item) =>
                item.id === id
            );

          return (
            question &&
            answers[id] ===
              question.correctAnswer
          );
        }
      ).length;

    const answeredThisView =
      new Set();

    let timerId = null;
    let secondsLeft = 0;

    if (config.restart) {
      localStorage.removeItem(
        storageKey
      );
    }

    // ----------------------------------------------------------
    // DOM ELEMENTS
    // ----------------------------------------------------------

    const qNumber =
      document.getElementById(
        "question-number"
      );

    const qTotal =
      document.getElementById(
        "question-total"
      );

    const qText =
      document.getElementById(
        "question-text"
      );

    const qCategory =
      document.getElementById(
        "question-category"
      );

    const qIllustration =
      document.getElementById(
        "question-illustration"
      );

    const qHelp =
      document.getElementById(
        "question-help"
      );

    const grid =
      document.getElementById(
        "answer-grid"
      );

    const next =
      document.getElementById(
        "next-btn"
      );

    const previous =
      document.getElementById(
        "previous-btn"
      );

    const progress =
      document.getElementById(
        "question-progress"
      );

    const scoreIndicator =
      document.getElementById(
        "score-indicator"
      );

    const feedback =
      document.getElementById(
        "answer-feedback"
      );

    const pips =
      document.getElementById(
        "question-pips"
      );

    const timerWrap =
      document.getElementById(
        "timer-wrap"
      );

    const timer =
      document.getElementById(
        "timer"
      );

    qTotal.textContent =
      questions.length;

    // ----------------------------------------------------------
    // SAVE PROGRESS
    // ----------------------------------------------------------

    function persist() {
      localStorage.setItem(
        storageKey,
        JSON.stringify({
          level: config.level,
          index,
          answers,
          total: questions.length,
          completed: false,
          updatedAt: Date.now()
        })
      );
    }

    // ----------------------------------------------------------
    // TIMER
    // ----------------------------------------------------------

    function clearTimer() {
      if (timerId) {
        window.clearInterval(
          timerId
        );
      }

      timerId = null;
    }

    function startTimer() {
      clearTimer();

      const limit =
        config.level >= 10
          ? 45
          : config.level >= 8
          ? 60
          : 0;

      if (!limit) {
        if (timerWrap) {
          timerWrap.hidden = true;
        }

        return;
      }

      if (timerWrap) {
        timerWrap.hidden = false;
      }

      secondsLeft = limit;

      if (timer) {
        timer.textContent =
          secondsLeft;
      }

      timerId =
        window.setInterval(
          () => {
            secondsLeft -= 1;

            if (timer) {
              timer.textContent =
                secondsLeft;
            }

            if (timerWrap) {
              timerWrap.classList.toggle(
                "urgent",
                secondsLeft <= 10
              );
            }

            if (
              secondsLeft <= 0
            ) {
              clearTimer();

              toast(
                "Time's up! Let's keep learning. ⭐"
              );

              if (
                index <
                questions.length - 1
              ) {
                index += 1;

                persist();

                render();
              } else {
                finishQuiz();
              }
            }
          },
          1000
        );
    }

    // ----------------------------------------------------------
    // QUESTION PIPS
    // ----------------------------------------------------------

    function renderPips() {
      if (!pips) {
        return;
      }

      pips.innerHTML = "";

      questions.forEach(
        (question, i) => {
          const pip =
            document.createElement(
              "button"
            );

          pip.type = "button";

          pip.className =
            "question-pip";

          if (i === index) {
            pip.classList.add(
              "current"
            );
          }

          if (
            answers[question.id]
          ) {
            pip.classList.add(
              "answered"
            );
          }

          pip.textContent =
            String(i + 1);

          pip.setAttribute(
            "aria-label",
            `Go to question ${i + 1}`
          );

          pip.addEventListener(
            "click",
            () => {
              index = i;

              persist();

              render();
            }
          );

          pips.appendChild(pip);
        }
      );
    }

    // ==========================================================
    // RENDER QUESTION
    // ==========================================================

    function render(
      resetTimer = true
    ) {
      const question =
        questions[index];

      const selected =
        answers[question.id];

      const isAnswered =
        selected !== undefined;

      const percent =
        Math.round(
          ((index + 1) /
            questions.length) *
            100
        );

      if (qNumber) {
        qNumber.textContent =
          index + 1;
      }

      if (qText) {
        qText.textContent =
          question.question;
      }

      if (qCategory) {
        qCategory.textContent =
          question.category;
      }

      if (qIllustration) {
        qIllustration.textContent =
          question.emoji ||
          "🧠";
      }

      if (qHelp) {
        qHelp.textContent =
          isAnswered
            ? "Your answer is saved. You can change it before finishing."
            : "Choose one answer.";
      }

      if (progress) {
        progress.style.width =
          `${percent}%`;
      }

      if (scoreIndicator) {
        scoreIndicator.textContent =
          score;
      }

      if (previous) {
        previous.disabled =
          index === 0;
      }

      if (next) {
        next.disabled =
          !isAnswered;

        next.innerHTML =
          index ===
          questions.length - 1
            ? 'Finish Quiz <span>✓</span>'
            : 'Next <span>→</span>';
      }

      if (feedback) {
        feedback.className =
          "answer-feedback";

        feedback.textContent =
          "";
      }

      if (grid) {
        grid.innerHTML = "";
      }

      question.options.forEach(
        (
          option,
          optionIndex
        ) => {
          const button =
            document.createElement(
              "button"
            );

          button.type = "button";

          button.className =
            "answer-option";

          button.setAttribute(
            "role",
            "radio"
          );

          button.setAttribute(
            "aria-checked",
            String(
              selected === option
            )
          );

          button.tabIndex = 0;

          if (
            selected === option
          ) {
            button.classList.add(
              "selected"
            );
          }

          const letter =
            document.createElement(
              "span"
            );

          letter.className =
            "option-letter";

          letter.textContent =
            String.fromCharCode(
              65 + optionIndex
            );

          const label =
            document.createElement(
              "span"
            );

          label.className =
            "option-text";

          label.textContent =
            option;

          const mark =
            document.createElement(
              "span"
            );

          mark.className =
            "option-check";

          mark.textContent =
            selected === option
              ? "✓"
              : "";

          button.append(
            letter,
            label,
            mark
          );

          // ----------------------------------------------------
          // SELECT ANSWER
          // ----------------------------------------------------

          const choose = () => {
            const wasCorrect =
              answers[
                question.id
              ] ===
              question.correctAnswer;

            const isCorrect =
              option ===
              question.correctAnswer;

            answers[
              question.id
            ] = option;

            // Correct answer changed from wrong/unanswered
            if (
              !wasCorrect &&
              isCorrect
            ) {
              score += 1;
            }

            // Correct answer changed to wrong
            if (
              wasCorrect &&
              !isCorrect
            ) {
              score -= 1;
            }

            answeredThisView.add(
              question.id
            );

            persist();

            render(false);

            if (feedback) {
              feedback.classList.add(
                isCorrect
                  ? "correct"
                  : "learning"
              );

              feedback.textContent =
                isCorrect
                  ? `Correct! ${question.explanation}`
                  : `Not quite. ${question.explanation}`;
            }
          };

          button.addEventListener(
            "click",
            choose
          );

          button.addEventListener(
            "keydown",
            (event) => {
              if (
                event.key ===
                  "Enter" ||
                event.key === " "
              ) {
                event.preventDefault();

                choose();
              }
            }
          );

          grid?.appendChild(
            button
          );
        }
      );

      // --------------------------------------------------------
      // RESTORE FEEDBACK
      // --------------------------------------------------------

      if (
        isAnswered &&
        answeredThisView.has(
          question.id
        ) &&
        feedback
      ) {
        feedback.classList.add(
          selected ===
            question.correctAnswer
            ? "correct"
            : "learning"
        );

        feedback.textContent =
          selected ===
          question.correctAnswer
            ? `Correct! ${question.explanation}`
            : `Not quite. ${question.explanation}`;
      }

      renderPips();

      if (resetTimer) {
        startTimer();
      }
    }

    // ==========================================================
    // PREVIOUS
    // ==========================================================

    function goPrevious() {
      if (index === 0) {
        return;
      }

      index -= 1;

      persist();

      render();
    }

    // ==========================================================
    // NEXT
    // ==========================================================

    function goNext() {
      const question =
        questions[index];

      if (
        answers[question.id] ===
        undefined
      ) {
        toast(
          "Please choose an answer first! 😊"
        );

        return;
      }

      if (
        index ===
        questions.length - 1
      ) {
        finishQuiz();

        return;
      }

      index += 1;

      persist();

      render();
    }

    // ==========================================================
    // FINISH QUIZ
    // ==========================================================

    async function finishQuiz() {
      clearTimer();

      if (next) {
        next.disabled = true;
      }

      if (previous) {
        previous.disabled = true;
      }

      if (qHelp) {
        qHelp.textContent =
          "Saving your real score…";
      }

      persist();

      try {
        const response =
          await fetch(
            config.submitUrl,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",

                "X-CSRFToken":
                  csrfToken(),

                "X-Requested-With":
                  "XMLHttpRequest"
              },

              body: JSON.stringify({
                answers
              }),

              credentials:
                "same-origin"
            }
          );

        const data =
          await response.json();

        if (
          !response.ok ||
          !data.ok
        ) {
          throw new Error(
            data.error ||
              "Could not save the quiz."
          );
        }

        // Remove unfinished state
        localStorage.removeItem(
          storageKey
        );

        // ------------------------------------------------------
        // CATEGORY HISTORY
        // ------------------------------------------------------

        const correctCategories =
          questions
            .filter(
              (question) =>
                answers[
                  question.id
                ] ===
                question.correctAnswer
            )
            .map(
              (question) =>
                question.category
            );

        // ------------------------------------------------------
        // HISTORY
        // ------------------------------------------------------

        const history =
          safeJSON(
            localStorage.getItem(
              `${STORAGE_PREFIX}.history`
            ),
            []
          );

        history.unshift({
          level: config.level,

          score: data.score,

          total: data.total,

          percentage:
            data.percentage,

          passed:
            data.passed,

          correctCategories:
            Array.from(
              new Set(
                correctCategories
              )
            ),

          completedAt:
            Date.now()
        });

        localStorage.setItem(
          `${STORAGE_PREFIX}.history`,
          JSON.stringify(
            history.slice(
              0,
              20
            )
          )
        );

        // ------------------------------------------------------
        // RESULT PAGE
        // ------------------------------------------------------

        window.location.href =
          data.result_url;

      } catch (error) {
        if (next) {
          next.disabled = false;
        }

        if (previous) {
          previous.disabled =
            index === 0;
        }

        if (qHelp) {
          qHelp.textContent =
            "We could not save the quiz yet. Please try again.";
        }

        toast(
          error.message ||
            "Please try again."
        );
      }
    }

    // ----------------------------------------------------------
    // BUTTON EVENTS
    // ----------------------------------------------------------

    previous?.addEventListener(
      "click",
      goPrevious
    );

    next?.addEventListener(
      "click",
      goNext
    );

    // ----------------------------------------------------------
    // PRESERVE SAVED QUESTIONS
    // ----------------------------------------------------------

    if (saved) {
      const savedIds =
        new Set(
          Object.keys(
            saved.answers || {}
          )
        );

      questions.sort(
        (a, b) => {
          const aSaved =
            savedIds.has(a.id)
              ? 0
              : 1;

          const bSaved =
            savedIds.has(b.id)
              ? 0
              : 1;

          return (
            aSaved - bSaved
          );
        }
      );
    }

    // Initial render
    render();
  }

  // ============================================================
  // DOM READY
  // ============================================================

  document.addEventListener(
    "DOMContentLoaded",
    function () {
      initDashboard();
      initLevel();
      wireMobileMenu();
    }
  );

})();