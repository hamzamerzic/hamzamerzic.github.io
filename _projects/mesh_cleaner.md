---
layout: page
title: Mesh Cleaner
description: Clean and process 3D mesh files for use in physics-based simulation environments
img: assets/img/objects.png
permalink: /mesh_cleaner/
importance: 1
category: fun
giscus_comments: true
---

<p>
  Mesh Cleaner is a tool that cleans 3D mesh files and computes their geometric properties such as volume, center of mass, and moments of inertia. The idea behind this project was to automate the tedious process of preparing 3D models for use in Gazebo—as explained in the <a href="https://classic.gazebosim.org/tutorials?tut=inertia" target="_blank">classic Gazebo tutorial</a>.
</p>

<p>Supported file formats: <strong>.stl, .obj, .dae</strong> (max size: 20MB)</p>

<form id="uploadForm" onsubmit="event.preventDefault(); uploadFile();">
  <label for="fileInput"><strong>Select or drop a 3D model:</strong></label>
  <div id="dropArea">
    <input type="file" id="fileInput" accept=".stl,.obj,.dae" required hidden />
    <div id="dropText">📂 Drop file here or click to browse</div>
  </div>
  <br>

<label for="massInput"><strong>Mass (kg):</strong></label>
<input type="number" id="massInput" step="any" value="1.0" min="0.001" required />
<br><br>

  <details>
    <summary><strong>Advanced options</strong></summary>
    <label>
      <input type="checkbox" id="saveNormals" />
      Save vertex normals
      <br><small style="opacity: 0.75;">(May help with rendering, but increases file size.)</small>
    </label><br>
    <label>
      <input type="checkbox" id="useConvexHull" />
      Generate convex hull
      <br><small style="opacity: 0.75;">(Useful for models with holes or open surfaces.)</small>
    </label>
  </details>
  <br>

<button type="submit">🚀 Upload & Clean</button>

</form>

<hr />
<p><strong>Results:</strong></p>
<p id="usageTip" style="display:none;">
  <em>The XML snippet below (inside <code>&lt;inertial&gt;</code>) can be used in URDF/SDF robot model files.</em>
</p>
<pre id="response">Waiting for upload...</pre>
<a id="downloadLink" style="display:none;" download>⬇ Download Cleaned Mesh</a>
<a id="view3DLink" style="display:none;" target="_blank">🔍 View in 3D Viewer</a>

<p style="margin-top: 2em;">
  ✨ This tool was <a href="https://hamzamerzic.info/blog/2025/website-migration/">modernized</a> from my earlier WordPress setup.<br />
  If you notice any regressions or bugs, please reach out or comment below—I’d love to hear from you.
</p>

<script>
document.addEventListener("DOMContentLoaded", () => {
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const dropText = document.getElementById("dropText");

  const updateDropText = () => {
    if (fileInput.files.length > 0) {
      dropText.textContent = `📁 Selected: ${fileInput.files[0].name}`;
    } else {
      dropText.textContent = "📂 Drop file here or click to browse";
    }
  };

  dropArea.addEventListener("click", () => fileInput.click());

  ["dragenter", "dragover"].forEach(event =>
    dropArea.addEventListener(event, e => {
      e.preventDefault();
      dropArea.classList.add("highlight");
    })
  );

  ["dragleave", "drop"].forEach(event =>
    dropArea.addEventListener(event, e => {
      e.preventDefault();
      dropArea.classList.remove("highlight");
    })
  );

  dropArea.addEventListener("drop", e => {
    fileInput.files = e.dataTransfer.files;
    updateDropText();
  });

  fileInput.addEventListener("change", updateDropText);
});

async function uploadFile() {
  const file = document.getElementById("fileInput").files[0];
  const mass = document.getElementById("massInput").value;
  const saveNormals = document.getElementById("saveNormals").checked;
  const useConvexHull = document.getElementById("useConvexHull").checked;
  const responseEl = document.getElementById("response");
  const linkEl = document.getElementById("downloadLink");
  const viewLinkEl = document.getElementById("view3DLink");
  const usageTip = document.getElementById("usageTip");

  if (!file) return alert("Please select a file.");
  if (file.size > 20 * 1024 * 1024) return alert("File size must be under 20MB.");
  const validExtensions = ['.stl', '.obj', '.dae'];
  if (!validExtensions.some(ext => file.name.toLowerCase().endsWith(ext)))
    return alert("Unsupported file format. Please upload a .stl, .obj, or .dae file.");

  responseEl.textContent = "⏳ Uploading and processing...";
  usageTip.style.display = linkEl.style.display = viewLinkEl.style.display = "none";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("mass", mass);
  formData.append("save_normals", saveNormals);
  formData.append("use_convex_hull", useConvexHull);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch("https://mesh-cleaner-692118822266.europe-west1.run.app/upload", {
      method: "POST",
      body: formData,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    const data = await res.json();

    if (!res.ok) {
      responseEl.textContent = "❌ Error: " + (data.error || "Unknown error.");
      return;
    }

    responseEl.textContent = data.metrics;
    usageTip.style.display = "block";

    const cleanedMeshURL = `https://mesh-cleaner-692118822266.europe-west1.run.app${data.download_url}`;
    linkEl.href = cleanedMeshURL;
    linkEl.style.display = "inline";

    viewLinkEl.href = `/3d-viz/?file=${encodeURIComponent(cleanedMeshURL)}`;
    viewLinkEl.style.display = "inline";
  } catch (err) {
    responseEl.textContent = "❌ Upload failed: " + (err.name === "AbortError" ? "Timeout" : err.message);
  }
}
</script>

<style>
#uploadForm {
  padding: 1em;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 12px;
  max-width: 500px;
}

input[type="number"],
#uploadForm button {
  font-size: 1.1em;
  padding: 0.5em;
  margin-top: 0.3em;
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: var(--input-bg, #fff);
  color: black;
}

#uploadForm button {
  background-color: #12b075;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1em;
  color: white;
  transition: background 0.2s ease;
}

#uploadForm button:hover {
  background-color: #0e8d5d;
}

#dropArea {
  border: 2px dashed #bbb;
  padding: 1.5em;
  text-align: center;
  cursor: pointer;
  border-radius: 10px;
  transition: background 0.3s ease;
}

#dropArea.highlight {
  background: #e0ffe8;
}

#dropText {
  font-size: 0.95em;
  color: inherit;
}

pre {
  padding: 1em;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #eee;
  border-radius: 8px;
}

#downloadLink,
#view3DLink {
  display: inline-block;
  margin-top: 1em;
  padding: 0.5em;
  width: 100%;
  box-sizing: border-box;
  background-color: #12b075;
  border-radius: 8px;
  color: white;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

#downloadLink:hover,
#view3DLink:hover {
  background-color: #0e8d5d;
}
</style>
