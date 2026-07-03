const form = document.getElementById("convert-form");
const dropzone = document.getElementById("dropzone");
const dropzoneLabel = document.getElementById("dropzone-label");
const fileInput = document.getElementById("file-input");
const urlInput = document.getElementById("url-input");
const ocrToggle = document.getElementById("ocr-toggle");
const ocrLang = document.getElementById("ocr-lang");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const previewEl = document.getElementById("preview");
const warningsEl = document.getElementById("warnings");
const downloadBtn = document.getElementById("download-btn");

let lastPayload = null;

dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});
dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  if (event.dataTransfer.files.length) {
    fileInput.files = event.dataTransfer.files;
    updateDropzoneLabel();
  }
});
fileInput.addEventListener("change", updateDropzoneLabel);

function updateDropzoneLabel() {
  dropzoneLabel.textContent = fileInput.files.length
    ? fileInput.files[0].name
    : "Glissez un fichier ici, ou cliquez pour le choisir";
}

function triggerDownload(data) {
  const binary = atob(data.content_b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: data.mimetype });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = data.filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function showError(message) {
  resultEl.hidden = false;
  warningsEl.innerHTML = `<p class="error">${message}</p>`;
  previewEl.textContent = "";
  downloadBtn.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultEl.hidden = true;
  statusEl.hidden = false;
  statusEl.textContent = "Conversion en cours…";

  const formData = new FormData();
  if (fileInput.files.length) {
    formData.append("file", fileInput.files[0]);
  }
  if (urlInput.value.trim()) {
    formData.append("url", urlInput.value.trim());
  }
  formData.append("ocr", ocrToggle.checked ? "on" : "off");
  formData.append("ocr_lang", ocrLang.value);

  try {
    const response = await fetch("/convert", { method: "POST", body: formData });
    const data = await response.json();
    statusEl.hidden = true;

    if (!response.ok) {
      showError(data.error || "Une erreur est survenue.");
      return;
    }

    lastPayload = data;
    resultEl.hidden = false;
    previewEl.textContent = data.preview;
    warningsEl.innerHTML = data.warnings.length
      ? `<ul>${data.warnings.map((w) => `<li>${w}</li>`).join("")}</ul>`
      : "";
    downloadBtn.hidden = false;
    downloadBtn.textContent = `Télécharger ${data.filename}`;
    triggerDownload(data);
  } catch (error) {
    statusEl.hidden = true;
    showError(`Erreur inattendue : ${error}`);
  }
});

downloadBtn.addEventListener("click", () => {
  if (lastPayload) {
    triggerDownload(lastPayload);
  }
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/sw.js").catch(() => {});
}
