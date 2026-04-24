# Network Monitor - Home Assistant Addon

Monitor your network devices, track IP changes, and receive Telegram notifications. All local, all secure.

## Features

✅ **Automatic network scanning** every hour (192.168.1.0/24)  
✅ **Device identification** via MAC OUI lookup (recognizes Samsung, Apple, TP-Link, etc.)  
✅ **Web dashboard** to visualize your network  
✅ **Secure API** with authentication  
✅ **Telegram notifications** for IP changes & offline devices  
✅ **Local database** SQLite - everything stays on your network  
✅ **Zero cloud** - completely offline  

## Installation

1. **Add the repository to Home Assistant:**
   - Settings → Devices & Services → Add-ons → Create add-on repository
   - URL: `https://github.com/elbarto8383/network_manager.git`

2. **Install the addon:**
   - Find "Network Monitor" in the add-on store
   - Click Install

3. **Configure the addon:**
   - Set your network range (default: `192.168.1.0/24`)
   - Set API Key (random string for web dashboard)
   - (Optional) Add Telegram bot token and chat ID for notifications

4. **Start the addon:**
   - Click Start
   - Open the Web UI

## Configuration

### Network Range
Default: `192.168.1.0/24`  
Set this to your local network subnet.

### Scan Interval
Default: `1` hour  
How often to scan for devices (1-24 hours).

### API Key
Generate a random string for web dashboard authentication.  
Example: `your-secure-random-key-here`

### Telegram Notifications (Optional)
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your Chat ID from [@userinfobot](https://t.me/userinfobot)
3. Enter credentials in addon options

## Usage

### Web Dashboard
Open the addon's Web UI to see:
- All devices on your network
- Which IP each device has
- When devices were last seen
- Online/offline status

### Security
- ✅ API Key required for all endpoints
- ✅ Database is local (not synced anywhere)
- ✅ Scans only your local network
- ✅ No external API calls (except Telegram if enabled)

## API

All endpoints require `X-API-Key` header:

```bash
curl -H "X-API-Key: your-key" http://localhost:5000/api/devices
```

### Endpoints

- `GET /api/devices` - All devices
- `GET /api/stats` - Network statistics
- `GET /api/device/<mac>` - Device history
- `POST /api/scan` - Trigger manual scan

## Examples

### Get all devices
```bash
curl -H "X-API-Key: your-key" http://localhost:5000/api/devices
```

### Trigger a scan
```bash
curl -X POST -H "X-API-Key: your-key" http://localhost:5000/api/scan
```

### Get device history
```bash
curl -H "X-API-Key: your-key" http://localhost:5000/api/device/aa:bb:cc:dd:ee:ff
```

## Troubleshooting

### No devices found
- Make sure `NETWORK_RANGE` matches your network
- Check if devices are responding to ping
- Ensure the addon has network permissions

### API Key not working
- Regenerate API Key in addon options
- Clear browser cache and localStorage
- Reload the dashboard

### Telegram not sending
- Verify bot token and chat ID are correct
- Make sure addon has internet access
- Check logs for errors

## Security Notes

🔒 **Local first** - All data stays on your Home Assistant instance  
🔒 **No external storage** - Database is SQLite on your filesystem  
🔒 **API authentication** - Every request requires API Key  
🔒 **Network isolated** - Only scans your local network  

## Support

Issues? Check the logs:
```
Settings → Devices & Services → Add-ons → Network Monitor → Logs
```

Or create an issue on GitHub: https://github.com/elbarto8383/network_manager/issues
