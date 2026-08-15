from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory
)
import os
import sqlite3
from flask import Flask, request, jsonify
from pathlib import Path
import uuid

from database import get_connection
from audio_utils import get_audio_metadata


app = Flask(__name__)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(exist_ok=True)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Database Test
# --------------------------------------------------

@app.route("/test-db")
def test_database():

    conn = get_connection()

    result = conn.execute(
        "SELECT COUNT(*) AS count FROM persons"
    ).fetchone()

    conn.close()

    return {
        "database": "connected",
        "people_count": result["count"]
    }


# --------------------------------------------------
# Submit Audio
# --------------------------------------------------

@app.route("/submit", methods=["POST"])
def submit_audio():

    try:

        # ------------------------------------------
        # Get form values
        # ------------------------------------------

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        audio_file = request.files.get("audio")


        # ------------------------------------------
        # Validate input
        # ------------------------------------------

        if not name:
            return jsonify({
                "error": "Name is required."
            }), 400

        if not phone:
            return jsonify({
                "error": "Phone number is required."
            }), 400

        if not audio_file:
            return jsonify({
                "error": "Audio file is required."
            }), 400

        if audio_file.filename == "":
            return jsonify({
                "error": "Invalid audio file."
            }), 400


        # ------------------------------------------
        # Generate unique filename
        # ------------------------------------------

        extension = Path(
            audio_file.filename
        ).suffix.lower()

        if not extension:
            extension = ".webm"

        filename = (
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )

        file_path = UPLOAD_FOLDER / filename


        # ------------------------------------------
        # Save audio file
        # ------------------------------------------

        audio_file.save(file_path)


        # ------------------------------------------
        # Extract audio metadata
        # ------------------------------------------

        metadata = get_audio_metadata(
            str(file_path)
        )


        # ------------------------------------------
        # Find person using phone
        # ------------------------------------------

        conn = get_connection()

        person = conn.execute(
            """
            SELECT person_id
            FROM persons
            WHERE phone = ?
            """,
            (phone,)
        ).fetchone()


        person_id = (
            person["person_id"]
            if person
            else None
        )


        # ------------------------------------------
        # Store submission
        # ------------------------------------------

        conn.execute(
            """
            INSERT INTO audio_submissions (
                person_id,
                name,
                phone,
                file_path,
                duration_seconds,
                sample_rate_khz,
                bitrate_kbps,
                loudness_db,
                noise_quality
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person_id,
                name,
                phone,
                str(file_path),
                metadata["duration_seconds"],
                metadata["sample_rate_khz"],
                metadata["bitrate_kbps"],
                metadata["loudness_db"],
                None
            )
        )

        conn.commit()
        conn.close()


        # ------------------------------------------
        # Return response
        # ------------------------------------------

        return jsonify({
            "message": "Audio submitted successfully.",
            "person_id": person_id,
            "metadata": metadata
        }), 201


    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Serve Uploaded Audio
# --------------------------------------------------

@app.route("/uploads/<filename>")
def uploaded_audio(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )
@app.route("/submissions")
def submissions():

    conn = get_connection()

    submissions = conn.execute(
        """
        SELECT
            submission_id,
            person_id,
            name,
            phone,
            file_path,
            duration_seconds,
            sample_rate_khz,
            bitrate_kbps,
            loudness_db,
            noise_quality,
            created_at
        FROM audio_submissions
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "submissions.html",
        submissions=submissions
    )

@app.route("/check-duplicate", methods=["POST"])
def check_duplicate():
    try:
        data = request.get_json()

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        phone = str(data.get("phone", "")).strip()

        # assignment.db is one level above the audio app folder
        db_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assignment.db")
        )

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        person = None

        # First check phone
        if phone:
            person = conn.execute(
                """
                SELECT person_id, name, email, phone
                FROM persons
                WHERE phone = ?
                LIMIT 1
                """,
                (phone,)
            ).fetchone()

        # If phone didn't match, check email
        if person is None and email:
            person = conn.execute(
                """
                SELECT person_id, name, email, phone
                FROM persons
                WHERE LOWER(email) = LOWER(?)
                LIMIT 1
                """,
                (email,)
            ).fetchone()

        conn.close()

        if person:
            return jsonify({
                "duplicate": True,
                "person_id": person["person_id"],
                "existing_name": person["name"],
                "existing_email": person["email"],
                "existing_phone": person["phone"]
            }), 200

        return jsonify({
            "duplicate": False,
            "message": "No matching person found."
        }), 200

    except Exception as e:
        print("Duplicate check error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Run Flask Application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )