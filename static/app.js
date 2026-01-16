// =====================
// Dare-Roulette App Logic
// =====================

// -------- DARES --------
const dares = [
    "Do 20 pushups right now",
    "Sing your favorite song",
    "Dance for 30 seconds",
    "Tell a joke",
    "Do 10 jumping jacks",
    "Show your room dramatically",
    "Act like a robot for 20 seconds",
    "Rap about your day",
    "Do your best animal impression"
];

// -------- STATE --------
let currentDare = null;
let isSpinning = false;

// -------- SPIN WHEEL --------
function spinWheel() {
    if (isSpinning) return;

    const wheel = document.getElementById("wheel");
    const dareText = document.getElementById("dareText");

    isSpinning = true;
    wheel.classList.add("spin-animation");

    setTimeout(() => {
        wheel.classList.remove("spin-animation");

        currentDare = dares[Math.floor(Math.random() * dares.length)];
        dareText.innerText = "🎯 " + currentDare;

        isSpinning = false;
    }, 3000);
}

// -------- UPLOAD (FRONTEND ONLY DEMO) --------
document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector("input[type=’file’]");

    if (!fileInput) return;

    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];

        if (!file) return;

        if (!file.type.startsWith("video/")) {
            alert("Please upload a video 📹");
            fileInput.value = "";
            return;
        }

        if (!currentDare) {
            alert("Spin & accept a dare first 🎡");
            fileInput.value = "";
            return;
        }

        console.log("Selected video:", file.name);
        console.log("For dare:", currentDare);
    });
});

// -------- UTILS --------
function formatNumber(num) {
    if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
    if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
    return num;
}
