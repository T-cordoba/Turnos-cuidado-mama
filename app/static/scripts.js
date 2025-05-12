function confirmarCancelacion(turno, nombre, fecha, boton) {
    Swal.fire({
        title: '¿Confirmar cancelación?',
        text: `¿Estás seguro de que quieres cancelar el turno de ${turno} reservado por ${nombre} para el día ${fecha}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#28a745', // Verde
        cancelButtonColor: '#dc3545', // Rojo
        confirmButtonText: 'Sí, cancelar',
        cancelButtonText: 'No'
    }).then((result) => {
        if (result.isConfirmed) {
            boton.closest('form').submit();
        }
    });
}

// Verifica si hay un ancla en la URL (para reservas)
const ancla = window.location.hash;
if (ancla) {
    const elemento = document.querySelector(ancla);
    if (elemento) {
        elemento.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Guarda la posición del scroll en localStorage (para reservas)
function guardarPosicionScroll() {
    localStorage.setItem('posicionScroll', window.scrollY);
}

// Restaura la posición del scroll al cargar la página con animación (para reservas)
document.addEventListener('DOMContentLoaded', () => {
    const posicionScroll = localStorage.getItem('posicionScroll');
    if (posicionScroll) {
        const targetPosition = parseInt(posicionScroll, 10);
        const startPosition = window.scrollY;
        const distance = targetPosition - startPosition;
        const duration = 1000; // Duración de la animación en milisegundos
        let startTime = null;

        // Función de easing (ease-in-out)
        function easeInOutQuad(t) {
            return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        }

        // Función para animar el desplazamiento
        function animarScroll(currentTime) {
            if (!startTime) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1); // Progreso entre 0 y 1
            const easedProgress = easeInOutQuad(progress); // Aplica la función de easing

            // Calcula la posición actual
            const scrollPosition = startPosition + distance * easedProgress;
            window.scrollTo(0, scrollPosition);

            // Si la animación no ha terminado, continúa
            if (timeElapsed < duration) {
                requestAnimationFrame(animarScroll);
            } else {
                localStorage.removeItem('posicionScroll'); // Limpia el valor después de usarlo
            }
        }

        // Inicia la animación
        requestAnimationFrame(animarScroll);
    }

    // Oculta automáticamente el mensaje flash después de 5 segundos
    const mensajes = document.querySelector('.mensajes');
    if (mensajes) {
        setTimeout(() => {
            mensajes.style.transition = 'opacity 0.5s ease';
            mensajes.style.opacity = '0';
            setTimeout(() => mensajes.remove(), 500); // Elimina el elemento después de la transición
        }, 5000); // 5 segundos
    }

    // Detecta si se realizó una cancelación y hace scroll al inicio
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('scrollToTop') === 'true') {
        setTimeout(() => {
            window.scrollTo({ top: 0, behavior: 'smooth' }); // Hace scroll al inicio de la página
        }, 100); // Pequeño retraso para evitar conflictos
    }
});