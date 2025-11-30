// Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const fileNameDisplay = document.getElementById('fileName');

const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');

const resultPanel = document.getElementById('resultPanel');
const docTypeEl = document.getElementById('docType');
const resultMessage = document.getElementById('resultMessage');
const previewText = document.getElementById('previewText');
const meterFill = document.getElementById('meterFill');
const confidenceText = document.getElementById('confidenceText');
const downloadJson = document.getElementById('downloadJson');
const uploadAnother = document.getElementById('uploadAnother');

// --------------------------------
// FILE SELECTION HANDLING
// --------------------------------

// Click on “browse”
browseBtn.addEventListener('click', () => fileInput.click());

// Updating UI when a file is selected
fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    fileNameDisplay.textContent = "📄 " + fileInput.files[0].name;
  }
});

// Drag-and-drop handlers
dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('drag');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('drag');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('drag');

  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    fileNameDisplay.textContent = "📄 " + e.dataTransfer.files[0].name;
  }
});

// Clear button
clearBtn.addEventListener('click', () => {
  fileInput.value = "";
  fileNameDisplay.textContent = "";
  resultPanel.classList.add('hidden');
});

// --------------------------------
// UPLOAD HANDLING
// --------------------------------

uploadBtn.addEventListener('click', async () => {
  if (!fileInput.files.length) {
    alert("Please choose a file first.");
    return;
  }

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading...";

  const fd = new FormData();
  fd.append("file", fileInput.files[0]);

  try {
    const res = await fetch("/upload", { method: "POST", body: fd });
    const data = await res.json();

    // Show the result panel
    resultPanel.classList.remove("hidden");

    docTypeEl.textContent = data.document_type?.toUpperCase() || "UNKNOWN";
    resultMessage.textContent = data.message || "";
    previewText.textContent = data.preview_text || "";

    // Confidence meter
    let conf = parseFloat(data.confidence) || 0;
    conf = Math.max(0, Math.min(100, conf));
    confidenceText.textContent = conf + "%";
    meterFill.style.width = conf + "%";

    if (conf >= 70) meterFill.style.background = "linear-gradient(90deg,#4ade80,#8bffb0)";
    else if (conf >= 35) meterFill.style.background = "linear-gradient(90deg,#ffd166,#ffb86b)";
    else meterFill.style.background = "linear-gradient(90deg,#ff6b6b,#ff9b9b)";

    // Download JSON
    downloadJson.onclick = () => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `cleverdocs_${Date.now()}.json`;
      a.click();

      URL.revokeObjectURL(url);
    };

    uploadAnother.onclick = () => {
      resultPanel.classList.add("hidden");
      fileInput.value = "";
      fileNameDisplay.textContent = "";
    };

  } catch (err) {
    console.error("Upload failed:", err);
    alert("Upload failed. Check the console.");
  }

  uploadBtn.disabled = false;
  uploadBtn.textContent = "Upload & Classify";
});
