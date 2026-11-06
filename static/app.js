(() => {
  "use strict";

  const form = document.getElementById("analysisForm");
  const questionInput = document.getElementById("questions");
  const fileInput = document.getElementById("fileInput");
  const dropzone = document.getElementById("dropzone");
  const fileList = document.getElementById("fileList");
  const runButton = document.getElementById("runButton");
  const resetButton = document.getElementById("resetButton");
  const resultsPanel = document.getElementById("resultsPanel");
  const resultContent = document.getElementById("resultContent");
  const resultMeta = document.getElementById("resultMeta");
  const errorBox = document.getElementById("errorBox");
  const copyButton = document.getElementById("copyButton");
  const downloadButton = document.getElementById("downloadButton");
  const charCount = document.getElementById("charCount");
  const apiStatus = document.getElementById("apiStatus");

  const MAX_FILE_BYTES = 25 * 1024 * 1024;
  const MAX_TOTAL_BYTES = 50 * 1024 * 1024;
  const allowedExtensions = [".csv", ".xlsx", ".xls", ".json", ".parquet", ".zip", ".tar.gz", ".tgz"];
  let selectedFiles = [];
  let latestResult = null;

  function fileExtension(name) {
    const lower = name.toLowerCase();
    return allowedExtensions.find((ext) => lower.endsWith(ext)) || "";
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function setLoading(loading) {
    runButton.disabled = loading;
    runButton.classList.toggle("loading", loading);
    runButton.querySelector(".button-label").textContent = loading ? "Analyzing…" : "Run analysis";
    runButton.setAttribute("aria-busy", String(loading));
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    errorBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function clearError() {
    errorBox.textContent = "";
    errorBox.hidden = true;
  }

  function renderFiles() {
    fileList.replaceChildren();
    selectedFiles.forEach((file, index) => {
      const item = document.createElement("div");
      item.className = "file-item";
      const type = document.createElement("div");
      type.className = "file-type";
      type.textContent = fileExtension(file.name).replace(".", "").replace(".gz", "").toUpperCase().slice(0, 6);
      const info = document.createElement("div");
      info.className = "file-info";
      const name = document.createElement("div");
      name.className = "file-name";
      name.textContent = file.name;
      name.title = file.name;
      const size = document.createElement("div");
      size.className = "file-size";
      size.textContent = formatBytes(file.size);
      info.append(name, size);
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "remove-file";
      remove.setAttribute("aria-label", "Remove " + file.name);
      remove.textContent = "×";
      remove.addEventListener("click", () => {
        selectedFiles.splice(index, 1);
        renderFiles();
      });
      item.append(type, info, remove);
      fileList.append(item);
    });
  }

  function addFiles(fileCollection) {
    clearError();
    const incoming = Array.from(fileCollection || []);
    const existing = new Set(selectedFiles.map((file) => file.name + ":" + file.size + ":" + file.lastModified));
    const accepted = [];
    const rejected = [];

    incoming.forEach((file) => {
      const key = file.name + ":" + file.size + ":" + file.lastModified;
      if (existing.has(key)) return;
      if (!fileExtension(file.name)) {
        rejected.push(file.name + " (unsupported format)");
        return;
      }
      if (file.size > MAX_FILE_BYTES) {
        rejected.push(file.name + " (over 25 MB)");
        return;
      }
      accepted.push(file);
      existing.add(key);
    });

    const next = selectedFiles.concat(accepted);
    const total = next.reduce((sum, file) => sum + file.size, 0);
    if (total > MAX_TOTAL_BYTES) {
      showError("These files exceed the 50 MB total upload limit. Remove a file or choose a smaller dataset.");
      return;
    }
    selectedFiles = next;
    renderFiles();
    if (rejected.length) {
      showError("Some files were not added: " + rejected.join(", ") + ".");
    }
  }

  function createAnswerValue(value) {
    const wrapper = document.createElement("div");
    wrapper.className = "answer-value";

    if (typeof value === "string" && /^data:image\/(png|webp);base64,/i.test(value)) {
      const image = document.createElement("img");
      image.className = "result-image";
      image.alt = "Chart generated from the analysis";
      image.loading = "lazy";
      image.src = value;
      wrapper.append(image);
      return wrapper;
    }

    if (value !== null && typeof value === "object") {
      wrapper.textContent = JSON.stringify(value, null, 2);
    } else if (typeof value === "string") {
      wrapper.textContent = value;
    } else {
      wrapper.textContent = String(value);
    }
    return wrapper;
  }

  function renderResults(data, elapsedMs) {
    latestResult = data;
    resultContent.replaceChildren();
    const isArray = Array.isArray(data);
    const entries = isArray
      ? data.map((value, index) => ["Result " + String(index + 1).padStart(2, "0"), value])
      : (data && typeof data === "object")
        ? Object.entries(data)
        : [["Result", data]];

    if (!entries.length) {
      const empty = document.createElement("div");
      empty.className = "answer-card";
      empty.textContent = "The analysis completed but returned no result items.";
      resultContent.append(empty);
    }

    entries.forEach(([label, value], index) => {
      const card = document.createElement("article");
      card.className = "answer-card";
      const heading = document.createElement("div");
      heading.className = "answer-label";
      if (isArray) {
        const n = document.createElement("span");
        n.className = "answer-index";
        n.textContent = String(index + 1).padStart(2, "0") + "  /  ";
        heading.append(n);
      }
      heading.append(document.createTextNode(String(label)));
      card.append(heading, createAnswerValue(value));
      resultContent.append(card);
    });

    const count = entries.length + (entries.length === 1 ? " result" : " results");
    resultMeta.textContent = count + " · completed in " + (elapsedMs / 1000).toFixed(1) + " seconds";
    resultsPanel.hidden = false;
    resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function checkApi() {
    try {
      const response = await fetch("/health", { method: "GET", cache: "no-store" });
      if (!response.ok) throw new Error("API unavailable");
      apiStatus.classList.add("online");
      apiStatus.classList.remove("offline");
      apiStatus.lastElementChild.textContent = "API online";
    } catch (_error) {
      apiStatus.classList.add("offline");
      apiStatus.classList.remove("online");
      apiStatus.lastElementChild.textContent = "API unavailable";
    }
  }

  questionInput.addEventListener("input", () => {
    charCount.textContent = questionInput.value.length.toLocaleString() + " / 12,000";
  });

  document.querySelectorAll(".example-pill").forEach((button) => {
    button.addEventListener("click", () => {
      questionInput.value = button.dataset.prompt || "";
      questionInput.dispatchEvent(new Event("input"));
      questionInput.focus();
    });
  });

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      fileInput.click();
    }
  });
  fileInput.addEventListener("change", () => {
    addFiles(fileInput.files);
    fileInput.value = "";
  });
  ["dragenter", "dragover"].forEach((type) => {
    dropzone.addEventListener(type, (event) => {
      event.preventDefault();
      dropzone.classList.add("drag-over");
    });
  });
  ["dragleave", "drop"].forEach((type) => {
    dropzone.addEventListener(type, (event) => {
      event.preventDefault();
      dropzone.classList.remove("drag-over");
    });
  });
  dropzone.addEventListener("drop", (event) => addFiles(event.dataTransfer.files));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();
    resultsPanel.hidden = true;

    const question = questionInput.value.trim();
    if (!question) {
      showError("Add at least one question before running the analysis.");
      questionInput.focus();
      return;
    }
    const payload = new FormData();
    payload.append("questions.txt", new Blob([question], { type: "text/plain;charset=utf-8" }), "questions.txt");
    selectedFiles.forEach((file, index) => payload.append("data_file_" + index, file, file.name));

    setLoading(true);
    const startedAt = performance.now();
    try {
      const response = await fetch("/api/", { method: "POST", body: payload });
      const raw = await response.text();
      let data;
      try {
        data = raw ? JSON.parse(raw) : null;
      } catch (_parseError) {
        throw new Error("The server returned an unexpected response. Please try again.");
      }
      if (!response.ok) {
        const detail = data && typeof data === "object" ? (data.detail || data.message) : null;
        throw new Error(detail || ("Analysis failed (HTTP " + response.status + ")."));
      }
      renderResults(data, performance.now() - startedAt);
    } catch (error) {
      showError(error.message || "Something went wrong while contacting the analysis service.");
    } finally {
      setLoading(false);
    }
  });

  resetButton.addEventListener("click", () => {
    questionInput.value = "";
    questionInput.dispatchEvent(new Event("input"));
    selectedFiles = [];
    fileInput.value = "";
    renderFiles();
    clearError();
    resultsPanel.hidden = true;
    resultContent.replaceChildren();
    latestResult = null;
    questionInput.focus();
  });

  copyButton.addEventListener("click", async () => {
    if (latestResult === null) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(latestResult, null, 2));
      copyButton.textContent = "Copied";
      window.setTimeout(() => { copyButton.textContent = "Copy JSON"; }, 1500);
    } catch (_error) {
      showError("Clipboard access is unavailable in this browser. Use Download instead.");
    }
  });

  downloadButton.addEventListener("click", () => {
    if (latestResult === null) return;
    const blob = new Blob([JSON.stringify(latestResult, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "tds-analysis-results.json";
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  });

  checkApi();
  window.setInterval(checkApi, 60000);
})();
