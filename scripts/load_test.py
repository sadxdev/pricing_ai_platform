import requests
import time

BASE = "http://127.0.0.1:8000"

for i in range(50):
    try:
        requests.post(f"{BASE}/auto-pricing/run?tenant_id=1")
        requests.post(f"{BASE}/rl/reward?tenant_id=1&sku_id=1&revenue=1200")
        requests.get(f"{BASE}/analytics/alerts/1?tenant_id=1")
        print(f"Iteration {i} done")
    except Exception as e:
        print("Error:", e)

    time.sleep(0.5)