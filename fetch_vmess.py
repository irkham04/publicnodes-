import os
import re
import asyncio
from telethon import TelegramClient

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TG_SESSION_B64"]

VMESS_RE = re.compile(r'vmess://[^\s]+')
CHANNEL = "nama_channel_anda"  # ganti sesuai target

async def main():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()

    vmess_links = []
    async for m in client.iter_messages(CHANNEL, limit=100):
        if m.message and "Free Public Proxy" in m.message:
            links = VMESS_RE.findall(m.message)
            vmess_links.extend(links)
        if len(vmess_links) >= 10:
            break

    vmess_links = vmess_links[:10]

    os.makedirs("results", exist_ok=True)
    with open("results/vmess.txt", "w") as f:
        f.write("\n".join(vmess_links))

    print(f"✅ Selesai! {len(vmess_links)} VMESS disimpan di results/vmess.txt")

asyncio.run(main())
