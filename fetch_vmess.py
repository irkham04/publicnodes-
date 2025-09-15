import os, re, base64, json, asyncio, pathlib
from telethon import TelegramClient

# ===== Setup session =====
SESSION_FILE = "tg_session.session"

if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))
    print("✅ Session dari TG_SESSION_B64 berhasil dibuat.")

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

VMESS_RE = re.compile(r'vmess://[A-Za-z0-9+/=]+')
CHANNEL = "@foolvpn"

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    # Ambil 200 pesan terakhir
    msgs = await client.get_messages(CHANNEL, limit=200)
    all_text = "\n".join(m.message or "" for m in msgs)

    # Filter pesan yang ada "public nodes"
    public_nodes_text = "\n".join(
        line for line in all_text.splitlines() if "public nodes" in line.lower()
    )

    # Ekstrak VMESS
    vmess_links = VMESS_RE.findall(public_nodes_text)

    # Hapus duplikat
    vmess_links = list(dict.fromkeys(vmess_links))

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
