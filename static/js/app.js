(() => {
    const navToggle = document.querySelector(".nav-toggle");
    const nav = document.getElementById("main-nav");
    if (navToggle && nav) {
        navToggle.addEventListener("click", () => {
            const open = nav.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", String(open));
        });
    }

    document.querySelectorAll(".toast").forEach((toast) => {
        const close = toast.querySelector(".toast-close");
        if (close) close.addEventListener("click", () => toast.remove());
        window.setTimeout(() => {
            toast.classList.add("toast-hide");
            window.setTimeout(() => toast.remove(), 260);
        }, 5200);
    });

    document.querySelectorAll(".btn, .choice-btn, .category-card, .lesson-card").forEach((element) => {
        element.addEventListener("pointerdown", () => element.classList.add("pressed"));
        element.addEventListener("pointerup", () => element.classList.remove("pressed"));
        element.addEventListener("pointerleave", () => element.classList.remove("pressed"));
    });

    const accountTabs = document.querySelectorAll("[data-account-tab]");
    const accountForms = document.querySelectorAll("[data-account-form]");
    if (accountTabs.length) {
        accountTabs.forEach((tab) => {
            tab.addEventListener("click", () => {
                const selected = tab.dataset.accountTab;
                accountTabs.forEach((item) => item.classList.toggle("active", item === tab));
                accountForms.forEach((form) => form.classList.toggle("hidden", form.dataset.accountForm !== selected));
            });
        });
    }

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    window.getCSRFToken = () => {
        if (csrfMeta && csrfMeta.content && csrfMeta.content !== "NOTPROVIDED") return csrfMeta.content;
        const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    };

    window.postJSON = async (url, payload = {}) => {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": window.getCSRFToken(),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            credentials: "same-origin",
            body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const error = new Error(data.error || "Request failed.");
            error.status = response.status;
            throw error;
        }
        return data;
    };
})();

