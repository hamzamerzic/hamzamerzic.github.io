---
layout: page
title: IKFast Generator
description: Generate analytic Inverse Kinematics solvers based on OpenRAVE's IKFast
img: assets/img/inverse_kinematics.png
permalink: /ikfast/
importance: 3
category: robotics
giscus_comments: true
---

<p>
  <strong>IKFast Generator</strong> is a tool that creates blazing-fast analytic inverse kinematics solvers for your robot, powered by <a href="http://openrave.org/docs/latest_stable/openravepy/ikfast/" target="_blank">OpenRAVE's IKFast</a>. Simply upload a <code>.dae</code> file of your robot, extract its kinematic structure, and generate a C++ solver ready for integration.
</p>

<p>Supported file format: <strong>.dae</strong> (max size: 32MB)</p>

<form id="uploadForm" class="ikfast-form" onsubmit="event.preventDefault(); uploadFile();">
  <label for="fileInput"><strong>Select or drop a robot model (.dae):</strong></label>
  <div id="dropArea" class="ikfast-drop">
    <input type="file" id="fileInput" accept=".dae" required hidden />
    <div id="dropText">📂 Drop file here or click to browse</div>
  </div>
  <br>
  <button class="ikfast-button" type="submit">⚙️ Start IKFast Generation</button>
</form>

<details style="margin-top: 1.5em;">
  <summary><strong>📁 Don’t have a file? Use an example</strong></summary>
  <div style="display: flex; gap: 1em; flex-wrap: wrap;">
    <a href="{{ '/assets/3d/abb_irb52_7_120.dae' | relative_url }}" download>
      <button type="button" class="ikfast-button">⬇️ Download Example</button>
    </a>
  </div>
  <small style="opacity: 0.75;">Use it with: baselink = <code>0</code>, eelink = <code>8</code>, solver = <code>Transform6D</code>, and leave free indices empty.</small>
</details>

<div id="ikfast-results" style="display:none;">
  <hr />
  <p><strong>Link Info:</strong></p>
  <p>
    Below you should see a graph of your robot. For each link its index and parents should be shown.<br />
    <small style="color: grey;">(In case of error or no output at all, please check that the joint limits are defined in your robot file.)</small>
  </p>
  <pre id="ikfast-link-info" class="ikfast-pre">Waiting for upload...</pre>

  <div id="ikfastFormContainer" style="display:none;">
    <hr />
    <p>
      <strong>Generate IKFast Solver:</strong><br>
      Provide parameters for the solver generation below. Refer to the <a href="http://openrave.org/docs/latest_stable/openravepy/ikfast/" target="_blank">IKFast docs</a> for info about free indices and solver types.
    </p>

    <form id="ikfastForm" class="ikfast-form" onsubmit="event.preventDefault(); generateSolver();">
      <label for="baselink">Base link index:</label>
      <input type="text" id="baselink" required />

      <label for="eelink">End effector link index:</label>
      <input type="text" id="eelink" required />

      <label for="freeindices">Free indices (comma-separated):</label>
      <input type="text" id="freeindices" placeholder="e.g. 0,3,5" />

      <label for="solver">Solver type:</label>
      <select id="solver" required>
        <option value="transform6d">Transform6D</option>
        <option value="rotation3d">Rotation3D</option>
        <option value="translation3d">Translation3D</option>
        <option value="direction3d">Direction3D</option>
        <option value="ray4d">Ray4D</option>
        <option value="lookat3d">Lookat3D</option>
        <option value="translationdirection5d">TranslationDirection5D</option>
        <option value="translationxy2d">TranslationXY2D</option>
        <option value="translationxyorientation3d">TranslationXYOrientation3D</option>
        <option value="translationxaxisangle4d">TranslationXAxisAngle4D</option>
        <option value="translationyaxisangle4d">TranslationYAxisAngle4D</option>
        <option value="translationzaxisangle4d">TranslationZAxisAngle4D</option>
      </select>

      <button class="ikfast-button" type="submit">⚙️ Generate Solver</button>
    </form>

  </div>

  <div id="ikfast-solver-output" style="display:none;">
    <hr />
    <p><strong>Solver Logs:</strong></p>
    <p><em>If everything goes correctly, the download link will appear below the logs.</em></p>
    <pre id="ikfast-solver-log" class="ikfast-pre">Placeholder.</pre>
    <a id="downloadSolverLink" style="display:none;" download>⬇️ Download Generated Solver</a>
  </div>
</div>

<details style="margin-top: 2em;">
  <summary><strong>🐟 Prefer to run it yourself? Click here to learn to fish:</strong></summary>
  <p style="margin-top: 1em;">
    To try it locally, first <strong>download the example file above</strong> (or use your own). Then run this command in your terminal (assuming you have <a href="https://www.docker.com/">Docker</a> set up):
  </p>
  <pre class="ikfast-pre">docker run --rm \\
  -v $(pwd):/data \\
  hamzamerzic/openrave-py3 \\
  python3 -m openravepy._openravepy_.ikfast \\
    --robot /data/abb_irb52_7_120.dae \\
    --iktype transform6d \\
    --baselink 0 \\
    --eelink 8 \\
    --savefile /data/ikfast_output.cpp
</pre>
</details>

<p style="margin-top: 2em;">
  ✨ This tool was <a href="https://hamzamerzic.info/blog/2025/website-migration/">modernized</a> from my earlier WordPress website.<br />
  If you notice any regressions or bugs, please reach out or comment below—I’d love to hear from you.
</p>

<script>
async function uploadFile() {
  const file = document.getElementById("fileInput").files[0];
  const responseEl = document.getElementById("ikfast-link-info");

  if (!file) return alert("Please select a file.");
  if (file.size > 32 * 1024 * 1024) return alert("File size must be under 32MB.");
  if (!file.name.toLowerCase().endsWith(".dae")) return alert("Only .dae files are supported.");

  document.getElementById("ikfast-results").style.display = "block";
  responseEl.textContent = "⏳ Uploading and analyzing...";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("https://robot-link-info-692118822266.europe-west1.run.app/robot_link_info", {
      method: "POST",
      body: formData
    });

    const text = await res.text();
    responseEl.textContent = res.ok ? text : "❌ Error: " + text;

    if (res.ok) {
      document.getElementById("ikfastFormContainer").style.display = "block";
    }
  } catch (err) {
    responseEl.textContent = "❌ Upload failed: " + err.message;
  }
}

async function generateSolver() {
  const baselink = document.getElementById("baselink").value.trim();
  const eelink = document.getElementById("eelink").value.trim();
  if (baselink === "" || eelink === "") {
    alert("Please provide both base link and end effector link indices.");
    return;
  }

  const solverLogEl = document.getElementById("ikfast-solver-log");
  const downloadLink = document.getElementById("downloadSolverLink");
  const solverOutputBlock = document.getElementById("ikfast-solver-output");

  solverLogEl.textContent = "";
  downloadLink.style.display = "none";
  solverOutputBlock.style.display = "block";

  const file = document.getElementById("fileInput").files[0];
  const formData = new FormData();
  formData.append("file", file);
  formData.append("solver", document.getElementById("solver").value);
  formData.append("baselink", baselink);
  formData.append("eelink", eelink);
  formData.append("freeindices", document.getElementById("freeindices").value);

  try {
    const res = await fetch("https://ikfast-solver-692118822266.europe-west1.run.app/generate_solver", {
      method: "POST",
      body: formData
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let logBuffer = "";
    let cppBuffer = "";
    let insideCpp = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      let chunk = decoder.decode(value, { stream: true });

      if (chunk.includes("📎 Begin generated ikfast_output.cpp")) {
        insideCpp = true;
        chunk = chunk.split("📎 Begin generated ikfast_output.cpp\n\n").pop();
      } else if (chunk.includes("📎 End of ikfast_output.cpp")) {
        chunk = chunk.split("📎 End of ikfast_output.cpp")[0];
        cppBuffer += chunk;

        const blob = new Blob([cppBuffer], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        downloadLink.href = url;
        downloadLink.download = "ikfast_generated.cpp";
        downloadLink.style.display = "inline-block";

        insideCpp = false;
        cppBuffer = "";
        continue;
      }

      if (insideCpp) {
        cppBuffer += chunk;
      } else {
        logBuffer += chunk;
        solverLogEl.textContent = logBuffer;
        solverLogEl.scrollTop = solverLogEl.scrollHeight;
      }
    }
  } catch (err) {
    solverLogEl.textContent = "❌ Solver generation failed: " + err.message;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const dropText = document.getElementById("dropText");

  const updateDropText = () => {
    dropText.textContent = fileInput.files.length > 0
      ? `📁 Selected: ${fileInput.files[0].name}`
      : "📂 Drop file here or click to browse";
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
</script>

<style>
.ikfast-form {
  padding: 1em;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 12px;
  max-width: 500px;
}

.ikfast-form label {
  margin-top: 1em;
  display: block;
  font-weight: bold;
}

.ikfast-form input,
.ikfast-form select {
  font-size: 1em;
  padding: 0.5em;
  margin-bottom: 0.8em;
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.ikfast-button {
  background-color: #12b075;
  color: white;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  transition: background 0.2s ease;
  margin-top: 1em;
  padding: 0.6em;
}

.ikfast-button:hover {
  background-color: #0e8d5d;
}

.ikfast-drop {
  border: 2px dashed #bbb;
  padding: 1.5em;
  text-align: center;
  cursor: pointer;
  border-radius: 10px;
  transition: background 0.3s ease;
}

.ikfast-drop.highlight {
  background: #e0ffe8;
}

.ikfast-pre {
  padding: 1em;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #eee;
  border-radius: 8px;
  max-height: 600px;
  overflow: auto;
  scroll-behavior: smooth;
}

#downloadSolverLink {
  display: none;
  margin-top: 1em;
  padding: 0.6em;
  background-color: #12b075;
  border-radius: 6px;
  text-decoration: none;
  color: white;
  font-weight: bold;
  text-align: center;
}

#downloadSolverLink:hover {
  background-color: #0e8d5d;
}
</style>
