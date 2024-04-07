from utils.colors import color_found, color_bad, color_found, color_collect
import requests
import xml.etree.ElementTree as ET
import json
import concurrent.futures
import re
import socket
import random
import time
import subprocess
from utils import ifconfigme

headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US",
        "Connection": "close",
}


class Enumeration:
    def __init__(self, hostname: str, emails: str, output_path: str, threads: int = 2, proxy: str = None, socks: str = None, tor: bool = False):
        self.hostname = hostname
        self.emails = emails if emails else None
        self.output = output_path if output_path else None
        self.thread_count = int(threads) if threads else 2
        self.proxy = {"http": proxy, "https": proxy} if proxy else None
        self.request_count = 0
        self.socks = {'http':  f'socks5://{socks}','https': f'socks5://{socks}'} if socks else None
        self.tor = tor

    def get_user_realm_info(self):
        base_url = "https://login.microsoftonline.com/getuserrealm.srf"
        url = f"{base_url}?login=user@{self.hostname}&xml=1"

        try:
            response = requests.get(url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if response.status_code != 200:
                print(color_bad(f"Status code for realm endpoint got blocked: {response.status_code}"))
            elif response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'xml' in content_type:
                    try:
                        root = ET.fromstring(response.content)
                        auth_url = root.find(".//AuthURL").text if root.find(".//AuthURL") is not None else None
                        is_federated_ns = root.find(".//IsFederatedNS").text if root.find(".//IsFederatedNS") is not None else None
                        mex_url = root.find(".//MEXURL").text  if root.find(".//MEXURL") is not None else None
                        domain_name = root.find(".//DomainName").text if root.find(".//DomainName") is not None else None
                        federation_brand_name = root.find(".//FederationBrandName").text if root.find(".//FederationBrandName") is not None else None
                        name_space_type = root.find(".//NameSpaceType").text if root.find(".//NameSpaceType") is not None else None


                        if auth_url is not None or is_federated_ns is not None or mex_url is not None or domain_name is not None or federation_brand_name is not None:
                            print(color_collect(f"User realm information for {self.hostname}"))
                            print(color_found(f"AuthURL: {auth_url}"))
                            print(color_found(f"IsFederatedNS: {is_federated_ns}"))
                            print(color_found(f"MEXURL: {mex_url}"))
                            print(color_found(f"DomainName: {domain_name}"))
                            print(color_found(f"FederationBrandName: {federation_brand_name}"))
                            if name_space_type is not None:
                                print(color_collect(f"=[ Target using AZURE AD ]= NameSpaceType: {name_space_type}"))
                        else:
                            message = color_bad("No user realm information found.")
                            print(message)
                    except (ET.ParseError, AttributeError):
                        print(color_bad("Error parsing the XML response."))
        except requests.exceptions.RequestException as e:
                print(color_bad(f"Error: {e}")) 


    def get_openid_configuration(self):
        url_template = "https://login.microsoftonline.com/{{data}}/v2.0/.well-known/openid-configuration"
        url = url_template.replace("{{data}}", self.hostname)

        try:
            response = requests.get(url, verify=False, timeout=5, headers=headers, proxies=self.proxy)
            response.raise_for_status()
            try:
                json_data = response.json()
            except json.JSONDecodeError:
                print("Error: Response does not contain valid JSON data.")
                return
            print("\n")
            print(color_found(f"OpenID Configuration: {url}"))
            important_keys = ['issuer', 'authorization_endpoint', 'token_endpoint', 'userinfo_endpoint', 'jwks_uri', 
                          'response_types_supported', 'id_token_signing_alg_values_supported', 'scopes_supported']
            for key in important_keys:
                if key in json_data:
                    data_print = f"[+]{key}:  {json_data[key]}"
                    print(color_collect(data_print))
            print("\n")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    
    def check_email(self, email):
        self.request_count += 1
        if self.request_count % 10 == 0:
            number = random.randint(1, 100)
            random_email = f'random{number}@{self.hostname}'
            if self.is_email_valid(random_email):
                print(color_bad(f"Random email is valid, you are blocked, sleep 60 seconds.. and try again.."))
                time.sleep(60)
                if self.is_email_valid(random_email):
                    print(color_bad(f"Random email still valid, you are blocked!!"))
                    print("[+] brute force using tor..")
                    ifconfigme.check_ip()
                    self.is_email_valid(email,tor=True)
        else: 
            if self.is_email_valid(email) and self.output is not None:
                print(f'{email} - VALID')
                file_write = 'valid_emails' + self.hostname + '.txt'
                with open(self.output + file_write, 'a+') as output_file:
                    output_file.write(email + '\n')

    def is_email_valid(self, email, tor=False):
        url = 'https://login.microsoftonline.com/common/GetCredentialType'
        body = '{"Username":"%s"}' % email
        session = requests.Session()
        if self.tor: 
            session.proxies = {'http':  'socks5://localhost:9050',
                   'https': 'socks5://localhost:9050'}
            subprocess.run(["sudo", "service", "tor", "restart"])
        if self.socks:
            session.proxies = self.socks

        if tor:
            session.proxies = {'http':  'socks5://localhost:9050',
                   'https': 'socks5://localhost:9050'}
            subprocess.run(["sudo", "service", "tor", "restart"])

        request = requests.post(url, data=body, headers=headers, verify=False, proxies=self.proxy)
        response = request.text
        valid = re.search('"IfExistsResult":0,', response)
        return valid is not None

    def process_emails(self):
        if self.emails:
            with open(self.emails, 'r') as f:
                emails = [line.strip() for line in f]
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                executor.map(self.check_email, emails)
        else:
            print(color_bad("No emails provided."))

    def resolve_hostname_tenant(self, host):
        try:
            if socket.gethostbyname(host):
                return True
            else:
                return False
        except socket.gaierror:
            print(color_bad(f"Hostname {host} could not be resolved."))
            return False

    def resolve_hostname(self):

        tenant_list = []
        mail_list = []
        onedrive_list = []

        url = f'https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc'
        headers = { 'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation"',
            'User-Agent' : 'AutodiscoverClient',
            'Accept-Encoding' : 'identity'
        }
        xml = f'<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:exm="http://schemas.microsoft.com/exchange/services/2006/messages" xmlns:ext="http://schemas.microsoft.com/exchange/services/2006/types" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Header><a:Action soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action><a:To soap:mustUnderstand="1">https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc</a:To><a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo></soap:Header><soap:Body><GetFederationInformationRequestMessage xmlns="http://schemas.microsoft.com/exchange/2010/Autodiscover"><Request><Domain>{self.hostname}</Domain></Request></GetFederationInformationRequestMessage></soap:Body></soap:Envelope>'

        try:
            r = requests.post(url, data=xml, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            domain_extract = re.findall('<Domain>(.*?)<\/Domain>', r.content.decode('utf-8'))
            tenant_extract = [i for i, x in enumerate(domain_extract) if ".onmicrosoft.com" in x and ".mail.onmicrosoft.com" not in x] # this line gets the matching list item numbers only
            if ( len(tenant_extract) > 0):
                for found_tenant in tenant_extract:
                    cleaned_tenant = (domain_extract[found_tenant]).replace('.onmicrosoft.com','').lower()
                    print(color_collect(f"Found tenant: {cleaned_tenant}"))
                    tenant_list.append(cleaned_tenant)
            else:
                print("No tenants found. Exiting.")

            mail_extract = [i for i, x in enumerate(domain_extract) if ".mail.onmicrosoft.com" in x]
            if ( len(mail_extract) > 0):
                for found_tenant in mail_extract:
                    cleaned_mail = (domain_extract[found_tenant]).replace('.mail.onmicrosoft.com','').lower()
                    mail_list.append(cleaned_mail)

            for test_tenant in tenant_list:
                test_hostname = f'{test_tenant}-my.sharepoint.com'
                if self.resolve_hostname_tenant(test_hostname):
                    onedrive_list.append(test_tenant)
        
            if ( len(onedrive_list) > 0 ):
                for onedrive_host in onedrive_list:
                    print(color_collect(f"[+] Onedrive URL: {onedrive_host}-my.sharepoint.com"))
                print("\n")
                if len(onedrive_list) == 1:
                    tenantname = onedrive_list[0]
                else:       
                    matching_mail =  list(set(onedrive_list) & set(mail_list))
                    if matching_mail:
                        tenantname = matching_mail[0]
                    else:
                        print("Could not reliably determine the primary domain. Try specifying different ones using the '-t' flag until you find it.")
                        for tenant in tenant_list:
                            print(f"{tenant}")
                return tenantname
            else:
                print(f"ERROR: NO ONEDRIVE DETECTED!")
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
