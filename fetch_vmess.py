import os, re, base64, json, asyncio, pathlib
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

# Simpan session jika ada di environment
if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

VMESS_RE = re.compile(r'vmess://[^\s]+')
CHANNEL_USERNAME = "foolvpn"
TOPIC_KEYWORD = "Free Public Proxy"  # Filter pesan terbaru

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    channel = await client.get_entity(CHANNEL_USERNAME)

    # Ambil pesan terakhir yang mengandung TOPIC_KEYWORD dan "vmess://"
    vmess_links = []
    async for m in client.iter_messages(channel, limit=500, reverse=True):
        if m.message and TOPIC_KEYWORD.lower() in m.message.lower():
            matches = VMESS_RE.findall(m.message)
            if matches:
                vmess_links.extend(matches)
        if len(vmess_links) >= 10:
            break

    # Ambil 10 VMESS terakhir
    vmess_links = list(dict.fromkeys(vmess_links))[-10:]

    print("🔗 10 VMESS terakhir (filter Free Public Proxy):")
    for i, v in enumerate(vmess_links, 1):
        print(f"{i}. {v}")

    results_json = []
    for link in vmess_links:
        b64 = link.split("://", 1)[1]
        pad = len(b64) % 4
        if pad:
            b64 += "=" * (4 - pad)
        try:
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            try:
                obj = json.loads(decoded)
            except Exception:
                obj = {"raw": decoded}
        except Exception as e:
            obj = {"error": str(e), "link": link}
        results_json.append(obj)

    # Simpan hasil
    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/vmess.txt").write_text("\n".join(vmess_links))
    pathlib.Path("results/vmess_decoded.json").write_text(
        json.dumps(results_json, indent=2, ensure_ascii=False)
    )

    print(f"✅ Total VMESS unik disimpan: {len(vmess_links)}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
