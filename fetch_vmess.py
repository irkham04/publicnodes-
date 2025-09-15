    combined_text = "\n".join(all_text)

    # Ekstrak VMESS dan hapus duplikat, ambil hanya 10 pertama
    vmess_links = list(dict.fromkeys(VMESS_RE.findall(combined_text)))[:10]

    print("🔗 Daftar VMESS unik (maksimal 10):")
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

    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/vmess.txt").write_text("\n".join(vmess_links))
    pathlib.Path("results/vmess_decoded.json").write_text(
        json.dumps(results_json, indent=2, ensure_ascii=False)
    )

    print(f"✅ Total VMESS unik ditemukan (dibatasi): {len(vmess_links)}")
    await client.disconnect()
