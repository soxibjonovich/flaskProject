import os
import csv
from typing import List, Dict


class CsvController(object):
    def __init__(
        self,
        root_directory: str
    ) -> None:
        self.root = root_directory

    def _find_csv_files(self, directory: str) -> List[str]:
        """
        Finds all CSV files within a given directory.

        Args:
            directory: The directory to search for CSV files.

        Returns:
            A list of full file paths for all CSV files found.
        """
        csv_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".csv"):
                    csv_files.append(os.path.join(root, file))
        return csv_files

    def _filter_csv_by_id(self, user_id: int, csv_files: List[str]) -> List[str]:
        """
        Filters a list of CSV files based on a user ID found in the filename.

        Args:
            user_id: The user ID to filter by.
            csv_files: A list of CSV file paths.

        Returns:
            A list of CSV file paths that contain the user ID in the filename.
        """
        sorted_csv_files = []
        for filename in csv_files:
            # Split filename considering separators (e.g., "-") and get second part (assuming user ID)
            parts = filename.split("-")
            if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) == user_id:
                sorted_csv_files.append(filename)
        return sorted_csv_files

    def _count_csv_rows(self, file: str) -> int:
        """
        Counts the number of rows (excluding header) in a CSV file.

        Args:
            file: The path to the CSV file.

        Returns:
            The number of rows in the CSV file.
        """
        with open(file, mode="r", newline="", encoding="utf-8") as csvfile:
            csvreader = csv.reader(csvfile)
            row_count = sum(1 for _ in csvreader)
        return row_count

    def prepare_user_data(self, user_id: int) -> dict[str, int]:
        """
        Prepares information about CSV files for a specific user.

        Args:
            user_id: The user ID to retrieve information for.

        Returns:
            A dictionary where keys are CSV file paths and values are the number of rows in each file.
        """
        csv_files = self._find_csv_files(self.root)
        user_csv_files = self._filter_csv_by_id(user_id, csv_files)
        result = {file: self._count_csv_rows(file) for file in user_csv_files}
        return result

    def get_info_from_file(self, file: str) -> List[str]:
        """
        Retrieves detailed information from a specific CSV file.

        Args:
            file: The path to the CSV file.

        Returns:
            A list of dictionaries where each dictionary represents a row in the CSV file.
        """
        with open(f"{file}", mode="r", newline="", encoding="utf-8") as csvfile:
            info = csv.reader(csvfile)
            a = []
            for _ in info:
                a.extend(_)
            return a

    def add_new_hash(self, hash: str, user_id: int) -> bool:
        """
        Adds a new hash to the hashes.csv file.
        """

        csv_files = self._find_csv_files(self.root)
        user_csv_files = self._filter_csv_by_id(user_id, csv_files)
        
        for file in user_csv_files:
            row_count = self._count_csv_rows(file)
            if row_count < 50:
                with open(file, mode="a", newline="", encoding="utf-8") as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow([hash])
                return True
            
        new_file_path = os.path.join(self.root, f"username-{user_id}-{len(user_csv_files) + 1}.csv")
        with open(new_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([hash])