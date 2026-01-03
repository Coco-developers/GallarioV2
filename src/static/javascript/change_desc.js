function ChangeDescription(){
  di = document.getElementById('description_input');
  dc = document.getElementById('description_cancel');
  db = document.getElementById('description_button');

  if (db.innerHTML == "Apply Changes"){
    ApplyChanges();
  }
  di.style.display = "inline";
  dc.style.display = "inline";
  db.innerHTML = "Apply Changes"
  di.focus();
}
function CancelDescription() {
  di = document.getElementById('description_input');
  dc = document.getElementById('description_cancel');
  db = document.getElementById('description_button');

  db.innerHTML = "Change Description"
  di.style.display = "none";
  dc.style.display = "none";
}
async function ApplyChanges() {
    const desc = document.getElementById("description_input").value;
    try {
        let response = await fetch("/description", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ description: desc })
        });

        if (response.ok) {
            const data = await response.json();
            document.querySelector("body > main > div.card.profile-header > h4").textContent = desc;
        } else {
            alert("Failed to update description.");
        }
    } catch (err) {
        console.error("Error:", err);
        alert("Something went wrong.");
    }
}
// to simulate a click
document.getElementById("description_input").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // stop form submission if inside a form
        document.getElementById("description_button").click(); // trigger the click
    }
});