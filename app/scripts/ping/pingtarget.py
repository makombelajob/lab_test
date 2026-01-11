import sys, subprocess, ipaddress, socket, json
from scripts.db.mysql_conn import get_connection

def is_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def resolve_host_ip(host):
    try:
        if is_ip(host):
            hostname = socket.gethostbyaddr(host)[0]
            return hostname, host
        else:
            ip = socket.gethostbyname(host)
            return host, ip
    except (socket.herror, socket.gaierror):
        if is_ip(host) :
            return None, host
        else:
            return host, None


def do_ping(host, count=3):
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
        print("Usage: python pingtarget.py <user_id> <hostname|ip>")
        sys.exit(1)

    user_id, target = sys.argv[1], sys.argv[2]

    conn = get_connection()

    # Resolve target to hostname + IP
    resolved_hostname, resolved_ip = resolve_host_ip(target)

    host_to_ping = resolved_ip if resolved_ip else target

    print(f"Pinging {host_to_ping} with 32 bytes of data:")

    # Perform ping
    ping_result = do_ping(host_to_ping, count=3)

    print(f"Ping statistics: Sent = {ping_result['sent']}, "
          f"Received = {ping_result['received']}, "
          f"Lost = {ping_result['lost']} ({ping_result['loss_percent']}% loss)")

    status = 1 if ping_result["received"] > 0 else 0

    # Final values stored in DB
    final_hostname = resolved_hostname if resolved_hostname else None
    final_ip = resolved_ip if resolved_ip else None

    ping_data = {
        "hostname": final_hostname,
        "ipAddress": final_ip,
        "status": status,
        "user_id": user_id,
    }

    # Marqueur JSON pour Symfony
    print("\n@@@PINGJSON@@@")
    print(json.dumps(ping_data))
    #print(json.dumps(ping_data))
    # 🔥 IMPORTANT: Always INSERT a new ping row (never UPDATE)
    # with conn.cursor() as cur:
    #     cur.execute("""
    #         INSERT INTO ping (user_id, hostname, ip_address, status)
    #         VALUES (%s, %s, %s, %s)
    #     """, (
    #         user_id,
    #         resolved_hostname,
    #         resolved_ip,
    #         status
    #     ))
    #     conn.commit()

    # conn.close()


if __name__ == "__main__":
    main()
