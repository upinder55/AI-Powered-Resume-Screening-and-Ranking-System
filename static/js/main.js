/**
 * TalentMatch AI - Client-side interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. File Upload Dropzone handling
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const filePreview = document.getElementById('file-preview');

    if (dropzone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            updateFilePreview(files);
        });

        fileInput.addEventListener('change', () => {
            updateFilePreview(fileInput.files);
        });
    }

    function updateFilePreview(files) {
        if (!filePreview) return;
        filePreview.innerHTML = '';
        if (files.length === 0) return;

        const countHeader = document.createElement('div');
        countHeader.style.fontWeight = '600';
        countHeader.style.fontSize = '0.85rem';
        countHeader.style.color = '#334155';
        countHeader.textContent = `Selected ${files.length} file(s) ready to screen:`;
        filePreview.appendChild(countHeader);

        Array.from(files).forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            const sizeKb = (file.size / 1024).toFixed(1);
            item.innerHTML = `
                <span>📄 <strong>${escapeHtml(file.name)}</strong> (${sizeKb} KB)</span>
                <span class="badge badge-neutral">Ready</span>
            `;
            filePreview.appendChild(item);
        });
    }

    // 2. Leaderboard Live Search & Filter
    const searchInput = document.getElementById('candidateSearch');
    const filterSelect = document.getElementById('verdictFilter');
    const tableBody = document.getElementById('candidatesTableBody');

    if (searchInput && tableBody) {
        const rows = tableBody.getElementsByTagName('tr');

        const filterRows = () => {
            const query = searchInput.value.toLowerCase().trim();
            const verdict = filterSelect ? filterSelect.value.toLowerCase() : 'all';

            for (let row of rows) {
                const text = row.textContent.toLowerCase();
                const rowVerdict = row.getAttribute('data-verdict') ? row.getAttribute('data-verdict').toLowerCase() : '';

                const matchesQuery = !query || text.includes(query);
                const matchesVerdict = verdict === 'all' || rowVerdict.includes(verdict);

                if (matchesQuery && matchesVerdict) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        };

        searchInput.addEventListener('input', filterRows);
        if (filterSelect) {
            filterSelect.addEventListener('change', filterRows);
        }
    }

    // Helper: HTML escaper
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});

// Demo login credentials filler
function fillCredentials(email, password) {
    const emailField = document.getElementById('email');
    const passwordField = document.getElementById('password');
    if (emailField && passwordField) {
        emailField.value = email;
        passwordField.value = password;
        const form = emailField.closest('form');
        if (form) form.submit();
    }
}
