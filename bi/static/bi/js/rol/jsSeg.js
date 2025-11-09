
function obtenerNamePage(){
    const path = window.location.pathname;
    const segmentos = path.split("/").filter(Boolean);
    const ultimo = segmentos[segmentos.length - 1];
    if (ultimo == 'perfil'){
        name_page='perfil';
    } else if (ultimo == 'gestUsers'){
        name_page='gestUsers';
    } else {
        name_page = 'home';
    }
    return name_page;
}
name_page = obtenerNamePage()


function verPassword(inputId, iconId) {
    const pwd = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
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

// --- Modal para agregar usuario ---
function abrirModalAgregar() {
    document.getElementById('userModalLabel').innerText = "Agregar nuevo usuario";
    document.getElementById('userForm').action = `/addUser/?next=${name_page}`;

    // Limpiar inputs
    document.getElementById('modalUsername').value = "";
    document.getElementById('modalUsername').disabled = false;
    document.getElementById('modalNombre').value = "";
    document.getElementById('modalNombre').required = true
    document.getElementById('modalApellido').value = "";
    document.getElementById('modalApellido').required = true
    document.getElementById('modalCorreo').value = "";
    document.getElementById('modalCorreo').disabled = false;
    document.getElementById('modalPassword1').value = "";
    document.getElementById('modalPassword1').required = true
    document.getElementById('modalPassword2').value = "";
    document.getElementById('modalPassword2').required = true
    document.getElementById('modalRol').value = "";
    document.getElementById('modalAvatar').value = "";

    // Limpiar vista previa de imagen
    const avatarPreview = document.getElementById('avatarPreview');
    if (avatarPreview) avatarPreview.src = "";
}

// --- Modal para editar usuario ---
function abrirModalEditar(id, username,nombre,apellido, correo, rolId, avatar_url) {
    document.getElementById('userModalLabel').innerText = "Editar usuario";
    document.getElementById('userForm').action = `/editUser/${id}/?next=${name_page}`;

    document.getElementById('modalUsername').value = username;
    document.getElementById('modalUsername').disabled = true;
    document.getElementById('modalNombre').value = nombre;
    document.getElementById('modalNombre').required = false
    document.getElementById('modalApellido').value = apellido;
    document.getElementById('modalApellido').required = false
    document.getElementById('modalCorreo').value = correo;
    document.getElementById('modalCorreo').disabled = true;
    document.getElementById('modalPassword1').value = "";
    document.getElementById('modalPassword1').required = false
    document.getElementById('modalPassword2').value = "";
    document.getElementById('modalPassword2').required = false
    document.getElementById('modalRol').value = rolId;
    document.getElementById('modalAvatar').value = "";

    const avatarPreview = document.getElementById('avatarPreview');
    if (avatarPreview && correo) {
        avatarPreview.src = avatar_url;
    }
}

function mostrarToastError(mensaje) {
    const toastEl = document.getElementById('errorToast');
    toastEl.querySelector('.toast-body').textContent = mensaje;

    const toast = new bootstrap.Toast(toastEl, { delay: 4000 }); 
    toast.show();
}

function validarPasswords(event) {
    const pass1 = document.getElementById('modalPassword1').value.trim();
    const pass2 = document.getElementById('modalPassword2').value.trim();

    if (pass1 !== pass2) {
        event.preventDefault();
        mostrarToastError("Las contraseñas no coinciden");
        return false;
    }
    return true;
}

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('usuariosContainer');
    const rowsPerPage = parseInt(container.dataset.rows) || 15;
    const rows = Array.from(container.querySelectorAll('.usuario-row'));
    let currentPage = 1;
    const totalPages = Math.ceil(rows.length / rowsPerPage);

    function showPage(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });
        document.getElementById('prevBtn').disabled = page === 1;
        document.getElementById('nextBtn').disabled = totalPages === 0 || page === totalPages;
    }

    showPage(currentPage);

    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    });

    document.getElementById('nextBtn').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    });
});