
(function () {
    console.log("Sanity Check!");
})()

var token = null;
var logged_in = false;

function handleLogInClick() {

    var username = document.getElementById("username_box").value;
    var password = document.getElementById("password_box").value;
    console.log("Username ", username);

    fetch('/users/tkn', {
        method: 'POST',
        headers: {
            'Content-type': 'application/x-www-form-urlencoded',
            'accept': 'application/json'
        },
        body: `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`
    })
    .then(response => {
        if (!response) {
            throw new Error("HTTP error " + response.status);
        }
        return response.json();
    })
    .then(json => {
        console.log(json);
        token = json['access_token'];
        console.log(token);
        if (token) { logged_in = true; }
    })
    
}
