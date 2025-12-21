# -----------------------------
# HORDE KEYS (Birden fazla key desteği - sırayla dene)
# -----------------------------
HORDE_KEYS = [
    "cQ9Kty7vhFWfD8nddDOq7Q",
    "ceIr0GFCjybUk_3ItTju0w",
    "_UZ8x88JEw4_zkIVI1GkpQ",
    "8PbI2lLTICOUMLE4gKzb0w",
    "SwxAZZWFvruz8ugHkFJV5w",
    "AEFG4kHNWHKPCWvZlEjVUg",
    "0000000000",
    "Q-zqB1m-7kjc5pywX52uKg",
    "pZCw23N2DBaP7M0vXmGdfQ"
]

# Çalışan bir key bulana kadar sırayla dene
HORDE_KEY = "0000000000"  # Varsayılan anonim (eğer hiçbiri çalışmazsa)
print("🔑 Horde key'leri test ediliyor...", flush=True)

for key in HORDE_KEYS:
    try:
        test_url = "https://stablehorde.net/api/v2/stats/totals"
        headers = {"apikey": key}
        response = requests.get(test_url, headers=headers, timeout=10)
        if response.status_code == 200:
            HORDE_KEY = key
            print(f"✅ Çalışan Horde Key bulundu: {key[:6]}******", flush=True)
            break
    except:
        continue

if HORDE_KEY == "0000000000":
    print("⚠️ Hiçbir key çalışmadı, anonim modda devam ediliyor (daha yavaş olabilir).", flush=True)
else:
    print(f"🚀 Horde Key aktif! Hızlı generation bekleniyor.", flush=True)
