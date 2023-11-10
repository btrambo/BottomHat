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

let theInterval = 0;
function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const title = messageJSON.title;
    const message = messageJSON.message;
    const likes = messageJSON.likes;
    const postid = messageJSON.id;
    // let messageHTML = "<div class=\"card text-center\">" +
    //     "              <div class=\"card-header\">" +
    //     "                " + username + "" +
    //     "              </div>" +
    //     "              <div class=\"card-body\">" +
    //     "                <h5 class=\"card-title\">" + title + "</h5>" +
    //     "                <p class=\"card-text\">" + message + "</p>" +
    //     "                <i onclick=\"clickFunction(" + postid + ")\" class=\"fa fa-thumbs-up\"> " + likes + "</i>" +
    //     "              </div>" +
    //     "              <div class=\"card-footer text-body-secondary\">" + "&nbsp;" +
    //     "              " +
    //     "              </div>" +
    //     "            </div><br>";

        let messageHTML = "<div class=\"card text-center\">" +
        "              <div class=\"card-header\">" +
        "                " + username + "" +
        "              </div>" +
        "              <div class=\"card-body\">" +
        "                <h5 class=\"card-title\">" + title + "</h5>" +
        "                <p class=\"card-text\">" + message + "</p>" +
        "<svg viewBox=\"0 0 130.000 130.000\" onclick=\"clickFunction(" + postid + ")\"    xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n" +
            "   xmlns:cc=\"http://creativecommons.org/ns#\"\n" +
            "   xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"\n" +
            "   xmlns:svg=\"http://www.w3.org/2000/svg\"\n" +
            "   xmlns=\"http://www.w3.org/2000/svg\"\n" +
            "   version=\"1.1\"\n" +

            "   id=\"svg2\">\n" +
            "  <defs\n" +
            "     id=\"defs8\" />\n" +
            "  <path\n" +
            "     d=\"M 65,29 C 59,19 49,12 37,12 20,12 7,25 7,42 7,75 25,80 65,118 105,80 123,75 123,42 123,25 110,12 93,12 81,12 71,19 65,29 z\"\n" +
            "     id=\"path4\"\n" +
            "     style=\"\" />\n" +
            "</svg>" + "&nbsp;<span style=\"font-size: 20px; color: darkred;\">" + likes + "</span>" +
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

function clickFunction(idd) {
    clearInterval(theInterval);
    const request = new XMLHttpRequest();

        request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            welcome()
        }
    }
    request.open("POST", "/like");
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(idd));
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

function seeGrades(currentelement) {

    const qcard = currentelement.closest(".card");
    const qcontent = currentelement.closest(".card").firstChild.nextElementSibling;
    const gcontent = qcontent.nextElementSibling;
    const qtext = currentelement.firstChild;
    const gtext = qtext.nextSibling;


    if (qcontent.style.display != "none") {
        qcontent.style.display = "none";
        qtext.style.display = "none";
        gtext.style.cssText = "display:block !important";
        gcontent.style.display = "flex";
        qcard.style.cssText = "background-color:darkred !important";

    }
    else {
        qcontent.style.display = "block";
        gcontent.style.display = "none";
        qtext.style.display = "block";
        gtext.style.cssText = "display:none !important";
        qcard.style.background = "#282828";}

}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    document.getElementById("exampleFormControlInput1").focus();

    updateChat();
    theInterval = setInterval(updateChat, 2000);
}