"""
normaliser.py
----------------------------------------
Data Normalization Module

Responsibilities
----------------
1. Normalize Year
2. Normalize Stock Ticker
3. Normalize Company Name
4. Normalize URLs
5. Normalize Sector Names
6. Normalize Numbers
"""

import re
import pandas as pd


class DataNormaliser:
    """
    Collection of data normalization functions.
    """

    # ----------------------------------------
    # Normalize Year
    # ----------------------------------------
    @staticmethod
    def normalize_year(value):
        """
        Convert different year formats into YYYY.

        Examples
        --------
        FY24      -> 2024
        2024-25   -> 2024
        2024      -> 2024
        """

        if pd.isna(value) or value == "":
            return None

        value = str(value).strip()

        # Case 1: "Mar 2023", "Dec 2012", "2024-25", "Report 2021" -> find a 4-digit year
        match = re.search(r"(20\d{2})", value)
        if match:
            return int(match.group(1))

        # Case 2: "FY24", "fy23" -> 2024, 2023
        match = re.search(r"FY(\d{2})", value, re.IGNORECASE)
        if match:
            year_short = int(match.group(1))
            # Handles FY00 to FY99
            return 2000 + year_short

        # Case 3: "Mar-13", "Dec-22" -> 2013, 2022
        match = re.search(r"\b(\d{2})\b", value)
        if match:
            return 2000 + int(match.group(1))

        # If no pattern matches (e.g., for "TTM", "ABC")
        return None

    # ----------------------------------------
    # Normalize Ticker
    # ----------------------------------------
    @staticmethod
    def normalize_ticker(value):
        """
        Convert ticker to uppercase and remove spaces.

        Examples
        --------
        tcs
        Tcs
        tcs.ns

        ->
        TCS
        TCS
        TCS
        """

        if pd.isna(value):
            return None

        ticker = str(value).upper().strip()

        ticker = ticker.replace(".NS", "")
        ticker = ticker.replace(".BO", "")

        ticker = ticker.replace(" ", "")

        return ticker

    # ----------------------------------------
    # Normalize Company Name
    # ----------------------------------------
    @staticmethod
    def normalize_company(value):
        """
        Clean company names.

        Examples
        --------
        tcs ltd.
        TCS LIMITED

        ->
        Tcs
        """

        if pd.isna(value):
            return None

        company = str(value).strip()

        # Strip common corporate-entity suffixes
        company = re.sub(
            r"\b(LTD|LIMITED|PVT|PRIVATE|INC|CORP|CORPORATION|PLC|LLP|CO|COMPANY)\b\.?",
            "",
            company,
            flags=re.IGNORECASE,
        )

        company = re.sub(r"\s+", " ", company)

        return company.title().strip()

    # ----------------------------------------
    # Normalize URL
    # ----------------------------------------
    @staticmethod
    def normalize_url(value):
        """
        Ensure URL begins with https:// (protocol check is case-insensitive
        so values like "HTTP://TCS.COM" aren't double-prefixed).
        """

        if pd.isna(value):
            return None

        url = str(value).strip()

        if not url:
            return None

        url = url.lower()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    # ----------------------------------------
    # Normalize Sector
    # ----------------------------------------
    @staticmethod
    def normalize_sector(value):
        """
        Normalize sector names.

        Examples
        --------
        information technology
        INFORMATION TECHNOLOGY

        ->
        Information Technology
        """

        if pd.isna(value):
            return None

        sector = str(value).strip()

        sector = re.sub(r"\s+", " ", sector)

        return sector.title()

    # ----------------------------------------
    # Normalize Number
    # ----------------------------------------
    @staticmethod
    def normalize_number(value):
        """
        Convert messy numeric strings into clean floats.

        Examples
        --------
        1,234.56  -> 1234.56
        45%       -> 45.0
        """

        if pd.isna(value):
            return None

        value = str(value).strip()

        value = value.replace(",", "")
        value = value.replace("%", "")

        try:
            return float(value)
        except ValueError:
            return None


# ---------------------------------------------------
# Example Usage
# ---------------------------------------------------
if __name__ == "__main__":

    normaliser = DataNormaliser()

    print(normaliser.normalize_year("FY24"))
    print(normaliser.normalize_year("2024-25"))

    print(normaliser.normalize_ticker("tcs.ns"))

    print(normaliser.normalize_company("TATA CONSULTANCY SERVICES LIMITED"))

    print(normaliser.normalize_url("www.tcs.com"))
    print(normaliser.normalize_url("HTTP://TCS.COM"))

    print(normaliser.normalize_sector("information technology"))

    print(normaliser.normalize_number("1,234.56"))
    print(normaliser.normalize_number("45%"))