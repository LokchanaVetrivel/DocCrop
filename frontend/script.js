// ==========================================
// DOCROP - FRONTEND JAVASCRIPT
// ==========================================


// ==========================================
// 0. GET HTML ELEMENTS
// ==========================================

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
// 1. MULTI-LANGUAGE SUPPORT
// ==========================================

const languageSelect =
    document.getElementById("languageSelect");


// Supported Indian languages
const supportedLanguages = {
    en: "en-IN",
    hi: "hi-IN",
    ta: "ta-IN",
    te: "te-IN",
    kn: "kn-IN",
    ml: "ml-IN",
    mr: "mr-IN",
    bn: "bn-IN",
    gu: "gu-IN",
    pa: "pa-IN",
    or: "or-IN"
};


// Current language
let currentLanguage =
    localStorage.getItem("selectedLanguage") || "en";


// Translation data
let translations = {};


// Load selected language
async function loadLanguage(language) {

    try {

        const response =
            await fetch(`languages/${language}.json`);

        if (!response.ok) {
            throw new Error(
                `Language file not found: ${language}.json`
            );
        }

        translations = await response.json();

        currentLanguage = language;

        // Change HTML language
        document.documentElement.lang = language;

        // Update all translated elements
        document
            .querySelectorAll("[data-i18n]")
            .forEach(function (element) {

                const key =
                    element.getAttribute("data-i18n");

                if (
                    translations[key] !== undefined
                ) {
                    element.textContent =
                        translations[key];
                }

            });


        // Update placeholders
        document
            .querySelectorAll("[data-i18n-placeholder]")
            .forEach(function (element) {

                const key =
                    element.getAttribute(
                        "data-i18n-placeholder"
                    );

                if (
                    translations[key] !== undefined
                ) {
                    element.placeholder =
                        translations[key];
                }

            });


        // Save selected language
        localStorage.setItem(
            "selectedLanguage",
            language
        );


        // Update voice recognition language
        if (recognition) {

            recognition.lang =
                supportedLanguages[language] || "en-IN";

        }


        console.log(
            "Language changed to:",
            language
        );

    }

    catch (error) {

        console.error(
            "Language loading error:",
            error
        );

    }

}


// Language dropdown
if (languageSelect) {

    languageSelect.addEventListener(
        "change",
        function () {

            loadLanguage(this.value);

        }
    );

    languageSelect.value =
        currentLanguage;

}


// Load language when page starts
loadLanguage(currentLanguage);


// ==========================================
// 2. IMAGE UPLOAD
// ==========================================

if (cropImage) {

    cropImage.addEventListener(
        "change",
        function () {

            if (cropImage.files.length === 0) {

                if (fileName) {
                    fileName.textContent =
                        "No image selected";
                }

                return;
            }


            const selectedFile =
                cropImage.files[0];


            if (fileName) {

                fileName.textContent =
                    "Selected: " +
                    selectedFile.name;

            }


            console.log(
                "Crop image selected:",
                selectedFile.name
            );

        }
    );

}


// ==========================================
// 3. VOICE INPUT
// ==========================================

let recognition = null;
let isRecording = false;


// Check browser support
if (
    "webkitSpeechRecognition" in window
) {

    recognition =
        new webkitSpeechRecognition();


    recognition.continuous = false;

    recognition.interimResults = false;


    // Use selected language
    recognition.lang =
        supportedLanguages[currentLanguage] ||
        "en-IN";


    // --------------------------------------
    // Voice started
    // --------------------------------------

    recognition.onstart = function () {

        isRecording = true;


        if (voiceButton) {

            voiceButton.textContent =
                "⏹ Stop Recording";

        }


        if (voiceStatus) {

            voiceStatus.textContent =
                getTranslation(
                    "listening",
                    "Listening... Speak about your crop."
                );

        }

    };


    // --------------------------------------
    // Voice result
    // --------------------------------------

    recognition.onresult =
        function (event) {

            const transcript =
                event.results[0][0].transcript;


            console.log(
                "Farmer said:",
                transcript
            );


            if (voiceStatus) {

                const message =
                    getTranslation(
                        "you_said",
                        "You said: "
                    );

                voiceStatus.textContent =
                    message + transcript;

            }

        };


    // --------------------------------------
    // Voice error
    // --------------------------------------

    recognition.onerror =
        function () {

            if (voiceStatus) {

                voiceStatus.textContent =
                    getTranslation(
                        "voice_error",
                        "Unable to understand. Please try again."
                    );

            }


            isRecording = false;


            if (voiceButton) {

                voiceButton.textContent =
                    getTranslation(
                        "start_recording",
                        "🎤 Start Recording"
                    );

            }

        };


    // --------------------------------------
    // Voice ended
    // --------------------------------------

    recognition.onend =
        function () {

            isRecording = false;


            if (voiceButton) {

                voiceButton.textContent =
                    getTranslation(
                        "start_recording",
                        "🎤 Start Recording"
                    );

            }

        };

}


// --------------------------------------
// Voice button
// --------------------------------------

if (voiceButton) {

    voiceButton.addEventListener(
        "click",
        function () {

            if (!recognition) {

                alert(
                    getTranslation(
                        "voice_not_supported",
                        "Voice input is not supported. Please use Google Chrome or Edge."
                    )
                );

                return;

            }


            if (isRecording) {

                recognition.stop();

            }

            else {

                // Update language before recording
                recognition.lang =
                    supportedLanguages[currentLanguage] ||
                    "en-IN";

                recognition.start();

            }

        }
    );

}


// ==========================================
// 4. ANALYZE CROP
// ==========================================

if (analyzeButton) {

    analyzeButton.addEventListener(
        "click",
        function () {


            // Check image
            if (
                !cropImage ||
                cropImage.files.length === 0
            ) {

                alert(
                    getTranslation(
                        "upload_first",
                        "Please upload a crop image first."
                    )
                );

                return;

            }


            const selectedFile =
                cropImage.files[0];


            console.log(
                "Starting crop analysis:",
                selectedFile.name
            );


            // Processing message
            analyzeButton.textContent =
                getTranslation(
                    "analyzing",
                    "⏳ Analyzing..."
                );


            analyzeButton.disabled = true;


            // --------------------------------------
            // Temporary demonstration result
            // Later connect with FastAPI + AI
            // --------------------------------------

            setTimeout(
                function () {


                    if (diseaseResult) {

                        diseaseResult.textContent =
                            getTranslation(
                                "analysis_ready",
                                "Analysis Ready"
                            );

                    }


                    if (confidenceResult) {

                        confidenceResult.textContent =
                            getTranslation(
                                "waiting_ai",
                                "Waiting for AI"
                            );

                    }


                    if (pestResult) {

                        pestResult.textContent =
                            getTranslation(
                                "processing",
                                "Processing"
                            );

                    }


                    if (severityResult) {

                        severityResult.textContent =
                            getTranslation(
                                "processing",
                                "Processing"
                            );

                    }


                    if (riskResult) {

                        riskResult.textContent =
                            getTranslation(
                                "processing",
                                "Processing"
                            );

                    }


                    if (recommendationResult) {

                        recommendationResult.textContent =
                            getTranslation(
                                "recommendation_waiting",
                                "AI recommendation will appear here after connecting the backend."
                            );

                    }


                    analyzeButton.textContent =
                        getTranslation(
                            "analyze_crop",
                            "🔍 Analyze My Crop"
                        );


                    analyzeButton.disabled = false;


                },
                1500
            );

        }
    );

}


// ==========================================
// 5. GET FARMER LOCATION
// ==========================================

if (locationButton) {

    locationButton.addEventListener(
        "click",
        function () {


            if (!navigator.geolocation) {

                if (locationStatus) {

                    locationStatus.textContent =
                        getTranslation(
                            "location_not_supported",
                            "Location services are not supported."
                        );

                }

                return;

            }


            if (locationStatus) {

                locationStatus.textContent =
                    getTranslation(
                        "getting_location",
                        "📍 Getting your location..."
                    );

            }


            navigator.geolocation.getCurrentPosition(


                // Success
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


                    if (locationStatus) {

                        locationStatus.textContent =
                            getTranslation(
                                "location_success",
                                "Location detected successfully."
                            );

                    }


                    /*
                     * Later we will send latitude
                     * and longitude to FastAPI.
                     *
                     * Then we can find:
                     *
                     * - Nearby agricultural shops
                     * - Dealers
                     * - Products
                     * - Input availability
                     */

                },


                // Error
                function () {

                    if (locationStatus) {

                        locationStatus.textContent =
                            getTranslation(
                                "location_error",
                                "Unable to access location. Please allow GPS permission."
                            );

                    }

                }

            );

        }
    );

}


// ==========================================
// 6. FOLLOW-UP IMAGE
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
                getTranslation(
                    "followup_message",
                    "Follow-up image upload will be connected to the progress monitoring module."
                )
            );

        }
    );

}


// ==========================================
// 7. TRANSLATION HELPER
// ==========================================

function getTranslation(
    key,
    defaultText
) {

    if (
        translations &&
        translations[key] !== undefined
    ) {

        return translations[key];

    }

    return defaultText;

}


// ==========================================
// 8. DOCROP STARTED
// ==========================================

console.log(
    "🌱 DocCrop frontend loaded successfully."
);

console.log(
    "🌐 Current language:",
    currentLanguage
);