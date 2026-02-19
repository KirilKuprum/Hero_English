function scrollToForm() {
    const element = document.getElementById("form-section");
    if (element) {
        element.scrollIntoView({ 
            behavior: "smooth", 
            block: "start" 
        });
    }і
}
document.getElementById("application-form")
    .addEventListener("submit", async function (e) {

    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch("http://localhost:8000/apply", {
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
