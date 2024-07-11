const save_button = document.getElementById("navbar_save");
const urllink_button = document.getElementById("navbar_urllink");
const editor_textarea = document.getElementById("editor");

save_button.style.display = "flex";
urllink_button.style.display = "none";

save_button.onclick = function () {
    if (editor_textarea.value) {
        save_button.classList.add("navbar_item_disabled")
        fetch("/api/upload", {
            method: "POST",
            headers: {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({text: editor_textarea.value})
        })
            .then((res) => res.json())
            .then((data) => {
                document.location.href = "/" + data["paste_id"];
                //history.replaceState(null, "", "/" + data["paste_id"]);
            })
    }
}
