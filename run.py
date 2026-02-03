from telethon import TelegramClient, events
import asyncio, time

api_id = 30423434        # <-- তোমার api_id
api_hash = "d14bd5bd80b90d951bcd861ad476a79a"  # <-- তোমার api_hash
session = "offline_userbot"

client = TelegramClient(session, api_id, api_hash)

OFFLINE = True
last_reply = {}

REPLY_TEXT = "আমি এখন offline আছি 🙂\nপরে রিপ্লাই দেব।"
DELAY = 1       # seconds
COOLDOWN = 60    # same user কে ১ মিনিটে ১বার

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global OFFLINE

    if not OFFLINE:
        return

    if not event.is_private:
        return

    sender = event.sender_id
    now = time.time()

    if sender in last_reply and now - last_reply[sender] < COOLDOWN:
        return

    await asyncio.sleep(DELAY)
    await event.reply(REPLY_TEXT)
    last_reply[sender] = now


@client.on(events.NewMessage(pattern="/offline"))
async def set_offline(event):
    global OFFLINE
    OFFLINE = True
    await event.reply("🟡 Offline mode ON")


@client.on(events.NewMessage(pattern="/online"))
async def set_online(event):
    global OFFLINE
    OFFLINE = False
    await event.reply("🟢 Online mode OFF")


print("Userbot running...")
client.start()
client.run_until_disconnected()
