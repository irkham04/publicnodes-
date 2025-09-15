import os, re, json, base64, asyncio, pathlib
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

# Simpan session jika ada di environment
if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

CHANNEL_USERNAME = "foolvpn"
KEYWORD = "Free Public Proxy"

# Regex sederhana untuk capture URL (vmess, vless, trojan)
URL_RE = re.compile(r'(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+)')

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    channel = await client.get_entity(CHANNEL_USERNAME)
    collected_messages = []

    # Iterasi pesan terbaru → lama, hanya pesan yang mengandung keyword
    async for m in client.iter_messages(channel, limit=None, reverse=False):
        if m.message and KEYWORD.lower() in m.message.lower():
            collected_messages.append(m.message)
        if len(collected_messages) >= 10:
            break

    # Ambil 10 pesan terakhir
    last_10_messages = collected_messages[-10:]

    print(f"🔗 10 pesan terakhir dengan keyword '{KEYWORD}':")
    for i, msg in enumerate(last_10_messages, 1):
        print(f"\n=== Pesan {i} ===\n{msg}")

    # Simpan format asli
    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/last_10_proxies.txt").write_text("\n\n".join(last_10_messages))

    # Buat JSON terstruktur dari info di pesan
    structured_results = []
    for msg in last_10_messages:
        info = {}
        for line in msg.splitlines():
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                info[key.strip()] = val.strip()
            # Tangkap URL terakhir di pesan
            urls = URL_RE.findall(line)
            if urls:
                info['URL'] = urls[-1]  # biasanya 1 URL per pesan
        structured_results.append(info)

    pathlib.Path("results/last_10_proxies.json").write_text(
        json.dumps(structured_results, indent=2, ensure_ascii=False)
    )

    print(f"\n✅ Total pesan unik terakhir disimpan: {len(last_10_messages)}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
