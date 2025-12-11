const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const formatSelect = document.getElementById("formatStyle");
const scrollBtn = document.getElementById("scrollDownBtn");

let messages = [];
let sending = false;

/* Escape HTML */
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* Convert to bullets or numbered */
function convertToMarkdownList(text, style) {
  const rawLines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);

  if (rawLines.length > 1) {
    return rawLines
      .map((l, i) => (style === "numbered" ? `${i + 1}. ${l}` : `- ${l}`))
      .join("\n");
  }

  return rawLines[0] || "";
}

/* Render assistant message */
function renderAssistantHtml(text) {
  const style = formatSelect.value;
  let markdown = text;

  if (style !== "plain") {
    markdown = convertToMarkdownList(text, style);
  }

  try {
    const rawHtml = marked.parse(markdown);
    return DOMPurify.sanitize(rawHtml);
  } catch (err) {
    return escapeHtml(text).replace(/\n/g, "<br>");
  }
}

/* Add message bubble */
function appendMessage(role, content) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const roleEl = document.createElement("div");
  roleEl.className = "role";
  roleEl.textContent = role === "user" ? "You" : "AI";

  const contentEl = document.createElement("div");
  contentEl.className = "content";

  if (role === "assistant") {
    contentEl.innerHTML = renderAssistantHtml(content);
  } else {
    contentEl.innerHTML = escapeHtml(content).replace(/\n/g, "<br>");
  }

  wrapper.appendChild(roleEl);
  wrapper.appendChild(contentEl);
  chatWindow.appendChild(wrapper);

  wrapper.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/* Disable input while sending */
function setSending(state) {
  sending = state;
  userInput.disabled = state;
  chatForm.querySelector("button").disabled = state;
}

/* Auto-resize textarea */
function autosizeTextarea(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = textarea.scrollHeight + "px";
}

autosizeTextarea(userInput);

userInput.addEventListener("input", e => autosizeTextarea(e.target));

/* Enter to send */
userInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

/* Handle form submit */
chatForm.addEventListener("submit", async event => {
  event.preventDefault();
  if (sending) return;

  const text = userInput.value.trim();
  if (!text) return;

  appendMessage("user", text);
  messages.push({ role: "user", content: text });

  userInput.value = "";
  autosizeTextarea(userInput);
  userInput.focus();
  setSending(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages, format_style: formatSelect.value })
    });

    const data = await response.json();

    if (!response.ok) {
      appendMessage("assistant", "Error: " + data.error);
    } else {
      const reply = data.reply || "";
      messages = data.messages || messages;
      appendMessage("assistant", reply);
    }
  } catch (err) {
    appendMessage("assistant", "Network error: " + err.message);
  }

  setSending(false);
});

/* SCROLL TO BOTTOM BTN */
function isAtBottom() {
  return (
    chatWindow.scrollHeight -
      chatWindow.scrollTop -
      chatWindow.clientHeight <
    60
  );
}

/* Show/hide button */
chatWindow.addEventListener("scroll", () => {
  if (isAtBottom()) {
    scrollBtn.classList.remove("visible");
  } else {
    scrollBtn.classList.add("visible");
  }
});

/* Scroll on click */
scrollBtn.addEventListener("click", () => {
  chatWindow.scrollTo({
    top: chatWindow.scrollHeight,
    behavior: "smooth"
  });
});

/* Auto-hide when a new message appears */
const observer = new MutationObserver(() => {
  if (isAtBottom()) {
    scrollBtn.classList.remove("visible");
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
});

observer.observe(chatWindow, { childList: true });
