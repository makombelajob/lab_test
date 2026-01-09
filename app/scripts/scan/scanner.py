import sys, subprocess, ipaddress, socket, ssl, time
import urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor
from scripts.db.mysql_conn import get_connection
from bs4 import BeautifulSoup
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def main():
    if len(sys.argv) < 3:
        print("Usage : python scanner.py <user_id> <hostname|ip>")
        sys.exit(0)
        
    user_id, target = sys.argv[1], sys.argv[2]

    start_port = 1
    end_port = 1024
    timeout = 5
    max_threads = 100
    
    print(f"\n==== Scan de la cible {target} ======\n")
    open_ports = []
    
    # ----------------------------
    # 1 Scan des ports
    # ----------------------------
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
    
    # ----------------------------
    # 2 Pour chaque port → bannière → version
    # ----------------------------
    print("\n======= Analyse des services & vulnérabiliés =======\n")

    for port in open_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((target, port))

                # ----------------------------
                # CORRECTION : fingerprinting automatique
                # ----------------------------
                banner = ""

                # 1) Lire si le service parle tout seul (FTP, SSH, MySQL, etc.)
                try:
                    data = sock.recv(1024)
                    if data:
                        banner += data.decode(errors="ignore")
                except:
                    pass

                # 2) Tester HTTP
                try:
                    sock.send(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                    data = sock.recv(1024)
                    if data:
                        banner += data.decode(errors="ignore")
                except:
                    pass

                # 3) Tester HTTPS
                try:
                    ssl_sock = ctx.wrap_socket(sock, server_hostname=target)
                    ssl_sock.send(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                    data = ssl_sock.recv(1024)
                    if data:
                        banner += data.decode(errors="ignore")
                except:
                    pass

                # 4) Tester SMTP
                try:
                    sock.send(b"EHLO test\r\n")
                    data = sock.recv(1024)
                    if data:
                        banner += data.decode(errors="ignore")
                except:
                    pass

                # 5) Tester RTSP
                try:
                    sock.send(b"OPTIONS * RTSP/1.0\r\n\r\n")
                    data = sock.recv(1024)
                    if data:
                        banner += data.decode(errors="ignore")
                except:
                    pass

                banner = banner.strip()
                # ----------------------------

                print(f"[PORT {port}]")
                if banner:
                    print(" Service :", banner)
                else:
                    print("Service : Inconnu ( no banner )")
                    print("-> Impossible de chercher des CVE\n")
                    continue

                # ----------------------------
                # Détection produit + version
                # ----------------------------
                product = None
                version = None

                # Cherche d'abord l'entête Server (HTTP/HTTPS)
                server_match = re.search(r"Server:\s*([A-Za-z\-]+)\/([0-9\.]+)", banner)
                if server_match:
                    product = server_match.group(1)
                    version = server_match.group(2)
                else:
                    # Fallback générique (FTP, RTSP, etc.)
                    generic = re.search(r"([A-Za-z\-]+)[/ _]?([0-9]+\.[0-9]+)", banner)
                    if generic:
                        product = generic.group(1)
                        version = generic.group(2)

                if not product:
                    print("   → Service détecté mais version inconnue\n")
                    continue

                print(f"   → Détecté : {product} {version}\n")

        except:
            print("  -> Erreur lors de la requête vulnérabilités\n")


if __name__ == "__main__":
    main()
