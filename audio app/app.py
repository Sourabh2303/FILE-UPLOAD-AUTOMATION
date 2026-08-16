import email

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


BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


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


@app.route("/submit", methods=["POST"])
def submit_audio():

    try:

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        audio_file = request.files.get("audio")


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


        audio_file.save(file_path)


        metadata = get_audio_metadata(
            str(file_path)
        )


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
        email = str(data.get("email", "")).strip().lower()
        phone = str(data.get("phone", "")).strip()
        print("Received from n8n:")
        print("Name:", repr(name))
        print("Email:", repr(email))
        print("Phone:", repr(phone))

        db_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assignment.db")
        )

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        person = None

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
            "message": "No matching person found.",
            "name": name,
            "email": email,
            "phone": phone
                    }), 200

    except Exception as e:
        print("Duplicate check error:", e)

        return jsonify({
            "error": str(e)
        }), 500

@app.route("/add-person", methods=["POST"])
def add_person():
    try:
        data = request.get_json()

        name = str(data.get("name") or "").strip()
        email = str(data.get("email") or "").strip().lower()
        phone = str(data.get("phone") or "").strip()

        if not name:
            return jsonify({
                "success": False,
                "message": "Name is required."
            }), 400

        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required."
            }), 400

        if not phone:
            return jsonify({
                "success": False,
                "message": "Phone is required."
            }), 400

        conn = get_connection()

        existing_person = conn.execute(
            """
            SELECT person_id
            FROM persons
            WHERE phone = ?
               OR LOWER(email) = ?
            LIMIT 1
            """,
            (phone, email)
        ).fetchone()

        if existing_person:
            conn.close()

            return jsonify({
                "success": False,
                "message": "Person already exists.",
                "person_id": existing_person["person_id"]
            }), 409

        last_person = conn.execute(
            """
            SELECT person_id
            FROM persons
            ORDER BY CAST(SUBSTR(person_id, 2) AS INTEGER) DESC
            LIMIT 1
            """
        ).fetchone()

        if last_person:
            last_number = int(last_person["person_id"][1:])
            person_id = f"P{last_number + 1:04d}"
        else:
            person_id = "P0001"

        conn.execute(
            """
            INSERT INTO persons (
                person_id,
                name,
                email,
                phone
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                person_id,
                name,
                email,
                phone
            )
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "New person added successfully.",
            "person_id": person_id,
            "name": name,
            "email": email,
            "phone": phone
        }), 201

    except Exception as e:
        print("Add person error:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
    