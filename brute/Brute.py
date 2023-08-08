import requests
from utils.colors import color_found, color_bad, color_found, color_info, color_collect
import concurrent.futures
import urllib3
import xml.etree.ElementTree as ET


# Suppress the InsecureRequestWarning by disabling SSL certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Brute:
    def __init__(self, hostname, permutation_wordlist_path="wordlists/permutations.txt", brute_blob=False, regions_wordlist_path="wordlists/regions.txt", paths_wordlist_path="wordlists/paths.txt", proxy=None):
        self.hostname = hostname
        self.permutation_wordlist_path = permutation_wordlist_path
        self.brute_blob = brute_blob
        self.regions_wordlist_path = regions_wordlist_path
        self.paths_wordlist_path = paths_wordlist_path
        self.proxy = {"http": proxy, "https": proxy} if proxy else None

    def get_name_from_tld(self):
        tld_parts = self.hostname.split(".")
        if len(tld_parts) > 1:
            return tld_parts[0]
        return self.hostname

    def enumerate_cloudapp(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }
        with open(self.regions_wordlist_path) as f:
            regions = f.readlines()
            for region in regions:
                url = "https://{}.{}.cloudapp.azure.com".format(
                    self.get_name_from_tld(), region.strip())
            try:
                response = requests.get(
                    url, timeout=5, verify=False, headers=headers, proxies=self.proxy)
                if response.status_code == 200:
                    print(color_found(f"Found open cloudapp: {url}"))
            except requests.exceptions.RequestException as e:
                pass

    def check_blob_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:
            response = requests.get(
                url, headers=headers, timeout=4, verify=False, proxies=self.proxy)
            if 'InvalidQueryParameterValue' in response.text:
                print(color_found(
                    f"Found [STORAGE]: {url}"))
                if self.brute_blob:
                    print(color_info(
                        f"Brute forcing paths at: {url} to find open containers..."))
                    self.check_urls_paths(url)
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_blob_urls(self):
        tld = self.get_name_from_tld()
        url_template = "https://{{data}}.blob.core.windows.net"

        try:
            with open(self.permutation_wordlist_path, "r") as f:
                lines = [line.strip() for line in f]

            single = url_template.replace("{{data}}", tld)
            urls = [url_template.replace(
                "{{data}}", tld + line) for line in lines]
            urls_with_slash = [url_template.replace(
                "{{data}}", tld + "-" + line) for line in lines]
            urls_reversed = [url_template.replace(
                "{{data}}", line + tld) for line in lines]
            # word + hostname + word + word
            patterns = [
                'dev',
                'prod',
                'crm',
                'uat',
            ]
            for pattern in patterns:
                urls_fuzzed = [url_template.replace(
                    "{{data}}", line + tld + pattern) for line in lines]

            all_urls = urls + urls_with_slash + \
                urls_reversed + [single] + urls_fuzzed

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                print(color_info('[+] Checking blob urls...'))
                executor.map(self.check_blob_url, all_urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_urls_paths(self, url):

        url_check = url + "/#path#?restype=container&comp=list"

        try:
            # TODO obj bug wordlist path if change to self.paths_wordlist_path not working
            with open("wordlists/paths.txt", "r") as wordlist_file:
                lines = [line.strip() for line in wordlist_file]
            urls = [url_check.replace("#path#", line) for line in lines]
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.check_blob_url_path, urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_blob_url_path(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:
            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if response.status_code == 200 and 'EnumerationResults' in response.text:
                length_blob = len(response.text)
                print(color_found(
                    f"[Blob] found: {url} with size: {length_blob}"))
            elif response.status_code == 200 and 'out of range input' in response.text:
                print(color_info(
                    f"[Blob] found,[check manually]: {url}"))
            elif response.status_code == 200 and 'ResourceNotFound' in response.text:
                print(color_info(
                    f"[Blob] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_queue_storage(self):
        tld = self.get_name_from_tld()
        url_template = "https://{{data}}.queue.core.windows.net"

        try:
            with open(self.permutation_wordlist_path, "r") as f:
                lines = [line.strip() for line in f]

            single = url_template.replace("{{data}}", tld)
            urls = [url_template.replace(
                "{{data}}", tld + line) for line in lines]
            urls_with_slash = [url_template.replace(
                "{{data}}", tld + "-" + line) for line in lines]
            urls_reversed = [url_template.replace(
                "{{data}}", line + tld) for line in lines]
            # word + hostname + word + word
            patterns = [
                'dev',
                'prod',
                'crm',
                'uat',
            ]
            for pattern in patterns:
                urls_fuzzed = [url_template.replace(
                    "{{data}}", line + tld + pattern) for line in lines]

            all_urls = urls + urls_with_slash + \
                urls_reversed + [single] + urls_fuzzed

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.check_queue_url, all_urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_queue_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:
            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if 'InvalidUri' in response.text or 'ResourceNotFound' in response.text:
                print(color_info(
                    f"[Queue] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_table_storage(self):
        tld = self.get_name_from_tld()
        url_template = "https://{{data}}.table.core.windows.net"

        try:
            with open(self.permutation_wordlist_path, "r") as f:
                lines = [line.strip() for line in f]

            single = url_template.replace("{{data}}", tld)
            urls = [url_template.replace(
                "{{data}}", tld + line) for line in lines]
            urls_with_slash = [url_template.replace(
                "{{data}}", tld + "-" + line) for line in lines]
            urls_reversed = [url_template.replace(
                "{{data}}", line + tld) for line in lines]
            # word + hostname + word + word
            patterns = [
                'dev',
                'prod',
                'crm',
                'uat',
            ]
            for pattern in patterns:
                urls_fuzzed = [url_template.replace(
                    "{{data}}", line + tld + pattern) for line in lines]

            all_urls = urls + urls_with_slash + \
                urls_reversed + [single] + urls_fuzzed

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.check_table_url, all_urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_table_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:

            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if 'InvalidUri' in response.text or 'ResourceNotFound' in response.text:
                print(color_info(
                    f"[Table] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_queue_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:

            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if 'InvalidUri' in response.text or 'ResourceNotFound' in response.text:
                print(color_info(
                    f"[Queue] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_file_storage(self):
        tld = self.get_name_from_tld()
        url_template = "https://{{data}}.file.core.windows.net"

        try:
            with open(self.permutation_wordlist_path, "r") as f:
                lines = [line.strip() for line in f]

            single = url_template.replace("{{data}}", tld)
            urls = [url_template.replace(
                "{{data}}", tld + line) for line in lines]
            urls_with_slash = [url_template.replace(
                "{{data}}", tld + "-" + line) for line in lines]
            urls_reversed = [url_template.replace(
                "{{data}}", line + tld) for line in lines]
            # word + hostname + word + word
            patterns = [
                'dev',
                'prod',
                'crm',
                'uat',
            ]
            for pattern in patterns:
                urls_fuzzed = [url_template.replace(
                    "{{data}}", line + tld + pattern) for line in lines]

            all_urls = urls + urls_with_slash + \
                urls_reversed + [single] + urls_fuzzed

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.check_file_url, all_urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_file_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:

            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)

            if 'InvalidQueryParameterValue' in response.text or 'InvalidHeaderValue' in response.text:
                print(color_info(
                    f"[Files URL] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_webapp_storage(self):
        tld = self.get_name_from_tld()
        url_template = "https://{{data}}.web.core.windows.net"

        try:
            with open(self.permutation_wordlist_path, "r") as f:
                lines = [line.strip() for line in f]

            single = url_template.replace("{{data}}", tld)
            urls = [url_template.replace(
                "{{data}}", tld + line) for line in lines]
            urls_with_slash = [url_template.replace(
                "{{data}}", tld + "-" + line) for line in lines]
            urls_reversed = [url_template.replace(
                "{{data}}", line + tld) for line in lines]
            # word + hostname + word + word
            patterns = [
                'dev',
                'prod',
                'crm',
                'uat',
            ]
            for pattern in patterns:
                urls_fuzzed = [url_template.replace(
                    "{{data}}", line + tld + pattern) for line in lines]

            all_urls = urls + urls_with_slash + \
                urls_reversed + [single] + urls_fuzzed

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.check_webapp_url, all_urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_webapp_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:

            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if 'WebContentNotFound' in response.text or 'HttpStatusCode' in response.text:
                print(color_info(
                    f"[Web app enpoint found] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass

    def check_dfs_storage(self):
        tld = self.get_name_from_tld()
        url_template = "https://{{data}}.web.core.windows.net"

        try:
            with open(self.permutation_wordlist_path, "r") as f:
                lines = [line.strip() for line in f]

            single = url_template.replace("{{data}}", tld)
            urls = [url_template.replace(
                "{{data}}", tld + line) for line in lines]
            urls_with_slash = [url_template.replace(
                "{{data}}", tld + "-" + line) for line in lines]
            urls_reversed = [url_template.replace(
                "{{data}}", line + tld) for line in lines]
            # word + hostname + word + word
            patterns = [
                'dev',
                'prod',
                'crm',
                'uat',
            ]
            for pattern in patterns:
                urls_fuzzed = [url_template.replace(
                    "{{data}}", line + tld + pattern) for line in lines]

            all_urls = urls + urls_with_slash + \
                urls_reversed + [single] + urls_fuzzed

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.check_dfs_url, all_urls)

        except FileNotFoundError:
            print("Error: Wordlist file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def check_dfs_url(self, url):

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; ARM Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "Connection": "close",
        }

        try:

            response = requests.get(
                url, headers=headers, timeout=5, verify=False, proxies=self.proxy)
            if 'InvalidUri' in response.text:
                print(color_info(
                    f"[DFS] found,[check manually or fuzzing paths]: {url}"))
            else:
                pass
        except requests.exceptions.RequestException as e:
            # print(f"Error making request to {url}: {e}")
            pass
