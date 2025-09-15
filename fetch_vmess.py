import os, re, base64, json, asyncio, pathlib
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

# Simpan session jika ada di environment
if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

# Regex untuk menangkap link
VMESS_RE = re.compile(r'vmess://[^\s]+')
VLESS_RE = re.compile(r'vless://[^\s]+')
TROJAN_RE = re.compile(r'trojan://[^\s]+')

CHANNEL_USERNAME = "foolvpn"
KEYWORD = "Free Public Proxy"

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    channel = await client.get_entity(CHANNEL_USERNAME)

    unique_links = []

    # Iterasi pesan dari terbaru
    async for m in client.iter_messages(channel, limit=None, reverse=False):
        if m.message and KEYWORD.lower() in m.message.lower():
            # Ekstrak semua link dari pesan yang mengandung keyword
            links = []
            links.extend(VMESS_RE.findall(m.message))
            links.extend(VLESS_RE.findall(m.message))
            links.extend(TROJAN_RE.findall(m.message))
            if links:
                unique_links.extend(links)
                # Hapus duplikat sambil jaga urutan
                unique_links = list(dict.fromkeys(unique_links))
            if len(unique_links) >= 10:
                break

    # Ambil 10 link terakhir
    last_10_links = unique_links[-10:]

    print("🔗 10 link terakhir (keyword Free Public Proxy):")
    for i, link in enumerate(last_10_links, 1):
        print(f"{i}. {link}")

    # Decode VMESS dan VLESS
    decoded_results = []
    for link in last_10_links:
        scheme = link.split("://", 1)[0].lower()
        if scheme in ["vmess", "vless"]:
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
        else:
            obj = {"raw": link}  # Trojan tidak perlu decode
        decoded_results.append(obj)

    # Simpan hasil
    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/last_10_links.txt").write_text("\n".join(last_10_links))
    pathlib.Path("results/last_10_links_decoded.json").write_text(
        json.dumps(decoded_results, indent=2, ensure_ascii=False)
    )

    print(f"\n✅ Total link unik terakhir disimpan: {len(last_10_links)}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
