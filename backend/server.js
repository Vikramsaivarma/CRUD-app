const express = require("express");
const { MongoClient, ObjectId } = require("mongodb");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const client = new MongoClient("mongodb://127.0.0.1:27017");


function valid(s) {

    return (
        s.rollNo &&
        /^[A-Za-z0-9]+$/.test(s.rollNo) &&

        s.name &&
        /^[A-Za-z ]+$/.test(s.name) &&

        Number(s.age) >= 18 &&
        Number(s.age) <= 26 &&

        s.department &&
        /^[A-Z]+$/.test(s.department) &&

        s.marks !== "" &&
        Number(s.marks) >= 0 &&
        Number(s.marks) < 100
    );
}


async function start() {

    await client.connect();

    console.log("MongoDB connected");

    const db = client.db("college");
    const students = db.collection("students");


    // Roll No must be unique
    await students.createIndex(
        { rollNo: 1 },
        { unique: true }
    );


    // Name must be unique
    await students.createIndex(
        { name: 1 },
        { unique: true }
    );


    // LOAD
    app.get("/students", async (req, res) => {

        res.json(await students.find().toArray());

    });


    // ADD
    app.post("/students", async (req, res) => {

        if (!valid(req.body)) {
            return res.status(400).json({
                error: "Invalid student details"
            });
        }

        try {

            await students.insertOne({
                rollNo: req.body.rollNo.trim(),
                name: req.body.name.trim(),
                age: Number(req.body.age),
                department: req.body.department.trim(),
                marks: Number(req.body.marks)
            });

            res.json({
                message: "Added"
            });

        } catch (error) {

            if (error.code === 11000) {
                return res.status(400).json({
                    error: "Roll No or Name already exists"
                });
            }

            res.status(500).json({
                error: "Could not add student"
            });
        }
    });


    // UPDATE
    app.put("/students/:id", async (req, res) => {

        if (
            !ObjectId.isValid(req.params.id) ||
            !valid(req.body)
        ) {
            return res.status(400).json({
                error: "Invalid student details"
            });
        }

        try {

            await students.updateOne(
                {
                    _id: new ObjectId(req.params.id)
                },
                {
                    $set: {
                        rollNo: req.body.rollNo.trim(),
                        name: req.body.name.trim(),
                        age: Number(req.body.age),
                        department: req.body.department.trim(),
                        marks: Number(req.body.marks)
                    }
                }
            );

            res.json({
                message: "Updated"
            });

        } catch (error) {

            if (error.code === 11000) {
                return res.status(400).json({
                    error: "Roll No or Name already exists"
                });
            }

            res.status(500).json({
                error: "Could not update student"
            });
        }
    });


    // DELETE
    app.delete("/students/:id", async (req, res) => {

        if (!ObjectId.isValid(req.params.id)) {
            return res.status(400).json({
                error: "Invalid ID"
            });
        }

        let result = await students.deleteOne({
            _id: new ObjectId(req.params.id)
        });

        res.json(result);
    });


    app.listen(3000, () => {
        console.log("Server running on port 3000");
    });
}

start();