import sys, socket, ssl, time, json, re, urllib.request, urllib.parse, warnings
from concurrent.futures import ThreadPoolExecutor
from scripts.db.mysql_conn import get_connection

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# =============================
# SSL context
# =============================
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# =============================
# OS FINGERPRINT ENGINE
# =============================
def os_http_tls_fingerprint(target):
    score = {"Linux": 0, "Windows": 0}

    # HTTP + HTTPS headers
    for proto in ["http", "https"]:
        try:
            r = urllib.request.urlopen(f"{proto}://{target}", timeout=6, context=ctx)
            headers = r.headers
            server = headers.get("Server", "").lower()

            if "ubuntu" in server or "debian" in server:
                score["Linux"] += 10
            if "apache" in server or "nginx" in server:
                score["Linux"] += 5
            if "iis" in server or "microsoft" in server:
                score["Windows"] += 15

            cookies = headers.get_all("Set-Cookie") or []
            for c in cookies:
                c = c.lower()
                if "asp.net" in c:
                    score["Windows"] += 15
                if "phpsessid" in c:
                    score["Linux"] += 5
        except:
            pass

    # TLS cipher
    try:
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw.settimeout(4)
        raw.connect((target, 443))
        tls = ctx.wrap_socket(raw, server_hostname=target)
        cipher = tls.cipher()[0]
        tls.close()

        if "ECDSA" in cipher:
            score["Linux"] += 5
        if "RSA" in cipher:
            score["Windows"] += 3
    except:
        pass

    total = sum(score.values())
    if total == 0:
        return None

    os_name = max(score, key=score.get)
    confidence = int((score[os_name] / total) * 100)

    if confidence < 40:
        return None

    return f"{os_name} ({confidence}%)"


def os_ports_fingerprint(open_ports):
    windows_ports = {135, 139, 445, 3389, 2179, 5800, 5900, 5040}
    linux_ports = {22, 111, 631, 2049, 5432}

    win_score = len(windows_ports.intersection(open_ports))
    linux_score = len(linux_ports.intersection(open_ports))

    if win_score > linux_score:
        return f"Windows (ports:{win_score})"
    if linux_score > win_score:
        return f"Linux (ports:{linux_score})"
    return None


# =============================
# Banner grabber
# =============================
def grab_banner(host, port):
    try:
        if port in (443, 8443, 9443):
            raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw.settimeout(3)
            raw.connect((host, port))
            tls = ctx.wrap_socket(raw, server_hostname=host)
            tls.send(b"HEAD / HTTP/1.0\r\n\r\n")
            data = tls.recv(2048)
            tls.close()
            return data.decode(errors="ignore")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((host, port))
        try:
            data = sock.recv(2048)
        except:
            sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            data = sock.recv(2048)
        sock.close()
        return data.decode(errors="ignore")
    except:
        return ""


# =============================
# MAIN
# =============================
def main():
    start_time = time.time()

    if len(sys.argv) < 3:
        print("Usage : python scanner.py <user_id> <hostname|ip>")
        return

    user_id, target = sys.argv[1], sys.argv[2]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id FROM ping
        WHERE user_id=%s AND ip_address=%s
        ORDER BY scan_at DESC
        LIMIT 1
    """, (user_id, target))

    row = cur.fetchone()
    if not row:
        print("❌ Aucun ping trouvé")
        return

    ping_id = row["id"]

    print(f"\n==== Scan de la cible {target} ======\n")

    # ---------------------------
    # Scan ports
    # ---------------------------
    open_ports = []
    timeout = 2

    def scan_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((target, port)) == 0:
                s.close()
                print(f"[+] Port ouvert : {port}")
                return port
            s.close()
        except:
            pass
        return None

    with ThreadPoolExecutor(max_workers=200) as exe:
        for p in exe.map(scan_port, range(1, 10001)):
            if p:
                open_ports.append(p)

    print("\nPorts ouverts :", open_ports)

    # ---------------------------
    # OS detection
    # ---------------------------
    os_guess = os_http_tls_fingerprint(target)
    os_ports = os_ports_fingerprint(open_ports)

    if os_ports:
        os_guess = os_ports if not os_guess else os_guess + " + " + os_ports
    if not os_guess:
        os_guess = "Inconnu"

    print("\n====== Détection du système ======")
    print(f" OS probable : {os_guess}\n")

    # ---------------------------
    # Services
    # ---------------------------
    print("======= Analyse des services =======\n")

    for port in open_ports:
        print(f"[PORT {port}]")

        banner = grab_banner(target, port)
        if not banner:
            print(" Service : Inconnu (no banner)\n")
            continue

        print(" Service :", banner.split("\n")[0])

        product = "unknown"
        version = None

        if "OpenSSH" in banner:
            m = re.search(r"OpenSSH[_ ]([0-9\.p]+)", banner)
            if m:
                product, version = "OpenSSH", m.group(1)

        m = re.search(r"Server:\s*([A-Za-z0-9\-_]+)\/([0-9\.]+)", banner)
        if m:
            product, version = m.group(1), m.group(2)

        print(f"   → Détecté : {product} {version}")

        try:
            cur.execute("SELECT id FROM scanner WHERE ping_id=%s AND port=%s", (ping_id, port))
            row = cur.fetchone()

            if row:
                cur.execute("""
                    UPDATE scanner SET service=%s, version=%s, state='open',
                    os_detected=%s, description=%s
                    WHERE ping_id=%s AND port=%s
                """, (product, version, os_guess, banner[:1000], ping_id, port))
            else:
                cur.execute("""
                    INSERT INTO scanner
                    (port, service, version, state, os_detected, ping_id, description)
                    VALUES (%s,%s,%s,'open',%s,%s,%s)
                """, (port, product, version, os_guess, ping_id, banner[:1000]))

            conn.commit()
            print("✅ Enregistré\n")
        except Exception as e:
            conn.rollback()
            print("❌ DB:", e)

    print(f"\nTemps d'exécution : {time.time() - start_time:.2f} secondes\n")


if __name__ == "__main__":
    main()
