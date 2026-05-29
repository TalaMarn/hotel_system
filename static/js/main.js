const receiptInput = document.querySelector('input[type="file"][name="receipt"]');
const receiptPreview = document.querySelector('#receiptPreview');

function showReceiptPreview(file) {
  if (!receiptPreview) return;

  receiptPreview.innerHTML = '';

  if (!file) {
    receiptPreview.classList.remove('show');
    return;
  }

  const fileName = document.createElement('strong');
  fileName.textContent = file.name;
  receiptPreview.appendChild(fileName);

  if (file.type.startsWith('image/')) {
    const image = document.createElement('img');
    image.alt = 'Receipt preview';
    image.src = URL.createObjectURL(file);
    image.onload = () => URL.revokeObjectURL(image.src);
    receiptPreview.appendChild(image);
  } else {
    const note = document.createElement('p');
    note.textContent = 'Preview is available for image receipts only.';
    receiptPreview.appendChild(note);
  }

  receiptPreview.classList.add('show');
}

if (receiptInput) {
  receiptInput.addEventListener('change', () => {
    showReceiptPreview(receiptInput.files[0]);
  });
}

const navToggle = document.querySelector('[data-nav-toggle]');
const navLinks = document.querySelector('[data-nav-links]');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
}

const tabButtons = document.querySelectorAll('[data-tab-target]');
const tabPanels = document.querySelectorAll('[data-tab-panel]');

tabButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = button.dataset.tabTarget;

    tabButtons.forEach((item) => item.classList.remove('active'));
    tabPanels.forEach((panel) => panel.hidden = true);

    button.classList.add('active');
    const panel = document.querySelector(`[data-tab-panel="${target}"]`);
    if (panel) {
      panel.hidden = false;
    }
  });
});
