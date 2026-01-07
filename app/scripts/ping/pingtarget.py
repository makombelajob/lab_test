import sys, subprocess, ipaddress, socket
from scripts.db.mysql_get_conn import get_connection

def is_ip(value):
    """Check if the value is an IP address"""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False

def resolve_host_ip(host):
    """
    Resolve host to (hostname, ip) tuple.
    - If host is IP: try reverse DNS, else None
    - If host is domain: forward DNS, else None
    """
    try:
        if is_ip(host):
            return socket.gethostbyaddr(host)[0], host
        else:
            return host, socket.gethostbyname(host)
    except (socket.herror, socket.gaierror):
        return (host if not is_ip(host) else None,
                host if is_ip(host) else None)

def do_ping(host, count=3):
    """
    Ping host `count` times.
    Prints Windows-style output.
    Returns a dict with ping statistics.
    """
    received = 0
    for _ in range(count):
        try:
            subprocess.check_output(
                ["ping", "-c", "1", "-W", "2", host],
                stderr=subprocess.DEVNULL
            )
            received += 1
            print(f"Reply from {host}: bytes=32 time<1ms TTL=128")
        except subprocess.CalledProcessError:
            print("Request timed out.")
    lost = count - received
    return {
        "sent": count,
        "received": received,
        "lost": lost,
        "loss_percent": int((lost / count) * 100)
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python emailfound.py <user_id> <hostname|ip>")
        sys.exit(1)

    user_id, target = sys.argv[1], sys.argv[2]

    conn = get_connection()

    # Dynamic column selection for IP/domain
    column = "ip_address" if is_ip(target) else "hostname"

    with conn.cursor(dictionary=True) as cur:
        cur.execute(
            f'SELECT * FROM ping WHERE user_id=%s AND {column}=%s ORDER BY id DESC LIMIT 1',
            (user_id, target)
        )
        row = cur.fetchone()
        if not row:
            print("No entry found in the database")
            return

    # Resolve hostname/IP
    resolved_hostname, resolved_ip = resolve_host_ip(target)

    # Determine host to ping
    host_to_ping = resolved_ip if resolved_ip else target
    print(f"Pinging {host_to_ping} with 32 bytes of data:")

    # Perform ping 3 times
    ping_result = do_ping(host_to_ping, count=3)
    print(f"Ping statistics: Sent = {ping_result['sent']}, "
          f"Received = {ping_result['received']}, "
          f"Lost = {ping_result['lost']} ({ping_result['loss_percent']}% loss)")

    # Update database
    status = 1 if ping_result['received'] > 0 else 0
    new_hostname = resolved_hostname if resolved_hostname else row['hostname']
    new_ip = resolved_ip if resolved_ip else row['ip_address']

    with conn.cursor() as cur:
        cur.execute(
            'UPDATE ping SET hostname=%s, ip_address=%s, status=%s WHERE id=%s',
            (new_hostname, new_ip, status, row['id'])
        )
        conn.commit()

    conn.close()

if __name__ == "__main__":
    main()
