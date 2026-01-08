import sys, subprocess, ipaddress, socket, ssl, time
import urllib.request, urllib.parse, urllib.error
from scripts.db.mysql_conn import get_connection
from bs4 import BeautifulSoup
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'


def extract_emails_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    emails = []

    # texte visible
    text = " ".join(soup.get_text().split())
    emails += re.findall(EMAIL_REGEX, text)

    # mailto
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('mailto:'):
            email = a['href'][7:].split('?')[0]
            emails.append(email)

    return list(set(emails))


def main():
    start_time = time.time()
    if len(sys.argv) < 3:
        print("Usage : python emailfound.py <user_id> <hostname|ip>")
        sys.exit(0)

    user_id, target = sys.argv[1], sys.argv[2]

    conn = get_connection()

    with conn.cursor(dictionary=True) as cur:
        cur.execute(
            '''SELECT id, hostname FROM ping
               WHERE user_id = %s
               AND ip_address = %s
               AND hostname IS NOT NULL
               ORDER BY scan_at DESC
               LIMIT 1''',
            (user_id, target)
        )

        row = cur.fetchone()
        if not row:
            print("Aucun hostname trouvé")
            return
        ## Retrieve some variable
        ping_id = row['id']
        base_url = row['hostname']
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'http://' + base_url

        print('Retrieve emails -', base_url)

        # ================= PAGE PRINCIPALE =================
        try:
            response = urllib.request.urlopen(base_url, context=ctx, timeout=10)
            html = response.read()
        except Exception as e:
            print("Erreur page principale :", e)
            return

        all_emails = []
        all_emails += extract_emails_from_html(html)

        soup = BeautifulSoup(html, 'html.parser')

        # ================= RÉCUPÉRATION DES LIENS =================
        linksFound = []

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()

            if not href:
                continue
            if href.startswith(('mailto:', '#', 'javascript:')):
                continue

            full_url = urllib.parse.urljoin(base_url, href)
            linksFound.append(full_url)

        linksFound = list(dict.fromkeys(linksFound))  # déduplication
        print("Liens trouvés :", len(linksFound))

        # ================= SÉLECTION 20 + 20 =================
        selected_links = linksFound[:20] + linksFound[-20:]
        selected_links = list(dict.fromkeys(selected_links))

        print("Liens exploités :", len(selected_links))

        # ================= EXPLOITATION DES LIENS =================
        for url in selected_links:
            print(" → Scan :", url)
            try:
                resp = urllib.request.urlopen(url, context=ctx, timeout=10)
                page_html = resp.read()
            except Exception:
                continue

            emails = extract_emails_from_html(page_html)
            all_emails += emails

        # ================= RÉSULTAT FINAL =================
        all_emails = list(set(all_emails))
        
        elapsed = time.time() - start_time
        print(f"\nTemps d'exécution : {elapsed:.2f} secondes")
        
        print("\nEmails trouvés (total) :")
        for email in all_emails:
            print(" -", email)
            
        # ============== Save in database ==========
        all_links = set(linksFound + selected_links)
        
        # retrieve username from email found
        users_found = set()
        for email in all_emails :
            if "@" in email :
                local_part = email.split("@")[0]
                users_found.add(local_part.lower())
                
        all_emails_str = ", ".join(sorted(set(all_emails)))
        all_users_str = ", ".join(sorted(set(users_found)))
        all_links_str = ", ".join(sorted(set(all_links)))
        
        ## Storing in dbs
        cur = conn.cursor(dictionary=True)
        try:  
            cur.execute(
                '''INSERT INTO reconn (email_found, user_found, link_found, ping_id)
               VALUES (%s, %s, %s, %s)''',
               (all_emails_str, all_users_str, all_links_str, ping_id)
            )
            conn.commit()
            print(f"✅ Emails, users et liens enregistrés pour cible={base_url}")
        except Exception as e :
            print("❌ Erreur lors de l'insertion :", e)
            conn.rollback()
if __name__ == "__main__":
    main()
