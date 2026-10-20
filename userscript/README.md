# COINVAULT Direct Terminal Link (Tampermonkey Userscript)

The **COINVAULT Userscript** allows players to automatically extract their active eFootball coin balance directly from authorized web pages (e.g. Konami My Page, Point Store, eFootball companion site) and securely sync it to their COINVAULT account via Bearer token authentication.

Entries submitted through this script receive the **"Verified via script"** status pill on all leaderboards.

---

## Installation Steps

1. **Install Tampermonkey**:
   - Install the official [Tampermonkey browser extension](https://www.tampermonkey.net/) for Chrome, Edge, Brave, or Firefox.

2. **Generate your COINVAULT API Token**:
   - Log in to your COINVAULT account.
   - Navigate to **Settings** (`/settings`) > **Developer & Script Integration**.
   - Under **Generate Personal API Token**, enter a descriptive label (e.g., `Desktop Chrome`) and click **Generate Secret Bearer Token**.
   - Copy the secret token (`cv_...`). *It will only be shown once in plain text.*

3. **Install the Userscript**:
   - Click Tampermonkey icon in your browser toolbar > **Create a new script**.
   - Delete any default template and paste the entire contents of `coinvault-verifier.user.js`.
   - Press **File > Save** (or `Ctrl+S`).

4. **Configure your Token**:
   - Navigate to your eFootball web page.
   - You will see a small, elegant floating **COINVAULT** pill in the lower right corner.
   - Click the gear icon (`⚙`) on the HUD pill.
   - Enter your COINVAULT server endpoint (defaults to `http://127.0.0.1:5000/api/v1/coins/log` for local dev or your production domain).
   - Paste your secret `cv_...` Bearer token.
   - Click **Save Configuration**.

5. **Syncing**:
   - When on your balance page, click **Sync** on the HUD pill.
   - The HUD will confirm with `✓ Synced: X coins` and your balance will update live across COINVAULT leaderboards.

---

## Technical Limitations & DOM Scraping Reality (Transparency Notice)

> **Important**: This companion script relies on browser DOM scraping of the rendered balance element.
> - **It is NOT a cryptographic game server hook**: Because Konami does not provide a public OAuth2 API for third-party balance queries, the script reads the numeric value rendered on screen.
> - **CSS Selector Changes**: If Konami redesigns their site markup or changes class names, the balance selector might fail. If this happens, right-click your coin balance on the webpage, select **Inspect Element**, find the class or id, and update the **Coin Balance CSS Selector** in the script settings.
> - **Anti-Cheat Layer**: Even with the script, entries undergo server-side statistical anomaly detection (`evaluate_entry_for_outliers`). Impossible single-day jumps or non-integer injections will still be flagged for admin review.
