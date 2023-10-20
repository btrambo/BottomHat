// function deleteMessage(messageId) {
//     const request = new XMLHttpRequest();
//     request.onreadystatechange = function () {
//         if (this.readyState === 4 && this.status === 200) {
//             console.log(this.response);
//         }
//     }
//     request.open("DELETE", "/chat-message/" + messageId);
//     request.send();
// }


function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const title = messageJSON.title;
    const message = messageJSON.message;
    let messageHTML = "<div class=\"card text-center\">" +
        "              <div class=\"card-header\">" +
        "                " + username + "" +
        "              </div>" +
        "              <div class=\"card-body\">" +
        "                <h5 class=\"card-title\">" + title + "</h5>" +
        "                <p class=\"card-text\">" + message + "</p>" +
        "                <i onclick=\"myFunction(this)\" class=\"fa fa-thumbs-up\"></i>" +
        "              </div>" +
        "              <div class=\"card-footer text-body-secondary\">" + "&nbsp;" +
        "              " +
        "              </div>" +
        "            </div><br>";
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("post-wrap");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("post-wrap");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    // chatMessages.scrollIntoView(false);
    // chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function sendChat() {
    const title = document.getElementById("exampleFormControlInput1");
    const message = document.getElementById("exampleFormControlTextarea1");
    const titleval = title.value;
    const messageval = message.value;
    title.value = "";
    message.value = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }

    const messageJSON = {"post-title": titleval, "post-message": messageval};
    console.log(messageJSON)
    request.open("POST", "/make-post");
    request.send(JSON.stringify(messageJSON));
    title.focus();
    message.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/post-history");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    document.getElementById("exampleFormControlInput1").focus();

    updateChat();
    setInterval(updateChat, 2000);
}