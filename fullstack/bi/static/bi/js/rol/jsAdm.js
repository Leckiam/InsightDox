document.addEventListener("DOMContentLoaded", () => {
    var form = document.getElementById('updateInfCost');
    form.addEventListener("submit", function (event) {

        // Evita que el form se envíe inmediatamente
        event.preventDefault();

        // Verifica si se seleccionó al menos un archivo
        const files = document.getElementById("archivo_informe").files;
        if (!files.length) {
            return; // no se envía nada
        }

        try {
            const updateFiles = document.getElementById("updateFiles");
            updateFiles.style.display = 'block'
        } catch (e) {
            console.error("Toast error:", e);
        }

        // Enviar de verdad después de mostrar el toast
        setTimeout(() => form.submit(), 100);
    });
});