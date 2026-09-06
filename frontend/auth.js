// ==========================================
// DOCROP AUTHENTICATION
// ==========================================


// LOGIN
function login() {

    const email =
        document.getElementById("loginEmail").value.trim();

    const password =
        document.getElementById("loginPassword").value.trim();


    if (email === "" || password === "") {

        alert("Please enter email and password.");

        return;
    }


    // Temporary frontend login

    alert("Login successful!");

    // Later:
    // send email + password to FastAPI


    window.location.href = "index.html";
}



// ==========================================
// CREATE ACCOUNT
// ==========================================

function createAccount() {

    const name =
        document.getElementById("name").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const phone =
        document.getElementById("phone").value.trim();

    const password =
        document.getElementById("password").value.trim();


    if (
        name === "" ||
        email === "" ||
        phone === "" ||
        password === ""
    ) {

        alert("Please fill all the fields.");

        return;
    }


    // Temporary frontend registration

    alert(
        "Account created successfully!"
    );


    // Go to login page

    window.location.href = "login.html";
}