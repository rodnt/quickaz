import re


class Gen:
    def __init__(self, email, wordlist_names=None, wordlist_lastnames=None, output="gen_mails.txt") -> None:
        self.email = email
        self.wordlist_names = wordlist_names if wordlist_names else "wordlists/names.txt"
        self.wordlist_lastnames = wordlist_lastnames if wordlist_lastnames else "wordlists/lastnames.txt"
        self.output = output


    def generate_emails(self):
        # Extract the domain from the input email
        try:
            input_email = self.email
            email_domain = input_email.split('@')[1]
        except IndexError:
            raise ValueError("Invalid email structure. Couldn't find an email domain.")

        # Define email patterns with anonymous functions to format the names
        patterns = [
            (re.compile('^[a-z][a-z]+@.+'), lambda f, l: f[0] + l),  # jdoe@domain.com
            (re.compile('^[a-z]+[a-z]+@.+'), lambda f, l: f + l),  # johndoe@domain.com
            (re.compile('^[a-z]+.[a-z]+@.+'), lambda f, l: f + '.' + l),  # john.doe@domain.com
            (re.compile('^[a-z]+_[a-z]+@.+'), lambda f, l: f + '_' + l),  # john_doe@domain.com
        ]

        # Read the first names
        with open(self.wordlist_names, 'r') as f:
            first_names = f.read().splitlines()

        # Read the last names
        with open(self.wordlist_lastnames, 'r') as f:
            last_names = f.read().splitlines()

        # Generated email addresses
        generated_emails = []

        # Check which pattern the input email matches and generate emails accordingly
        for pattern, formatter in patterns:
            if pattern.match(input_email):
                for first_name in first_names:
                    for last_name in last_names:
                        email = f'{formatter(first_name.lower(), last_name.lower())}@{email_domain}'
                        generated_emails.append(email)
                break  # If a match is found, no need to check the other patterns
        
        self.save_emails(generated_emails, self.output)

    def save_emails(self, emails, output_file):
        with open(output_file, 'w') as f:
            for email in emails:
                f.write(email + '\n')