function scrollToForm() {
    document.getElementById("form-section")
        .scrollIntoView({ behavior: "smooth" });
}

document.getElementById("application-form")
    .addEventListener("submit", async function (e) {

    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch("https://hero-english.onrender.com/apply", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        alert(result.message);
        document.getElementById("response-message").textContent = result.message;
        this.reset();

    } catch (err) {
        document.getElementById("response-message").textContent =
            "Error submitting the application.";
    }
});
