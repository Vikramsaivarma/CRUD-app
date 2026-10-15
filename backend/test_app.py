import unittest

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app import create_app


class FakeDeleteResult:
    acknowledged = True

    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class FakeStudentsCollection:
    def __init__(self):
        self.documents = []

    def create_index(self, *_args, **_kwargs):
        pass

    def find(self):
        return list(self.documents)

    def insert_one(self, student):
        if any(
            existing["rollNo"] == student["rollNo"]
            or existing["name"] == student["name"]
            for existing in self.documents
        ):
            raise DuplicateKeyError("duplicate student")
        self.documents.append({**student, "_id": ObjectId()})

    def update_one(self, selector, update):
        student = next(
            (item for item in self.documents if item["_id"] == selector["_id"]),
            None,
        )
        if student is not None:
            updated = {**student, **update["$set"]}
            if any(
                existing is not student
                and (
                    existing["rollNo"] == updated["rollNo"]
                    or existing["name"] == updated["name"]
                )
                for existing in self.documents
            ):
                raise DuplicateKeyError("duplicate student")
            student.update(update["$set"])

    def delete_one(self, selector):
        initial_count = len(self.documents)
        self.documents = [
            student for student in self.documents
            if student["_id"] != selector["_id"]
        ]
        return FakeDeleteResult(initial_count - len(self.documents))


class StudentApiTests(unittest.TestCase):
    def setUp(self):
        self.collection = FakeStudentsCollection()
        self.client = create_app(self.collection).test_client()

    def test_create_list_update_and_delete_student(self):
        student = {
            "rollNo": "A123",
            "name": "Jane Doe",
            "age": 20,
            "department": "CS",
            "marks": 91,
        }

        response = self.client.post("/students", json=student)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Added"})

        listed = self.client.get("/students")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json), 1)
        student_id = listed.json[0]["_id"]

        updated = {**student, "marks": 95}
        response = self.client.put(f"/students/{student_id}", json=updated)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/students").json[0]["marks"], 95)

        response = self.client.delete(f"/students/{student_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["deletedCount"], 1)
        self.assertEqual(self.client.get("/students").json, [])

    def test_rejects_invalid_and_duplicate_students(self):
        invalid = {
            "rollNo": "A-123",
            "name": "Jane Doe",
            "age": 20,
            "department": "CS",
            "marks": 91,
        }
        self.assertEqual(self.client.post("/students", json=invalid).status_code, 400)

        valid = {
            "rollNo": "A123",
            "name": "Jane Doe",
            "age": 20,
            "department": "CS",
            "marks": 91,
        }
        self.client.post("/students", json=valid)
        duplicate = {**valid, "rollNo": "B456"}
        response = self.client.post("/students", json=duplicate)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"],
            "Roll No or Name already exists",
        )

    def test_cors_allows_frontend_origin(self):
        response = self.client.get(
            "/students",
            headers={"Origin": "http://localhost:5500"},
        )
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"],
            "http://localhost:5500",
        )

    def test_serves_frontend_and_assets(self):
        with self.client.get("/") as page:
            self.assertEqual(page.status_code, 200)
            self.assertIn(b"/static/script.js", page.data)
        with self.client.get("/static/style.css") as stylesheet:
            self.assertEqual(stylesheet.status_code, 200)
        with self.client.get("/static/script.js") as script:
            self.assertEqual(script.status_code, 200)


if __name__ == "__main__":
    unittest.main()
