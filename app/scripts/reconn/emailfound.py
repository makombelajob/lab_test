import sys, subprocess, ipaddress, socket, ssl
from scripts.db.mysql_get_conn import get_connection

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
def main() :
    print('Hello')
if __name__== "__main__":
    main()
