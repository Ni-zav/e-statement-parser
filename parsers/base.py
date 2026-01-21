import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path

class BaseBankParser(ABC):
    """Base class for all bank statement parsers."""
    
    def __init__(self, account_name: str):
        self.account_name = account_name

    @abstractmethod
    def parse(self, filepath: str) -> pd.DataFrame:
        """Parse the bank statement and return a standardized DataFrame."""
        pass

    def get_standard_columns(self):
        """Returns the list of standardized columns for the output CSV."""
        return [
            'Date', 'Account', 'Category', 'Note', 'Amount', 
            'Type', 'Description', 'Currency'
        ]

    def create_empty_df(self):
        """Creates an empty DataFrame with the standardized columns."""
        return pd.DataFrame(columns=self.get_standard_columns())
