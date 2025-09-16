import os, json, base64, asyncio, pathlib, urllib.parse, uuid, re
from telethon import TelegramClient

SESSION_FILE = "tg_session.session"

if "TG_SESSION_B64" in os.environ:
    with open(SESSION_FILE, "wb") as f:
        f.write(base64.b64decode(os.environ["TG_SESSION_B64"]))

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

CHANNEL_USERNAME = "foolvpn"
KEYWORD = "Free Public Proxy"
FORCED_SERVER = "quiz.vidio.com"

def url_encode_remark(s):
    return urllib.parse.quote(s)

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    channel = await client.get_entity(CHANNEL_USERNAME)

    vmess_links, vless_links, trojan_links = [], [], []

    async for m in client.iter_messages(channel, limit=None, reverse=False):
        if m.message and KEYWORD.lower() in m.message.lower():
            info = {}
            for line in m.message.splitlines():
                line = line.strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    info[key.strip().lower()] = val.strip()

            vpn_type = info.get("vpn", "").lower()

            # ---------------- VMESS ----------------
            if vpn_type == "vmess" and len(vmess_links) < 5:
                vmess_obj = {
                    "v": 2,
                    "ps": info.get("id", f"VMESS-{uuid.uuid4().hex[:6]}"),
                    "add": FORCED_SERVER,
                    "port": int(info.get("port", 443)),
                    "id": info.get("uuid", str(uuid.uuid4())),
                    "aid": int(info.get("aid", 0)) if info.get("aid") else 0,
                    "net": "ws",
                    "type": "none",
                    "host": info.get("host", ""),
                    "path": info.get("path", ""),
                    "tls": info.get("tls", "1")
                }
                b64 = base64.b64encode(json.dumps(vmess_obj).encode()).decode()
                vmess_links.append(f"vmess://{b64}")

            # ---------------- VLESS ----------------
            elif vpn_type == "vless" and len(vless_links) < 5:
                port = info.get("port", "443")
                uuid_val = info.get("uuid", str(uuid.uuid4()))
                path = info.get("path", "")
                host = info.get("host", "")
                tls = info.get("tls", "")
                sni = info.get("sni", "")
                mode = info.get("mode", "")
                org = info.get("org","")
                country = info.get("country","")
                id_field = info.get("id","")
                params = ["net=ws", "type=ws"]
                if path: params.append(f"path={path}")
                if host: params.append(f"host={host}")
                if tls == "1": params.append("security=tls")
                if sni: params.append(f"sni={sni}")
                if mode: params.append(f"mode={mode}")
                param_str = "&".join(params)
                remark = f"{id_field} {country} {org} WS {mode} TLS"
                vless_links.append(f"vless://{uuid_val}@{FORCED_SERVER}:{port}?{param_str}#{url_encode_remark(remark)}")

            # ---------------- Trojan ----------------
            elif vpn_type == "trojan" and len(trojan_links) < 5:
                password = info.get("password", "pass123")
                port = info.get("port", "443")
                path = info.get("path", "")
                tls = info.get("tls", "")
                sni = info.get("sni", "")
                mode = info.get("mode", "")
                org = info.get("org", "")
                country = info.get("country","")
                id_field = info.get("id","")
                params = ["type=ws"]
                if path: params.append(f"path={urllib.parse.quote(path)}")
                if tls == "1": params.append("security=tls")
                if sni: params.append(f"sni={sni}")
                if mode: params.append(f"mode={mode}")
                param_str = "&".join(params)
                remark = f"{id_field} {country} {org} WS {mode} TLS"
                trojan_links.append(f"trojan://{password}@{FORCED_SERVER}:{port}?{param_str}#{url_encode_remark(remark)}")

        # Stop jika semua tipe sudah lengkap
        if len(vmess_links) >= 5 and len(vless_links) >= 5 and len(trojan_links) >= 5:
            break

    all_links = vmess_links + vless_links + trojan_links

    print("🔗 15 link terakhir (5 per tipe):")
    for i, link in enumerate(all_links, 1):
        print(f"{i}. {link}")

    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/last_links.txt").write_text("\n".join(all_links))
    pathlib.Path("results/last_links.json").write_text(json.dumps(all_links, indent=2, ensure_ascii=False))

    print(f"\n✅ Total link disimpan: {len(all_links)}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
