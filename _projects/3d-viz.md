---
layout: page
title: Model Viewer
description: Visualize 3D models and robots directly in your browser
img: assets/img/ur5.png
permalink: /3d-viz/
importance: 2
category: robotics
---

<p>Upload a 3D model file (<code>.dae</code>, <code>.obj</code>, <code>.stl</code>) to visualize it, or drag and drop it into the viewer below.</p>

<script>
  const EXAMPLE_MODEL_URL = "{{ '/assets/3d/abb_irb52_7_120.dae' | relative_url }}";
</script>

<div id="container" style="height: 60vh; position: relative; border: 2px dashed #ccc; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
  <button id="resetViewer" style="position: absolute; top: 10px; right: 10px; z-index: 3; border: none; padding: 0.4em 0.8em; border-radius: 4px; cursor: pointer;">Reset</button>
  <div id="fileDropOverlay" style="position: absolute; width: 100%; height: 100%; z-index: 2; cursor: pointer;"></div>
  <input type="file" id="fileUpload" accept=".dae,.obj,.stl" style="display: none;" />
  <div id="loading" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); display: none; text-align: center;">
    <div class="loader"></div>
    <div>Loading...</div>
  </div>
  <div id="uploadPrompt" style="pointer-events: none; color: #888; text-align: center; font-size: 1em; z-index: 1; position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);">
    <p>Click or drop a 3D model file here</p>
  </div>
</div>

<div style="margin-top: 1em;">
  <p>Don’t have a file?</p>
  <div style="display: flex; gap: 1em; flex-wrap: wrap;">
    <a href="{{ '/assets/3d/abb_irb52_7_120.dae' | relative_url }}" download>
      <button type="button" class="action-btn">⬇️ Download Example</button>
    </a>
    <button type="button" id="loadExample" class="action-btn">👁️ Preview Example</button>
  </div>
</div>

<script src="{{ '/assets/js/three.min.js' | relative_url }}"></script>
<script src="{{ '/assets/js/OrbitControls.js' | relative_url }}"></script>
<script src="{{ '/assets/js/ColladaLoader.js' | relative_url }}"></script>
<script src="{{ '/assets/js/OBJLoader.js' | relative_url }}"></script>
<script src="{{ '/assets/js/STLLoader.js' | relative_url }}"></script>

<script>
document.addEventListener("DOMContentLoaded", () => {
  if (!window.WebGLRenderingContext) return alert("Your browser does not support WebGL. Please upgrade.");

  const container = document.getElementById("container");
  const loadingElem = document.getElementById("loading");
  const uploadPrompt = document.getElementById("uploadPrompt");
  const fileInput = document.getElementById("fileUpload");
  const overlay = document.getElementById("fileDropOverlay");
  const resetBtn = document.getElementById("resetViewer");
  let camera, renderer, controls, boundingBox, obj, grid;
  const scene = new THREE.Scene();

  overlay.onclick = () => fileInput.click();

  const fileUrl = new URLSearchParams(window.location.search).get("file");
  if (fileUrl) {
    hidePrompt();
    const ext = fileUrl.split('.').pop().toLowerCase();
    loadingElem.style.display = "block";
    fetch(fileUrl)
      .then(res => ext === 'stl' ? res.arrayBuffer() : res.text())
      .then(data => loadModel(data, ext))
      .catch(() => loadingElem.textContent = "Error loading model from URL.");
  }

  fileInput.onchange = e => e.target.files[0] && handleFile(e.target.files[0]);

  container.ondragover = e => {
    e.preventDefault();
    container.classList.add("dragover");
  };
  container.ondragleave = () => container.classList.remove("dragover");
  container.ondrop = e => {
    e.preventDefault();
    container.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  };

  function handleFile(file) {
    hidePrompt();
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['dae', 'obj', 'stl'].includes(ext)) return alert("Unsupported file type.");
    const reader = new FileReader();
    reader.onload = e => loadModel(e.target.result, ext);
    ext === 'stl' ? reader.readAsArrayBuffer(file) : reader.readAsText(file);
  }

  document.getElementById("loadExample").onclick = () => {
    hidePrompt();
    loadingElem.style.display = "block";
    fetch(EXAMPLE_MODEL_URL)
      .then(res => res.text())
      .then(data => loadModel(data, "dae"))
      .catch(() => loadingElem.textContent = "Failed to load example model.");
  };

  resetBtn.onclick = () => {
    if (obj) scene.remove(obj);
    if (grid) scene.remove(grid);
    obj = null;
    grid = null;
    renderer?.renderLists?.dispose?.();
    uploadPrompt.style.display = "block";
    overlay.style.display = "block";
  };

  function hidePrompt() {
    uploadPrompt.style.display = "none";
    overlay.style.display = "none";
  }

  function loadModel(data, type) {
    loadingElem.style.display = "block";
    if (obj) scene.remove(obj);
    if (grid) scene.remove(grid);

    const loaderMap = {
      dae: () => new THREE.ColladaLoader().parse(data).scene,
      obj: () => new THREE.OBJLoader().parse(data),
      stl: () => new THREE.Mesh(new THREE.STLLoader().parse(data), new THREE.MeshStandardMaterial({ color: 0x666666 }))
    };

    try {
      const loaded = loaderMap[type]();
      loaded.traverse?.(child => {
        if (child instanceof THREE.Mesh) Object.assign(child.material, { flatShading: true });
        child.castShadow = child.receiveShadow = true;
      });

      obj = new THREE.Object3D();
      obj.add(loaded);
      scene.add(obj);

      boundingBox = new THREE.Box3().setFromObject(obj);
      setupScene();
    } catch (err) {
      console.error("Load error:", err);
      loadingElem.textContent = "Error loading model.";
    } finally {
      loadingElem.style.display = "none";
    }
  }

  function setupScene() {
    if (renderer) container.removeChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(25, container.clientWidth / container.clientHeight, 0.1, 2000);
    const width = boundingBox.max.z - boundingBox.min.z;
    const height = boundingBox.max.y - boundingBox.min.y;
    camera.position.set(
      Math.max(width, height) / Math.tan(Math.PI * camera.fov / 360),
      (boundingBox.min.y + boundingBox.max.y) / 2,
      (boundingBox.min.z + boundingBox.max.z) / 2
    );

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0xffffff);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.copy(boundingBox.getCenter(new THREE.Vector3()));
    controls.update();

    scene.clear();
    scene.add(obj);

    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const dirLight = new THREE.DirectionalLight(0xffffff, 1);
    dirLight.position.set(3, 3, 3);
    dirLight.castShadow = true;
    scene.add(dirLight);

    const size = Math.max(
      boundingBox.max.x - boundingBox.min.x,
      boundingBox.max.z - boundingBox.min.z
    ) * 4;
    grid = new THREE.GridHelper(size, 30);
    scene.add(grid);

    let resizeTimeout;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }, 150);
    });

    applyThemeBackground();
    watchThemeChange();
    render();
  }

  function applyThemeBackground() {
    const bg = getComputedStyle(document.documentElement).getPropertyValue("--global-bg-color").trim();
    if (bg) renderer.setClearColor(new THREE.Color(bg));
  }

  function watchThemeChange() {
    new MutationObserver(applyThemeBackground).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  }

  function render() {
    renderer.render(scene, camera);
  }

  function animate() {
    requestAnimationFrame(animate);
    render();
  }
  animate();
});
</script>

<style>
#loadExample:hover {
  background-color: #0e8d5d;
}

#container.dragover {
  border-color: #12b075;
  background-color: #f0fff7;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #12b075;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.5em;
}

.action-btn {
  background-color: #12b075;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 0.6em 1.2em;
  cursor: pointer;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
