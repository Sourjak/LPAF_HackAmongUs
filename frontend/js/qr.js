// QR Scanner UI Animation
// Adds a moving laser effect to simulate scanning

export function initScannerUI() {

    const qrContainer = document.querySelector('.qr-wrapper');

    if (!qrContainer) return;

    // Prevent duplicate lasers if function runs twice
    if (qrContainer.querySelector('.scanner-laser')) return;

    const laser = document.createElement('div');
    laser.className = 'scanner-laser';

    qrContainer.appendChild(laser);

    // Optional: Add glow effect animation
    laser.style.animation = "scan 2s linear infinite";
}
