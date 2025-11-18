function submitLogin() {
    buttonDisabled(true, 'btnSubmit');
    ocultarError();

    const email = document.getElementsByName("correoLog")[0];
    const password = document.getElementsByName("contrasenaLog")[0];

    if (!valLogin(email, password)) {
        buttonDisabled(false, 'btnSubmit');
        event.preventDefault();
        return;
    }
}

function mostrarError(nro) {
    error = 'e';
    switch (nro) {
        case 1:
            document.getElementById('error-list').style.display = 'block';
            document.getElementById(error + '-correo').style.display = 'block';
            break;
        case 2:
            document.getElementById('error-list').style.display = 'block';
            document.getElementById(error + '-password').style.display = 'block';
            break;
        default:
            break;
    }
}

function valLogin(email, password) {
    estado = true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!(email.value.length >= 5 && email.value.length < 150) || !emailRegex.test(email.value)){
        mostrarError(1);
        estado = false;
    }
    if (!(password.value.trim().length !=0)) {
        mostrarError(2);
        estado = false;
    }
    return estado;
}

function verPassword() {
    const pwd = document.getElementById('floatingPassword');
    const icon = document.getElementById('eye-icon');
    if (pwd.type === 'password') {
        pwd.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        pwd.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
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

function ocultarError() {
    document.getElementById('error-list').style.display = 'none';
    document.getElementById('e-correo').style.display = 'none';
    document.getElementById('e-password').style.display = 'none';
    if (document.getElementById('e-no-existe')) {
        document.getElementById('e-no-existe').style.display = 'none';
    }
}