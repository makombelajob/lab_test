import sys, socket, ssl, time, json
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from scripts.db.mysql_conn import get_connection
import re

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
    end_port = 1024
    timeout = 5
    max_threads = 100

    print(f"\n==== Scan de la cible {target} ======\n")

    # =============================
    # OS Fingerprint
    # =============================
    os_guess = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target, 80))
        ttl = s.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
        s.close()

        if ttl <= 64:
            os_guess = "Linux / Unix"
        elif ttl <= 128:
            os_guess = "Windows"
        else:
            os_guess = "Routeur / BSD"

        print("====== Détection du système ======")
        print(f" OS probable : {os_guess} (TTL={ttl})\n")
    except:
        print("====== Détection du système ======")
        print(" OS non détectable\n")

    # =============================
    # Scan ports
    # =============================
    open_ports = []

    def scan_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex((target, port)) == 0:
                    print(f"[+] Port ouvert : {port}")
                    return port
        except:
            pass
        return None

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(scan_port, range(start_port, end_port + 1))

    for p in results:
        if p:
            open_ports.append(p)

    if not open_ports:
        print("\nAucun Port ouvert")
        return

    print("\nPorts ouverts :", open_ports)
    print("\n======= Analyse des services & vulnérabilités =======\n")

    # =============================
    # Analyse ports
    # =============================
    for port in open_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((target, port))

                banner = ""

                try:
                    banner += sock.recv(1024).decode(errors="ignore")
                except:
                    pass

                try:
                    sock.send(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                    banner += sock.recv(1024).decode(errors="ignore")
                except:
                    pass

                try:
                    ssl_sock = ctx.wrap_socket(sock, server_hostname=target)
                    ssl_sock.send(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                    banner += ssl_sock.recv(1024).decode(errors="ignore")
                except:
                    pass

                banner = banner.strip()

                print(f"[PORT {port}]")
                if not banner:
                    print("Service : Inconnu ( no banner )")
                    print("-> Impossible de chercher des CVE\n")

                    # insert minimal
                    cur.execute("""
                        INSERT INTO scanner (port, state, ping_id, os_detected)
                        VALUES (%s,%s,%s,%s)
                    """, (port, "open", ping_id, os_guess))
                    conn.commit()
                    continue

                print(" Service :", banner)

                # =============================
                # Detect product + version
                # =============================
                product = None
                version = None

                server_match = re.search(r"Server:\s*([A-Za-z\-]+)\/([0-9\.]+)", banner)
                if server_match:
                    product = server_match.group(1)
                    version = server_match.group(2)
                else:
                    generic = re.search(r"([A-Za-z\-]+)[/ _]?([0-9]+\.[0-9]+)", banner)
                    if generic:
                        product = generic.group(1)
                        version = generic.group(2)

                if not product:
                    print("   → Service détecté mais version inconnue\n")

                    cur.execute("""
                        INSERT INTO scanner (port, state, ping_id, os_detected, description)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (port, "open", ping_id, os_guess, banner[:1000]))
                    conn.commit()
                    continue

                print(f"   → Détecté : {product} {version}")

                # =============================
                # CVE lookup
                # =============================
                vuln_list = []
                bad = ["http","https","ftp","smtp","imap","pop","tcp","udp","rtsp"]

                if product.lower() not in bad and re.match(r"[0-9]+\.[0-9]+", version):
                    try:
                        query = f"{product} {version}"
                        url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=" + urllib.parse.quote(query)
                        resp = urllib.request.urlopen(url, timeout=15)
                        data = json.loads(resp.read().decode())

                        for v in data.get("vulnerabilities", [])[:5]:
                            cve = v["cve"]["id"]
                            vuln_list.append(cve)
                    except:
                        pass

                vuln_str = ", ".join(vuln_list) if vuln_list else None

                # =============================
                # INSERT into DB
                # =============================
                try:
                    cur.execute("""
                        INSERT INTO scanner
                        (port, service, version, script_vuln, state, os_detected, ping_id, description)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        port,
                        product,
                        version,
                        vuln_str,
                        "open",
                        os_guess,
                        ping_id,
                        banner[:1000]
                    ))
                    conn.commit()
                except Exception as e:
                    print("❌ Erreur insertion DB :", e)
                    conn.rollback()

        except Exception as e:
            print("  -> Erreur port", port, e)

    elapsed = time.time() - start_time
    print(f"\nTemps d'exécution : {elapsed:.2f} secondes\n")

if __name__ == "__main__":
    main()
