import os, json, base64, asyncio, pathlib, urllib.parse
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

CHANNEL_USERNAME = "foolvpn"
KEYWORD = "Free Public Proxy"

FORCED_SERVER = "quiz.vidio.com"  # paksa semua server di URL

def url_encode_remark(s):
    return urllib.parse.quote(s)

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

            # ---------------- VMESS ----------------
            if vpn_type == "vmess" and vmess_count < 3:
                vmess_obj = {
                    "v": 2,
                    "ps": info.get("id", "VMESS"),
                    "add": FORCED_SERVER,
                    "port": int(info.get("port", 0)),
                    "id": info.get("uuid", ""),
                    "aid": int(info.get("aid", 0)) if info.get("aid") else 0,
                    "net": "ws",
                    "type": "none",
                    "host": info.get("host", ""),
                    "path": info.get("path", ""),
                    "tls": info.get("tls", "")
                }
                b64 = base64.b64encode(json.dumps(vmess_obj).encode()).decode()
                url = f"vmess://{b64}"
                vmess_count += 1

            # ---------------- VLESS ----------------
            elif vpn_type == "vless":
                port = info.get("port", "")
                uuid = info.get("uuid", "")
                path = info.get("path", "")
                host = info.get("host", "")
                tls = info.get("tls", "")
                sni = info.get("sni", "")
                mode = info.get("mode", "")
                org = info.get("org","")
                country = info.get("country","")
                id_field = info.get("id","")
                params = [f"net=ws", f"type=ws"]
                if path: params.append(f"path={path}")
                if host: params.append(f"host={host}")
                if tls == "1": params.append("security=tls")
                if sni: params.append(f"sni={sni}")
                if mode: params.append(f"mode={mode}")
                param_str = "&".join(params)
                remark = f"{id_field} {country} {org} WS {mode} TLS"
                url = f"vless://{uuid}@{FORCED_SERVER}:{port}?{param_str}#{url_encode_remark(remark)}"

            # ---------------- Trojan ----------------
            elif vpn_type == "trojan":
                password = info.get("password", "")
                port = info.get("port", "")
                path = info.get("path", "")
                tls = info.get("tls", "")
                sni = info.get("sni", "")
                mode = info.get("mode", "")
                org = info.get("org", "")
                country = info.get("country","")
                id_field = info.get("id","")
                params = [f"type=ws"]
                if path: params.append(f"path={urllib.parse.quote(path)}")
                if tls == "1": params.append("security=tls")
                if sni: params.append(f"sni={sni}")
                if mode: params.append(f"mode={mode}")
                param_str = "&".join(params)
                remark = f"{id_field} {country} {org} WS {mode} TLS"
                url = f"trojan://{password}@{FORCED_SERVER}:{port}?{param_str}#{url_encode_remark(remark)}"

            if url:
                collected_links.append(url)

        if len(collected_links) >= 10 and vmess_count >= 3:
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
