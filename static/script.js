const chatBoxIcon = document.getElementById('chatbox-btn-wrapper')
const chatBoxCloseBtn = document.querySelector('#chatbox .chatbox-close')
var chatBoxWrapper = document.getElementById('chatbox')
var chatBoxTextField = document.getElementById('chatbox-message-field')
var chatBoxSendMessage = document.getElementById('chatbox-send-btn')
var chatboxBody = document.querySelector(".chatbox-body")
const optionsContainer = document.getElementById('chatbox-options');
var resizeHandle = document.getElementById("resize_handler");

var nav_options = JSON.parse(nav)
var events_options = JSON.parse(eve)

function loadNavOptions(){
    nav_options.sort((a, b) => {
        if (a.faculty < b.faculty) return -1;
        if (a.faculty > b.faculty) return 1;
        if (a.block < b.block) return -1;
        if (a.block > b.block) return 1;
        // Extract the last character of the 'floor' string and convert it to a number
        var aFloorNumber = Number(a.floor.slice(-1));
        var bFloorNumber = Number(b.floor.slice(-1));
        return aFloorNumber - bFloorNumber;
    });
    displayNavOptions(nav_options)
}

function displayNavOptions(OPTIONS){
    // Display the sorted options in the chatbox-options div
    optionsContainer.style.display = 'block';

    chatBoxTextField.oninput = filterNavOptions;

    optionsContainer.innerHTML = ''; // Clear existing options

    // Generate the HTML structure with styles
    let currentFaculty = '';
    let currentBlock = '';
    let currentFloor = 0;
    let html = '';
    nav_options.forEach(option => {
        if (option.faculty !== currentFaculty) {
            if (currentFaculty !== '') {
                html += '</details></details></details>'; // Close previous floor, block, and faculty
            }
            html += `<details open><summary>${option.faculty}</summary><details open><summary> Block ${option.block}</summary><details open><summary> Floor ${option.floor} </summary>`;
            currentFaculty = option.faculty;
            currentBlock = option.block;
            currentFloor = option.floor;
        } else if (option.block !== currentBlock) {
            html += '</details></details>'; // Close previous floor and block
            html += `<details open><summary>Block ${option.block}</summary><details open><summary> Floor ${option.floor} </summary>`;
            currentBlock = option.block;
            currentFloor = option.floor;
        } else if (option.floor !== currentFloor) {
            html += '</details>'; // Close previous floor
            html += `<details open><summary>Floor ${option.floor}</summary>`;
            currentFloor = option.floor;
        }
        html += `<a class="room-button" onclick="selectOption('${option.faculty} \\nBlock ${option.block} \\nFloor ${option.floor} \\n ${option.room}')"> ${option.room} </a>`;
    });
    html += '</details></details></details>'; // Close last floor, block, and faculty

    // Append the generated HTML to the options container
    optionsContainer.innerHTML = html;

    // Add the "Return" button
    const returnButton = document.createElement('button');
    returnButton.className = "option-button return-button";
    returnButton.innerText = "Return";
    returnButton.onclick = goBack;
    optionsContainer.appendChild(returnButton);
}

function filterNavOptions() {
    // Get the current value of the text field
    let filterText = chatBoxTextField.value.toLowerCase();

    // Initially hide all details elements and room buttons
    document.querySelectorAll('details, .room-button').forEach(element => {
        element.style.display = 'none';
    });

    // Filter and show matching faculties, blocks, floors, and rooms
    document.querySelectorAll('details').forEach(details => {
        // Check if the current details element or any of its children match the filter text
        let textContent = details.textContent.toLowerCase();
        let summaryText = details.querySelector('summary').textContent.toLowerCase();

        // Show the details if the text content includes the filter text and it's a room button&& details.querySelector('.room-button')
        if (textContent.includes(filterText) ) {
            details.style.display = 'block';
        }

        if(details.style.display === 'block'){
            // Filter and show matching room buttons
            details.querySelectorAll('.room-button').forEach(button => {
                // Check if the current button's text matches the filter text
                let buttonText = button.textContent.toLowerCase();

                // Show the button if the button text includes the filter text
                if (buttonText.includes(filterText)) {
                    button.style.display = 'block';
                    button.closest('details').style.display = 'block';
                    button.closest('details').open = true;
                    button.closest('details').parentElement.open = true;
                    button.closest('details').parentElement.parentElement.open = true;
                }else{
                    if(summaryText.includes(filterText)){
                        button.style.display = 'block';
                        button.closest('details').style.display = 'block';
                        button.closest('details').open = true;
                        button.closest('details').parentElement.open = true;
                        button.closest('details').parentElement.parentElement.open = true;
                    }
                }
            });
        }

         // Show the details if the summary text includes the filter text
        if (summaryText.includes(filterText)) {
            details.style.display = 'block';
            showAllChildren(details);
        }
    });

    // Helper function to show all children details and buttons
    function showAllChildren(details) {
        Array.from(details.children).forEach(child => {
            if (child.tagName.toLowerCase() === 'details') {
                child.style.display = 'block';
                //showAllChildren(child); // Recursively show children
            }else if (child.classList.contains('room-button')) {
                child.style.display = 'block'; // Show room buttons
            }
        });
    }
}

function loadEventsOptions() {
    // After loading, sort the options by the time column
    events_options.sort((a, b) => new Date(a.time) - new Date(b.time));
    displayEventsOptions(events_options);
}

function displayEventsOptions(OPTIONS) {
    // Display the sorted options in the chatbox-options div
    optionsContainer.style.display = 'block';
    chatBoxTextField.oninput = filterEventsOptions;

    optionsContainer.innerHTML = ''; // Clear existing options
    OPTIONS.forEach(option => {
        const optionElement = document.createElement('button');
        optionElement.className = "option-button"
        optionElement.innerText = option.name; // Use other properties like time, venue, etc., as needed
        optionElement.onclick = () => selectOption(option.name);
        optionsContainer.appendChild(optionElement);
    });
    // Add the "Return" button
    const returnButton = document.createElement('button');
    returnButton.className = "option-button return-button";
    returnButton.innerText = "Return";
    returnButton.onclick = goBack;
    optionsContainer.appendChild(returnButton);
}

function goBack(){
    [].forEach.call(document.querySelectorAll('.chatbox-selection'), function (el) {
      el.style.display = 'flex'
    });
    chatBoxTextField.oninput = null;
    optionsContainer.style.display = 'none';
    setTimeout(function() {
        botResponse("return");
    }, 500);
}

function filterEventsOptions() {
    // Get the filter text from the textarea
    const filterText = chatBoxTextField.value.toLowerCase();
    // Filter the options based on the filter text
    const filteredOptions = events_options.filter(option => option.name.toLowerCase().includes(filterText));
    // Display the filtered options
    displayEventsOptions(filteredOptions);
}

function appendMessage(){
    // Get the user's message
    var message = chatBoxTextField.value;

    // Create a new div for the message
    var messageDiv = document.createElement('div');
    messageDiv.className = 'chatbox-item chatbox-msg-receiver';

    var userAvatar = document.createElement('div');
    userAvatar.className = 'chatbox-user-avatar';

    var span = document.createElement("SPAN");
    span.className = "material-symbols-outlined"
    span.innerText = "person"

    var contentWrapper = document.createElement('div');
    contentWrapper.className = "chatbox-item-content-wrapper"

    var content_span = document.createElement("SPAN");
    content_span.className = "chatbox-item-content"
    content_span.innerText = message;

    userAvatar.appendChild(span)
    contentWrapper.appendChild(content_span)

    // Append the message to the chat dialog
    messageDiv.appendChild(userAvatar)
    messageDiv.appendChild(contentWrapper)

    // Clear the input field
    chatBoxTextField.value = '';

    chatboxBody.prepend(messageDiv);
    messageDiv.scrollIntoView({ block: "start", behavior: "smooth" });
    setTimeout(function() {
        botResponse(message);
    }, 800);
}

// Chatbot Selection JavaScript
function selectOption(option) {
    [].forEach.call(document.querySelectorAll('.chatbox-selection'), function (el) {
      el.style.display = 'none'
    });
    // Create a new div for the message
    var messageDiv = document.createElement('div');
    messageDiv.className = 'chatbox-item chatbox-msg-receiver';

    var userAvatar = document.createElement('div');
    userAvatar.className = 'chatbox-user-avatar';

    var span = document.createElement("SPAN");
    span.className = "material-symbols-outlined"
    span.innerText = "person"

    var contentWrapper = document.createElement('div');
    contentWrapper.className = "chatbox-item-content-wrapper"

    var content_span = document.createElement("SPAN");
    content_span.className = "chatbox-item-content"
    content_span.innerText = option;

    userAvatar.appendChild(span)
    contentWrapper.appendChild(content_span)

    // Append the message to the chat dialog
    messageDiv.appendChild(userAvatar)
    messageDiv.appendChild(contentWrapper)

    // Clear the input field
    chatBoxTextField.value = '';

    chatboxBody.prepend(messageDiv);
    messageDiv.scrollIntoView({ block: "start", behavior: "smooth" });

    setTimeout(function() {
        botResponse(option);
        if(option === "Events"){
            loadEventsOptions();
        }else if(option === "Navigation"){
            loadNavOptions()
        }
    }, 500);
}

function isDataUrl(s) {
    return /^data:image\/\w+;base64,/.test(s);
}

function botResponse(userInput){
    var xhr = new XMLHttpRequest();
    userInput = userInput.replaceAll('\n', '__n__')
    xhr.open("GET", "/get?msg=" + userInput, true);
    xhr.onload = function () {
        if (xhr.readyState == 4 && xhr.status == "200") {
            var list = JSON.parse(xhr.responseText);
            for(var item of list){
                // Create a new div for the message
                var messageDiv = document.createElement('div');
                messageDiv.className = 'chatbox-item chatbox-msg-sender';

                var userAvatar = document.createElement('div');
                userAvatar.className = 'chatbox-user-avatar';

                var span = document.createElement("SPAN");
                span.className = "material-symbols-outlined"
                span.innerText = "person"

                var contentWrapper = document.createElement('div');
                contentWrapper.className = "chatbox-item-content-wrapper"

                if(isDataUrl(item)){
                    var img = document.createElement("IMG");
                    img.src = item;
                    img.style.cursor = "pointer"
                    img.onclick = (function(i) {
                        return function() {
                            var modal = document.createElement("DIV");
                            modal.className = "modal";
                            var modalContent = document.createElement("IMG");
                            modalContent.className = "modal-content";
                            modalContent.src = i;
                            modal.appendChild(modalContent);
                            document.body.appendChild(modal);
                            modal.onclick = function() {
                                document.body.removeChild(modal);
                            }
                        };
                    })(item);
                    contentWrapper.appendChild(img);
                }else {
                    var content_span = document.createElement("SPAN");
                    content_span.className = "chatbox-item-content"
                    content_span.innerText = item;
                    contentWrapper.appendChild(content_span)
                }
                
                userAvatar.appendChild(span)
                contentWrapper.appendChild(content_span)

                // Append the message to the chat dialog
                messageDiv.appendChild(userAvatar)
                messageDiv.appendChild(contentWrapper)

                chatboxBody.prepend(messageDiv);
                messageDiv.scrollIntoView({ block: "start", behavior: "smooth" });
            }
        }
    }
    xhr.send();
}

chatBoxIcon.addEventListener('click', e =>{
    e.preventDefault()

    if(chatBoxWrapper.classList.contains('show')){
        chatBoxWrapper.classList.remove('show')
    }else{
        chatBoxWrapper.classList.add('show')
        chatBoxIcon.style.display = 'none'
    }
})

chatBoxCloseBtn.addEventListener('click', e => {
    e.preventDefault()
    if(chatBoxWrapper.classList.contains('show')){
        if(!chatBoxWrapper.classList.contains('closing'))
            chatBoxWrapper.classList.add('closing');
            setTimeout(()=>{
            chatBoxWrapper.classList.remove('show');
            chatBoxWrapper.classList.remove('closing');
            }, 500)
    }

    chatBoxIcon.removeAttribute('style')
})

chatBoxSendMessage.addEventListener('click', appendMessage)

const chatBoxTextFieldHeight = chatBoxTextField.clientHeight
chatBoxTextField.addEventListener('keyup', e=>{
    var maxHeight = getComputedStyle(chatBoxTextField).getPropertyValue('--chatbox-max-height')
    chatBoxTextField.removeAttribute('style')
    setTimeout(()=>{
        if(chatBoxTextField.scrollHeight > maxHeight){
            chatBoxTextField.style.height = `${maxHeight}px`
        }else{
            chatBoxTextField.style.height = `${chatBoxTextField.scrollHeight}px`
        }
    },0)
})

optionsContainer.style.display = 'none';