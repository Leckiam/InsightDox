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
    document.getElementById('userForm').action = "/addUser/"; // o usa {% url 'addUser' %} en el HTML

    // Limpiar inputs
    document.getElementById('modalUsername').value = "";
    document.getElementById('modalUsername').disabled = false;
    document.getElementById('modalCorreo').value = "";
    document.getElementById('modalCorreo').disabled = false;
    document.getElementById('modalPassword').value = "";
    document.getElementById('modalPassword').required = true
    document.getElementById('modalRol').value = "";
    document.getElementById('modalAvatar').value = "";

    // Limpiar vista previa de imagen
    const avatarPreview = document.getElementById('avatarPreview');
    if (avatarPreview) avatarPreview.src = "";
}

// --- Modal para editar usuario ---
function abrirModalEditar(id, username, correo, rolId, avatar_url) {
    document.getElementById('userModalLabel').innerText = "Editar usuario";
    document.getElementById('userForm').action = `/editUser/${id}/`;

    document.getElementById('modalUsername').value = username;
    document.getElementById('modalUsername').disabled = true;
    document.getElementById('modalCorreo').value = correo;
    document.getElementById('modalCorreo').disabled = true;
    document.getElementById('modalPassword').value = "";
    document.getElementById('modalPassword').required = false
    document.getElementById('modalRol').value = rolId;
    document.getElementById('modalAvatar').value = "";

    // También puedes actualizar la vista previa si tienes el avatar actual del usuario
    const avatarPreview = document.getElementById('avatarPreview');
    if (avatarPreview && correo) {
        avatarPreview.src = avatar_url; // Ejemplo, ajusta según tu modelo
    }
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
        document.getElementById('nextBtn').disabled = page === totalPages;
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