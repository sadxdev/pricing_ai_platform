import os
import requests
import time

BASE_URL = "http://nginx"   # internal docker network

TENANT_QUERY_PARAM = "tenant_id=1"


# ----------------------------------------
# Get service account token from Keycloak
# ----------------------------------------
def get_auth_token() -> str:
    res = requests.post(
        "http://keycloak:8080/realms/pricing-ai/protocol/openid-connect/token",
        data={
            "client_id": os.getenv("HEALTH_CHECK_CLIENT_ID", "health-check-service"),
            "client_secret": os.getenv("HEALTH_CHECK_CLIENT_SECRET"),
            "grant_type": "client_credentials"
        },
        timeout=10
    )
    token = res.json().get("access_token")
    if not token:
        raise Exception(f"Failed to get health check token: {res.json()}")
    return token


# ----------------------------------------
# Replace path params like /skus/{id}
# ----------------------------------------
def replace_path_params(path: str):
    return (
        path.replace("{id}", "1")
            .replace("{sku_id}", "1")
            .replace("{tenant_id}", "1")
    )


# ----------------------------------------
# Inject required query params dynamically
# ----------------------------------------
def add_required_query_params(path: str):
    """
    Always inject tenant_id as query param (covers Query(...) routes).
    Also inject sku_id for endpoints that need it.
    Bearer token is sent separately to cover Depends(get_tenant_id) routes.
    """

    # Always add tenant_id as query param
    if "tenant_id=" not in path:
        path += "?" + TENANT_QUERY_PARAM if "?" not in path else "&" + TENANT_QUERY_PARAM

    # Add sku_id only for endpoints that need it
    sku_required_paths = [
        "/skus/1",
        "/pricing/recommend/1",
        "/pricing/calculate/1",
        "/price-history/1",
        "/pricing-explain/1",
        "/analytics/",
        "/optimization/",
        "/rl/reward",
        "/ml/explain-demand/",
    ]

    if any(p in path for p in sku_required_paths):
        if "sku_id=" not in path:
            path += "&sku_id=1"

    return path


# ----------------------------------------
# Safe JSON parser — handles empty/non-JSON
# ----------------------------------------
def _safe_json(res):
    try:
        return res.json()
    except Exception:
        return f"Non-JSON response (status={res.status_code}, body={res.text[:200]!r})"


# ----------------------------------------
# Fetch endpoints from OpenAPI schema
# ----------------------------------------
def fetch_all_endpoints():
    url = "http://nginx/openapi.json"

    try:
        res = requests.get(url, timeout=5)
    except Exception as e:
        print("Failed to connect to OpenAPI:", str(e))
        return []

    if res.status_code != 200:
        print("Failed to load OpenAPI schema")
        return []

    data = res.json()
    paths = data.get("paths", {})

    endpoints = []

    for path, methods in paths.items():
        for method, meta in methods.items():
            method = method.upper()

            # Only GET endpoints
            if method != "GET":
                continue

            # Skip endpoints that require request body
            if meta.get("requestBody"):
                continue

            # Skip heavy ML / training / dataset endpoints
            if any(x in path for x in [
                "training",
                "dataset",
                "ml/predict",
                "/metrics",
            ]):
                continue

            clean_path = replace_path_params(path)
            clean_path = add_required_query_params(clean_path)

            endpoints.append(clean_path)

    # Add /health separately — lives outside /v1
    endpoints.append("/health")

    return endpoints


# ----------------------------------------
# Run health checks on all endpoints
# ----------------------------------------
def run_health_checks():
    endpoints = fetch_all_endpoints()
    results = []

    # Get service account token once for all requests
    try:
        token = get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": "1"
        }
        print("Service account token acquired successfully")
    except Exception as e:
        print(f"Failed to acquire token: {e}")
        headers = {"X-Tenant-ID": "1"}

    print(f"Running health checks for {len(endpoints)} endpoints...\n")

    for ep in endpoints:
        # /health lives outside /v1 so use base nginx URL
        if ep == "/health":
            url = "http://nginx/health"
        else:
            url = f"{BASE_URL}{ep}"

        try:
            start = time.time()
            res = requests.get(url, headers=headers, timeout=10)
            latency = round((time.time() - start) * 1000, 2)

            results.append({
                "endpoint": ep,
                "status_code": res.status_code,
                "success": res.status_code < 400,
                "latency_ms": latency,
                "error_detail": _safe_json(res) if res.status_code in [422, 500] else None
            })

        except Exception as e:
            results.append({
                "endpoint": ep,
                "success": False,
                "error": str(e)
            })

    return results


# ----------------------------------------
# Export results for email report
# ----------------------------------------
results = run_health_checks()