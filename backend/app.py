import logging
import math
import os
import re

from bson import ObjectId
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def _number(value):
    if isinstance(value, bool) or value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def _student_from_payload(payload):
    if not isinstance(payload, dict):
        return None

    roll_no = payload.get("rollNo")
    name = payload.get("name")
    department = payload.get("department")
    age = _number(payload.get("age"))
    marks = _number(payload.get("marks"))

    if not (
        isinstance(roll_no, str)
        and re.fullmatch(r"[A-Za-z0-9]+", roll_no)
        and isinstance(name, str)
        and re.fullmatch(r"[A-Za-z ]+", name)
        and age is not None
        and 18 <= age <= 26
        and isinstance(department, str)
        and re.fullmatch(r"[A-Z]+", department)
        and marks is not None
        and 0 <= marks < 100
    ):
        return None

    return {
        "rollNo": roll_no.strip(),
        "name": name.strip(),
        "age": age,
        "department": department.strip(),
        "marks": marks,
    }


def _json_student(student):
    return {**student, "_id": str(student["_id"])}


def create_app(students_collection=None):
    app = Flask(__name__, static_folder="../frontend", static_url_path="/static")
    CORS(app)

    if students_collection is None:
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017"))
        database = client[os.getenv("MONGODB_DATABASE", "college")]
        students_collection = database["students"]
        students_collection.create_index("rollNo", unique=True)
        students_collection.create_index("name", unique=True)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/students")
    def load_students():
        try:
            return jsonify([_json_student(student) for student in students_collection.find()])
        except Exception:
            app.logger.exception("Could not load students")
            return jsonify(error="Could not load students"), 500

    @app.post("/students")
    def add_student():
        student = _student_from_payload(request.get_json(silent=True))
        if student is None:
            return jsonify(error="Invalid student details"), 400

        try:
            students_collection.insert_one(student)
            return jsonify(message="Added")
        except DuplicateKeyError:
            return jsonify(error="Roll No or Name already exists"), 400
        except Exception:
            app.logger.exception("Could not add student")
            return jsonify(error="Could not add student"), 500

    @app.put("/students/<student_id>")
    def update_student(student_id):
        student = _student_from_payload(request.get_json(silent=True))
        if not ObjectId.is_valid(student_id) or student is None:
            return jsonify(error="Invalid student details"), 400

        try:
            students_collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": student},
            )
            return jsonify(message="Updated")
        except DuplicateKeyError:
            return jsonify(error="Roll No or Name already exists"), 400
        except Exception:
            app.logger.exception("Could not update student")
            return jsonify(error="Could not update student"), 500

    @app.delete("/students/<student_id>")
    def delete_student(student_id):
        if not ObjectId.is_valid(student_id):
            return jsonify(error="Invalid ID"), 400

        try:
            result = students_collection.delete_one({"_id": ObjectId(student_id)})
            return jsonify(
                acknowledged=result.acknowledged,
                deletedCount=result.deleted_count,
            )
        except Exception:
            app.logger.exception("Could not delete student")
            return jsonify(error="Could not delete student"), 500

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_app().run(host="127.0.0.1", port=3000)
