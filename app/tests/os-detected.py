import requests
import socket
import ssl
from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings()

def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def get_headers(url):
    try:
        r = requests.get(url, timeout=10, allow_redirects=True, verify=False)
        return r.headers, r.cookies, r.url
    except:
        return None, None, None

def get_tls(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.cipher()[0], ssock.version()
    except:
        return None, None

def detect_proxy(headers):
    proxy_headers = [
        "cf-ray","cf-cache-status","x-amz-cf-id","x-sucuri-id",
        "x-fastly-request-id","akamai-grn","x-cdn"
    ]
    for h in headers:
        if h.lower() in proxy_headers:
            return True
    server = headers.get("Server","").lower()
    if "cloudflare" in server or "akamai" in server:
        return True
    return False

def analyze(headers, cookies, tls):
    score = {"Linux":0,"Windows":0,"BSD":0}

    server = headers.get("Server","").lower()

    # HTTP
    if "ubuntu" in server or "debian" in server:
        score["Linux"] += 5
    if "nginx" in server or "apache" in server:
        score["Linux"] += 2
    if "iis" in server or "microsoft" in server:
        score["Windows"] += 5

    # Cookies
    for c in cookies:
        n = c.name.lower()
        if "asp.net" in n:
            score["Windows"] += 6
        if "phpsessid" in n:
            score["Linux"] += 2

    # TLS
    cipher, proto = tls
    if cipher:
        if "ECDSA" in cipher:
            score["Linux"] += 2
        if "RSA" in cipher:
            score["Windows"] += 1

    return score

def normalize(score):
    total = sum(score.values())
    if total == 0:
        return {k:0 for k in score}
    return {k:round((v/total)*100,1) for k,v in score.items()}

def main(url):
    print("Target:", url)
    domain = urlparse(url).netloc

    ip = resolve_domain(domain)
    if not ip:
        print("DNS resolution failed")
        return

    headers, cookies, final_url = get_headers(url)
    if not headers:
        print("HTTP connection failed")
        return

    tls = get_tls(domain)

    print("\nIP:", ip)
    print("Final URL:", final_url)
    print("Server:", headers.get("Server"))
    print("TLS:", tls)

    if detect_proxy(headers):
        print("\n⚠️ Proxy/CDN detected — OS may be masked")

    score = analyze(headers, cookies, tls)
    proba = normalize(score)

    print("\nOS Probability:")
    for k,v in proba.items():
        print(f"{k}: {v}%")

    likely = max(proba, key=proba.get)
    conf = proba[likely]

    if conf < 70:
        print("\nLikely OS: Unknown / Masked")
    else:
        print(f"\nLikely OS: {likely} ({conf}%)")

if __name__ == "__main__":
    main(input("URL: "))
