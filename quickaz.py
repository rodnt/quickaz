import os
import typer
from utils.colors import color_good, color_bad
from enumeration import Enumeration
from brute import Brute
from utils import organizer
from enumeration import Enumeration
from generator import gen
from typing_extensions import Annotated

organizer = organizer.Organizer()
PERMUTATION_WORDLIST = organizer.get_permutation_wordlist_path()
PATHS_WORDLIST = organizer.get_paths_wordlist_path()
REGIONS_WORDLIST = organizer.get_regions_wordlist_path()
EMAILS_WORDLIST = organizer.get_emails_wordlist_path()
FIRST_NAMES_WORDLIST = organizer.get_first_names_wordlist_path()
LAST_NAMES_WORDLIST = organizer.get_last_names_wordlist_path()

app = typer.Typer()
# Main menu
@app.command()
def main_menu(hostname: str, permutation_wordlist_path: Annotated[str, typer.Option(help="Wordlist with common names to permute while brute force blobs and others services")] = PERMUTATION_WORDLIST, brute_blob: Annotated[bool, typer.Option(help="Enable brute force blobs")]= False, paths_wordlist_path: Annotated[str, typer.Option(help="Wordlist with common paths to discover open containers")] = PATHS_WORDLIST, regions_wordlist_path: Annotated[str, typer.Option(help="Wordlist with common regions to discover cloudpass")] = REGIONS_WORDLIST, verbose: bool = False, emails: Annotated[str, typer.Option(help="Wordlist with emails to enumerate")] = EMAILS_WORDLIST, output: Annotated[str, typer.Option(help="Output folder")] = "output", enum_mails: Annotated[bool, typer.Option(help="Enable enumerate emails from wordlist provided or from email generator")] = False, gen_emails: Annotated[str, typer.Option(help="Email pattern to generate emails based on schemas: foo.bar@example.com or fbar@example.com")] = "", first_names: Annotated[str, typer.Option(help="Wordlist with firstnames to generate with gen_emails flag")] = FIRST_NAMES_WORDLIST, last_names: Annotated[str, typer.Option(help="Wordlist with surname to generate with gen_emails flag")] = LAST_NAMES_WORDLIST, threads: Annotated[str, typer.Option(help="Threads while enumerate emails > 2 maybe you get false positives")] = 2, enumall: Annotated[bool, typer.Option(help="Enumerate web,queue,files and others")] = False, proxy: Annotated[str, typer.Option(help="Proxy to use")] = "", socks_proxy: Annotated[str, typer.Option(help="Socks proxy to use")] = "", tor: Annotated[bool, typer.Option(help="Use tor proxy")]= False):




    if output != "":
        try:
            os.mkdir(output)
        except FileExistsError:
            print(color_bad(f"[-] {output} directory already exists."))
    if output == "":
        output = "output"
        try:
            os.mkdir(output)
        except FileExistsError:
            print(color_bad(f"[-] {output} directory already exists."))

    if hostname:
        message = color_good(f"[+] Hostname set to: {hostname}\n[+] Wordlist set to: {permutation_wordlist_path}\n[+] Blob enumeration set to: {brute_blob}\n[+] Paths wordlist set to: {paths_wordlist_path}\n[+] Regions wordlist set to: {regions_wordlist_path} \n[+] Verbose set to: {verbose}\n[+] Emails wordlist set to: {emails}\n[+] Output file set to: {output}, \n[+] Enumerate emails set to: {enum_mails}\n[+] Generate emails set to: {gen_emails}\n[+] First names wordlist set to: {first_names}\n[+] Last names wordlist set to: {last_names}")
        print(message)
        print("\n")

    if gen_emails and enum_mails:
        # verify if dir exists
        try:
           if os.path.isdir(output):
               domain = gen_emails.split("@")[1]
               emails_file = f"{domain}_mails.txt"
               path_emails = os.path.join(output, emails_file)
               print(color_good(f"[+] Emails file set to: {path_emails}"))
               gen_obj = gen.Gen(gen_emails, first_names, last_names, path_emails)
               gen_obj.generate_emails()
               emails = path_emails
        except Exception as e:
            print(color_bad(f"[-] Error: {e}"))
    
        if proxy != "":
            http_proxy = proxy
        else:
            http_proxy = ""

        if socks_proxy != "":
            socks_proxy = socks_proxy
        else:
            socks_proxy = ""
    

    
    brute_obj = Brute.Brute(hostname, permutation_wordlist_path, brute_blob, paths_wordlist_path, regions_wordlist_path, proxy=http_proxy)
    enumeration_obj = Enumeration.Enumeration(hostname, emails, output, threads, proxy=http_proxy, socks=socks_proxy, tor=tor)
    if enum_mails:
        enumeration_obj.process_emails()
    enumeration_obj.get_user_realm_info()
    enumeration_obj.get_openid_configuration()
    enumeration_obj.resolve_hostname() # sharepoint and tenant
    brute_obj.check_blob_urls()
    if enumall:
        print(color_good(f"[+] Enumerating web, queue, files and tables.."))
        brute_obj.enumerate_cloudapp()
        brute_obj.check_webapp_storage()
        brute_obj.check_queue_storage()
        brute_obj.check_file_storage()
        brute_obj.check_table_storage()

if __name__ == "__main__":
    app()
