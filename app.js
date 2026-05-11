// State
let state = {
    isLoggedIn: false,
    user: null,
    currentChat: [],
    history: [],
    model: "mistralai/mistral-7b-instruct"
};

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const authTrigger = document.getElementById('auth-trigger');
const authModal = document.getElementById('auth-modal');
const closeModal = document.querySelector('.close-modal');
const toggleAuth = document.getElementById('toggle-auth');
const authTitle = document.getElementById('auth-title');
const authSubmit = document.getElementById('auth-submit');

// --- UI Actions ---

function setInput(text) {
    userInput.value = text;
    userInput.focus();
}

// Toggle Auth Modal
authTrigger.onclick = () => authModal.style.display = 'flex';
closeModal.onclick = () => authModal.style.display = 'none';
window.onclick = (e) => { if (e.target == authModal) authModal.style.display = 'none'; };

// Toggle Login/Register
let isLoginView = true;
toggleAuth.onclick = () => {
    isLoginView = !isLoginView;
    authTitle.textContent = isLoginView ? "Login" : "Sign Up";
    authSubmit.textContent = isLoginView ? "Continue" : "Create Account";
    toggleAuth.textContent = isLoginView ? "Sign up" : "Login";
};

// --- Chat Logic ---

function appendMessage(role, content) {
    const welcome = document.querySelector('.welcome-screen');
    if (welcome) welcome.remove();

    const msgDiv = document.createElement('div');
    msgDiv.className = `message-bubble ${role}`;
    
    // Simple markdown-like line breaks
    msgDiv.innerHTML = `<div class="content">${content.replace(/\n/g, '<br>')}</div>`;
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return msgDiv;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';
    
    const aiMsgDiv = appendMessage('ai', '<span class="typing">Thinking...</span>');

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: text,
                model: state.model,
                history: state.currentChat
            })
        });

        const data = await response.json();
        const aiResponse = data.choices[0].message.content;
        
        aiMsgDiv.innerHTML = `<div class="content">${aiResponse.replace(/\n/g, '<br>')}</div>`;
        
        state.currentChat.push({ role: "user", content: text });
        state.currentChat.push({ role: "assistant", content: aiResponse });

        // Auto-detect Excel request in AI response for demo
        if (aiResponse.toLowerCase().includes("excel") || aiResponse.toLowerCase().includes("report")) {
            addDownloadButton(aiMsgDiv, text);
        }

    } catch (error) {
        aiMsgDiv.innerHTML = `<span style="color: #FF6363">Error: ${error.message}</span>`;
    }
}

function addDownloadButton(container, context) {
    const btn = document.createElement('button');
    btn.className = 'primary-btn download-btn';
    btn.innerHTML = '<i data-lucide="download"></i> Download Excel Report';
    btn.style.marginTop = '12px';
    btn.onclick = async () => {
        // In a real app, the AI would provide JSON. For demo, we send mock data.
        const mockData = [
            { "Item": "Rent", "Amount": 50000, "Category": "Fixed" },
            { "Item": "Salary", "Amount": 150000, "Category": "Fixed" },
            { "Item": "Marketing", "Amount": 15000, "Category": "Marketing" }
        ];
        
        const response = await fetch("/api/generate-excel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ data: mockData, filename: "Business_Report.xlsx" })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "Business_Report.xlsx";
        document.body.appendChild(a);
        a.click();
        a.remove();
    };
    container.appendChild(btn);
    lucide.createIcons();
}

// Event Listeners
sendBtn.onclick = sendMessage;
userInput.onkeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
};

// Auto-resize
userInput.oninput = () => {
    userInput.style.height = 'auto';
    userInput.style.height = (userInput.scrollHeight) + 'px';
};
