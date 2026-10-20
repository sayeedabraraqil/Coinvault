/**
 * COINVAULT — Real-Time WebSocket / Activity Stream
 * Listens for live balance logs, emits rank changes, and manages toast popups.
 */

(function () {
  'use strict';

  if (typeof io === 'undefined') return;

  const socket = io();

  socket.on('connect', () => {
    console.log('[COINVAULT RT] Connected to live platform stream.');
  });

  socket.on('activity_feed', (data) => {
    // 1. Show Toast
    showLiveToast(data);

    // 2. Prepend to Activity Ticker / Feed container if on page
    const feedContainer = document.getElementById('live-activity-stream');
    if (feedContainer) {
      const item = document.createElement('div');
      item.className = 'glass-panel p-3 rounded-lg flex items-center justify-between text-xs animate-pulse-subtle border-borderUi-active';
      const isPositive = data.delta > 0;
      const sign = isPositive ? '+' : '';
      const colorClass = isPositive ? 'text-brand-turf' : 'text-brand-crimson';

      item.innerHTML = `
        <div class="flex items-center gap-2.5">
          <img src="${data.avatar_url}" class="w-6 h-6 rounded-full border border-borderUi-subtle object-cover" />
          <span class="font-semibold text-txt-primary">${data.display_name}</span>
          ${data.source === 'script' ? '<span class="px-1.5 py-0.5 rounded bg-brand-cyan/15 text-brand-cyan text-[10px] font-mono border border-brand-cyan/30">Verified</span>' : ''}
        </div>
        <div class="mono font-bold ${colorClass}">
          ${sign}${Number(data.delta).toLocaleString()}
          <span class="text-txt-muted font-normal text-[10px] ml-1">(${Number(data.amount).toLocaleString()} total)</span>
        </div>
      `;

      feedContainer.insertBefore(item, feedContainer.firstChild);

      // Keep only 10 items in feed list
      if (feedContainer.children.length > 10) {
        feedContainer.removeChild(feedContainer.lastChild);
      }
    }
  });

  function showLiveToast(data) {
    const toastArea = document.getElementById('toast-notification-area');
    if (!toastArea) return;

    const toast = document.createElement('div');
    toast.className = 'glass-panel px-4 py-3 rounded-xl shadow-terminal flex items-center gap-3 border-l-4 border-l-brand-gold text-xs transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-auto max-w-sm';

    const isPositive = data.delta > 0;
    const sign = isPositive ? '+' : '';
    const color = isPositive ? 'text-brand-turf' : 'text-brand-crimson';

    toast.innerHTML = `
      <img src="${data.avatar_url}" class="w-8 h-8 rounded-full border border-borderUi-subtle flex-shrink-0" />
      <div class="flex-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-txt-primary">${data.display_name}</span>
          <span class="text-[10px] text-txt-muted mono">${data.timestamp}</span>
        </div>
        <div class="text-txt-secondary mt-0.5">
          Logged balance: <b class="text-brand-gold mono">${Number(data.amount).toLocaleString()}</b> 
          <span class="mono font-semibold ${color}">(${sign}${Number(data.delta).toLocaleString()})</span>
        </div>
      </div>
    `;

    toastArea.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-4', 'opacity-0');
    });

    // Auto dismiss after 5s
    setTimeout(() => {
      toast.classList.add('opacity-0', '-translate-y-2');
      setTimeout(() => toast.remove(), 350);
    }, 5000);
  }
})();
