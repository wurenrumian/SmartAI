async function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    const identity = document.getElementById('identity').value;
    const gender = document.getElementById('gender').value;
    const familyBackground = document.getElementById('familyBackground').value;
    const priorBackground = document.getElementById('priorBackground').value;

    const chatBox = document.getElementById('chatBox');
    chatBox.innerHTML += `<div class="message user-message"><strong>你:</strong> ${userInput}</div>`;

    const response = await fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            userInput,
            identity,
            gender,
            familyBackground,
            priorBackground
        }),
    });

    const data = await response.json();
    chatBox.innerHTML += `<div class="message ai-message"><strong>AI:</strong> ${data.response}</div>`;

    // 清空用户输入
    document.getElementById('userInput').value = '';
    
    // 滚动到底部
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 添加回车键发送消息的功能
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});