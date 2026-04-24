# Network Monitor - Home Assistant Addon

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![HA Addon](https://img.shields.io/badge/Home%20Assistant-Addon-41BDF5.svg)](https://www.home-assistant.io/addons)

Monitor your network devices, track IP changes, and receive Telegram notifications. **Fully local. Fully secure.**

---

## ☕ Support this project

If this addon saves you time, consider buying me a coffee!

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/elbarto83)

---

## Features

✅ **Automatic network scanning** every hour (configurable)  
✅ **Device identification** via MAC OUI lookup — recognizes Samsung, Apple, TP-Link, Xiaomi, etc.  
✅ **Web dashboard** to see all your devices at a glance  
✅ **Secure API** with API Key authentication on every endpoint  
✅ **Telegram notifications** for:
- Device changes IP address
- Device goes offline for too long
- Daily summary report

✅ **Local database** — SQLite, everything stays on your Home Assistant  
✅ **Zero cloud** — completely offline, no external services  

---

## Installation (step by step)

### Requirements

- Home Assistant OS or Home Assistant Supervised
- **NOT compatible** with Home Assistant Core or Container (addon support required)
- Internet connection (only for first-time MAC OUI database download and optional Telegram)

---

### Step 1 — Add the repository to Home Assistant

1. Open Home Assistant in your browser
2. Go to **Settings** (bottom left gear icon)
3. Click **Add-ons**
4. Click the **three dots** (⋮) button in the top-right corner
5. Select **Repositories**
6. In the text field that appears, paste this URL:

   ```
   https://github.com/elbarto8383/network_manager.git
   ```

7. Click **Add**
8. Click **Close**

---

### Step 2 — Install the addon

1. Scroll down in the **Add-ons** page (or search at top for "Network Monitor")
2. Click on **Network Monitor**
3. Click **Install** and wait (first install takes ~2 minutes, it downloads dependencies)
4. When Install is complete, you will see the addon page

---

### Step 3 — Configure the addon

1. On the addon page, click the **Configuration** tab
2. Fill in your settings:

   | Field | Description | Example |
   |-------|-------------|---------|
   | `network_range` | Your network subnet | `192.168.1.0/24` |
   | `scan_interval_hours` | How often to scan (hours) | `1` |
   | `offline_threshold_hours` | Alert after X hours offline | `2` |
   | `api_key` | Random password for web dashboard | `MySecret123` |
   | `telegram_enabled` | Enable Telegram notifications | `false` |
   | `telegram_bot_token` | Bot token from BotFather | _(optional)_ |
   | `telegram_chat_id` | Your Telegram chat ID | _(optional)_ |

3. Click **Save**

#### How to find your network range

If you don't know your subnet, check on Home Assistant:
- Go to **Settings** → **System** → **Network**
- Your local IP will look like `192.168.1.x` or `10.0.0.x`
- The range will be `192.168.1.0/24` or `10.0.0.0/24`

#### How to set up Telegram (optional)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. Copy the **bot token** you receive (format: `123456:ABC-DEF...`)
4. Search for **@userinfobot** on Telegram and send `/start`
5. Copy your **Chat ID** (a number like `123456789`)
6. Set `telegram_enabled` to `true` and paste both values

---

### Step 4 — Start the addon

1. Click the **Info** tab on the addon page
2. Toggle **Start on boot** to ON (recommended)
3. Click **Start**
4. Wait ~10 seconds for the addon to initialize
5. Check the **Logs** tab — you should see:
   ```
   🚀 Network Monitor - Home Assistant Addon
   ==========================================
   📍 Network range: 192.168.1.0/24
   🔄 Scan interval: every 1 hour(s)
   🔐 API Key: SET
   [+] Starting web server on http://0.0.0.0:5000
   [*] Initial scan...
   ```

---

### Step 5 — Open the Web Dashboard

1. Click the **Open Web UI** button on the addon page
2. A browser window opens to `http://[your-ha-ip]:5000`
3. On first open, it will ask for your **API Key**
4. Enter the `api_key` you set in Step 3
5. Click OK — the key is saved in your browser for future visits

You will see your network devices appear as the initial scan completes (takes 1–5 minutes depending on network size).

---

## Web Dashboard

The dashboard shows:

| Column | Description |
|--------|-------------|
| **Device** | Hostname or device name |
| **IP Address** | Current IP on the network |
| **MAC Address** | Physical hardware address |
| **Manufacturer** | Auto-detected brand (Samsung, Apple, etc.) |
| **Last Seen** | When the device was last found |
| **Status** | Online / Offline |

The dashboard auto-refreshes every 30 seconds. You can also trigger a manual scan with the **Scan Now** button.

---

## API Reference

All endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: MySecret123" http://[your-ha-ip]:5000/api/devices
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/devices` | All devices with status |
| `GET` | `/api/stats` | Online/offline counts |
| `GET` | `/api/device/<mac>` | IP history for one device |
| `POST` | `/api/scan` | Trigger a manual scan |

---

## Security

This addon is designed with local security in mind:

| Feature | Detail |
|---------|--------|
| **API Key required** | Every request must include your key |
| **Local database** | SQLite on Home Assistant, never synced externally |
| **Network scoped** | Only scans your configured local network range |
| **No telemetry** | Zero data sent to external servers |
| **Offline-first** | Works with no internet (Telegram optional) |

---

## Troubleshooting

### No devices found after scan
- Verify your `network_range` matches your actual network
- Some devices block ping — they may not appear
- Check the **Logs** tab for error messages

### API Key rejected (401 error)
- Double-check the key in addon Configuration
- In the dashboard: click **Set API Key** button and re-enter it
- The key is case-sensitive

### Telegram messages not arriving
- Confirm `telegram_enabled` is `true` in Configuration
- Verify the bot token format: `123456789:ABC-defGhI...`
- Make sure you have started a chat with your bot (send `/start` to it)
- Check Logs for specific error messages

### Addon won't start
- Check the **Logs** tab immediately after clicking Start
- Make sure port `5000` is not used by another addon

---

## Support

Found a bug or have a feature request?  
Open an issue: [github.com/elbarto8383/network_manager/issues](https://github.com/elbarto8383/network_manager/issues)

---

## License

MIT — free to use, modify, and distribute.

---

## ☕ Donate

If this project is useful to you, a small donation keeps it going!

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/elbarto83)
