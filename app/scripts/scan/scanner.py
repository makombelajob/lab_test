import sys, subprocess, ipaddress, socket, ssl, time
import urllib.request, urllib.parse, urllib.error
from scripts.db.mysql_conn import get_connection
from bs4 import BeautifulSoup
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def main():
    print('Scanner is ready !!')
    
if __name__ == "__main__":
    main()