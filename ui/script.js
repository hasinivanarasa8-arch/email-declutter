async function nextEmail() {
    const res = await fetch("http://127.0.0.1:5000/next");
    const data = await res.json();

    document.getElementById("subject").innerText = data.subject;
    document.getElementById("email-text").innerText = data.email_text;
    document.getElementById("sender").innerText = data.sender;

    const predictionElement = document.getElementById("prediction");

    predictionElement.innerText = "Predicted: " + data.prediction;

    // Remove previous classes
    predictionElement.className = "";

    // Add color class
    predictionElement.classList.add(data.prediction);
}