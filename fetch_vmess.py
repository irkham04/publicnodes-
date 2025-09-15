import os, re, base64, json, asyncio, pathlib
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

VMESS_RE = re.compile(r'vmess://[^\s]+')
CHANNEL_USERNAME = "foolvpn"
TOPIC_TITLE = "Public Nodes"  # Topik/thread yang ingin diambil

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    # Ambil entity channel
    channel = await client.get_entity(CHANNEL_USERNAME)

    # Ambil list threads/topics di channel
    threads = await client.get_forum_topics(channel)
    topic_id = None
    for t in threads:
        if t.title.lower() == TOPIC_TITLE.lower():
            topic_id = t.id
            break

    if topic_id is None:
        print(f"❌ Thread '{TOPIC_TITLE}' tidak ditemukan di channel {CHANNEL_USERNAME}")
        await client.disconnect()
        return

    # Ambil semua pesan di thread tertentu
    msgs = await client.get_messages(channel, limit=None, topic_id=topic_id)
    print(f"📄 Total pesan di thread '{TOPIC_TITLE}': {len(msgs)}")

    all_text = []

    for m in msgs:
        if m.message:
            all_text.append(m.message)
        if m.media:
            path = await m.download_media(file="downloads/")
            print(f"📄 Attachment diunduh ke {path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    all_text.append(f.read())
            except Exception as e:
                print(f"⚠️ Gagal baca attachment {path}: {e}")

    combined_text = "\n".join(all_text)

    # Ekstrak VMESS dan hapus duplikat
    vmess_links = list(dict.fromkeys(VMESS_RE.findall(combined_text)))

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

    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/vmess.txt").write_text("\n".join(vmess_links))
    pathlib.Path("results/vmess_decoded.json").write_text(
        json.dumps(results_json, indent=2, ensure_ascii=False)
    )

    print(f"✅ Total VMESS unik ditemukan: {len(vmess_links)}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
