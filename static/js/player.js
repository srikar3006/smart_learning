(() => {
    const config = window.RHYME_CONFIG;
    if (!config) return;

    const media = document.getElementById("rhyme-media");
    const iframe = document.getElementById("rhyme-media-frame");
    const repeatBtn = document.getElementById("repeat-btn");
    const voiceBtn = document.getElementById("voice-btn");
    const completeBtn = document.getElementById("complete-btn");
    const repeatCount = document.getElementById("repeat-count");
    const sideRepeat = document.getElementById("side-repeat");
    const status = document.getElementById("complete-status");
    const fallback = document.getElementById("fallback-stage");
    let playLogged = false;
    let speaking = false;

    const notify = (message, kind = "success") => {
        const stack = document.querySelector(".toast-stack") || (() => {
            const el = document.createElement("div");
            el.className = "toast-stack";
            document.body.appendChild(el);
            return el;
        })();
        const toast = document.createElement("div");
        toast.className = `toast toast-${kind}`;
        toast.innerHTML = `<span class="toast-icon">${kind === "success" ? "✓" : "!"}</span><span>${message}</span><button class="toast-close" type="button">×</button>`;
        toast.querySelector(".toast-close").onclick = () => toast.remove();
        stack.appendChild(toast);
        setTimeout(() => toast.remove(), 4200);
    };

    const logPlay = async () => {
        if (playLogged) return;
        playLogged = true;
        try {
            const data = await window.postJSON(config.logPlayUrl);
            if (data.completed && status) status.textContent = "Completed";
            if (data.new_badges?.length) notify(`New badge: ${data.new_badges.join(", ")}`);
        } catch (error) {
            playLogged = false;
        }
    };

    if (media) {
        media.addEventListener("ended", logPlay);
        media.addEventListener("timeupdate", () => {
            const frame = document.getElementById("audio-stage");
            if (frame) frame.style.setProperty("--audio-progress", `${(media.currentTime / Math.max(media.duration || 1, 1)) * 100}%`);
        });
    }

    if (repeatBtn) {
        repeatBtn.addEventListener("click", async () => {
            try {
                if (media) {
                    media.currentTime = 0;
                    await media.play();
                } else if (iframe) {
                    iframe.src = iframe.src;
                } else if (window.speechSynthesis && fallback) {
                    window.speechSynthesis.cancel();
                    speakFallback();
                }
                const data = await window.postJSON(config.logRepeatUrl);
                if (repeatCount) repeatCount.textContent = data.repeat_count;
                if (sideRepeat) sideRepeat.textContent = data.repeat_count;
                repeatBtn.classList.add("pulse");
                setTimeout(() => repeatBtn.classList.remove("pulse"), 450);
            } catch (error) {
                notify(error.message, "error");
            }
        });
    }

    const speakFallback = () => {
        if (!fallback || !window.speechSynthesis) {
            notify("Voice mode is not supported by this browser.", "error");
            return;
        }
        const text = fallback.dataset.lyrics || "";
        if (!text.trim()) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.82;
        utterance.pitch = 1.08;
        utterance.onstart = () => {
            speaking = true;
            fallback.classList.add("speaking");
            if (voiceBtn) voiceBtn.textContent = "■ Stop listening";
        };
        utterance.onend = async () => {
            speaking = false;
            fallback.classList.remove("speaking");
            if (voiceBtn) voiceBtn.textContent = "▶ Listen to rhyme";
            await logPlay();
        };
        window.speechSynthesis.speak(utterance);
    };

    if (voiceBtn) {
        voiceBtn.addEventListener("click", () => {
            if (speaking) {
                window.speechSynthesis.cancel();
                speaking = false;
                fallback?.classList.remove("speaking");
                voiceBtn.textContent = "▶ Listen to rhyme";
            } else {
                speakFallback();
            }
        });
    }

    if (completeBtn) {
        completeBtn.addEventListener("click", async () => {
            completeBtn.disabled = true;
            try {
                const data = await window.postJSON(config.markCompleteUrl);
                if (data.completed) {
                    completeBtn.textContent = "✓ Completed";
                    if (status) status.textContent = "Completed";
                    notify("Lesson marked as learned. Great work! ✨");
                }
            } catch (error) {
                completeBtn.disabled = false;
                notify(error.message, "error");
            }
        });
    }
})();

