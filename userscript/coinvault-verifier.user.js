// ==UserScript==
// @name         COINVAULT — eFootball Live Balance Verifier
// @namespace    https://coinvault.terminal
// @version      1.0.0
// @description  Securely extracts your active eFootball coin balance from authorized web companion pages and syncs it to your COINVAULT terminal account.
// @author       COINVAULT Product Engineering
// @match        https://*.konami.net/*
// @match        https://*.efootball.com/*
// @match        http://localhost:5000/*
// @match        http://127.0.0.1:5000/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @connect      localhost
// @connect      127.0.0.1
// @connect      *
// ==/UserScript==

(function() {
    'use strict';

    // ==========================================
    // CONFIGURATION & PERSISTENCE
    // ==========================================
    const DEFAULT_CONFIG = {
        apiEndpoint: GM_getValue('cv_endpoint', 'http://127.0.0.1:5000/api/v1/coins/log'),
        apiToken: GM_getValue('cv_token', ''),
        balanceSelector: GM_getValue('cv_selector', '.coin-amount, [data-testid="coin-balance"], .ef-coins-count, #coin_amount, .user-coin-val'),
        autoSync: GM_getValue('cv_autosync', false)
    };

    console.log('[COINVAULT Verifier] Script active. Target selector:', DEFAULT_CONFIG.balanceSelector);

    // ==========================================
    // BALANCE EXTRACTOR
    // ==========================================
    function parseCoinBalance() {
        const selectors = DEFAULT_CONFIG.balanceSelector.split(',').map(s => s.trim());
        let el = null;

        for (const sel of selectors) {
            el = document.querySelector(sel);
            if (el && el.innerText.trim()) break;
        }

        if (!el) {
            return {
                found: false,
                message: `No balance element matching selectors: "${DEFAULT_CONFIG.balanceSelector}". If the website HTML changed, update the selector in settings.`
            };
        }

        // Clean text: strip commas, currency symbols, whitespace
        const rawText = el.innerText.replace(/[^0-9]/g, '');
        const amount = parseInt(rawText, 10);

        if (isNaN(amount) || amount < 0) {
            return {
                found: false,
                message: `Element found ("${el.innerText}") but could not parse a valid numeric integer balance.`
            };
        }

        return { found: true, amount: amount, element: el };
    }

    // ==========================================
    // DISPATCH TO COINVAULT API
    // ==========================================
    function syncBalanceToVault(amount, sourceNotes = 'Synced via Tampermonkey Extension') {
        const token = GM_getValue('cv_token', '');
        const endpoint = GM_getValue('cv_endpoint', 'http://127.0.0.1:5000/api/v1/coins/log');

        if (!token) {
            alert('[COINVAULT] Missing Bearer Token!\nPlease open your COINVAULT Settings > API Tokens, generate a token, and configure it in the Userscript menu.');
            openSettingsModal();
            return;
        }

        updateStatusBadge('Syncing...', '#f5c451');

        GM_xmlhttpRequest({
            method: 'POST',
            url: endpoint,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            data: JSON.stringify({
                amount: amount,
                note: sourceNotes,
                client_timestamp: new Date().toISOString()
            }),
            onload: function(response) {
                try {
                    const res = JSON.parse(response.responseText);
                    if (response.status === 201 || (response.status === 200 && res.status === 'skipped')) {
                        updateStatusBadge(`✓ Synced: ${amount.toLocaleString()} coins`, '#00f084');
                        setTimeout(() => resetStatusBadge(), 5000);
                    } else {
                        updateStatusBadge(`Sync Failed: ${res.error || response.statusText}`, '#ff3b56');
                    }
                } catch (e) {
                    updateStatusBadge(`Error parsing API response`, '#ff3b56');
                }
            },
            onerror: function(err) {
                console.error('[COINVAULT] HTTP error:', err);
                updateStatusBadge(`Connection Error: Check URL`, '#ff3b56');
            }
        });
    }

    // ==========================================
    // FLOATING HUD PILL
    // ==========================================
    let hudElement = null;

    function renderFloatingHUD() {
        if (hudElement) return;

        hudElement = document.createElement('div');
        hudElement.id = 'coinvault-hud-root';
        hudElement.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: rgba(8, 10, 13, 0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(245, 196, 81, 0.35);
            border-radius: 9999px;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            color: #f1f5f9;
            font-size: 13px;
            font-weight: 500;
        `;

        hudElement.innerHTML = `
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#f5c451; box-shadow:0 0 8px #f5c451;" id="cv-hud-dot"></span>
                <span style="font-weight:700; letter-spacing:0.5px; color:#f5c451;">COINVAULT</span>
            </div>
            <span id="cv-hud-status" style="color:#94a3b8;">Ready</span>
            <button id="cv-btn-sync" style="background:rgba(245, 196, 81, 0.15); border:1px solid #f5c451; color:#f5c451; border-radius:6px; padding:4px 10px; cursor:pointer; font-weight:600; font-size:12px;">Sync</button>
            <button id="cv-btn-cfg" style="background:none; border:none; color:#64748b; cursor:pointer; font-size:14px; padding:2px;">⚙</button>
        `;

        document.body.appendChild(hudElement);

        document.getElementById('cv-btn-sync').onclick = () => {
            const result = parseCoinBalance();
            if (result.found) {
                syncBalanceToVault(result.amount);
            } else {
                alert(`[COINVAULT] ${result.message}`);
            }
        };

        document.getElementById('cv-btn-cfg').onclick = () => openSettingsModal();
    }

    function updateStatusBadge(msg, color) {
        const st = document.getElementById('cv-hud-status');
        const dot = document.getElementById('cv-hud-dot');
        if (st) {
            st.innerText = msg;
            st.style.color = color;
        }
        if (dot) {
            dot.style.background = color;
            dot.style.boxShadow = `0 0 8px ${color}`;
        }
    }

    function resetStatusBadge() {
        updateStatusBadge('Ready', '#94a3b8');
    }

    // ==========================================
    // SETTINGS MODAL
    // ==========================================
    function openSettingsModal() {
        const old = document.getElementById('cv-cfg-modal');
        if (old) old.remove();

        const modal = document.createElement('div');
        modal.id = 'cv-cfg-modal';
        modal.style.cssText = `
            position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 1000000;
            display: flex; align-items: center; justify-content: center; font-family: sans-serif;
        `;
        modal.innerHTML = `
            <div style="background:#0f1318; border:1px solid rgba(255,255,255,0.15); border-radius:14px; padding:24px; width:440px; color:#f1f5f9;">
                <h3 style="margin-top:0; color:#f5c451; font-size:18px;">COINVAULT Script Settings</h3>
                <p style="font-size:12px; color:#94a3b8; line-height:1.4;">Extracts your balance and transmits it to your COINVAULT terminal with verified source badge.</p>
                
                <label style="display:block; font-size:12px; margin-top:12px; color:#94a3b8;">COINVAULT API Endpoint</label>
                <input id="cv-in-url" type="text" value="${GM_getValue('cv_endpoint', 'http://127.0.0.1:5000/api/v1/coins/log')}" style="width:100%; box-sizing:border-box; background:#1b2433; border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#fff; padding:8px; margin-top:4px; font-size:12px;">
                
                <label style="display:block; font-size:12px; margin-top:12px; color:#94a3b8;">Personal Bearer API Token (cv_...)</label>
                <input id="cv-in-tok" type="password" value="${GM_getValue('cv_token', '')}" placeholder="Paste token generated in COINVAULT settings" style="width:100%; box-sizing:border-box; background:#1b2433; border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#fff; padding:8px; margin-top:4px; font-size:12px;">
                
                <label style="display:block; font-size:12px; margin-top:12px; color:#94a3b8;">Coin Balance CSS Selector (Comma-separated fallbacks)</label>
                <input id="cv-in-sel" type="text" value="${GM_getValue('cv_selector', '.coin-amount, [data-testid=\"coin-balance\"], .ef-coins-count, #coin_amount')}" style="width:100%; box-sizing:border-box; background:#1b2433; border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#fff; padding:8px; margin-top:4px; font-size:12px;">
                
                <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:20px;">
                    <button id="cv-btn-cancel" style="background:#212c3d; border:none; color:#94a3b8; border-radius:6px; padding:8px 16px; cursor:pointer;">Cancel</button>
                    <button id="cv-btn-save" style="background:#f5c451; border:none; color:#080a0d; font-weight:700; border-radius:6px; padding:8px 16px; cursor:pointer;">Save Configuration</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('cv-btn-cancel').onclick = () => modal.remove();
        document.getElementById('cv-btn-save').onclick = () => {
            GM_setValue('cv_endpoint', document.getElementById('cv-in-url').value.trim());
            GM_setValue('cv_token', document.getElementById('cv-in-tok').value.trim());
            GM_setValue('cv_selector', document.getElementById('cv-in-sel').value.trim());
            DEFAULT_CONFIG.balanceSelector = document.getElementById('cv-in-sel').value.trim();
            alert('COINVAULT settings updated successfully.');
            modal.remove();
        };
    }

    // Initialize HUD when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', renderFloatingHUD);
    } else {
        renderFloatingHUD();
    }
})();
