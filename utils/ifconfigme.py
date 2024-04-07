import requests
import urllib3
urllib3.disable_warnings()

def check_ip():
    print("[+] Checking IP.. before request..")
    ifconfigme = 'https://ifconfig.me'
    r = requests.get(url=ifconfigme, verify=False, allow_redirects=True)
    print(r.text)