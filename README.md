# 🤖 Voice Activity Monitor Bot

Welcome to the **Voice Activity Monitor Bot** — a professional Discord bot that tracks muted users in voice channels, sends warnings, and applies timeouts when necessary. Built with **Python and discord.py**, fully configurable via slash commands.

---

## ✨ Features

✔ Track users who stay muted in voice channels  
✔ Send warning messages after configurable time  
✔ Automatically timeout users after continued inactivity  
✔ Multiple bypass roles (e.g., Automod, staff)  
✔ Dynamic live console dashboard  
✔ Slash commands for live configuration  
✔ Mute status check command  
✔ Multiple warning channels support  
✔ AFK channel ignore (optional)  
✔ Professional and scalable design

---

## 🛠 Commands

### Configuration (Admin Only)

/set_warning_time <seconds>
👉 Set time before warning is sent.

---

/set_timeout_time <seconds>
👉 Set total mute duration before timeout.

---

/add_bypass_role <role>
👉 Add a role to bypass tracking.

---

/remove_bypass_role <role>
👉 Remove a bypass role.

---

### Monitoring

/mutestatus @user
👉 Check how long a user has been muted in VC.

---

## ⚙️ Setup

1. Install dependencies:

```bash
pip install discord.py
```

Configure bot token and IDs in code:

TOKEN = "YOUR_BOT_TOKEN"

Enable these intents in Developer Portal:

Server Members Intent

Voice State Intent

Invite bot with:

applications.commands
bot

Run the bot:

python bot.py
🚀 Permissions Required

Moderate Members (for timeouts)

Send Messages

View Channels

Slash Command Scope

🧠 How It Works

User joins voice and stays muted

Timer starts tracking muted time

Warning after configured time

Timeout after continued inactivity

Bypass roles are ignored

📌 Notes

Commands sync instantly per guild during testing

Global sync may take up to 1 hour

Role hierarchy matters for timeouts

System channel is optional (warnings use configured channels)

💡 Future Ideas

Database logging

Web dashboard

Advanced analytics

Role-based rules

Made with ❤️ and professional care for Discord communities.
