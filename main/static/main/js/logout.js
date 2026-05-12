/* ================= SESSION TIMER ================= */

// Simpan waktu login pertama (kalau belum ada)
if (!localStorage.getItem("loginTime")) {
    localStorage.setItem("loginTime", new Date().toISOString());
}

function formatDuration(ms) {
    let totalSeconds = Math.floor(ms / 1000);

    let hours = Math.floor(totalSeconds / 3600);
    let minutes = Math.floor((totalSeconds % 3600) / 60);
    let seconds = totalSeconds % 60;

    return `${hours}j ${minutes}m ${seconds}s`;
}

function updateSessionDuration() {
    let loginTime = new Date(localStorage.getItem("loginTime"));
    let now = new Date();

    let diff = now - loginTime;

    document.getElementById("sessionDuration").textContent = formatDuration(diff);
}

// update tiap detik
setInterval(updateSessionDuration, 1000);
updateSessionDuration();



/* ================= DEVICE DETECTION ================= */

function getDeviceInfo() {
    const ua = navigator.userAgent;

    let os = "Unknown OS";
    let browser = "Unknown Browser";

    // OS detect
    if (ua.includes("Windows NT 10")) os = "Windows 10/11";
    else if (ua.includes("Windows NT 6")) os = "Windows";
    else if (ua.includes("Mac")) os = "MacOS";
    else if (ua.includes("Android")) os = "Android";
    else if (ua.includes("iPhone")) os = "iOS";
    else if (ua.includes("Linux")) os = "Linux";

    // Browser detect
    if (ua.includes("Chrome")) browser = "Chrome";
    if (ua.includes("Firefox")) browser = "Firefox";
    if (ua.includes("Safari") && !ua.includes("Chrome")) browser = "Safari";
    if (ua.includes("Edge")) browser = "Edge";

    return `${os} · ${browser}`;
}

document.getElementById("deviceInfo").textContent = getDeviceInfo();



/* ================= LOGOUT ================= */

document.getElementById('btnConfirmLogout').addEventListener('click', function () {

    document.getElementById('logoutLoading').classList.add('show');

    setTimeout(function () {
        document.getElementById('logoutLoading').classList.remove('show');

        document.getElementById('logoutSuccess').classList.add('show');

        // 🔥 Hapus session waktu login
        localStorage.removeItem("loginTime");

        setTimeout(function () {
            window.location.href = "{% url 'login' %}";
        }, 3200);

    }, 1600);
});
