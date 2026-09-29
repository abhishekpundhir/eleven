const orbWrap = document.getElementById("orbWrap");
const conversation = document.getElementById("conversation");
const sparkleContainer = document.getElementById("sparkleContainer");


// ============================================================
// PHOENIX UI
// ============================================================

window.PhoenixUI = {

    setState(state) {

        if (!orbWrap) return;

        orbWrap.classList.remove(
            "idle",
            "listening",
            "thinking",
            "speaking"
        );

        orbWrap.classList.add(
            state
        );

        const labels = {

            idle: "Operational",

            listening: "Listening...",

            thinking: "Thinking...",

            speaking: "Speaking..."

        };

        const status =
            document.getElementById("status");

        if (status) {

            status.textContent =
                labels[state] || "Phoenix";

        }
    },


    setConversation(text) {

        if (!conversation) return;

        conversation.textContent =
            text || "";
    }
};


// ============================================================
// BACKGROUND SPARKLES
// ============================================================

function createSparkles() {

    if (!sparkleContainer) return;

    for (
        let i = 0;
        i < 50;
        i++
    ) {

        const sparkle =
            document.createElement("span");

        sparkle.className =
            "sparkle";

        sparkle.style.left =
            `${Math.random() * 100}%`;

        sparkle.style.top =
            `${Math.random() * 100}%`;

        sparkle.style.animationDelay =
            `${Math.random() * 5}s`;

        sparkleContainer.appendChild(
            sparkle
        );
    }
}


createSparkles();