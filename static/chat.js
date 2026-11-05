
// Select HTML elements
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = form.querySelector("button");

// Handle form submission
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = input.value.trim();

    // Ignore empty messages
    if (message === "") {
        return;
    }

    // Display user message
    addMessage(message, "user");

    // Clear input
    input.value = "";

    // Disable input while waiting
    input.disabled = true;
    sendButton.disabled = true;

    // Display loading message
    const loadingMessage = addMessage("Typing...", "bot");

    try {
        // Send message to Flask backend
        const response = await fetch("/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        });

        // Parse the server response
        const data = await response.json();

        // Check for API or server errors
        if (!response.ok) {
            throw new Error(
                data.error || "Unable to get an AI response."
            );
        }

        // Remove loading message
        loadingMessage.remove();

        // Display AI response
        addMessage(
            data.reply || "Sorry, I could not generate a response.",
            "bot"
        );

    } catch (error) {

        // Remove loading message
        loadingMessage.remove();

        // Display error message
        addMessage(
            error.message || "Something went wrong. Please try again.",
            "bot"
        );

        console.error("Chatbot error:", error);

    } finally {

        // Enable input again
        input.disabled = false;
        sendButton.disabled = false;

        // Return focus to input
        input.focus();
    }
});


// Function to display messages
function addMessage(text, sender) {

    // Create message container
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", `${sender}-message`);

    // Create avatar
    const avatar = document.createElement("div");
    avatar.classList.add("avatar");

    avatar.textContent = sender === "user" ? "👤" : "🤖";

    // Create message content container
    const content = document.createElement("div");
    content.classList.add("message-content");

    // Create sender name
    const name = document.createElement("span");
    name.classList.add("sender");

    name.textContent = sender === "user"
        ? "You"
        : "AI Assistant";

    // Create message text
    const paragraph = document.createElement("p");
    paragraph.textContent = text;

    // Assemble message
    content.appendChild(name);
    content.appendChild(paragraph);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    // Add message to chat window
    chatBox.appendChild(messageDiv);

    // Scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageDiv;
}
