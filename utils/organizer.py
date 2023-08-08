import os
import typer

PERMUTATION_WORDLIST = "wordlists/permutation.txt"
PATHS_WORDLIST = "wordlists/paths.txt"
REGIONS_WORDLIST = "wordlists/regions.txt"
FIRST_NAMES_WORDLIST = "wordlists/names/brazil_firstnames.txt"
LAST_NAMES_WORDLIST = "wordlists/names/brazil_secondname.txt"


class Organizer:
    def __init__(self):
        self.permutation_wordlist = PERMUTATION_WORDLIST
        self.paths_wordlist = PATHS_WORDLIST
        self.regions_wordlist = REGIONS_WORDLIST

    def get_permutation_wordlist_path(self, custom_path: str = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path
        elif os.path.exists(PERMUTATION_WORDLIST):
            return PERMUTATION_WORDLIST
        else:
            raise typer.BadParameter("Wordlist file not found.")
        
    def get_paths_wordlist_path(self, custom_path: str = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path
        elif os.path.exists(PATHS_WORDLIST):
            return PATHS_WORDLIST
        else:
            raise typer.BadParameter("Wordlist file not found.")
    
    def get_regions_wordlist_path(self, custom_path: str = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path
        elif os.path.exists(REGIONS_WORDLIST):
            return REGIONS_WORDLIST
        else:
            raise typer.BadParameter("Wordlist file not found.")
        
    def get_emails_wordlist_path(self, custom_path: str = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path
        else:
            return None
    def get_first_names_wordlist_path(self, custom_path: str = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path
        else:
            return FIRST_NAMES_WORDLIST
    def get_last_names_wordlist_path(self, custom_path: str = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path
        else:
            return LAST_NAMES_WORDLIST