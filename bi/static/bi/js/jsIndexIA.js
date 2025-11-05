document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("btn-consultar").addEventListener("click", async () => {
        const pregunta = document.getElementById("pregunta-ia").value;
        const respuestaDiv = document.getElementById("respuesta-ia");

        // Limpiar respuesta anterior
        respuestaDiv.textContent = "Cargando...";

        try {
            const response = await fetch("/consultar_ia/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken')
                },
                body: JSON.stringify({ pregunta: pregunta })
            });

            // Usar reader para leer streaming
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let respuesta = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                respuesta += decoder.decode(value);
                respuestaDiv.textContent = respuesta;  // actualizar en tiempo real
            }
        } catch (error) {
            console.error("Error:", error);
            respuestaDiv.textContent = "Error al consultar la IA.";
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
})