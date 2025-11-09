function submitRec() {
    buttonDisabled(true, 'btnSubmit');
    ocultarError();

    // Obtener el campo emailRec correcto
    const email = document.getElementsByName("emailRec")[0]; 
    
    if (!valRecover(email)) {
        event.preventDefault(); // event.preventDefault() debe estar aquí
        buttonDisabled(false, 'btnSubmit');
        return; // Detiene el envío
    }
    
    return true; // Permitir el envío del formulario
}
function valRecover(email) {
    estado = true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!(email.value.length >= 5 && email.value.length < 150) || !emailRegex.test(email.value)) {
        mostrarError(1);
        estado = false;
    }
    return estado;
}

function buttonDisabled(opcion, buttonID) {
    let button;
    if (opcion == true) {
        button = document.getElementById(buttonID);
        button.classList.add('disabled');
    } else {
        button = document.getElementById(buttonID);
        button.classList.remove('disabled');
    }
}
function mostrarError(nro) {
    switch (nro) {
        case 1:
            document.getElementById('e-email').style.display = 'block';
            document.getElementById('error-list').style.display = 'block';
            break;
        default:
            break;
    }
}
function ocultarError() {
    document.getElementById('error-list').style.display = 'none';
    document.getElementById('e-email').style.display = 'none';
    if (document.getElementById('e-no-existe')) {
        document.getElementById('e-no-existe').style.display = 'none';
    }
}