/**
 * COINVAULT — Core Client Architecture
 * Controls Theme, Lenis Smooth Scroll, Mouse Spotlight, Command Palette (Cmd+K),
 * Modal Controllers, and Count-Up Odometer animations.
 */

(function () {
  'use strict';

  // 1. THEME MANAGEMENT (Dark-first, true light mode)
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const htmlEl = document.documentElement;

  function initTheme() {
    const savedTheme = localStorage.getItem('cv_theme') || 'dark';
    if (savedTheme === 'light') {
      htmlEl.classList.remove('dark');
      htmlEl.classList.add('light');
    } else {
      htmlEl.classList.remove('light');
      htmlEl.classList.add('dark');
    }
    updateThemeToggleIcon();
  }

  function toggleTheme() {
    const isDark = htmlEl.classList.contains('dark');
    if (isDark) {
      htmlEl.classList.remove('dark');
      htmlEl.classList.add('light');
      localStorage.setItem('cv_theme', 'light');
    } else {
      htmlEl.classList.remove('light');
      htmlEl.classList.add('dark');
      localStorage.setItem('cv_theme', 'dark');
    }
    updateThemeToggleIcon();
    // Dispatch custom event for ECharts re-render
    window.dispatchEvent(new CustomEvent('cv:themeChanged', { detail: { theme: isDark ? 'light' : 'dark' } }));
  }

  function updateThemeToggleIcon() {
    if (!themeToggleBtn) return;
    const isDark = htmlEl.classList.contains('dark');
    themeToggleBtn.innerHTML = isDark
      ? `<svg class="w-4 h-4 text-brand-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`
      : `<svg class="w-4 h-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>`;
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }
  initTheme();

  // 2. MOUSE SPOTLIGHT FOLLOWER
  const spotlight = document.querySelector('.mouse-spotlight');
  if (spotlight && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let ticking = false;
    window.addEventListener('mousemove', (e) => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
          document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`);
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  // 3. LENIS SMOOTH SCROLL
  if (typeof Lenis !== 'undefined' && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const lenis = new Lenis({
      duration: 1.1,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 0.9,
    });
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  }

  // 4. ANIMATED COUNT-UP / ODOMETER NUMBERS
  function animateCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach((el) => {
      const target = parseInt(el.getAttribute('data-counter'), 10);
      if (isNaN(target)) return;

      const duration = 1200; // ms
      const startTime = performance.now();
      const startVal = 0;

      function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Easing: easeOutExpo
        const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const current = Math.floor(startVal + (target - startVal) * ease);
        el.innerText = current.toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          el.innerText = target.toLocaleString();
        }
      }
      requestAnimationFrame(update);
    });
  }
  document.addEventListener('DOMContentLoaded', animateCounters);

  // 5. COMMAND PALETTE (Cmd+K / Ctrl+K)
  const cmdPaletteModal = document.getElementById('cmd-palette-modal');
  const cmdSearchInput = document.getElementById('cmd-search-input');
  const cmdResultsList = document.getElementById('cmd-results-list');

  function openCommandPalette() {
    if (!cmdPaletteModal) return;
    cmdPaletteModal.classList.remove('hidden');
    cmdPaletteModal.classList.add('flex');
    if (cmdSearchInput) {
      cmdSearchInput.value = '';
      cmdSearchInput.focus();
    }
    renderDefaultCommands();
  }

  function closeCommandPalette() {
    if (!cmdPaletteModal) return;
    cmdPaletteModal.classList.add('hidden');
    cmdPaletteModal.classList.remove('flex');
  }

  function renderDefaultCommands() {
    if (!cmdResultsList) return;
    cmdResultsList.innerHTML = `
      <div class="px-3 py-2 text-xs font-semibold text-txt-muted uppercase tracking-wider">Quick Navigation</div>
      <a href="/leaderboards" class="cmd-item flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-pitch-elevated text-sm text-txt-primary">
        <span class="flex items-center gap-2"><span>🏆</span> Global Leaderboards</span>
        <span class="text-xs text-txt-muted mono">G then L</span>
      </a>
      <a href="/analytics" class="cmd-item flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-pitch-elevated text-sm text-txt-primary">
        <span class="flex items-center gap-2"><span>📊</span> Market Analytics</span>
        <span class="text-xs text-txt-muted mono">G then A</span>
      </a>
      <a href="/compare" class="cmd-item flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-pitch-elevated text-sm text-txt-primary">
        <span class="flex items-center gap-2"><span>⚔️</span> Head-to-Head Duel</span>
        <span class="text-xs text-txt-muted mono">G then C</span>
      </a>
      <a href="/achievements" class="cmd-item flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-pitch-elevated text-sm text-txt-primary">
        <span class="flex items-center gap-2"><span>🎖️</span> Badges & Milestones</span>
        <span class="text-xs text-txt-muted mono">G then M</span>
      </a>
      <div class="px-3 py-2 text-xs font-semibold text-txt-muted uppercase tracking-wider mt-2">Actions</div>
      <button onclick="window.COINVAULT.openLogModal();" class="w-full text-left cmd-item flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-pitch-elevated text-sm text-brand-gold">
        <span class="flex items-center gap-2"><span>⚡</span> Log Coin Balance</span>
        <span class="text-xs text-txt-muted mono">L</span>
      </button>
    `;
  }

  let debounceTimer = null;
  if (cmdSearchInput) {
    cmdSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      clearTimeout(debounceTimer);
      if (q.length < 2) {
        renderDefaultCommands();
        return;
      }
      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/v1/search/users?q=${encodeURIComponent(q)}`);
          const users = await res.json();
          if (!users.length) {
            cmdResultsList.innerHTML = `<div class="p-4 text-center text-sm text-txt-muted">No players or vaults found matching "${q}".</div>`;
            return;
          }
          cmdResultsList.innerHTML = `
            <div class="px-3 py-2 text-xs font-semibold text-txt-muted uppercase tracking-wider">Players Found (${users.length})</div>
            ${users
              .map(
                (u) => `
              <a href="${u.url}" class="cmd-item flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-pitch-elevated text-sm text-txt-primary">
                <div class="flex items-center gap-3">
                  <img src="${u.avatar_url}" class="w-7 h-7 rounded-full border border-borderUi-subtle object-cover" />
                  <div>
                    <div class="font-medium">${u.display_name}</div>
                    <div class="text-xs text-txt-muted mono">@${u.username}</div>
                  </div>
                </div>
                <div class="text-right">
                  <span class="mono font-bold text-brand-gold">${u.balance.toLocaleString()}</span>
                  <span class="text-xs text-txt-muted block">coins</span>
                </div>
              </a>
            `
              )
              .join('')}
          `;
        } catch (err) {
          console.error('Search error', err);
        }
      }, 200);
    });
  }

  // Keyboard shortcut listener
  window.addEventListener('keydown', (e) => {
    // Cmd+K or Ctrl+K
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      if (cmdPaletteModal && !cmdPaletteModal.classList.contains('hidden')) {
        closeCommandPalette();
      } else {
        openCommandPalette();
      }
    }
    // Escape closes modals
    if (e.key === 'Escape') {
      closeCommandPalette();
      window.COINVAULT.closeLogModal();
    }
    // Press 'l' when not typing in an input
    if (e.key.toLowerCase() === 'l' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      window.COINVAULT.openLogModal();
    }
  });

  // 6. GLOBAL COINVAULT NAMESPACE
  window.COINVAULT = {
    openLogModal: function () {
      const modal = document.getElementById('log-coin-modal');
      if (modal) {
        closeCommandPalette();
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        const amtInput = document.getElementById('coin-amount-input');
        if (amtInput) amtInput.focus();
      }
    },
    closeLogModal: function () {
      const modal = document.getElementById('log-coin-modal');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    },
    openCommandPalette: openCommandPalette,
    closeCommandPalette: closeCommandPalette,
    animateCounters: animateCounters,
  };
})();
