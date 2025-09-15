from telethon import TelegramClient
import re, base64, json, pathlib, asyncio, os

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
PHONE = os.environ["TELEGRAM_PHONE"]

SESSION = "tg_session"
VMESS_RE = re.compile(r'vmess://[A-Za-z0-9+/=]+')


async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(phone=PHONE)

    # ambil 30 pesan terakhir dari channel @foolvpn
    msgs = await client.get_messages("@foolvpn", limit=30)
    all_text = "\n".join(m.message or "" for m in msgs)

    vmess_links = VMESS_RE.findall(all_text)
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

    print(f"✅ Total VMESS ditemukan: {len(vmess_links)}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
