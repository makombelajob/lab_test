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
# OS FINGERPRINT ENGINE
# =============================
def os_http_tls_fingerprint(target):
    score = {"Linux": 0, "Windows": 0}

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

    windows_core_ports = {135, 139, 445, 5985}
    if windows_core_ports.intersection(open_ports):
        os_guess = "Windows (system ports detected)"

    print("\n====== Détection du système ======")
    print(f" OS probable : {os_guess}\n")

    # ---------------------------
    # Services
    # ---------------------------
    print("======= Analyse des services =======\n")

    scanner_rows = []
    for port in open_ports:
        print(f"[PORT {port}]")

        banner = grab_banner(target, port)
        if not banner:
            print(" Service : Inconnu (no banner)\n")
            continue

        print(" Service :", banner.split("\n")[0])

        # =============================
        # SERVICE DETECTION (CORRIGÉ)
        # =============================
        product = "unknown"
        version = None
        b = banner.lower()

        # OpenSSH
        if "openssh" in b:
            m = re.search(r"OpenSSH[_ ]([0-9\.p]+)", banner)
            if m:
                product, version = "OpenSSH", m.group(1)

        # FTP (robuste)
        if port == 21:
            if "pure-ftpd" in b:
                product = "Pure-FTPd"
                version = None

            elif "filezilla server" in b:
                product = "FileZilla Server"
                m = re.search(r"FileZilla Server\s*([0-9\.]+(?:\s*beta)?)", banner, re.I)
                version = m.group(1) if m else None

            elif "vsftpd" in b:
                product = "vsftpd"
                m = re.search(r"vsftpd\s*([0-9\.]+)", banner, re.I)
                version = m.group(1) if m else None

            elif "proftpd" in b:
                product = "ProFTPD"
                m = re.search(r"ProFTPD\s*([0-9\.]+)", banner, re.I)
                version = m.group(1) if m else None

        # SMTP (Exim)
        if port in (25, 26, 465, 587):
            if "exim" in b:
                product = "Exim"
                m = re.search(r"Exim\s+([0-9\.]+)", banner, re.I)
                version = m.group(1) if m else None

        # HTTP
        m = re.search(r"Server:\s*([^\r\n]+)", banner, re.IGNORECASE)
        if m and product == "unknown":
            server_line = m.group(1)
            m2 = re.search(r"([A-Za-z\-]+)[/ ]([0-9\.]+)", server_line)
            product = m2.group(1) if m2 else server_line.strip()
            version = m2.group(2) if m2 else None

        # MySQL
        if port == 3306:
            product = "MySQL"

        # SMB
        if port in (139, 445):
            product = "SMB"

        # FTPS
        if port == 990:
            product = "FTPS"

        # WinRM
        if port == 5985:
            product = "WinRM"

        print(f"   → Détecté : {product} {version}")

        # =============================
        # CVE lookup (inchangé)
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
                        cve_data = v.get("cve", {})
                        metrics = cve_data.get("metrics", {})
                        cvss = 0

                        if "cvssMetricV31" in metrics:
                            cvss = metrics["cvssMetricV31"][0]["cvssData"].get("baseScore", 0)
                        elif "cvssMetricV30" in metrics:
                            cvss = metrics["cvssMetricV30"][0]["cvssData"].get("baseScore", 0)

                        vuln_list.append({"id": cve_data.get("id"), "cvss": cvss})
                except:
                    pass

        if vuln_list:
            print("   ⚠️  CVE trouvées :", vuln_list)
        else:
            print("   ✓ Aucune CVE connue")

        vuln_str = ", ".join(v["id"] for v in vuln_list) if vuln_list else None
        # ================= JSON POUR SYMFONY =================
        # scanner_rows.append({
        #    "port": port,
        #    "service": product,
        #    "version": version,
        #    "script_vuln": vuln_str,
        #    "state": "open",
        #    "os_detected": os_guess,
        #    "description": banner[:1000]
           
        # })
        # reconn_data = {
        #     "ping_id": ping_id,
        #     "scanner": scanner_rows
        # }
        # print("\n@@@RECONNJSON@@@")
        # print(json.dumps(reconn_data))
        ##############################
        #  Store in DB
        ##############################
        try:
            cur.execute("SELECT id FROM scanner WHERE ping_id=%s AND port=%s", (ping_id, port))
            row = cur.fetchone()

            if row:
                cur.execute("""
                    UPDATE scanner SET service=%s, version=%s, script_vuln=%s, state='open',
                    os_detected=%s, description=%s
                    WHERE ping_id=%s AND port=%s
                """, (product, version, vuln_str, os_guess, banner[:1000], ping_id, port))
            else:
                cur.execute("""
                    INSERT INTO scanner
                    (port, service, version, script_vuln, state, os_detected, ping_id, description)
                    VALUES (%s,%s,%s,%s,'open',%s,%s,%s)
                """, (port, product, version, vuln_str, os_guess, ping_id, banner[:1000]))

            conn.commit()
            print("✅ Enregistré\n")
        except Exception as e:
            conn.rollback()
            print("❌ DB:", e)

    print(f"\nTemps d'exécution : {time.time() - start_time:.2f} secondes\n")


if __name__ == "__main__":
    main()
