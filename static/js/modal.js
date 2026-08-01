document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteModal');
    const deleteButtons = document.querySelectorAll('[data-toggle="modal"]'); // Busca por atributo de datos
    const confirmLink = document.getElementById('confirmDeleteLink');
    const closeBtn = document.querySelector('.close-btn');
    const cancelBtn = document.querySelector('.cancel-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Aseguramos que solo el botón de borrado de usuario abra este modal específico
            if (this.getAttribute('data-target') === '#deleteModal') {
                confirmLink.href = this.href;
                modal.style.display = 'flex';
            }
        });
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
});