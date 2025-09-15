import os, re, json, base64, asyncio, pathlib
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

CHANNEL_USERNAME = "foolvpn"
KEYWORD = "Free Public Proxy"

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    channel = await client.get_entity(CHANNEL_USERNAME)

    collected_links = []
    vmess_count = 0

    async for m in client.iter_messages(channel, limit=None, reverse=False):
        if m.message and KEYWORD.lower() in m.message.lower():
            info = {}
            for line in m.message.splitlines():
                line = line.strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    info[key.strip().lower()] = val.strip()

            vpn_type = info.get("vpn", "").lower()
            url = None

            if vpn_type == "vmess" and vmess_count < 3:
                # Bangun VMESS URL
                vmess_obj = {
                    "v": 2,
                    "ps": info.get("id", "VMESS"),
                    "add": info.get("server", ""),
                    "port": int(info.get("port", 0)),
                    "id": info.get("uuid", ""),
                    "aid": int(info.get("aid", 0)) if info.get("aid") else 0,
                    "net": info.get("transport", "ws"),
                    "type": "none",
                    "host": info.get("host", ""),
                    "path": info.get("path", ""),
                    "tls": info.get("tls", "")
                }
                b64 = base64.b64encode(json.dumps(vmess_obj).encode()).decode()
                url = f"vmess://{b64}"
                vmess_count += 1
            elif vpn_type == "vless":
                # Bangun VLESS URL
                server = info.get("server", "")
                port = info.get("port", "")
                uuid = info.get("uuid", "")
                net = info.get("transport", "ws")
                path = info.get("path", "")
                host = info.get("host", "")
                tls = info.get("tls", "")
                params = []
                if net:
                    params.append(f"net={net}")
                if path:
                    params.append(f"path={path}")
                if host:
                    params.append(f"host={host}")
                if tls:
                    params.append(f"security={tls}")
                param_str = "&".join(params)
                url = f"vless://{uuid}@{server}:{port}?{param_str}"
            elif vpn_type == "trojan":
                # Bangun Trojan URL
                password = info.get("password", "")
                server = info.get("server", "")
                port = info.get("port", "")
                url = f"trojan://{password}@{server}:{port}"

            if url:
                collected_links.append(url)

        if len(collected_links) >= 10:
            break

    last_10_links = collected_links[:10]

    print("🔗 10 link terakhir (3 VMESS maksimal, sisanya VLESS/Trojan):")
    for i, link in enumerate(last_10_links, 1):
        print(f"{i}. {link}")

    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/last_10_links.txt").write_text("\n".join(last_10_links))
    pathlib.Path("results/last_10_links.json").write_text(json.dumps(last_10_links, indent=2, ensure_ascii=False))

    print(f"\n✅ Total link disimpan: {len(last_10_links)}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
