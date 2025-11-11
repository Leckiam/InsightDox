document.addEventListener("DOMContentLoaded", () => {
    const btnConsultar = document.getElementById("btn-consultar");
    const inputPregunta = document.getElementById("pregunta-ia");
    const respuestaDiv = document.getElementById("respuesta-ia");

    btnConsultar.addEventListener("click", async () => {
        const pregunta = inputPregunta.value.trim();
        if (!pregunta) return;

        respuestaDiv.textContent = "💭 Procesando pregunta...";
        respuestaDiv.style.opacity = "0.7";

        try {
            const response = await fetch("/consultar_ia/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ pregunta }),
            });

            if (!response.ok || !response.body) {
                throw new Error(`Error HTTP ${response.status}`);
            }

            const decoder = new TextDecoder();
            let respuesta = "";
            let buffer = "";
            let lastUpdate = Date.now();

            // Usamos streaming nativo
            const stream = response.body
                .pipeThrough(new TextDecoderStream()) // decodifica binario -> texto
                .getReader();

            for await (const chunk of readStream(stream)) {
                buffer += chunk;

                // Actualiza texto cada 50–70 ms para fluidez
                if (Date.now() - lastUpdate > 60) {
                    respuesta += buffer;
                    respuestaDiv.textContent = respuesta;
                    buffer = "";
                    lastUpdate = Date.now();
                }
            }

            // Finaliza
            respuesta += buffer;
            respuestaDiv.textContent = respuesta;
            respuestaDiv.style.opacity = "1";
        } catch (err) {
            console.error("❌ Error en streaming:", err);
            respuestaDiv.textContent = "⚠️ Error al consultar la IA. Solo se aceptan preguntas sobre los movimientos economicos registrados";
        }
    });

    // Helper moderno
    async function* readStream(reader) {
        try {
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                yield value;
            }
        } finally {
            reader.releaseLock();
        }
    }

    // Cookie CSRF
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
    }
});
