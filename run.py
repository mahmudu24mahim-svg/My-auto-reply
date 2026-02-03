from telethon import TelegramClient, events
import asyncio, time
import sqlite3

# ================= Configuration =================
api_id = 30423434      # <-- Telegram API ID
api_hash = "d14bd5bd80b90d951bcd861ad476a79a" # <-- Telegram API HASH
session = "offline_userbot"  # session file name

AUTO_REPLY_TEXT = "༄●⃝♔︎=͟͟͞͞𝐔𝐧𝐤𝐧𝐨𝐰𝐧 এখন offline আছে 🙂 পরে রিপ্লাই দিবে।/nPlease Wait My dear....."
OFFLINE_TIMEOUT = 300  # seconds, last seen > 5 mins = offline
DELAY = 3              # seconds before reply
COOLDOWN = 60          # seconds, same user cooldown
# =================================================

client = TelegramClient(session, api_id, api_hash)

last_reply = {}
pending_messages = {}

# ================= Database Setup =================
conn = sqlite3.connect("messages.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    message_text TEXT,
    timestamp TEXT,
    status TEXT
)""")
conn.commit()
# ===================================================

# Function to save messages
def save_message(sender, text, status):
    c.execute("INSERT INTO messages (sender_id, message_text, timestamp, status) VALUES (?, ?, ?, ?)",
              (sender, text, time.ctime(), status))
    conn.commit()

# Auto-reply Handler
@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    sender = event.sender_id
    now = time.time()

    # Ignore self messages
    if sender == (await client.get_me()).id:
        return

    # Save all incoming messages to DB as pending
    save_message(sender, event.raw_text, "pending")
    pending_messages[sender] = event

    # Auto-reply only if offline
    me = await client.get_me()
    user = await client.get_entity(sender)
    # Simple offline detection: last message > OFFLINE_TIMEOUT
    # (Note: Telethon cannot always get exact last_seen)
    # For simplicity, we use delay + cooldown
    if sender in last_reply and now - last_reply[sender] < COOLDOWN:
        return

    await asyncio.sleep(DELAY)
    await event.reply(AUTO_REPLY_TEXT)
    save_message(sender, AUTO_REPLY_TEXT, "sent")
    last_reply[sender] = now

# Periodic check to delete pending messages if user is online
async def delete_on_online():
    while True:
        for sender_id, event in list(pending_messages.items()):
            try:
                # check if user is online
                user = await client.get_entity(sender_id)
                if getattr(user.status, "was_online", None):
                    # user is online, delete pending bot reply
                    await event.delete()
                    save_message(sender_id, event.raw_text, "deleted")
                    pending_messages.pop(sender_id)
            except:
                pass
        await asyncio.sleep(60)  # check every minute

# Start client
async def main():
    await client.start()
    print("Userbot running...")
    client.loop.create_task(delete_on_online())
    await client.run_until_disconnected()

asyncio.run(main())
