---
layout: page
title: Mesh Cleaner
description: Clean and process 3D mesh files for use in physics-based robotics simulation environments
img: assets/img/objects.png
permalink: /mesh_cleaner/
importance: 1
category: fun
---

<h2>Mesh Cleaner</h2>
<p>
  Mesh Cleaner is a tool that cleans 3D mesh files and computes their geometric properties such as volume, center of mass, and moments of inertia. The idea behind this project was to automate the tedious process of preparing 3D models for use in Gazebo—as explained in the <a href="https://classic.gazebosim.org/tutorials?tut=inertia" target="_blank">classic Gazebo tutorial</a>.
</p>

<p>Supported file formats: <strong>.stl, .obj, .dae</strong> (max size: 20MB)</p>

<form id="uploadForm">
  <label for="fileInput"><strong>Select 3D model:</strong></label><br>
  <input type="file" id="fileInput" accept=".stl,.obj,.dae" required /><br><br>

<label for="massInput"><strong>Mass (kg):</strong></label><br>
<input type="number" id="massInput" step="0.1" value="1.0" min="0.01" required /><br><br>

  <details>
    <summary style="cursor:pointer; font-weight:bold;">Advanced options</summary>
    <label>
      <input type="checkbox" id="saveNormals">
      Save vertex normals in output mesh
      <br><small style="opacity: 0.75;">(This may help with some rendering tools, but increases file size. Not always necessary.)</small>
    </label><br>
    <label>
      <input type="checkbox" id="useConvexHull">
      Generate convex hull if mesh is not watertight
      <br><small style="opacity: 0.75;">(Useful for models with holes or open surfaces.)</small>
    </label><br>
  </details>
  <br>

<button type="button" onclick="uploadFile()">🚀 Upload & Clean</button>

</form>

<hr>
<p><strong>Results:</strong></p>
<p id="usageTip" style="display:none; margin-top: 1em;">
  <em>The XML snippet below (inside <code>&lt;inertial&gt;</code>) can be directly used in URDF or SDF robot model files, for example when simulating in Gazebo or ROS-based environments.</em>
</p>
<pre id="response">Waiting for upload...</pre>
<a id="downloadLink" style="display:none;" download>⬇ Download Cleaned Mesh</a>

<script>
async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const mass = document.getElementById("massInput").value;
  const saveNormals = document.getElementById("saveNormals").checked;
  const useConvexHull = document.getElementById("useConvexHull").checked;
  const responseEl = document.getElementById("response");
  const linkEl = document.getElementById("downloadLink");
  const usageTip = document.getElementById("usageTip");

  if (!file) {
    alert("Please select a file.");
    return;
  }

  if (file.size > 20 * 1024 * 1024) {
    alert("File size must be under 20MB.");
    return;
  }

  responseEl.textContent = "⏳ Uploading and processing...";
  usageTip.style.display = "none";
  linkEl.style.display = "none";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("mass", mass);
  formData.append("save_normals", saveNormals);
  formData.append("use_convex_hull", useConvexHull);

  try {
    const res = await fetch("https://mesh-cleaner-692118822266.europe-west1.run.app/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      responseEl.textContent = "❌ Error: " + data.error;
      return;
    }

    responseEl.textContent = data.metrics;
    usageTip.style.display = "block";

    responseEl.textContent = data.metrics;
    linkEl.href = `https://mesh-cleaner-692118822266.europe-west1.run.app${data.download_url}`;
    linkEl.style.display = "inline";
  } catch (err) {
    responseEl.textContent = "❌ Upload failed: " + err.message;
  }
}
</script>

<style>
#uploadForm {
  padding: 1em;
  border: 1px solid;
  border-radius: 8px;
  max-width: 500px;
}

input[type="file"],
input[type="number"],
button {
  font-size: 1em;
  padding: 0.5em;
  margin-top: 0.3em;
  width: 100%;
  box-sizing: border-box;
}

button {
  background-color: #12b075;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 1em;
}

button:hover {
  background-color: #0e8d5d;
}

pre {
  padding: 1em;
  max-width: 100%;
  white-space: pre-wrap;
  word-wrap: break-word;
}

#downloadLink {
  display: inline-block;
  margin-top: 1em;
  padding: 0.6em 1em;
  background-color: #12b075;
  text-decoration: none;
  border-radius: 5px;
}
</style>
