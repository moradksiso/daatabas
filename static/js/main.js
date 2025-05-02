// تهيئة العناصر عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تغيير شريط التنقل عند التمرير
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Animación de entrada para las tarjetas de archivos
    const fileCards = document.querySelectorAll('.card');
    fileCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });

    // Efecto hover para las tarjetas
    fileCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
        });
    });

    // Inicializar contador de caracteres para campos de texto
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counterEl = document.createElement('div');
        counterEl.className = 'text-muted small text-end mt-1';
        counterEl.innerHTML = `<span class="current-count">${textarea.value.length}</span>/${maxLength}`;
        textarea.parentNode.insertBefore(counterEl, textarea.nextSibling);

        textarea.addEventListener('input', function() {
            const currentCount = this.value.length;
            const counterSpan = this.parentNode.querySelector('.current-count');
            counterSpan.textContent = currentCount;

            if (currentCount > maxLength * 0.8) {
                counterSpan.classList.add('text-warning');
            } else {
                counterSpan.classList.remove('text-warning');
            }

            if (currentCount > maxLength * 0.95) {
                counterSpan.classList.add('text-danger');
            } else {
                counterSpan.classList.remove('text-danger');
            }
        });
    });

    // Inicializar filtros de búsqueda
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            if (this.value.length > 2) {
                document.getElementById('searchClearBtn').style.display = 'block';
            } else {
                document.getElementById('searchClearBtn').style.display = 'none';
            }
        });

        const clearBtn = document.getElementById('searchClearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', function() {
                searchInput.value = '';
                this.style.display = 'none';
                document.getElementById('searchFilterForm').submit();
            });
        }
    }

    // Inicializar vista previa de imágenes al subir archivos
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const previewContainer = document.getElementById('filePreview');
            if (!previewContainer) return;

            previewContainer.innerHTML = '';

            if (this.files && this.files[0]) {
                const file = this.files[0];
                const reader = new FileReader();

                reader.onload = function(e) {
                    if (file.type.startsWith('image/')) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'img-fluid rounded';
                        previewContainer.appendChild(img);
                    } else {
                        const icon = document.createElement('div');
                        icon.className = 'text-center p-4';

                        if (file.type === 'application/pdf') {
                            icon.innerHTML = '<i class="bi bi-file-pdf text-danger" style="font-size: 4rem;"></i>';
                        } else if (file.type.includes('word')) {
                            icon.innerHTML = '<i class="bi bi-file-word text-primary" style="font-size: 4rem;"></i>';
                        } else if (file.type.includes('excel') || file.type.includes('spreadsheet')) {
                            icon.innerHTML = '<i class="bi bi-file-excel text-success" style="font-size: 4rem;"></i>';
                        } else {
                            icon.innerHTML = '<i class="bi bi-file-earmark text-secondary" style="font-size: 4rem;"></i>';
                        }

                        const fileName = document.createElement('p');
                        fileName.className = 'mt-2';
                        fileName.textContent = file.name;

                        icon.appendChild(fileName);
                        previewContainer.appendChild(icon);
                    }
                }

                reader.readAsDataURL(file);
            }
        });
    }
});

// Función para mostrar alertas personalizadas
function showAlert(message, type = 'info', duration = 5000) {
    // Crear el elemento de alerta
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show custom-alert`;

    // Añadir icono según el tipo
    let icon = '';
    if (type === 'success') {
        icon = '<i class="bi bi-check-circle-fill me-2"></i>';
    } else if (type === 'danger') {
        icon = '<i class="bi bi-exclamation-triangle-fill me-2"></i>';
    } else if (type === 'warning') {
        icon = '<i class="bi bi-exclamation-circle-fill me-2"></i>';
    } else {
        icon = '<i class="bi bi-info-circle-fill me-2"></i>';
    }

    // Añadir contenido
    alertEl.innerHTML = `
        ${icon}${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Añadir al DOM
    document.body.appendChild(alertEl);

    // Posicionar la alerta
    alertEl.style.position = 'fixed';
    alertEl.style.top = '20px';
    alertEl.style.right = '20px';
    alertEl.style.zIndex = '9999';
    alertEl.style.minWidth = '300px';
    alertEl.style.maxWidth = '500px';
    alertEl.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
    alertEl.style.opacity = '0';
    alertEl.style.transform = 'translateY(-20px)';
    alertEl.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

    // Mostrar la alerta con animación
    setTimeout(() => {
        alertEl.style.opacity = '1';
        alertEl.style.transform = 'translateY(0)';
    }, 10);

    // Ocultar la alerta después del tiempo especificado
    setTimeout(() => {
        alertEl.style.opacity = '0';
        alertEl.style.transform = 'translateY(-20px)';

        // Eliminar del DOM después de la animación
        setTimeout(() => {
            alertEl.remove();
        }, 300);
    }, duration);

    // Permitir cerrar la alerta haciendo clic en el botón
    const closeBtn = alertEl.querySelector('.btn-close');
    closeBtn.addEventListener('click', function() {
        alertEl.style.opacity = '0';
        alertEl.style.transform = 'translateY(-20px)';

        setTimeout(() => {
            alertEl.remove();
        }, 300);
    });
}

// Función para confirmar acciones peligrosas
function confirmAction(message, callback) {
    // Crear el modal de confirmación
    const modalEl = document.createElement('div');
    modalEl.className = 'modal fade';
    modalEl.id = 'confirmActionModal';
    modalEl.tabIndex = '-1';
    modalEl.setAttribute('aria-hidden', 'true');

    modalEl.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-warning text-white">
                    <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill me-2"></i>تأكيد</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-danger" id="confirmBtn">تأكيد</button>
                </div>
            </div>
        </div>
    `;

    // Añadir al DOM
    document.body.appendChild(modalEl);

    // Inicializar el modal
    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    // Manejar la confirmación
    const confirmBtn = document.getElementById('confirmBtn');
    confirmBtn.addEventListener('click', function() {
        modal.hide();
        if (typeof callback === 'function') {
            callback();
        }
    });

    // Eliminar el modal del DOM cuando se cierre
    modalEl.addEventListener('hidden.bs.modal', function() {
        modalEl.remove();
    });
}
