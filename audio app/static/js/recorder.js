let mediaRecorder;
let audioChunks = [];
let recordedAudioBlob = null;

const startButton = document.getElementById("startRecording");
const stopButton = document.getElementById("stopRecording");
const recordingStatus = document.getElementById("recordingStatus");
const audioPreview = document.getElementById("audioPreview");
const audioForm = document.getElementById("audioForm");
const audioFileInput = document.getElementById("audioFile");


// Start recording
startButton.addEventListener("click", async () => {

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        audioChunks = [];

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.addEventListener("dataavailable", event => {

            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }

        });

        mediaRecorder.addEventListener("stop", () => {

            recordedAudioBlob = new Blob(
                audioChunks,
                {
                    type: mediaRecorder.mimeType
                }
            );

            const audioURL = URL.createObjectURL(
                recordedAudioBlob
            );

            audioPreview.src = audioURL;
            audioPreview.hidden = false;

            recordingStatus.textContent =
                "Recording completed.";

            // Stop microphone
            stream.getTracks().forEach(track => {
                track.stop();
            });
        });

        mediaRecorder.start();

        startButton.disabled = true;
        stopButton.disabled = false;

        recordingStatus.textContent =
            "Recording...";

    } catch (error) {

        console.error(error);

        recordingStatus.textContent =
            "Microphone access was denied or unavailable.";
    }
});


// Stop recording
stopButton.addEventListener("click", () => {

    if (
        mediaRecorder &&
        mediaRecorder.state === "recording"
    ) {
        mediaRecorder.stop();

        startButton.disabled = false;
        stopButton.disabled = true;
    }

});


// Submit form
audioForm.addEventListener("submit", async event => {

    event.preventDefault();

    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;

    const uploadedFile = audioFileInput.files[0];

    let audioFile = uploadedFile;


    // If no uploaded file, use recorded audio
    if (!audioFile && recordedAudioBlob) {

        audioFile = new File(
            [recordedAudioBlob],
            "recording.webm",
            {
                type: recordedAudioBlob.type
            }
        );
    }


    // Validate audio
    if (!audioFile) {

        alert("Please upload or record an audio file.");
        return;
    }


    // Prepare multipart form data
    const formData = new FormData();

    formData.append("name", name);
    formData.append("phone", phone);
    formData.append("audio", audioFile);


    try {

        const response = await fetch(
            "/submit",
            {
                method: "POST",
                body: formData
            }
        );


        const result = await response.json();


        if (response.ok) {

            alert(result.message);

            audioForm.reset();

            audioPreview.src = "";
            audioPreview.hidden = true;

            recordedAudioBlob = null;

            recordingStatus.textContent =
                "Not recording.";

        } else {

            alert(
                result.error ||
                "Submission failed."
            );
        }

    } catch (error) {

        console.error(error);

        alert(
            "Could not connect to the server."
        );
    }

});