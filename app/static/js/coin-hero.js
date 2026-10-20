/**
 * COINVAULT — 3D WebGL Hero Coin Token
 * Renders an interactive 3D eFootball metallic gold token.
 * Degrades gracefully if WebGL is unavailable or prefers-reduced-motion is active.
 */

(function () {
  'use strict';

  const container = document.getElementById('webgl-coin-hero');
  if (!container) return;

  const fallback = document.getElementById('webgl-coin-fallback');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reducedMotion || typeof THREE === 'undefined') {
    if (fallback) fallback.style.display = 'block';
    return;
  }

  try {
    const width = container.clientWidth || 320;
    const height = container.clientHeight || 320;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Coin Mesh: Cylinder with chamfered geometry
    const geometry = new THREE.CylinderGeometry(1.6, 1.6, 0.22, 64);
    
    // Luxury Gold Physical Material
    const material = new THREE.MeshStandardMaterial({
      color: 0xF5C451,
      metalness: 0.88,
      roughness: 0.22,
    });

    const coin = new THREE.Mesh(geometry, material);
    coin.rotation.x = Math.PI / 2.3;
    coin.rotation.z = Math.PI / 6;
    scene.add(coin);

    // Inner rim
    const rimGeom = new THREE.TorusGeometry(1.45, 0.04, 16, 64);
    const rimMat = new THREE.MeshStandardMaterial({ color: 0xFFD875, metalness: 0.95, roughness: 0.15 });
    const rim = new THREE.Mesh(rimGeom, rimMat);
    rim.rotation.x = Math.PI / 2;
    coin.add(rim);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const goldKeyLight = new THREE.PointLight(0xF5C451, 3.5, 20);
    goldKeyLight.position.set(4, 4, 5);
    scene.add(goldKeyLight);

    const turfFillLight = new THREE.PointLight(0x00F084, 1.2, 20);
    turfFillLight.position.set(-4, -3, 3);
    scene.add(turfFillLight);

    // Subtle interactive tilt on mousemove
    let mouseX = 0;
    let mouseY = 0;
    container.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 1.5;
      mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 1.5;
    });

    let frameId;
    function animate() {
      frameId = requestAnimationFrame(animate);

      // Continuous slow majestic rotation
      coin.rotation.y += 0.008;

      // Mouse influence
      coin.rotation.x = (Math.PI / 2.3) + mouseY * 0.4;
      coin.rotation.z = (Math.PI / 6) + mouseX * 0.4;

      renderer.render(scene, camera);
    }
    animate();

    // Resize handling
    window.addEventListener('resize', () => {
      const newW = container.clientWidth || 320;
      const newH = container.clientHeight || 320;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    });

    if (fallback) fallback.style.display = 'none';
  } catch (e) {
    console.warn('WebGL initialization failed, falling back to static visual.', e);
    if (fallback) fallback.style.display = 'block';
  }
})();
