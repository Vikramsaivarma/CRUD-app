const url = "http://localhost:3000/students";

let editId = null;


// VALIDATION
function valid() {

    let rollNo = document.getElementById("rollNo").value.trim();
    let name = document.getElementById("name").value.trim();
    let age = document.getElementById("age").value;
    let dept = document.getElementById("department").value.trim();
    let marks = document.getElementById("marks").value;

    if (!rollNo || !name || !age || !dept || marks === "") {
        alert("No field can be empty");
        return false;
    }

    if (!/^[A-Za-z0-9]+$/.test(rollNo)) {
        alert("Roll No can contain only letters and numbers");
        return false;
    }

    if (!/^[A-Za-z ]+$/.test(name)) {
        alert("Name must contain only letters and spaces");
        return false;
    }

    if (age < 18 || age > 26) {
        alert("Age must be between 18 and 26");
        return false;
    }

    if (!/^[A-Z]+$/.test(dept)) {
        alert("Department must contain CAPITAL letters only");
        return false;
    }

    if (marks < 0 || marks >= 100) {
        alert("Marks must be between 0 and 99");
        return false;
    }

    return true;
}


// LOAD
function load() {

    fetch(url)
        .then(res => res.json())
        .then(data => {

            let output = "";

            data.forEach(s => {

                output += `
                    <tr>
                        <td>${s.rollNo}</td>
                        <td>${s.name}</td>
                        <td>${s.age}</td>
                        <td>${s.department}</td>
                        <td>${s.marks}</td>

                        <td>
                            <button onclick="edit('${s._id}')">
                                Edit
                            </button>

                            <button onclick="del('${s._id}')">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            });

            document.getElementById("data").innerHTML = output;
        });
}


// ADD
function add() {

    if (!valid()) return;

    let student = {
        rollNo: document.getElementById("rollNo").value.trim(),
        name: document.getElementById("name").value.trim(),
        age: Number(document.getElementById("age").value),
        department: document.getElementById("department").value.trim(),
        marks: Number(document.getElementById("marks").value)
    };

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(student)
    })
    .then(res => res.json())
    .then(result => {

        if (result.error) {
            alert(result.error);
            return;
        }

        alert("Student added");
        clear();
        load();
    });
}


// EDIT
function edit(id) {

    fetch(url)
        .then(res => res.json())
        .then(data => {

            let s = data.find(x => x._id === id);

            editId = id;

            document.getElementById("rollNo").value = s.rollNo;
            document.getElementById("name").value = s.name;
            document.getElementById("age").value = s.age;
            document.getElementById("department").value = s.department;
            document.getElementById("marks").value = s.marks;
        });
}


// UPDATE
function update() {

    if (editId === null) {
        alert("Click Edit first");
        return;
    }

    if (!valid()) return;

    let student = {
        rollNo: document.getElementById("rollNo").value.trim(),
        name: document.getElementById("name").value.trim(),
        age: Number(document.getElementById("age").value),
        department: document.getElementById("department").value.trim(),
        marks: Number(document.getElementById("marks").value)
    };

    fetch(url + "/" + editId, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(student)
    })
    .then(res => res.json())
    .then(result => {

        if (result.error) {
            alert(result.error);
            return;
        }

        alert("Student updated");
        clear();
        load();
    });
}


// DELETE
function del(id) {

    fetch(url + "/" + id, {
        method: "DELETE"
    })
    .then(() => {
        alert("Student deleted");
        load();
    });
}


// CLEAR
function clear() {

    document.getElementById("rollNo").value = "";
    document.getElementById("name").value = "";
    document.getElementById("age").value = "";
    document.getElementById("department").value = "";
    document.getElementById("marks").value = "";

    editId = null;
}

load();