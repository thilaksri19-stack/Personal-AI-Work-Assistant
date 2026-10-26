/* ============================================================
   PERSONAL AI — MAIN JAVASCRIPT
============================================================ */


/* ============================================================
   DOM ELEMENTS
============================================================ */

// Upload elements

const fileInput =
    document.getElementById("fileInput");

const uploadButton =
    document.getElementById("uploadButton");

const attachButton =
    document.getElementById("attachButton");

const sidebarUploadButton =
    document.getElementById(
        "sidebarUploadButton"
    );

const uploadModal =
    document.getElementById("uploadModal");

const closeModal =
    document.getElementById("closeModal");

const dropZone =
    document.getElementById("dropZone");

const selectedFiles =
    document.getElementById("selectedFiles");

const uploadStatus =
    document.getElementById("uploadStatus");


// Chat elements

const questionInput =
    document.getElementById("questionInput");

const askButton =
    document.getElementById("askButton");

const chatMessages =
    document.getElementById("chatMessages");

const welcomeScreen =
    document.getElementById("welcomeScreen");

const newChatButton =
    document.getElementById("newChatButton");


// Sidebar elements

const mobileMenu =
    document.getElementById("mobileMenu");

const sidebar =
    document.querySelector(".sidebar");

const sidebarDocumentList =
    document.getElementById(
        "sidebarDocumentList"
    );

const documentCount =
    document.getElementById(
        "documentCount"
    );

const storageCount =
    document.getElementById(
        "storageCount"
    );

const storageProgress =
    document.getElementById(
        "storageProgress"
    );

const deleteAllButton =
    document.getElementById(
        "deleteAllButton"
    );


/* ============================================================
   GLOBAL VARIABLES
============================================================ */

let selectedFileList = [];

let isAsking = false;


/* ============================================================
   INITIALIZATION
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDocuments();

        setupSuggestionCards();

        setupQuestionInput();

        setupUploadEvents();

        setupMobileMenu();

        setupNewChat();

    }
);


/* ============================================================
   UPLOAD EVENT SETUP
============================================================ */

function setupUploadEvents() {


    /* --------------------------------------------------------
       Attach button
    -------------------------------------------------------- */

    if (attachButton) {

        attachButton.addEventListener(
            "click",
            openUploadModal
        );

    }


    /* --------------------------------------------------------
       Sidebar upload button
    -------------------------------------------------------- */

    if (sidebarUploadButton) {

        sidebarUploadButton.addEventListener(
            "click",
            openUploadModal
        );

    }


    /* --------------------------------------------------------
       Close modal
    -------------------------------------------------------- */

    if (closeModal) {

        closeModal.addEventListener(
            "click",
            closeUploadModal
        );

    }


    /* --------------------------------------------------------
       Click outside modal
    -------------------------------------------------------- */

    if (uploadModal) {

        uploadModal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    uploadModal
                ) {

                    closeUploadModal();

                }

            }
        );

    }


    /* --------------------------------------------------------
       Drop zone click
    -------------------------------------------------------- */

    if (dropZone) {

        dropZone.addEventListener(
            "click",
            function () {

                if (fileInput) {

                    fileInput.click();

                }

            }
        );

    }


    /* --------------------------------------------------------
       File input
    -------------------------------------------------------- */

    if (fileInput) {

        fileInput.addEventListener(
            "change",
            function () {

                selectedFileList = [
                    ...fileInput.files
                ];

                renderSelectedFiles();

            }
        );

    }


    /* --------------------------------------------------------
       Drag over
    -------------------------------------------------------- */

    if (dropZone) {

        dropZone.addEventListener(
            "dragover",
            function (event) {

                event.preventDefault();

                dropZone.classList.add(
                    "dragover"
                );

            }
        );

    }


    /* --------------------------------------------------------
       Drag leave
    -------------------------------------------------------- */

    if (dropZone) {

        dropZone.addEventListener(
            "dragleave",
            function () {

                dropZone.classList.remove(
                    "dragover"
                );

            }
        );

    }


    /* --------------------------------------------------------
       Drop
    -------------------------------------------------------- */

    if (dropZone) {

        dropZone.addEventListener(
            "drop",
            function (event) {

                event.preventDefault();

                dropZone.classList.remove(
                    "dragover"
                );


                selectedFileList = [
                    ...event.dataTransfer.files
                ];


                renderSelectedFiles();

            }
        );

    }


    /* --------------------------------------------------------
       Upload button
    -------------------------------------------------------- */

    if (uploadButton) {

        uploadButton.addEventListener(
            "click",
            uploadDocuments
        );

    }


    /* --------------------------------------------------------
       Delete all
    -------------------------------------------------------- */

    if (deleteAllButton) {

        deleteAllButton.addEventListener(
            "click",
            deleteAllDocuments
        );

    }

}


/* ============================================================
   OPEN UPLOAD MODAL
============================================================ */

function openUploadModal() {

    if (!uploadModal) {
        return;
    }


    uploadModal.classList.add(
        "open"
    );


    if (fileInput) {

        fileInput.value = "";

    }


    selectedFileList = [];


    if (selectedFiles) {

        selectedFiles.innerHTML = "";

    }


    if (uploadStatus) {

        uploadStatus.textContent = "";

    }

}


/* ============================================================
   CLOSE UPLOAD MODAL
============================================================ */

function closeUploadModal() {

    if (!uploadModal) {
        return;
    }


    uploadModal.classList.remove(
        "open"
    );

}


/* ============================================================
   RENDER SELECTED FILES
============================================================ */

function renderSelectedFiles() {

    if (!selectedFiles) {
        return;
    }


    selectedFiles.innerHTML = "";


    if (
        selectedFileList.length === 0
    ) {

        return;

    }


    selectedFileList.forEach(
        function (file) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "selected-file";


            /* File icon */

            const icon =
                document.createElement(
                    "div"
                );


            icon.className =
                "file-icon";


            icon.textContent =
                getFileExtension(
                    file.name
                );


            /* File name */

            const name =
                document.createElement(
                    "div"
                );


            name.className =
                "selected-file-name";


            name.textContent =
                file.name;


            /* File size */

            const size =
                document.createElement(
                    "div"
                );


            size.className =
                "selected-file-size";


            size.textContent =
                formatFileSize(
                    file.size
                );


            item.appendChild(
                icon
            );


            item.appendChild(
                name
            );


            item.appendChild(
                size
            );


            selectedFiles.appendChild(
                item
            );

        }
    );

}


/* ============================================================
   UPLOAD DOCUMENTS
============================================================ */

async function uploadDocuments() {

    if (
        selectedFileList.length === 0
    ) {

        if (uploadStatus) {

            uploadStatus.textContent =
                "Please select at least one file.";

        }

        return;

    }


    /* --------------------------------------------------------
       Disable button
    -------------------------------------------------------- */

    uploadButton.disabled = true;


    if (uploadStatus) {

        uploadStatus.textContent =
            "Uploading and processing documents...";

    }


    /* --------------------------------------------------------
       Create FormData
    -------------------------------------------------------- */

    const formData =
        new FormData();


    selectedFileList.forEach(
        function (file) {

            formData.append(
                "files",
                file
            );

        }
    );


    try {

        /* ----------------------------------------------------
           Send request
        ---------------------------------------------------- */

        const response =
            await fetch(
                "/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        /* ----------------------------------------------------
           Parse JSON
        ---------------------------------------------------- */

        const result =
            await response.json();


        /* ----------------------------------------------------
           Check response
        ---------------------------------------------------- */

        if (
            !response.ok
            ||
            !result.success
        ) {

            throw new Error(
                result.message ||
                "Document upload failed."
            );

        }


        /* ----------------------------------------------------
           Success
        ---------------------------------------------------- */

        if (uploadStatus) {

            uploadStatus.textContent =
                `✓ ${result.document_count} document(s) processed · ${result.chunk_count} chunks created`;

        }


        /* ----------------------------------------------------
           Clear selected files
        ---------------------------------------------------- */

        selectedFileList = [];


        if (fileInput) {

            fileInput.value = "";

        }


        if (selectedFiles) {

            selectedFiles.innerHTML = "";

        }


        /* ----------------------------------------------------
           Refresh document list
        ---------------------------------------------------- */

        await loadDocuments();


        /* ----------------------------------------------------
           Close modal
        ---------------------------------------------------- */

        setTimeout(
            function () {

                closeUploadModal();

            },
            1200
        );


    }
    catch (error) {

        console.error(
            "Upload error:",
            error
        );


        if (uploadStatus) {

            uploadStatus.textContent =
                `❌ ${error.message}`;

        }

    }
    finally {

        uploadButton.disabled =
            false;

    }

}


/* ============================================================
   LOAD DOCUMENTS
============================================================ */

async function loadDocuments() {

    try {

        const response =
            await fetch(
                "/documents"
            );


        const result =
            await response.json();


        if (
            !response.ok
            ||
            !result.success
        ) {

            throw new Error(
                result.message ||
                "Could not load documents."
            );

        }


        renderDocuments(
            result.documents || []
        );


    }
    catch (error) {

        console.error(
            "Document loading error:",
            error
        );

    }

}


/* ============================================================
   RENDER DOCUMENTS
============================================================ */

function renderDocuments(
    documents
) {


    /* --------------------------------------------------------
       Update counts
    -------------------------------------------------------- */

    if (documentCount) {

        documentCount.textContent =
            documents.length;

    }


    if (storageCount) {

        storageCount.textContent =
            documents.length;

    }


    /* --------------------------------------------------------
       Clear list
    -------------------------------------------------------- */

    if (!sidebarDocumentList) {
        return;
    }


    sidebarDocumentList.innerHTML =
        "";


    /* ========================================================
       NO DOCUMENTS
    ======================================================== */

    if (
        documents.length === 0
    ) {

        sidebarDocumentList.innerHTML = `

            <div class="empty-documents">

                <div class="empty-document-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                    >

                        <path
                            d="M7 3h7l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"
                        />

                        <path
                            d="M14 3v5h5"
                        />

                        <path
                            d="M8.5 13h7M8.5 16h5"
                        />

                    </svg>

                </div>

                <div class="empty-document-title">
                    No documents
                </div>

                <div class="empty-document-text">
                    Upload files to build your
                    knowledge base.
                </div>

            </div>

        `;


        if (storageProgress) {

            storageProgress.style.width =
                "0%";

        }


        if (deleteAllButton) {

            deleteAllButton.style.display =
                "none";

        }


        return;

    }


    /* --------------------------------------------------------
       Show delete all
    -------------------------------------------------------- */

    if (deleteAllButton) {

        deleteAllButton.style.display =
            "flex";

    }


    /* ========================================================
       DOCUMENT ITEMS
    ======================================================== */

    documents.forEach(
        function (documentData) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "mini-document";


            /* ------------------------------------------------
               File icon
            ------------------------------------------------ */

            const icon =
                document.createElement(
                    "div"
                );


            icon.className =
                "file-icon";


            icon.textContent =
                documentData.type
                    .toUpperCase();


            /* ------------------------------------------------
               Information
            ------------------------------------------------ */

            const info =
                document.createElement(
                    "div"
                );


            info.className =
                "mini-document-info";


            const name =
                document.createElement(
                    "div"
                );


            name.className =
                "mini-document-name";


            name.textContent =
                documentData.name;


            name.title =
                documentData.name;


            const type =
                document.createElement(
                    "div"
                );


            type.className =
                "mini-document-type";


            type.textContent =
                formatFileSize(
                    documentData.size
                );


            info.appendChild(
                name
            );


            info.appendChild(
                type
            );


            /* ------------------------------------------------
               Delete button
            ------------------------------------------------ */

            const deleteButton =
                document.createElement(
                    "button"
                );


            deleteButton.className =
                "delete-document";


            deleteButton.type =
                "button";


            deleteButton.title =
                `Delete ${documentData.name}`;


            deleteButton.setAttribute(
                "aria-label",
                `Delete ${documentData.name}`
            );


            deleteButton.innerHTML =
                "🗑";


            deleteButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();


                    deleteDocument(
                        documentData.name
                    );

                }
            );


            /* ------------------------------------------------
               Build document item
            ------------------------------------------------ */

            item.appendChild(
                icon
            );


            item.appendChild(
                info
            );


            item.appendChild(
                deleteButton
            );


            sidebarDocumentList.appendChild(
                item
            );

        }
    );


    /* ========================================================
       STORAGE PROGRESS
    ======================================================== */

    const progress =
        Math.min(
            documents.length * 10,
            100
        );


    if (storageProgress) {

        storageProgress.style.width =
            `${progress}%`;

    }

}


/* ============================================================
   DELETE ONE DOCUMENT
============================================================ */

async function deleteDocument(
    filename
) {

    const confirmed =
        confirm(
            `Are you sure you want to delete "${filename}"?`
        );


    if (!confirmed) {

        return;

    }


    try {

        console.log(
            `Deleting document: ${filename}`
        );


        /* ----------------------------------------------------
           Send DELETE request
        ---------------------------------------------------- */

        const response =
            await fetch(
                `/documents/${encodeURIComponent(filename)}`,
                {
                    method: "DELETE"
                }
            );


        /* ----------------------------------------------------
           Parse response
        ---------------------------------------------------- */

        const result =
            await response.json();


        /* ----------------------------------------------------
           Check response
        ---------------------------------------------------- */

        if (
            !response.ok
            ||
            !result.success
        ) {

            throw new Error(
                result.message ||
                "Failed to delete document."
            );

        }


        /* ----------------------------------------------------
           Refresh document list
        ---------------------------------------------------- */

        await loadDocuments();


        console.log(
            `${filename} deleted successfully.`
        );


    }
    catch (error) {

        console.error(
            "Delete error:",
            error
        );


        alert(
            `❌ ${error.message}`
        );

    }

}


/* ============================================================
   DELETE ALL DOCUMENTS
============================================================ */

async function deleteAllDocuments() {

    const confirmed =
        confirm(
            "Are you sure you want to delete ALL documents?"
        );


    if (!confirmed) {

        return;

    }


    try {

        /* ----------------------------------------------------
           Disable button
        ---------------------------------------------------- */

        deleteAllButton.disabled =
            true;


        deleteAllButton.innerHTML =
            "Deleting...";


        /* ----------------------------------------------------
           Send DELETE request
        ---------------------------------------------------- */

        const response =
            await fetch(
                "/documents",
                {
                    method: "DELETE"
                }
            );


        /* ----------------------------------------------------
           Parse response
        ---------------------------------------------------- */

        const result =
            await response.json();


        /* ----------------------------------------------------
           Check response
        ---------------------------------------------------- */

        if (
            !response.ok
            ||
            !result.success
        ) {

            throw new Error(
                result.message ||
                "Failed to delete documents."
            );

        }


        /* ----------------------------------------------------
           Refresh list
        ---------------------------------------------------- */

        await loadDocuments();


        /* ----------------------------------------------------
           Clear chat
        ---------------------------------------------------- */

        clearChat();


        alert(
            result.message ||
            "All documents deleted successfully."
        );


    }
    catch (error) {

        console.error(
            "Delete all error:",
            error
        );


        alert(
            `❌ ${error.message}`
        );

    }
    finally {

        deleteAllButton.disabled =
            false;


        deleteAllButton.innerHTML =
            `
            <span>🗑</span>
            <span>Delete all documents</span>
            `;

    }

}


/* ============================================================
   QUESTION INPUT SETUP
============================================================ */

function setupQuestionInput() {

    if (!questionInput) {
        return;
    }


    /* --------------------------------------------------------
       Enter to send
    -------------------------------------------------------- */

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter"
                &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendQuestion();

            }

        }
    );


    /* --------------------------------------------------------
       Auto resize textarea
    -------------------------------------------------------- */

    questionInput.addEventListener(
        "input",
        function () {

            questionInput.style.height =
                "auto";


            questionInput.style.height =
                Math.min(
                    questionInput.scrollHeight,
                    130
                ) + "px";

        }
    );

}


/* ============================================================
   ASK QUESTION
============================================================ */

async function sendQuestion() {

    if (isAsking) {

        return;

    }


    const question =
        questionInput.value.trim();


    /* --------------------------------------------------------
       Empty question
    -------------------------------------------------------- */

    if (!question) {

        return;

    }


    /* --------------------------------------------------------
       Set state
    -------------------------------------------------------- */

    isAsking = true;


    /* --------------------------------------------------------
       Hide welcome
    -------------------------------------------------------- */

    if (welcomeScreen) {

        welcomeScreen.style.display =
            "none";

    }


    /* --------------------------------------------------------
       Add user message
    -------------------------------------------------------- */

    addMessage(
        question,
        "user"
    );


    /* --------------------------------------------------------
       Clear input
    -------------------------------------------------------- */

    questionInput.value = "";

    questionInput.style.height =
        "auto";


    /* --------------------------------------------------------
       Disable ask button
    -------------------------------------------------------- */

    if (askButton) {

        askButton.disabled =
            true;

    }


    /* --------------------------------------------------------
       Loading ID
    -------------------------------------------------------- */

    const loadingId =
        `loading-${Date.now()}`;


    addLoadingMessage(
        loadingId
    );


    try {

        console.log(
            "Sending question:",
            question
        );


        /* ====================================================
           CALL FLASK /ask
        ==================================================== */

        const response =
            await fetch(
                "/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question

                    })

                }
            );


        /* ----------------------------------------------------
           Parse JSON
        ---------------------------------------------------- */

        let result;


        try {

            result =
                await response.json();

        }
        catch (jsonError) {

            throw new Error(
                "Server returned an invalid response."
            );

        }


        /* ----------------------------------------------------
           Remove loading
        ---------------------------------------------------- */

        removeLoadingMessage(
            loadingId
        );


        /* ----------------------------------------------------
           Check API error
        ---------------------------------------------------- */

        if (
            !response.ok
            ||
            !result.success
        ) {

            throw new Error(
                result.message ||
                "Failed to get an answer."
            );

        }


        /* ====================================================
           DISPLAY ANSWER
        ==================================================== */

        const answer =
            result.answer ||
            "No answer was returned.";


        const citations =
            result.citations ||
            [];


        addMessage(
            answer,
            "assistant",
            citations
        );


        /* ----------------------------------------------------
           Debug search query
        ---------------------------------------------------- */

        console.log(
            "Search query:",
            result.search_query
        );


    }
    catch (error) {

        console.error(
            "RAG error:",
            error
        );


        /* ----------------------------------------------------
           Remove loading
        ---------------------------------------------------- */

        removeLoadingMessage(
            loadingId
        );


        /* ----------------------------------------------------
           Display error
        ---------------------------------------------------- */

        addMessage(
            `Unable to generate an answer.\n\n${error.message}`,
            "assistant"
        );

    }
    finally {

        isAsking = false;


        if (askButton) {

            askButton.disabled =
                false;

        }


        questionInput.focus();

    }

}


/* ============================================================
   LOADING MESSAGE
============================================================ */

function addLoadingMessage(
    loadingId
) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "message-row assistant";


    row.id =
        loadingId;


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "message-avatar";


    avatar.textContent =
        "✦";


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    const roleLabel =
        document.createElement(
            "div"
        );


    roleLabel.className =
        "message-role";


    roleLabel.textContent =
        "Personal AI";


    const messageText =
        document.createElement(
            "div"
        );


    messageText.className =
        "message-text";


    messageText.innerHTML = `

        <span class="thinking">

            Thinking

            <span>.</span>
            <span>.</span>
            <span>.</span>

        </span>

    `;


    content.appendChild(
        roleLabel
    );


    content.appendChild(
        messageText
    );


    row.appendChild(
        avatar
    );


    row.appendChild(
        content
    );


    chatMessages.appendChild(
        row
    );


    scrollChatToBottom();

}


/* ============================================================
   REMOVE LOADING MESSAGE
============================================================ */

function removeLoadingMessage(
    loadingId
) {

    const element =
        document.getElementById(
            loadingId
        );


    if (element) {

        element.remove();

    }

}


/* ============================================================
   ADD CHAT MESSAGE
============================================================ */

function addMessage(
    text,
    role,
    citations = []
) {

    if (!chatMessages) {

        return;

    }


    const row =
        document.createElement(
            "div"
        );


    row.className =
        `message-row ${role}`;


    /* --------------------------------------------------------
       Avatar
    -------------------------------------------------------- */

    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "message-avatar";


    avatar.textContent =
        role === "user"
            ? "T"
            : "✦";


    /* --------------------------------------------------------
       Content
    -------------------------------------------------------- */

    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    /* --------------------------------------------------------
       Role
    -------------------------------------------------------- */

    const roleLabel =
        document.createElement(
            "div"
        );


    roleLabel.className =
        "message-role";


    roleLabel.textContent =
        role === "user"
            ? "You"
            : "Personal AI";


    /* --------------------------------------------------------
       Message text
    -------------------------------------------------------- */

    const messageText =
        document.createElement(
            "div"
        );


    messageText.className =
        "message-text";


    /*
       textContent is intentionally used
       instead of innerHTML for normal answers.
       This prevents generated content from
       being interpreted as HTML.
    */

    messageText.textContent =
        text;


    content.appendChild(
        roleLabel
    );


    content.appendChild(
        messageText
    );


    /* ========================================================
       CITATIONS
    ======================================================== */

    if (
        citations
        &&
        citations.length > 0
    ) {

        const sources =
            document.createElement(
                "div"
            );


        sources.className =
            "sources";


        const title =
            document.createElement(
                "div"
            );


        title.className =
            "sources-title";


        title.textContent =
            "Sources";


        sources.appendChild(
            title
        );


        citations.forEach(
            function (citation) {

                const card =
                    document.createElement(
                        "span"
                    );


                card.className =
                    "source-card";


                card.textContent =
                    citation;


                sources.appendChild(
                    card
                );

            }
        );


        content.appendChild(
            sources
        );

    }


    /* --------------------------------------------------------
       Add to DOM
    -------------------------------------------------------- */

    row.appendChild(
        avatar
    );


    row.appendChild(
        content
    );


    chatMessages.appendChild(
        row
    );


    scrollChatToBottom();

}


/* ============================================================
   SCROLL CHAT
============================================================ */

function scrollChatToBottom() {

    if (!chatMessages) {

        return;

    }


    chatMessages.scrollTo({

        top:
            chatMessages.scrollHeight,

        behavior:
            "smooth"

    });

}


/* ============================================================
   SUGGESTION CARDS
============================================================ */

function setupSuggestionCards() {

    const cards =
        document.querySelectorAll(
            ".suggestion-card"
        );


    cards.forEach(
        function (card) {

            card.addEventListener(
                "click",
                function () {

                    const question =
                        card.dataset.question;


                    if (!questionInput) {

                        return;

                    }


                    questionInput.value =
                        question;


                    questionInput.focus();


                    /* Auto resize */

                    questionInput.style.height =
                        "auto";


                    questionInput.style.height =
                        Math.min(
                            questionInput.scrollHeight,
                            130
                        ) + "px";

                }
            );

        }
    );

}


/* ============================================================
   NEW CHAT
============================================================ */

function setupNewChat() {

    if (!newChatButton) {

        return;

    }


    newChatButton.addEventListener(
        "click",
        function () {

            clearChat();

        }
    );

}


/* ============================================================
   CLEAR CHAT
============================================================ */

function clearChat() {

    if (!chatMessages) {

        return;

    }


    /*
       Remove all messages.
       Welcome screen is inside chatMessages,
       so we preserve it separately.
    */

    const messages =
        chatMessages.querySelectorAll(
            ".message-row"
        );


    messages.forEach(
        function (message) {

            message.remove();

        }
    );


    if (welcomeScreen) {

        welcomeScreen.style.display =
            "";

    }


    if (questionInput) {

        questionInput.value = "";

        questionInput.style.height =
            "auto";

    }


    console.log(
        "New conversation started."
    );

}


/* ============================================================
   MOBILE MENU
============================================================ */

function setupMobileMenu() {

    if (!mobileMenu) {

        return;

    }


    mobileMenu.addEventListener(
        "click",
        function () {

            if (!sidebar) {

                return;

            }


            sidebar.classList.toggle(
                "open"
            );

        }
    );


    /* --------------------------------------------------------
       Close sidebar after selecting item
    -------------------------------------------------------- */

    if (sidebar) {

        sidebar.addEventListener(
            "click",
            function (event) {

                const target =
                    event.target.closest(
                        ".navigation-item"
                    );


                if (
                    target
                    &&
                    window.innerWidth <= 720
                ) {

                    sidebar.classList.remove(
                        "open"
                    );

                }

            }
        );

    }

}


/* ============================================================
   FILE EXTENSION
============================================================ */

function getFileExtension(
    filename
) {

    if (!filename) {

        return "FILE";

    }


    const parts =
        filename.split(".");


    if (
        parts.length < 2
    ) {

        return "FILE";

    }


    return parts[
        parts.length - 1
    ].toUpperCase();

}


/* ============================================================
   FILE SIZE
============================================================ */

function formatFileSize(
    bytes
) {

    if (
        bytes === null
        ||
        bytes === undefined
        ||
        isNaN(bytes)
    ) {

        return "";

    }


    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return `${(
            bytes / 1024
        ).toFixed(1)} KB`;

    }


    if (
        bytes <
        1024 * 1024 * 1024
    ) {

        return `${(
            bytes /
            (1024 * 1024)
        ).toFixed(1)} MB`;

    }


    return `${(
        bytes /
        (1024 * 1024 * 1024)
    ).toFixed(1)} GB`;

}


/* ============================================================
   ESCAPE / SANITIZE HELPER
============================================================ */

function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value;


    return div.innerHTML;

}


/* ============================================================
   KEYBOARD SHORTCUT
============================================================ */

document.addEventListener(
    "keydown",
    function (event) {

        /*
           Ctrl + K
           Focus question input
        */

        if (
            (event.ctrlKey ||
             event.metaKey)
            &&
            event.key.toLowerCase()
            === "k"
        ) {

            event.preventDefault();


            if (questionInput) {

                questionInput.focus();

            }

        }


        /*
           Escape
           Close modal
        */

        if (
            event.key === "Escape"
        ) {

            if (
                uploadModal
                &&
                uploadModal.classList.contains(
                    "open"
                )
            ) {

                closeUploadModal();

            }

        }

    }
);


/* ============================================================
   ONLINE / OFFLINE STATUS
============================================================ */

window.addEventListener(
    "online",
    function () {

        console.log(
            "Browser is online."
        );

    }
);


window.addEventListener(
    "offline",
    function () {

        console.warn(
            "Browser is offline."
        );

    }
);