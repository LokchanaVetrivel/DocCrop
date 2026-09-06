// ==========================================
// DOCROP - FRONTEND JAVASCRIPT
// ==========================================

// Get HTML elements
const cropImage = document.getElementById("cropImage");
const fileName = document.getElementById("fileName");

const voiceButton = document.getElementById("voiceButton");
const voiceStatus = document.getElementById("voiceStatus");

const analyzeButton = document.getElementById("analyzeButton");

const diseaseResult = document.getElementById("diseaseResult");
const confidenceResult = document.getElementById("confidenceResult");
const pestResult = document.getElementById("pestResult");
const severityResult = document.getElementById("severityResult");
const riskResult = document.getElementById("riskResult");

const recommendationResult =
    document.getElementById("recommendationResult");

const locationButton =
    document.getElementById("locationButton");

const locationStatus =
    document.getElementById("locationStatus");


// ==========================================
// 1. IMAGE UPLOAD
// ==========================================

cropImage.addEventListener("change", function () {

    if (cropImage.files.length === 0) {
        fileName.textContent = "No image selected";
        return;
    }

    const selectedFile = cropImage.files[0];

    fileName.textContent =
        "Selected: " + selectedFile.name;

    console.log("Crop image selected:", selectedFile.name);
});


// ==========================================
// 2. VOICE INPUT
// ==========================================

let recognition = null;
let isRecording = false;

// Check browser support
if ("webkitSpeechRecognition" in window) {

    recognition = new webkitSpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    recognition.onstart = function () {

        isRecording = true;

        voiceButton.textContent =
            "⏹ Stop Recording";

        voiceStatus.textContent =
            "Listening... Speak about your crop.";
    };

    recognition.onresult = function (event) {

        const transcript =
            event.results[0][0].transcript;

        console.log("Farmer said:", transcript);

        voiceStatus.textContent =
            "You said: " + transcript;
    };

    recognition.onerror = function () {

        voiceStatus.textContent =
            "Unable to understand. Please try again.";

        isRecording = false;

        voiceButton.textContent =
            "🎤 Start Recording";
    };

    recognition.onend = function () {

        isRecording = false;

        voiceButton.textContent =
            "🎤 Start Recording";
    };

} else {

    voiceStatus.textContent =
        "Voice input is not supported in this browser.";
}


// Voice button
voiceButton.addEventListener("click", function () {

    if (!recognition) {
        alert(
            "Voice input is not supported. Please use Google Chrome or Edge."
        );
        return;
    }

    if (isRecording) {

        recognition.stop();

    } else {

        recognition.start();

    }

});


// ==========================================
// 3. ANALYZE CROP
// ==========================================

analyzeButton.addEventListener("click", function () {

    // Check image
    if (cropImage.files.length === 0) {

        alert(
            "Please upload a crop image first."
        );

        return;
    }

    const selectedFile = cropImage.files[0];

    console.log(
        "Starting crop analysis:",
        selectedFile.name
    );


    // Show processing message
    analyzeButton.textContent =
        "⏳ Analyzing...";

    analyzeButton.disabled = true;


    // Temporary demonstration result
    // Later this will be replaced by
    // the FastAPI + AI response.

    setTimeout(function () {

        diseaseResult.textContent =
            "Analysis Ready";

        confidenceResult.textContent =
            "Waiting for AI";

        pestResult.textContent =
            "Processing";

        severityResult.textContent =
            "Processing";

        riskResult.textContent =
            "Processing";

        recommendationResult.textContent =
            "AI recommendation will appear here after connecting the backend.";


        analyzeButton.textContent =
            "🔍 Analyze My Crop";

        analyzeButton.disabled = false;


    }, 1500);

});


// ==========================================
// 4. GET FARMER LOCATION
// ==========================================

locationButton.addEventListener("click", function () {

    if (!navigator.geolocation) {

        locationStatus.textContent =
            "Location services are not supported.";

        return;
    }

    locationStatus.textContent =
        "📍 Getting your location...";

    navigator.geolocation.getCurrentPosition(

        function (position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;

            console.log(
                "Latitude:",
                latitude
            );

            console.log(
                "Longitude:",
                longitude
            );

            locationStatus.textContent =
                "Location detected successfully.";

            /*
             * Later we will send latitude and longitude
             * to the backend and use them to find:
             *
             * - Nearby agricultural shops
             * - Dealers
             * - Products
             * - Input availability
             */

        },

        function () {

            locationStatus.textContent =
                "Unable to access location. Please allow GPS permission.";

        }

    );

});


// ==========================================
// 5. FOLLOW-UP IMAGE
// ==========================================

const followupButton =
    document.querySelector(
        ".followup-section .secondary-btn"
    );

if (followupButton) {

    followupButton.addEventListener(
        "click",
        function () {

            alert(
                "Follow-up image upload will be connected to the progress monitoring module."
            );

        }
    );

}


// ==========================================
// DOCROP STARTED
// ==========================================

console.log(
    "🌱 DocCrop frontend loaded successfully."
);