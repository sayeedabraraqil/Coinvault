/**
 * COINVAULT — Motion & Kinetic Choreography Engine
 * Powered by GSAP, ScrollTrigger, and 3D Perspective Tilt.
 */

(function () {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1. GSAP ENTRANCE SEQUENCES
  function initGsapEntrances() {
    if (typeof gsap === 'undefined' || reducedMotion) return;

    // Stagger in metric and podium cards
    const fadeEls = document.querySelectorAll('.gsap-fade-up');
    if (fadeEls.length > 0) {
      gsap.fromTo(
        fadeEls,
        { opacity: 0, y: 24 },
        { opacity: 1, y: 0, duration: 0.65, stagger: 0.08, ease: 'power2.out' }
      );
    }

    // Hero title entrance
    const heroTitle = document.querySelector('.gsap-hero-title');
    if (heroTitle) {
      gsap.fromTo(
        heroTitle,
        { opacity: 0, y: 30, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'power3.out' }
      );
    }
  }

  // 2. 3D INTERACTIVE PERSPECTIVE TILT (PODIUM CARDS)
  function init3DTiltCards() {
    if (reducedMotion) return;

    const cards = document.querySelectorAll('.tilt-card');
    cards.forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = ((y - centerY) / centerY) * -8; // deg
        const rotateY = ((x - centerX) / centerX) * 8; // deg

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        card.style.transition = 'transform 0.1s ease-out';
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        card.style.transition = 'transform 0.5s ease-out';
      });
    });
  }

  // 3. CELEBRATION CONFETTI
  window.triggerConfetti = function () {
    if (typeof confetti === 'function' && !reducedMotion) {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.7 },
        colors: ['#F5C451', '#00F084', '#FFFFFF', '#00D8F6'],
      });
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    initGsapEntrances();
    init3DTiltCards();
  });
})();
