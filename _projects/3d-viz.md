---
layout: page
title: 3D Model Viewer
description: Visualize 3D models directly in your browser
img: assets/img/abb_irb_52.png
permalink: /3d-viz/
importance: 2
category: fun
---

<p>Upload a 3D model file (<code>.dae</code>, <code>.obj</code>, <code>.stl</code>) to visualize it.</p>

<!-- Upload Form -->
<form id="vizUploadForm">
  <label for="fileUpload"><strong>Select 3D model (.dae, .obj, .stl):</strong></label><br>
  <input type="file" id="fileUpload" accept=".dae,.obj,.stl" /><br><br>

<button type="button" id="loadExample">👁️ Preview Example Model</button>

</form>

<p style="margin-top: 1em;">
  Don’t have a file? <a href="{{ '/assets/3d/abb_irb52_7_120.dae' | relative_url }}" download>Download an example</a>.
</p>

<!-- 3D Container -->
<div id="container" style="height: 60vh; position: relative;">
  <div id="loading" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); display: none;">
    Loading model... <span id="progress">0%</span>
  </div>
</div>

<!-- Include Three.js and necessary scripts -->
<script src="{{ '/assets/js/three.min.js' | relative_url }}"></script>
<script src="{{ '/assets/js/OrbitControls.js' | relative_url }}"></script>
<script src="{{ '/assets/js/ColladaLoader.js' | relative_url }}"></script>
<script src="{{ '/assets/js/OBJLoader.js' | relative_url }}"></script>
<script src="{{ '/assets/js/STLLoader.js' | relative_url }}"></script>

<script>
document.addEventListener("DOMContentLoaded", () => {
  if (!window.WebGLRenderingContext) {
    alert("Your browser does not support WebGL. Please upgrade.");
    return;
  }

  const container = document.getElementById("container");
  const loadingElem = document.getElementById("loading");
  loadingElem.style.display = "none";
  const progressElem = document.getElementById("progress");

  const scene = new THREE.Scene();
  let camera, renderer, controls, boundingBox, obj;

  // 🔍 Load from URL parameter if present
  const urlParams = new URLSearchParams(window.location.search);
  const fileUrl = urlParams.get("file");
  if (fileUrl) {
    const ext = fileUrl.split('.').pop().toLowerCase();
    loadingElem.style.display = "block";
    fetch(fileUrl)
      .then(res => {
        if (!res.ok) throw new Error("Fetch failed");
        return ext === 'stl' ? res.arrayBuffer() : res.text();
      })
      .then(data => loadModelFromText(data, ext))
      .catch(err => {
        console.error(err);
        loadingElem.textContent = "Error loading model from URL.";
      });
  }

  // File upload handler
  document.getElementById("fileUpload").addEventListener("change", event => {
    const file = event.target.files[0];
    if (!file) return;

    const extension = file.name.split('.').pop().toLowerCase();
    if (!['dae', 'obj', 'stl'].includes(extension)) {
      alert("Unsupported file type. Please upload a .dae, .obj, or .stl file.");
      return;
    }

    const reader = new FileReader();
    reader.onload = e => loadModelFromText(e.target.result, extension);
    if (extension === 'stl') {
      reader.readAsArrayBuffer(file);
    } else {
      reader.readAsText(file);
    }
  });

  // Example model button
  document.getElementById("loadExample").addEventListener("click", () => {
    loadingElem.style.display = "block";
    fetch("{{ '/assets/3d/abb_irb52_7_120.dae' | relative_url }}")
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch example");
        return res.text();
      })
      .then(data => loadModelFromText(data, "dae"))
      .catch(err => {
        console.error(err);
        loadingElem.textContent = "Failed to load example model.";
      });
  });

  // Loader logic
  function loadModelFromText(fileContent, type) {
    loadingElem.style.display = "block";
    progressElem.textContent = "0%";

    try {
      if (obj) scene.remove(obj);

      const loaderMap = {
        dae: () => new THREE.ColladaLoader().parse(fileContent).scene,
        obj: () => new THREE.OBJLoader().parse(fileContent),
        stl: () => {
          const geometry = new THREE.STLLoader().parse(fileContent);
          const material = new THREE.MeshStandardMaterial({ color: 0x555555 });
          return new THREE.Mesh(geometry, material);
        }
      };

      const loaded = loaderMap[type]();
      loaded.traverse?.(child => {
        if (child instanceof THREE.Mesh) {
          child.material.flatShading = true;
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });

      obj = new THREE.Object3D();
      obj.add(loaded);
      scene.add(obj);

      boundingBox = new THREE.Box3().setFromObject(obj);

      setupScene();
      animate();
      loadingElem.style.display = "none";
    } catch (err) {
      console.error("Load error:", err);
      loadingElem.textContent = "Error loading model.";
    }
  }

  function setupScene() {
    if (renderer) container.removeChild(renderer.domElement);

    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(25, aspect, 0.1, 2000);

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
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(
      (boundingBox.min.x + boundingBox.max.x) / 2,
      (boundingBox.min.y + boundingBox.max.y) / 2,
      (boundingBox.min.z + boundingBox.max.z) / 2
    );
    controls.addEventListener("change", render);
    controls.update();

    scene.clear();
    scene.add(obj);

    scene.add(new THREE.AmbientLight(0xffffff, 0.3));
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(2, 2, 2);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 1024;
    directionalLight.shadow.mapSize.height = 1024;
    scene.add(directionalLight);

    const size = Math.max(
      boundingBox.max.x - boundingBox.min.x,
      boundingBox.max.z - boundingBox.min.z
    ) * 2;
    scene.add(new THREE.GridHelper(size, 10));

    window.addEventListener("resize", onWindowResize);
    applyThemeBackground();
    watchThemeChange();
  }

  function onWindowResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    render();
  }

  function applyThemeBackground() {
    const bgColor = getComputedStyle(document.documentElement).getPropertyValue("--global-bg-color").trim();
    if (bgColor) renderer.setClearColor(new THREE.Color(bgColor));
  }

  function watchThemeChange() {
    const observer = new MutationObserver(() => applyThemeBackground());
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    applyThemeBackground();
  }

  function render() {
    if (renderer && camera) renderer.render(scene, camera);
  }

  function animate() {
    requestAnimationFrame(animate);
    render();
  }
});
</script>

<style>
#vizUploadForm {
  padding: 1em;
  border: 1px solid;
  border-radius: 8px;
  max-width: 500px;
  margin-bottom: 1em;
}

#vizUploadForm input[type="file"],
#vizUploadForm button {
  font-size: 1em;
  padding: 0.5em;
  margin-top: 0.3em;
  width: 100%;
  box-sizing: border-box;
}

#vizUploadForm button {
  background-color: #12b075;
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  margin-top: 1em;
}

#vizUploadForm button:hover {
  background-color: #0e8d5d;
}
</style>
