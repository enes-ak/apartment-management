function panoyaKopyala(elementId) {
    const metin = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(metin).then(function () {
        bildirimGoster('Kopyalandi!');
    });
}

function bildirimGoster(mesaj, tip = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${tip} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${mesaj}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

document.addEventListener('htmx:afterRequest', function (event) {
    const mesaj = event.detail.xhr.getResponseHeader('X-Bildirim');
    if (mesaj) {
        bildirimGoster(decodeURIComponent(mesaj));
    }
});
