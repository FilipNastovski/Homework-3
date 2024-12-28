from bs4 import BeautifulSoup
from typing import List
import requests


class IssuerCodeExtractor:
    def __init__(self):
        self.url = "https://www.mse.mk/en/stats/symbolhistory/ADIN"

        self.urls = [
            "https://www.mse.mk/en/issuers/JSC-with-special-reporting-obligations",
            "https://www.mse.mk/en/issuers/free-market"
        ]

    def get_issuer_codes_from_dropdown(self) -> List[str]:
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        dropdown = soup.find('select', {'id': 'Code'})
        options = dropdown.find_all('option')
        codes = [option['value'] for option in options if option['value']]

        return codes

    def get_issuer_codes(self) -> List[str]:
        all_codes = []

        for url in self.urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                soup = BeautifulSoup(response.content, 'html.parser')

                table = soup.find('table', {'id': 'otherlisting-table'})
                if table:
                    # skip header row if it exists
                    rows = table.find_all('tr')

                    # Extract the symbol (first column) from each row
                    for row in rows:
                        columns = row.find_all('td')
                        if columns:  # Make sure row has columns
                            symbol = columns[0].get_text(strip=True)
                            if symbol:  # Only add non-empty symbols
                                all_codes.append(symbol)

            except requests.RequestException as e:
                print(f"Error fetching data from {url}: {e}")

        # Remove duplicates while preserving order
        unique_codes = list(dict.fromkeys(all_codes))
        return unique_codes

    def filter_codes(self, codes: List[str]) -> List[str]:
        return [code for code in codes if
                not any(char.isdigit() for char in code)]

    def get_data(self) -> List[str]:
        return self.get_issuer_codes()
