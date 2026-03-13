// Student attendance submission handler

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("attendance-form");

    if (!form) return;

    form.addEventListener("submit", async function(e) {

        e.preventDefault();

        const name = document.getElementById("name").value.trim();
        const roll = document.getElementById("roll").value.trim();

        const token = document.getElementById("token").value;

        if (!name || !roll) {
            alert("Please fill all fields.");
            return;
        }

        try {

            const response = await fetch(
                "https://lpaf-hackamongus.onrender.com/submit_attendance",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: name,
                        roll: roll,
                        token: token
                    })
                }
            );

            const result = await response.text();

            if (response.ok) {
                window.location.href = "/success.html";
            } else {
                alert(result);
            }

        } catch (error) {
            console.error(error);
            alert("Network error. Please try again.");
        }

    });

});
