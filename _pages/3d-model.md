---
layout: default
title: "3D Model Viewer"
permalink: /3d-model/
---

<div id="container" style="height: 60vh;"></div>

<!-- Include Three.js and necessary scripts -->
<script src="{{ '/assets/js/three.min.js' | relative_url }}"></script>
<script src="{{ '/assets/js/ColladaLoader.js' | relative_url }}"></script>
<script src="{{ '/assets/js/OrbitControls.js' | relative_url }}"></script>

<script>
document.addEventListener("DOMContentLoaded", () => {
    if (!window.WebGLRenderingContext) {
        alert("Your browser does not support WebGL. Please upgrade.");
    }

    const container = document.getElementById("container");
    const scene = new THREE.Scene();
    
    let camera, renderer, controls, boundingBox;

    // Load Model
    const loader = new THREE.ColladaLoader();
    loader.load("{{ '/assets/3d/abb_irb52_7_120.dae' | relative_url }}", function (collada) {
        const dae = collada.scene;
        dae.traverse(child => {
            if (child instanceof THREE.Mesh) {
                child.material.flatShading = true;
            }
        });

        const obj = new THREE.Object3D();
        scene.add(obj);
        obj.add(dae);

        boundingBox = new THREE.Box3().setFromObject(obj);

        init();  // Initialize AFTER model loads
        animate();
    });

    // Initialize Three.js
    function init() {
        const aspect = container.clientWidth / container.clientHeight;
        camera = new THREE.PerspectiveCamera(25, aspect, 0.1, 2000);
        const width = boundingBox.max.z - boundingBox.min.z;
        const height = boundingBox.max.y - boundingBox.min.y;

        camera.position.set(
            Math.max(width, height) / Math.tan(Math.PI * camera.fov / 360),
            (boundingBox.min.y + boundingBox.max.y) / 2,
            (boundingBox.min.z + boundingBox.max.z) / 2
        );

        // Improved lighting
        scene.add(new THREE.AmbientLight(0xffffff, 0.3));
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(2, 2, 2);
        scene.add(directionalLight);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setClearColor(0xffffff); // Use clear color instead of scene.background
        container.appendChild(renderer.domElement);

        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(
            (boundingBox.min.x + boundingBox.max.x) / 2,
            (boundingBox.min.y + boundingBox.max.y) / 2,
            (boundingBox.min.z + boundingBox.max.z) / 2
        );
        controls.addEventListener("change", render); // Only render when camera moves
        controls.update();

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
        let bgColor = getComputedStyle(document.documentElement).getPropertyValue("--global-bg-color").trim();
        if (bgColor) {
            renderer.setClearColor(new THREE.Color(bgColor)); // Use renderer.setClearColor
        }
    }

    function watchThemeChange() {
        const observer = new MutationObserver(() => applyThemeBackground());
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

        applyThemeBackground(); // Set initial color
    }

    function render() {
        renderer.render(scene, camera);
    }

    function animate() {
        requestAnimationFrame(animate);
        render();
    }
});
</script>
