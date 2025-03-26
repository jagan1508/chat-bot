document.getElementById("chat-form").addEventListener("submit", async function(event) {
    event.preventDefault(); 
    
    const userInput = document.getElementById("user-input").value;
    const chatHistory = document.getElementById("chat-history");
    
    // Append user message
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user-message");
    userMessage.textContent = `You: ${userInput}`;
    chatHistory.appendChild(userMessage);
    
    document.getElementById("user-input").value = ""; 
    
    try {
        const response = await fetch("http://127.0.0.1/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: userInput })
        });
        
        if (!response.ok) throw new Error("Server error");
        
        const data = await response.json();
        
        const botMessage = document.createElement("div");
        botMessage.classList.add("message", "bot-message");
        botMessage.textContent = `Chatbot: ${data.answer}`;
        chatHistory.appendChild(botMessage);
    } catch (error) {
        const errorMessage = document.createElement("div");
        errorMessage.classList.add("message", "error-message");
        errorMessage.textContent = "Error: Unable to reach chatbot!";
        chatHistory.appendChild(errorMessage);
    }
    
    chatHistory.scrollTop = chatHistory.scrollHeight; 
});
