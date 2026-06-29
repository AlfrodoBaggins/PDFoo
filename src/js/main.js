const API = "http://127.0.0.1:8456/api";

function icon(svg) {
  return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${svg}</svg>`;
}

const tools = [
  {
    id: "merge",
    icon: icon(`<path d="M12 3v9"/><path d="M9 9l3 3 3-3"/><path d="M4 14h16"/><rect x="4" y="14" width="7" height="7" rx="1"/><rect x="13" y="14" width="7" height="7" rx="1"/>`),
    title: "Merge PDF",
    desc: "Combine multiple PDFs into one document.",
    multiple: true,
    accept: ".pdf",
    options: null,
    endpoint: `${API}/merge`,
    downloadName: "merged.pdf",
  },
  {
    id: "split",
    icon: icon(`<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M12 3v18"/><path d="M9 12l3-3 3 3"/>`),
    title: "Split PDF",
    desc: "Extract pages by range (e.g. 1-3, 5, 7-9) or split all.",
    multiple: false,
    accept: ".pdf",
    options: {
      label: "Page ranges (leave empty for all pages)",
      placeholder: "e.g. 1-3, 5, 7-9",
    },
    endpoint: `${API}/split`,
    downloadName: "split.pdf",
  },
  {
    id: "compress",
    icon: icon(`<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M12 3v7"/><path d="M9 7l3-3 3 3"/><path d="M12 14v7"/><path d="M9 17l3 3 3-3"/>`),
    title: "Compress PDF",
    desc: "Reduce file size. Choose your quality trade-off.",
    multiple: false,
    accept: ".pdf",
    options: {
      type: "select",
      label: "Compression level",
      choices: [
        { value: "maximum", label: "Maximum (smallest file, lower quality)" },
        { value: "recommended", label: "Recommended (good balance)" },
        { value: "minimum", label: "Minimum (high quality, larger file)" },
      ],
    },
    endpoint: `${API}/compress`,
    downloadName: "compressed.pdf",
  },
  {
    id: "rotate",
    icon: icon(`<circle cx="12" cy="12" r="8"/><path d="M12 4l3 3-3 3"/><path d="M12 20l-3-3 3-3"/>`),
    title: "Rotate PDF",
    desc: "Rotate specific pages by 90\u00B0, 180\u00B0, or 270\u00B0. Leave range empty to rotate all pages.",
    multiple: false,
    accept: ".pdf",
    options: {
      type: "group",
      fields: [
        {
          type: "select",
          label: "Rotation angle",
          id: "rotate-angle",
          choices: [
            { value: "90", label: "90\u00B0" },
            { value: "180", label: "180\u00B0" },
            { value: "270", label: "270\u00B0" },
          ],
        },
        {
          type: "text",
          label: "Page range (leave empty for all)",
          id: "rotate-range",
          placeholder: "e.g. 1-3, 5, 7-9",
        },
      ],
    },
    endpoint: `${API}/rotate`,
    downloadName: "rotated.pdf",
  },
  {
    id: "pdf-to-jpg",
    icon: icon(`<rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="M4 17l4-4 3 3 3-3 4 4"/>`),
    title: "PDF to JPG",
    desc: "Convert each PDF page into a high-quality JPG image.",
    multiple: false,
    accept: ".pdf",
    options: {
      label: "Image quality (DPI)",
      type: "select",
      choices: [
        { value: "150", label: "150 DPI (smaller)" },
        { value: "200", label: "200 DPI (balanced)" },
        { value: "300", label: "300 DPI (high quality)" },
      ],
    },
    endpoint: `${API}/pdf-to-jpg`,
    downloadName: "pages.zip",
  },
  {
    id: "jpg-to-pdf",
    icon: icon(`<path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2z"/><circle cx="9" cy="13" r="2"/><path d="M5 18l3-3 2 2 3-3 4 4"/>`),
    title: "JPG to PDF",
    desc: "Convert one or more JPG images into a PDF document.",
    multiple: true,
    accept: ".jpg,.jpeg,.png",
    options: null,
    endpoint: `${API}/jpg-to-pdf`,
    downloadName: "converted.pdf",
  },
];

/* ─── State ─── */
let currentTool = null;
let selectedFiles = [];
let pendingDownload = null;

/* ─── DOM refs ─── */
const appEl = document.getElementById("app");

/* ─── Render ─── */
function render() {
  const toolCards = tools
    .map(
      (t) => `
    <div class="tool-card" data-tool="${t.id}">
      <div class="tool-card-icon">${t.icon}</div>
      <h3>${t.title}</h3>
      <p>${t.desc}</p>
    </div>`
    )
    .join("");

  appEl.innerHTML = `
    <section class="hero">
      <div class="hero-logo">
        <div class="logo-icon">P</div>
        <span class="logo-text">PD<span class="logo-serif">f</span>oo</span>
      </div>
      <h1>PDF tools, <span>right on your desktop</span></h1>
      <p>Merge, split, compress, rotate, and convert PDFs. No uploads to the cloud \u2014 everything stays local.</p>
    </section>

    <div class="tool-grid">${toolCards}</div>

    <footer>PDFoo \u2014 Your documents never leave your machine.</footer>

    <div id="panel-root"></div>
  `;

  document.querySelectorAll(".tool-card").forEach((card) => {
    card.addEventListener("click", () => {
      const id = card.dataset.tool;
      const tool = tools.find((t) => t.id === id);
      openPanel(tool);
    });
  });
}

/* ─── Panel ─── */
function openPanel(tool) {
  currentTool = tool;
  selectedFiles = [];
  pendingDownload = null;
  const panelRoot = document.getElementById("panel-root");

  let optionsHtml = "";
  if (tool.options) {
    if (tool.options.type === "group") {
      optionsHtml = tool.options.fields.map((f) => {
        if (f.type === "select") {
          const opts = f.choices
            .map((c) => `<option value="${c.value}">${c.label}</option>`)
            .join("");
          return `
            <div class="form-group">
              <label>${f.label}</label>
              <select id="${f.id}">${opts}</select>
            </div>`;
        }
        return `
          <div class="form-group">
            <label>${f.label}</label>
            <input type="text" id="${f.id}" placeholder="${f.placeholder || ""}" />
          </div>`;
      }).join("");
    } else if (tool.options.type === "select") {
      const opts = tool.options.choices
        .map((c) => `<option value="${c.value}">${c.label}</option>`)
        .join("");
      optionsHtml = `
        <div class="form-group">
          <label>${tool.options.label}</label>
          <select id="tool-option">${opts}</select>
        </div>`;
    } else {
      optionsHtml = `
        <div class="form-group">
          <label>${tool.options.label}</label>
          <input type="text" id="tool-option" placeholder="${tool.options.placeholder || ""}" />
        </div>`;
    }
  }

  panelRoot.innerHTML = `
    <div class="panel-overlay" id="panel-overlay">
      <div class="panel">
        <div class="panel-header">
          <h2>${tool.icon} ${tool.title}</h2>
          <button class="panel-close" id="panel-close">&times;</button>
        </div>
        <p class="panel-desc">${tool.desc}</p>

        <div class="drop-zone" id="drop-zone">
          <div class="drop-zone-icon">\u{1F4C1}</div>
          <div class="drop-zone-text">
            <strong>Click to browse</strong> or drag files here
          </div>
          <div class="drop-zone-hint">${tool.multiple ? "Select one or more files" : "Select a file"} (${tool.accept})</div>
        </div>

        <ul class="file-list" id="file-list"></ul>

        ${optionsHtml}

        <div id="progress-area"></div>

        <button class="btn btn-primary" id="process-btn" disabled>
          \u2699\uFE0F Process
        </button>
        <div id="result-area"></div>
      </div>
    </div>
  `;

  const overlay = document.getElementById("panel-overlay");
  const closeBtn = document.getElementById("panel-close");
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = tool.accept;
  fileInput.multiple = tool.multiple;
  fileInput.style.display = "none";
  overlay.appendChild(fileInput);

  closeBtn.addEventListener("click", () => panelRoot.innerHTML = "");
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) panelRoot.innerHTML = "";
  });

  dropZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => handleFiles(fileInput.files, tool));

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });
  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    handleFiles(e.dataTransfer.files, tool);
  });

  document.getElementById("process-btn").onclick = () => process(tool);
}

function handleFiles(files, tool) {
  selectedFiles = Array.from(files);
  updateFileList();
  const btn = document.getElementById("process-btn");
  btn.disabled = selectedFiles.length === 0;
}

function updateFileList() {
  const list = document.getElementById("file-list");
  list.innerHTML = selectedFiles
    .map(
      (f, i) =>
        `<li>
          <span>${f.name}</span>
          <span>
            <span class="file-size">${(f.size / 1024 / 1024).toFixed(1)} MB</span>
            <button class="file-remove" data-index="${i}">&times;</button>
          </span>
        </li>`
    )
    .join("");

  list.querySelectorAll(".file-remove").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.dataset.index);
      selectedFiles.splice(idx, 1);
      updateFileList();
      document.getElementById("process-btn").disabled = selectedFiles.length === 0;
    });
  });
}

/* ─── Process ─── */
async function process(tool) {
  const progressArea = document.getElementById("progress-area");
  const resultArea = document.getElementById("result-area");
  const processBtn = document.getElementById("process-btn");

  pendingDownload = null;
  processBtn.onclick = null;
  processBtn.textContent = "\u2699\uFE0F Process";
  progressArea.innerHTML = `
    <div class="progress-bar"><div class="progress-bar-fill" id="progress-fill"></div></div>
    <div class="progress-text" id="progress-text">Processing\u2026</div>
  `;
  resultArea.innerHTML = "";
  processBtn.disabled = true;

  const fill = document.getElementById("progress-fill");
  const progText = document.getElementById("progress-text");
  let p = 0;
  const interval = setInterval(() => {
    p = Math.min(p + Math.random() * 15, 85);
    fill.style.width = p + "%";
  }, 400);

  try {
    const form = new FormData();
    if (tool.multiple) {
      selectedFiles.forEach((f) => form.append("files", f));
    } else {
      form.append("file", selectedFiles[0]);
    }

    const optionEl = document.getElementById("tool-option");
    const angleEl = document.getElementById("rotate-angle");
    const rangeEl = document.getElementById("rotate-range");
    if (optionEl) {
      if (tool.id === "split") {
        form.append("ranges", optionEl.value);
      } else if (tool.id === "compress") {
        form.append("level", optionEl.value);
      } else if (tool.id === "pdf-to-jpg") {
        form.append("dpi", optionEl.value);
      }
    }
    if (angleEl) {
      form.append("angle", angleEl.value);
      if (rangeEl && rangeEl.value.trim()) {
        form.append("ranges", rangeEl.value);
      }
    }

    const res = await fetch(tool.endpoint, { method: "POST", body: form });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    clearInterval(interval);
    fill.style.width = "100%";
    progText.textContent = "Ready";

    const data = await res.json();
    pendingDownload = {
      url: `${API}/download/${data.token}`,
      name: data.name,
    };

    processBtn.disabled = false;
    processBtn.textContent = `\u{1F4E5} Download ${data.name}`;
    processBtn.onclick = () => {
      const a = document.createElement("a");
      a.href = pendingDownload.url;
      a.download = pendingDownload.name;
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      setTimeout(() => document.body.removeChild(a), 1000);
      processBtn.textContent = "\u2705 Done";
      processBtn.onclick = null;
    };
  } catch (err) {
    clearInterval(interval);
    fill.style.width = "0%";
    progText.textContent = "Error: " + err.message;
    processBtn.disabled = false;
    processBtn.onclick = () => process(tool);
    processBtn.textContent = "\u{1F6AB} Try Again";
  }
}

/* ─── Health check ─── */
async function checkBackend() {
  try {
    const res = await fetch(`${API}/health`);
    if (res.ok) return true;
  } catch {}
  return false;
}

/* ─── Init ─── */
(async () => {
  render();
  const ok = await checkBackend();
  if (!ok) {
    const hero = document.querySelector(".hero");
    if (hero) {
      hero.innerHTML += `<p style="margin-top:1rem;color:var(--error);font-size:0.875rem;">\u26A0\uFE0F Backend not running. Start the Python server on port 8456.</p>`;
    }
  }
})();
