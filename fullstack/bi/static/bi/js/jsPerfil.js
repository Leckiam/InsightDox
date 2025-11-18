// --- Vista previa del avatar ---
function previewAvatar(event) {
    const reader = new FileReader();
    reader.onload = function () {
        const output = document.getElementById('avatarPreview');
        if (output) {
            output.src = reader.result;
        }
    };
    reader.readAsDataURL(event.target.files[0]);
}
