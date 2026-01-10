import sys, socket, ssl, time, json, re
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from scripts.db.mysql_conn import get_connection

# =============================
# SSL context (safe)
# =============================
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def main():
    start_time = time.time()

    if len(sys.argv) < 3:
        print("Usage : python scanner.py <user_id> <hostname|ip>")
        sys.exit(0)

    user_id, target = sys.argv[1], sys.argv[2]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # =======================
    # Get ping_id
    # =======================
    cur.execute("""
        SELECT id FROM ping
        WHERE user_id=%s AND ip_address=%s
        ORDER BY scan_at DESC
        LIMIT 1
    """, (user_id, target))

    row = cur.fetchone()
    if not row:
        print("❌ Aucun ping trouvé pour cette cible")
        return

    ping_id = row["id"]

    start_port = 1
    end_port = 10000
    timeout = 3
    max_threads = 200

    print(f"\n==== Scan de la cible {target} ======\n")

    # =============================
    # OS Fingerprint (simple TTL)
    # =============================
    os_guess = "Inconnu"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((target, 80))
        ttl = s.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
        s.close()

        if ttl <= 64:
            os_guess = "Linux / Unix"
        elif ttl <= 128:
            os_guess = "Windows"
        else:
            os_guess = "Routeur / BSD"
    except:
        pass

    print("====== Détection du système ======")
    print(f" OS probable : {os_guess}\n")

    # =============================
    # Scan ports
    # =============================
    open_ports = []

    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            if result == 0:
                print(f"[+] Port ouvert : {port}")
                return port
        except:
            pass
        return None

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for p in executor.map(scan_port, range(start_port, end_port + 1)):
            if p:
                open_ports.append(p)

    if not open_ports:
        print("\nAucun Port ouvert")
        return

    print("\nPorts ouverts :", open_ports)
    print("\n======= Analyse des services =======\n")

    # =============================
    # Analyse ports
    # =============================
    for port in open_ports:
        print(f"[PORT {port}]")
        banner = ""

        # ---- TCP + lecture passive
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            try:
                banner = sock.recv(1024).decode(errors="ignore")
            except:
                pass

            # ---- tentative HTTP si rien reçu
            if not banner:
                try:
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = sock.recv(1024).decode(errors="ignore")
                except:
                    pass

            sock.close()
        except:
            pass

        # ---- tentative TLS propre (nouvelle connexion)
        if not banner:
            try:
                raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raw.settimeout(2)
                raw.connect((target, port))
                tls = ctx.wrap_socket(raw, server_hostname=target)
                tls.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = tls.recv(1024).decode(errors="ignore")
                tls.close()
            except:
                pass

        if not banner:
            print(" Service : Inconnu (no banner)\n")
            continue

        banner = banner.strip()
        print(" Service :", banner)

        # =============================
        # Detect product + version
        # =============================
        product = None
        version = None

        # Apache / nginx style
        m1 = re.search(r"Server:\s*([A-Za-z0-9\-_]+)\/([0-9\.]+)", banner)

        # FileZilla style
        m2 = re.search(r"(FileZilla Server)\s+([0-9\.]+)", banner)

        # Splunk style
        m3 = re.search(r"Server:\s*(Splunkd)", banner)

        # Fallback generic
        m4 = re.search(r"([A-Za-z][A-Za-z0-9\-_]+)[/ ]([0-9]+\.[0-9]+)", banner)

        if m1:
            product, version = m1.group(1), m1.group(2)
        elif m2:
            product, version = m2.group(1), m2.group(2)
        elif m3:
            product, version = m3.group(1), "unknown"
        elif m4:
            product, version = m4.group(1), m4.group(2)
        else:
            # IMPORTANT : ne jamais laisser product à None
            product = "unknown"
            version = None

        if product != "unknown":
            print(f"   → Détecté : {product} {version}")
        else:
            print("   → Service détecté mais version inconnue")

        # =============================
        # CVE lookup
        # =============================
        vuln_list = []
        bad = ["http", "https", "ftp", "smtp", "imap", "pop", "tcp", "udp", "rtsp"]

        if product and version and product.lower() not in bad and re.match(r"[0-9]+\.[0-9]+", str(version)):
            try:
                query = f"{product} {version}"
                url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=" + urllib.parse.quote(query)
                resp = urllib.request.urlopen(url, timeout=15)
                data = json.loads(resp.read().decode())

                for v in data.get("vulnerabilities", [])[:5]:
                    vuln_list.append(v["cve"]["id"])
            except:
                pass

        vuln_str = ", ".join(vuln_list) if vuln_list else None

        # =============================
        # Insert / Update DB
        # =============================
        try:
            cur.execute("SELECT id FROM scanner WHERE ping_id=%s AND port=%s", (ping_id, port))
            row = cur.fetchone()

            if row is None:
                cur.execute("""
                    INSERT INTO scanner
                    (port, service, version, script_vuln, state, os_detected, ping_id, description)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (port, product, version, vuln_str, "open", os_guess, ping_id, banner[:1000]))
            else:
                cur.execute("""
                    UPDATE scanner SET
                        service=%s,
                        version=%s,
                        script_vuln=%s,
                        state=%s,
                        os_detected=%s,
                        description=%s
                    WHERE ping_id=%s AND port=%s
                """, (product, version, vuln_str, "open", os_guess, banner[:1000], ping_id, port))

            conn.commit()
            print(f"✅ Port {port} enregistré\n")

        except Exception as e:
            conn.rollback()
            print("❌ DB :", e, "\n")

    elapsed = time.time() - start_time
    print(f"\nTemps d'exécution : {elapsed:.2f} secondes\n")


if __name__ == "__main__":
    main()
