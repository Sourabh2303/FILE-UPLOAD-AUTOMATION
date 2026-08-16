# ConsultBae AI Automation Assignment

This project implements the data consolidation and audio collection requirements of the ConsultBae AI Automation assignment.

## Project Overview

The project consists of:

1. Consolidating candidate/worker data from multiple CSV sources.
2. Cleaning and normalizing the source data.
3. Resolving duplicate people across different sources.
4. Storing the consolidated data in SQLite.
5. Building a web-based audio collection application.
6. Recording or uploading audio files.
7. Extracting audio metadata.
8. Storing audio submissions and metadata in SQLite.
9. Providing a submission listing page with audio playback.

## 1. Data Consolidation

Three source datasets were processed:

- CBNexus contacts
- Naukri applicants
- Gig workers

### Data Cleaning

The source data was cleaned using Python and Pandas.

Cleaning included:

- Removing duplicate/header rows.
- Standardizing names.
- Normalizing phone numbers.
- Standardizing verification values.
- Cleaning email values.
- Normalizing dates.
- Handling missing values.
- Correcting misplaced/invalid records.
- Standardizing text fields.

### Entity Resolution

Records belonging to the same person across different sources were identified using normalized:

- Name
- Email
- Phone number

A unique `person_id` was generated for each resolved person.

Example:

```text
P0001 -> Tanvi Gupta
```

### Consolidation Results

| Dataset / Entity | Count |
|---|---:|
| Unique people | 56 |
| Naukri records | 42 |
| Gig Worker records | 25 |
| CBNexus records | 30 |
| Source relationships | 95 |

## 2. SQLite Database

The consolidated data is stored in:

```text
assignment.db
```

### Main Tables

```text
persons
naukri_records
gig_worker_records
cbnexus_records
person_sources
audio_submissions
```

### Database Structure

```text
persons
   |
   +-- naukri_records
   +-- gig_worker_records
   +-- cbnexus_records
   |
   +-- person_sources

persons
   |
   +-- audio_submissions
```

The `person_sources` table maintains the relationship between a master person and their source records.

## 3. Audio Collection Application

The audio collection application was built using:

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite
- FFmpeg / FFprobe

### Features

#### Candidate Information

The application accepts:

- Name
- Phone number

#### Audio Input

Users can either:

- Upload an audio file
- Record audio directly using the browser microphone

#### Audio Processing

The application extracts:

- Duration
- Sample rate
- Bitrate
- Loudness

#### Person Matching

The submitted phone number is matched against the master `persons` table.

Example:

```text
Phone: 9000000254
        |
        v
P0001
        |
        v
Tanvi Gupta
```

If the phone number does not exist in the master table, the submission is still accepted and `person_id` remains empty.

#### Audio Storage

Uploaded and recorded audio files are stored in:

```text
audio app/uploads/
```

The corresponding metadata is stored in the SQLite database.

## 4. Audio Submission View

The application provides an audio submission page:

```text
http://127.0.0.1:5000/
```

Users can:

1. Enter their name.
2. Enter their phone number.
3. Upload an audio file OR record audio.
4. Preview the recording.
5. Submit the audio.

## 5. Audio Submissions View

All submitted recordings can be viewed at:

```text
http://127.0.0.1:5000/submissions
```

The page displays:

- Submission ID
- Person ID
- Name
- Phone
- Duration
- Sample rate
- Bitrate
- Loudness
- Audio player
- Submission timestamp

Users can directly play the submitted audio from the browser.

## 6. Project Structure

```text
ConsultBae-Assignment/
|
+-- README.md
+-- assignment.db
+-- data_cleaning.ipynb
|
+-- audio app/
    |
    +-- app.py
    +-- database.py
    +-- audio_utils.py
    +-- requirements.txt
    +-- test.py
    |
    +-- templates/
    |   +-- index.html
    |   +-- submissions.html
    |
    +-- static/
    |   +-- js/
    |       +-- recorder.js
    |
    +-- uploads/
```

## 7. Requirements

### Python

Python 3.x is required.

### Python Packages

Install the required packages using:

```bash
pip install -r requirements.txt
```

The application uses Flask.

SQLite is provided through Python's built-in `sqlite3` module.

### FFmpeg

FFmpeg and FFprobe are required for audio metadata extraction.

Verify installation:

```bash
ffmpeg -version
```

```bash
ffprobe -version
```

## 8. Running the Application

Navigate to the audio application directory:

```bash
cd "audio app"
```

Activate the virtual environment if required:

```bash
myenv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask application:

```bash
python app.py
```

The application will run at:

```text
http://127.0.0.1:5000
```

## 9. Testing the Application

### Database Health Check

Open:

```text
http://127.0.0.1:5000/test-db
```

Expected response:

```json
{
    "database": "connected",
    "people_count": 56
}
```

### Audio Submission

Open:

```text
http://127.0.0.1:5000/
```

Enter a name and phone number and either upload or record audio.

### Submission Listing

Open:

```text
http://127.0.0.1:5000/submissions
```

The submitted audio and extracted metadata should be displayed.

## 10. Database Validation

The consolidated database currently contains:

```text
persons:             56
naukri_records:      42
gig_worker_records:  25
cbnexus_records:     30
person_sources:      95
```

Audio submissions are stored in the `audio_submissions` table and increase whenever a new recording or uploaded audio file is submitted.

## 11. Example Audio Metadata

A test audio file produced the following metadata:

```text
Duration:      5.0 seconds
Sample Rate:   44.1 kHz
Bitrate:       705.6 kbps
Loudness:      -21.1 LUFS
```

## 12. Technologies Used

```text
Python
Pandas
Flask
SQLite
HTML
CSS
JavaScript
FFmpeg
FFprobe
```

## 13. Application Flow

```text
                    DATA SOURCES
                         |
          +--------------+--------------+
          v              v              v
       CBNexus         Naukri       Gig Workers
          |              |              |
          +--------------+--------------+
                         |
                         v
                  Data Cleaning
                         |
                         v
                 Entity Resolution
                         |
                         v
                    SQLite DB
                         |
                         v
                  Master Persons
                         |
                         v
              Audio Collection App
                         |
             +-----------+-----------+
             v                       v
        Upload Audio          Record Audio
             |                       |
             +-----------+-----------+
                         |
                         v
                  Save Audio File
                         |
                         v
                FFmpeg / FFprobe
                         |
                         v
              Audio Metadata
                         |
                         v
                Person Matching
                         |
                         v
                SQLite Storage
                         |
                         v
              Submission Dashboard
```

## 14. API Endpoints

### Home

```text
GET /
```

Displays the audio submission form.

### Database Health Check

```text
GET /test-db
```

Checks the SQLite connection and returns the number of people in the master table.

### Submit Audio

```text
POST /submit
```

Accepts:

```text
name
phone
audio
```

The endpoint:

1. Validates the submitted information.
2. Saves the audio file.
3. Extracts audio metadata.
4. Finds the corresponding `person_id`.
5. Stores the submission in SQLite.
6. Returns the submission result.

### Uploaded Audio

```text
GET /uploads/<filename>
```

Serves stored audio files for browser playback.

### Submissions

```text
GET /submissions
```

Displays all submitted recordings and their extracted audio properties.

## 15. Example Submit Response

A successful audio submission returns a response similar to:

```json
{
    "message": "Audio submitted successfully.",
    "person_id": "P0001",
    "metadata": {
        "duration_seconds": 5.0,
        "sample_rate_khz": 44.1,
        "bitrate_kbps": 705.6,
        "loudness_db": -21.1
    }
}
```

## 16. Error Handling

The application validates required fields before processing.

Examples:

### Missing Name

```text
Name is required.
```

### Missing Phone

```text
Phone number is required.
```

### Missing Audio

```text
Audio file is required.
```

### Unknown Phone

If a valid audio submission contains a phone number that does not exist in the master `persons` table, the audio is still stored and `person_id` is set to `NULL`.

## 17. Current Implementation Status

### Data Consolidation

- [x] Load source datasets
- [x] Clean source data
- [x] Normalize fields
- [x] Resolve duplicate people
- [x] Generate person IDs
- [x] Create SQLite database
- [x] Store source records
- [x] Store person-source relationships

### Audio Collection

- [x] Name input
- [x] Phone input
- [x] Audio upload
- [x] Browser audio recording
- [x] Audio preview
- [x] Audio file storage
- [x] Duration extraction
- [x] Sample rate extraction
- [x] Bitrate extraction
- [x] Loudness extraction
- [x] Person matching
- [x] SQLite persistence
- [x] Submission listing
- [x] Audio playback

## 18. Future Improvements

Possible future improvements include:

- Noise/quality estimation.
- Better matching for unmatched submissions.
- File size and duration limits.
- Improved frontend styling.
- Authentication for the submission dashboard.
- Cloud-based audio storage.
- Production deployment.
- Automated testing.
