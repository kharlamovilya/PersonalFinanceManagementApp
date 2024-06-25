import csv
import os
import random
from datetime import datetime

from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator

from modules.dateSelection import select_transaction_date

CSV_FILE = "finances.csv"
DATA_KEYS = ["date", "category", "expense_type", "title", "amount", "currency", "description"]
CATEGORIES = ["Income", "Expense", "Liability"]
EXPENSES = ["Housing", "Transportation", "Food", "Utilities", "Insurance", "Healthcare", "Financial Operations",
            "Personal Spending", "Other"]
CURRENCIES = ["USD", "EUR", "CNY", "JPY", "RUB", "HKD"]
CATEGORY_MAX_LENGTH = 20
TITLE_MAX_LENGTH = 30
AMOUNT_MAX_LENGTH = 10
DESCRIPTION_MAX_LENGTH = 200
FILTERS = ["Newest", "Oldest", "Amount Increases", "Amount Decreases", "Expense Type"]


def get_input_with_confirmation(message, choices=None, input_type="text", min_allowed=0, validate=None,
                                keybindings=None, mandatory=False, default=None):
    """Creates Inquirer prompt with confirmation"""
    while True:
        if input_type == "text":
            # For inquirer.text
            data = inquirer.text(message=message).execute()
        elif input_type == "number":
            # For inquirer.number
            data = inquirer.number(message=message, min_allowed=min_allowed, validate=validate).execute()
        elif input_type == "select":
            # For inquirer.select
            data = inquirer.select(message=message, choices=choices, keybindings=keybindings, mandatory=mandatory,
                                   default=default).execute()
        else:
            data = None

        if data is None:
            return None
        proceed = inquirer.confirm(message="Proceed?", default=True).execute()
        if proceed:
            return data


class Transaction:
    """Describes a Transaction, which is used as a row in storage file."""

    def __init__(self, category: str = '', date: str = '', expense_type: str = '', title: str = '', amount: int = 0,
                 currency: str = "USD", description: str = "", fill: bool = True, fill_random: bool = False):
        """Initializes a Transaction object.
        :param category: category of a transaction (Income, Expense etc.), stored in CATEGORIES.
        :param date: date of the transaction YYYY-MM-DD format.
        :param expense_type: only for expenses, sets expense type of transaction (Food, Housing etc.). stored in EXPENSES.
        :param title: a title of a transaction.
        :param amount: amount of money of a transaction.
        :param currency: the used currency of a transaction.
        :param description: some description of a transaction.
        :param fill: fills a transaction manually through a console menu if True.
        :param fill_random: fills a transaction automatically with random values if True.
        """
        self.category = category
        self.date = date
        self.expense_type = expense_type
        self.title = title
        self.amount = amount
        self.currency = currency
        self.description = description
        if fill:
            if fill_random:
                self.fill_random()
            else:
                self.fill()

    def __str__(self):
        """Returns a string representation of Transaction object."""
        expense_info = f" - {self.expense_type}" if self.category == "Expense" else ""
        return (f"{self.date:10} | {self.category.title() + expense_info:{CATEGORY_MAX_LENGTH + 7}} | Title: "
                f"{self.title:{TITLE_MAX_LENGTH}} | {self.amount:{AMOUNT_MAX_LENGTH}} {self.currency} | "
                f"Description: {self.description}")

    def fill(self):
        """Fills manually a Transaction object through console."""
        self.category = get_input_with_confirmation(input_type="select",
                                                    message="Choose a category of the transaction: ",
                                                    choices=CATEGORIES)
        if self.category == "Expense":
            self.expense_type = get_input_with_confirmation(input_type="select", message="Choose a type of expense: ",
                                                            choices=EXPENSES)

        self.title = get_input_with_confirmation(message="Enter a title for the transaction: ")

        self.amount = get_input_with_confirmation(input_type="number", message="Enter amount of money: ", min_allowed=0,
                                                  validate=EmptyInputValidator())
        self.currency = get_input_with_confirmation(input_type="select", message="Choose currency of the transaction: ",
                                                    choices=CURRENCIES, default="USD")
        self.description = get_input_with_confirmation(message="Enter a description: ")
        print('')

    def edit(self, field: str) -> bool:
        """Edits an exact field of a Transaction object. Returns status.
        :param field: a field of a transaction to be edited
        :return: True if edited successfully, False if not.
        :rtype: bool
        """
        # Choices stands for fields that are filled with inquirer.select
        choices = None
        if field == DATA_KEYS[0]:
            # Edit date
            new_date = select_transaction_date()
            if new_date is not None:
                self.date = new_date
        elif field == DATA_KEYS[1]:
            # Set category choices
            choices = CATEGORIES
        elif field == DATA_KEYS[2]:
            # Set expense types choices
            choices = EXPENSES
        elif field == DATA_KEYS[3]:
            # Edit title
            self.title = get_input_with_confirmation(message="Enter a title for the transaction: ")
        elif field == DATA_KEYS[4]:
            # Edit amount
            self.amount = get_input_with_confirmation(input_type="number", message="Enter amount of money: ",
                                                      min_allowed=0, validate=EmptyInputValidator())
        elif field == DATA_KEYS[5]:
            # Edit currency
            self.currency = get_input_with_confirmation(input_type="select",
                                                        message="Choose currency of the transaction: ",
                                                        choices=CURRENCIES)
        elif field == DATA_KEYS[6]:
            # Edit description
            self.description = get_input_with_confirmation(message="Enter a description: ")

        if choices:
            # Edit fields that are filled with inquirer.select
            new_field = get_input_with_confirmation(input_type="select",
                                                    message=f"Change {field} of the transaction, Ctrl-z to back: ",
                                                    choices=choices, keybindings={"skip": [{"key": ["c-z"]}]})
            if new_field is None:
                # If choice skipped
                return False
            # Change old attributes to new
            setattr(self, field, new_field)
        return True

    def fill_random(self):
        """Automatically fills a Transaction object with randomly chosen values."""
        self.category = random.choice(CATEGORIES)
        self.date = f"{random.randint(2020, 2024)}-0{random.randint(1, 9)}-{random.randint(10, 28)}"
        if self.category == "Expense":
            # Expense type has only to be changed if the category is "Expense"
            self.expense_type = random.choice(EXPENSES)
        self.title = random.choice(["apple", "banana", "cherry"])
        self.amount = random.randint(100, 10000)
        self.description = "some description"
        # Print the current instance
        print(self)


class TransactionManager:
    """This class provides with Transaction objects in storage and operations with them."""

    def __init__(self):
        """Initializes a Transactions object."""
        self.all_transactions: list[Transaction] = []
        self.filtered_transactions: list[Transaction] = []
        if not os.path.isfile(CSV_FILE):
            # Create the storage file if it does not exist.
            with open(CSV_FILE, 'w', newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, DATA_KEYS, delimiter='|')
                writer.writeheader()

    def get_transactions_from_csv(self, transaction_type: str, filtered_by: str) -> [list[Transaction], int, int]:
        """
        Gets transactions of an exact type (All, Expenses, Incomes, Liabilities)
        from the storage filtered in specified order.
        :rtype: [list[Transaction], int, int]
        :param transaction_type:  some value of CATEGORIES or All.
        :param filtered_by: some filter of FILTERS.
        :return: a list of filtered transactions, amount of money involved, amount of transactions.
        """
        with open(CSV_FILE, 'r', encoding="utf-8") as file:
            filtered = (line.replace('\n', '') for line in file)
            reader = csv.reader(filtered)
            # Skip the header
            next(reader, None)
            self.all_transactions: list[Transaction] = []
            transactions: list[Transaction] = []
            total = 0
            for row in reader:
                row = row[0].split('|')
                tmp = Transaction(category=row[1], date=row[0], expense_type=row[2], title=row[3], amount=int(row[4]),
                                  currency=row[5], description=row[6], fill=False)
                self.all_transactions.append(tmp)
                try:
                    if transaction_type in row or transaction_type == "All":
                        transactions.append(tmp)
                        if transaction_type != "All":
                            total += int(row[4])
                        else:
                            if tmp.category != "Income":
                                total -= int(row[4])
                            else:
                                total += int(row[4])
                except ValueError:
                    pass
                except Exception as error:
                    raise error
        if len(transactions) > 0:
            # Filter if there are transactions
            self.filtered_transactions = transactions
            transactions = self.__filter(filtered_by)
        return transactions, total, len(transactions)

    def __filter(self, filtered_by: str) -> list[Transaction]:
        """Returns filtered transactions in the storage. Does not apply changes to the storage file.
        :rtype: list[Transaction]
        :param filtered_by: some filter of FILTERS
        :return: a filtered list of transactions.
        """
        if filtered_by == "Newest":
            return sorted(self.filtered_transactions, key=lambda x: (datetime.strptime(x.date, '%Y-%m-%d'), x.amount),
                          reverse=True)
        if filtered_by == "Oldest":
            return sorted(self.filtered_transactions, key=lambda x: (datetime.strptime(x.date, '%Y-%m-%d'), x.amount))
        if filtered_by == "Amount Increases":
            return sorted(self.filtered_transactions, key=lambda x: (x.amount, x.date))
        if filtered_by == "Amount Decreases":
            return sorted(self.filtered_transactions, key=lambda x: (x.amount, x.date), reverse=True)
        if filtered_by == "Expense Type":
            return sorted(self.filtered_transactions, key=lambda x: (x.expense_type, x.date, x.amount))
        return self.filtered_transactions

    @staticmethod
    def append(transaction: Transaction):
        """Adds a Transaction to the storage.
        :param transaction: a Transaction to be appended
        """
        try:
            with open(CSV_FILE, 'a', newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, DATA_KEYS, delimiter='|')
                writer.writerow(transaction.__dict__)
        except Exception as e:
            print(f"Error writing to CSV: {e}")

    def delete(self, selected_transaction: Transaction) -> bool:
        """Deletes a Transaction from the storage. Returns status.
        :rtype: bool
        :param selected_transaction:
        :return: True if deleted successfully, False if not.
        """
        try:
            self.all_transactions = [t for t in self.all_transactions if t != selected_transaction]
            self.__rewrite_csv()
        except Exception as e:
            print(f"Error deleting a transaction: {e}")
            return False
        return True

    def edit(self, selected_transaction: Transaction, selected_field: str) -> bool:
        """Edits a specified Transaction and rewrites the storage. Returns status.
        :param selected_transaction: a transaction to be edited.
        :param selected_field: a field of the selected transaction to be edited.
        :return: True if edited successfully, False if not.
        :rtype: bool
        """
        edited = False
        for transaction in self.all_transactions:
            if transaction == selected_transaction:
                edited = transaction.edit(selected_field)
                break
        if edited:
            self.__rewrite_csv()
            return True
        return False

    def __rewrite_csv(self):
        """Rewrites the CSV file with updated transactions."""
        try:
            with open(CSV_FILE, 'w', newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, DATA_KEYS, delimiter='|')
                writer.writeheader()
                for transaction in self.all_transactions:
                    writer.writerow(transaction.__dict__)
        except Exception as e:
            print(f"Error rewriting CSV: {e}")
