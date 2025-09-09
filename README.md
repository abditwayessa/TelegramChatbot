# Coop App Telegram Support Chatbot 🤖💬

The **Coop App Telegram Support Chatbot** is an intelligent customer support assistant built with Python.  
It helps Coopbank customers and staff access essential services like branch and ATM locators, daily exchange rates, FAQs, and direct support — all within Telegram.  

---

## ✨ Features

- 🌐 **Multi-language Support** — 3 languages, switch anytime.  
- 🏦 **Branch & ATM Locator** — Quickly find the nearest Coopbank branch or ATM.  
- 💱 **Daily Exchange Rates** — Get updated rates instantly.  
- ❓ **Q&A Support** — The bot responds automatically to predefined and fuzzy-matched queries.  
- 📞 **Support Contact Info** — Directly access Coopbank’s support details.  
- 📢 **Broadcast Messaging**  
  - Send announcements with or without images.  
  - Delete broadcast messages from all users.  
- 👤 **User Management**  
  - Send targeted messages to specific users.  
  - Delete messages sent by users.  
- 📊 **Statistics** — Track bot usage and user engagement.  
- 🛠️ **Extensible** — Built to grow with future needs.  

---

## 🗂️ Directory Structure

CoopAppTelegramBot/
│── atm.json # ATM location data
│── branch.json # Branch location data
│── broadcast.json # Broadcast management
│── env.txt # Environment variables (API keys, DB settings)
│── log.txt # Logs (runtime activity)
│── users.json # User tracking and metadata
│── bot.py # Main bot application
│── models.py # Database models (SQLAlchemy)
│── requirements.txt # Python dependencies
│── test_connection.py # Database connection test


---

## ⚙️ Requirements

Create a `requirements.txt` with the following:  
python-telegram-bot==13.7
SQLAlchemy==1.4.25
asyncpg==0.23.0
fuzzywuzzy==0.18.0


Install dependencies:  
```bash
pip install -r requirements.txt
```
🚀 Getting Started

Clone the repository:
```
git clone https://github.com/yourusername/CoopAppTelegramBot.git
cd CoopAppTelegramBot
```

Set up your environment variables in ```env.txt```:
```
TELEGRAM_API_KEY=your_telegram_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
ADMIN_ID= telegram id of admin
```

Run the bot:
```
python bot.py
```
🌍 Usage Examples

```/start``` → Welcome message and language selection.

```/branch finfinne``` → Locate Coopbank Finfinne branches with their detail.

```/atm finfinne``` → Locate Coopbank Finfinne branches ATM.

```/exchange``` → Get today’s exchange rates.

```/contact_us``` → To get support contact details.

```/language``` → Change language(Supports ```Afaan Oromoo```, ```አማርኛ```, ```English```)

Admins can:

```/broadcastimage <message> <image_ur>``` → Send broadcast message text with image to all users.

```/broadcast <message>``` → Send broadcast message text only.

```/send <user_chat_id> <message>``` → Send message to specific users.

```/delete <user_chat_id> <message_id>>``` → Delete message that sent to specific users.

```/verify_broadcast``` → Verify broadcast message before it is sent to the users.

```/delete_broadcast``` → Delete broadcasted message.

```/info``` → Get bot status


🔒 Security & Privacy

Only usrname and user id collected(To send broadcast and support specific users)

Users interact anonymously unless they initiate contact.

Broadcasts and logs are securely stored and managed.

📌 Future Enhancements

AI-powered natural language understanding (NLU).

Integration with Coopbank’s core systems for real-time services.

Advanced analytics dashboard for the support team.

👨‍💻 Author

Developed by Abdi T. Wayessa with ❤️ using Python & Telegram Bot API.
