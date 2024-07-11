const save_button = document.getElementById("navbar_save");
const urllink_button = document.getElementById("navbar_urllink");
const urllink_content = document.getElementById("urllink_content");
const editor_textarea = document.getElementById("editor");

save_button.style.display = "flex";
urllink_button.style.display = "flex";

save_button.classList.add("navbar_item_disabled");

editor_textarea.value = paste_value
urllink_content.textContent = "/" + document.location.href.split("/").slice(-1)[0]

urllink_button.onclick = function () {
     navigator.clipboard.writeText(document.location.href);
}