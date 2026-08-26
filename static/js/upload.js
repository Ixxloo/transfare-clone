const MAX_BYTES = 200 * 1024 * 1024;

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const fileList = document.getElementById("file-list");
const uploadBtn = document.getElementById("upload-btn");

let selected = [];
function csrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
function fmt(bytes) {
  const units = ["B", "KB", "MB", "GB"];
  let i = 0, n = bytes;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return n.toFixed(1) + " " + units[i];
}

function render() {
  const total = selected.reduce((s, f) => s + f.size, 0);
  fileList.innerHTML = selected
    .map(f => `<div>${f.name} — ${fmt(f.size)}</div>`)
    .join("");

  if (total > MAX_BYTES) {
    fileList.innerHTML += `<div class="error">Too large: ${fmt(total)} of 200 MB max</div>`;
    uploadBtn.disabled = true;
  } else {
    uploadBtn.disabled = selected.length === 0;
  }
}

function addFiles(files) {
  selected = selected.concat(Array.from(files));
  render();
}

dropzone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", e => addFiles(e.target.files));

dropzone.addEventListener("dragover", e => {
  e.preventDefault();
  dropzone.classList.add("dragging");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragging"));
dropzone.addEventListener("drop", e => {
  e.preventDefault();
  dropzone.classList.remove("dragging");
  addFiles(e.dataTransfer.files);
});

// PUT one file to R2, reporting progress
function putFile(url, file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", url);
    xhr.setRequestHeader("Content-Type", file.type || "application/octet-stream");
    xhr.upload.onprogress = e => {
      if (e.lengthComputable) onProgress(e.loaded / e.total);
    };
    xhr.onload = () => (xhr.status < 300 ? resolve() : reject(new Error(xhr.status)));
    xhr.onerror = () => reject(new Error("Network error"));
    xhr.send(file);
  });
}

uploadBtn.addEventListener("click", async () => {
  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading…";

  try {
    const initRes = await fetch("/api/upload/init/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
      body: JSON.stringify({
        files: selected.map(f => ({ name: f.name, size: f.size, type: f.type })),
      }),
    });
    const init = await initRes.json();
    if (!initRes.ok) throw new Error(init.error);

    for (let i = 0; i < selected.length; i++) {
      const target = init.uploads.find(u => u.name === selected[i].name);
      await putFile(init.uploads[i].url, selected[i], pct => {
        uploadBtn.textContent = `Uploading ${i + 1}/${selected.length} — ${Math.round(pct * 100)}%`;
      });
    }

    const doneRes = await fetch("/api/upload/complete/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
      body: JSON.stringify({ token: init.token }),
    });
    const done = await doneRes.json();
    if (!doneRes.ok) throw new Error(done.error);

    const link = window.location.origin + done.download_url;
    fileList.innerHTML = `<div class="success">Ready: <a href="${link}">${link}</a></div>`;
    uploadBtn.textContent = "Done";

  } catch (err) {
    fileList.innerHTML += `<div class="error">Failed: ${err.message}</div>`;
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Try again";
  }
});