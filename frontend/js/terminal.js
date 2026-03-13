const terminal = document.getElementById('terminal-content');
const logs = [
    "Scanning network environment...",
    "Gateway handshake: SUCCESS",
    "Initializing Dynamic Token Generator...",
    "System Status: SECURE - Ready for Session",
];

let i = 0;
function typeLog() {
    if (i < logs.length) {
        const p = document.createElement("p");
        p.className = "mt-1";
        p.innerHTML = `<span class="text-white">[OK]</span> ${logs[i]}`;
        terminal.appendChild(p);
        i++;
        setTimeout(typeLog, 1200);
    }
}
window.onload = typeLog;
