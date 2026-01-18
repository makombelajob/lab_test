import sys, socket, ssl, time, json, re, urllib.request, urllib.parse, warnings
from concurrent.futures import ThreadPoolExecutor
from scripts.db.mysql_conn import get_connection

sys.stdout.reconfigure(line_buffering=True)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# =============================
# SSL context
# =============================
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# =============================
# PORT FALLBACK MAP
# =============================
PORT_SERVICE_MAP = {
    53:  "DNS",
    88:  "Kerberos",
    135: "MSRPC",
    139: "SMB",
    389: "LDAP",
    445: "SMB",
    464: "Kerberos",
    593: "RPC over HTTP",
    636: "LDAPS",
    2179: "Hyper-V",
    3268: "LDAP GC",
    3269: "LDAPS GC",
    3389: "RDP",
    9389: "AD Web Services"
}

# =============================
# OS detection (ports-based)
# =============================
def os_ports_fingerprint(open_ports):
    windows_ports = {135, 139, 445, 3389, 5985}
    if windows_ports.intersection(open_ports):
        return "Windows (system ports detected)"
    return "Inconnu"

# =============================
# Banner grabber
# =============================
def grab_banner(host, port):
    try:
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
        print("Usage : python scanner.py <user_id> <target>")
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
    # Port scan
    # ---------------------------
    open_ports = []

    def scan_port(port):
        try:
            s = socket.socket()
            s.settimeout(2)
            if s.connect_ex((target, port)) == 0:
                print(f"[+] Port ouvert : {port}")
                return port
            s.close()
        except:
            pass

    with ThreadPoolExecutor(max_workers=200) as exe:
        for p in exe.map(scan_port, range(1, 10001)):
            if p:
                open_ports.append(p)

    print("\nPorts ouverts :", open_ports)

    os_guess = os_ports_fingerprint(open_ports)
    print(f"\n====== Détection du système ======")
    print(f" OS probable : {os_guess}\n")

    # ---------------------------
    # Services
    # ---------------------------
    print("======= Analyse des services =======\n")

    for port in open_ports:
        print(f"[PORT {port}]")

        banner = grab_banner(target, port)
        product = "unknown"
        version = None

        if banner:
            print(" Service :", banner.split("\n")[0])
            b = banner.lower()

            # OpenSSH Windows FIX
            if "openssh" in b:
                product = "OpenSSH"
                m = re.search(r"OpenSSH[_a-zA-Z\-]*([0-9]+\.[0-9]+)", banner)
                if m:
                    version = m.group(1)

            # FTP
            if port == 21:
                if "filezilla" in b:
                    product = "FileZilla Server"
                    m = re.search(r"FileZilla Server\s*([0-9\.]+)", banner)
                    version = m.group(1) if m else None

            # HTTP
            m = re.search(r"Server:\s*([^\r\n]+)", banner, re.I)
            if m and product == "unknown":
                server_line = m.group(1)
                m2 = re.search(r"([A-Za-z\-]+)[/ ]([0-9\.]+)", server_line)
                product = m2.group(1) if m2 else server_line
                version = m2.group(2) if m2 else None

        else:
            product = PORT_SERVICE_MAP.get(port, "unknown")
            print(" Service : Inconnu (no banner)")

        # Fixed services
        if port == 3306:
            product = "MySQL"
        if port == 5985:
            product = "WinRM"

        print(f"   → Détecté : {product} {version}")

        # =============================
        # CVE lookup (TA LOGIQUE)
        # =============================
        vuln_list = []
        bad = ["http","https","ftp","smtp","imap","pop","tcp","udp","rtsp"]

        if product and version:
            if product.lower() not in bad and re.search(r"[0-9]+\.[0-9]+", str(version)):
                try:
                    query = f"{product} {version}"
                    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=" + urllib.parse.quote(query)
                    resp = urllib.request.urlopen(url, timeout=15, context=ctx)
                    data = json.loads(resp.read().decode())

                    for v in data.get("vulnerabilities", []):
                        cve = v.get("cve", {})
                        metrics = cve.get("metrics", {})
                        cvss = 0
                        if "cvssMetricV31" in metrics:
                            cvss = metrics["cvssMetricV31"][0]["cvssData"].get("baseScore", 0)
                        elif "cvssMetricV30" in metrics:
                            cvss = metrics["cvssMetricV30"][0]["cvssData"].get("baseScore", 0)
                        vuln_list.append({"id": cve.get("id"), "cvss": cvss})
                except:
                    pass

        if vuln_list:
            print("   ⚠️  CVE trouvées :", vuln_list)
        else:
            print("   ✓ Aucune CVE connue")

        vuln_str = ", ".join(v["id"] for v in vuln_list) if vuln_list else None

        # =============================
        # DB INSERT / UPDATE (TA LOGIQUE)
        # =============================
        try:
            cur.execute(
                "SELECT id FROM scanner WHERE ping_id=%s AND port=%s",
                (ping_id, port)
            )
            row = cur.fetchone()

            if row:
                cur.execute("""
                    UPDATE scanner SET
                        service=%s,
                        version=%s,
                        script_vuln=%s,
                        state='open',
                        os_detected=%s,
                        description=%s
                    WHERE ping_id=%s AND port=%s
                """, (
                    product,
                    version,
                    vuln_str,
                    os_guess,
                    banner[:1000],
                    ping_id,
                    port
                ))
            else:
                cur.execute("""
                    INSERT INTO scanner
                        (port, service, version, script_vuln, state, os_detected, ping_id, description)
                    VALUES
                        (%s,%s,%s,%s,'open',%s,%s,%s)
                """, (
                    port,
                    product,
                    version,
                    vuln_str,
                    os_guess,
                    ping_id,
                    banner[:1000]
                ))

            conn.commit()
            print("✅ Enregistré\n")

        except Exception as e:
            conn.rollback()
            print("❌ DB:", e)

    print(f"\nTemps d'exécution : {time.time() - start_time:.2f} secondes\n")

if __name__ == "__main__":
    main()
