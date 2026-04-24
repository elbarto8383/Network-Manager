# Network Monitor

Un tool leggero per monitorare la tua rete locale, tracciare quali device sono su quali IP, e ricevere notifiche quando cambiano.

## Features

- 📍 **Scansione automatica** ogni ora della rete locale (192.168.1.0/24)
- 🔍 **Identificazione automatica** dei device tramite MAC OUI lookup
- 📊 **Dashboard web** per visualizzare lo stato della rete
- 🔐 **API sicura** con autenticazione per API Key
- 📱 **Notifiche Telegram** per:
  - Device cambia IP
  - Device offline da X ore
  - Report giornaliero riepilogativo
- 💾 **Database locale** SQLite - tutto rimane sulla tua rete
- 🛡️ **Zero cloud** - niente dati esterni, tutto offline

## Setup rapido

```bash
# Clona il repo
git clone https://github.com/elbarto8383/network_manager.git
cd network_manager

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili
cp .env.example .env
# Modifica .env con: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, API_KEY

# Avvia
python main.py
```

Accedi a `http://localhost:5000` (usa l'API Key dal file `.env`)

## Architettura

```
network_manager/
├── app/
│   ├── api.py          # Flask API (sicura, con API Key)
│   ├── scanner.py      # Scansione rete + MAC OUI lookup
│   ├── db.py           # Database SQLite
│   └── notifier.py     # Notifiche Telegram
├── static/
│   └── dashboard.html  # Dashboard web
├── main.py             # Entrypoint
├── requirements.txt
└── .env.example
```

## Sicurezza

✅ API Key per tutti gli endpoint  
✅ Validazione input ristretta  
✅ Database locale (zero esposizione)  
✅ CORS disabilitato per default  
✅ Scansioni solo sulla rete locale  

## CLI

```bash
python main.py scan          # Scansione manuale
python main.py report        # Report giornaliero manuale
python main.py daemon        # Avvia scansioni automatiche ogni ora
```
