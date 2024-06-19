"""
This module provides with a Personal Finance Management
console based app with user-friendly prompts.
"""
import csv
import os
import random
import sys
from calendar import monthrange
from datetime import date as dt
from datetime import datetime

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.validator import EmptyInputValidator

# Environment variables
CSV_FILE = "finances.csv"
DATA_KEYS = ["date", "category", "expense_type", "title", "amount", "currency", "description"]
CATEGORIES = ["Income", "Expense", "Liability"]
EXPENSES = ["Housing", "Transportation", "Food", "Utilities", "Insurance", "Healthcare", "Financial Operations",
            "Personal Spending"]
CURRENCIES = ["USD", "EUR", "CNY", "JPY", "RUB", "HKD"]
CATEGORY_MAX_LENGTH = 20
TITLE_MAX_LENGTH = 30
AMOUNT_MAX_LENGTH = 10
DESCRIPTION_MAX_LENGTH = 200
FILTERS = ["Newest", "Oldest", "Amount Increases", "Amount Decreases", "Expense Type"]


def clear():
    """Clears console."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_input_with_confirmation(message, choices=None, input_type="text", min_allowed=None, validate=None,
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

    def __init__(self, category='', date='', expense_type='', title='', amount=0, currency="USD", description="",
                 fill=True, fill_random=False):
        """Initializes a Transaction object."""
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

    def edit(self, field) -> bool:
        """Edits an exact field of a Transaction object. Returns status."""
        # Choices stands for fields that are filled with inquirer.select
        choices = None
        if field == DATA_KEYS[0]:
            # Edit date
            new_date = App().select_transaction_date()
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


class Transactions:
    """This class provides with Transaction objects in storage and operations with them."""

    def __init__(self):
        """Initializes a Transactions object."""
        self.all_transactions = []
        self.filtered_transactions = []
        if not os.path.isfile(CSV_FILE):
            # Create the storage file if it does not exist.
            with open(CSV_FILE, 'w', newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, DATA_KEYS, delimiter='|')
                writer.writeheader()

    def get_transactions_from_csv(self, transaction_type, filtered_by) -> [list[Transaction], int, int]:
        """
        Gets transactions of an exact type (All, Expenses, Incomes, Liabilities)
        from the storage filtered in specified order.
        Returns list of transactions, amount of money and amount of transactions
        """
        with open(CSV_FILE, 'r', encoding="utf-8") as file:
            filtered = (line.replace('\n', '') for line in file)
            reader = csv.reader(filtered)
            # Skip the header
            next(reader, None)
            self.all_transactions = []
            transactions = []
            total = 0
            for row in reader:
                row = row[0].split('|')
                tmp = Transaction(category=row[1], date=row[0], expense_type=row[2], title=row[3], amount=int(row[4]),
                                  currency=row[5], description=row[6], fill=False)
                self.all_transactions.append(tmp)
                try:
                    if transaction_type in row or transaction_type == "All":
                        transactions.append(tmp)
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

    def __filter(self, filtered_by):
        """Return filtered transactions in the storage. Does not change the storage file."""
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
    def append(row):
        """Adds a Transaction to the storage."""
        try:
            with open(CSV_FILE, 'a', newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, DATA_KEYS, delimiter='|')
                writer.writerow(row)
        except Exception as e:
            print(f"Error writing to CSV: {e}")

    def delete(self, selected_transaction) -> bool:
        """Deletes a Transaction from the storage. Returns status."""
        try:
            self.all_transactions = [t for t in self.all_transactions if t != selected_transaction]
            self.__rewrite_csv()
        except Exception as e:
            print(f"Error deleting a transaction: {e}")
        return True

    def edit(self, selected_transaction, selected_field) -> bool:
        """Edits a specified Transaction and rewrites the storage. Returns status."""
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


class App:
    """This class provides with console interactions with Transactions object."""

    def __init__(self):
        """Initializes an App object."""
        self.debug = DEBUG
        self.transactions_manager = Transactions()

    def run(self):
        """Runs the console app."""
        while True:
            clear()
            self.__main_menu()

    def __main_menu(self):
        """Main menu of the app."""
        cmds = [{"name": "Show Transactions", "value": "show"}, {"name": "Add Transaction", "value": "add"},
                {"name": "Delete Transaction", "value": "delete"}, {"name": "Edit Transaction", "value": "edit"},
                {"name": "About", "value": "about"}, {"name": "Exit", "value": "exit"}]
        if self.debug:
            # Add debug features
            cmds.append(Separator(line=15 * '_'))
            cmds.append({"name": "Add Random Transaction", "value": "random"})
        cmd = inquirer.select(message="What do you want to do?\n", choices=cmds, default=None).execute()

        if cmd == "add":
            self.__add_transaction()
        elif cmd == "show":
            self.__get_transactions_menu(mode="See")
        elif cmd == "delete":
            self.__get_transactions_menu(mode="Delete")
        elif cmd == "edit":
            self.__get_transactions_menu(mode="Edit")
        elif cmd == 'exit':
            clear()
            print("Goodbye!")
            sys.exit()
        elif cmd == "random":
            self.__add_random_transaction()
        elif cmd == "about":
            self.__show_about()

    def __show_about(self):
        """Displays information about the application."""
        clear()
        about_text = """Finance Console App v1.0
            This application is a personal finance manager that helps you track your income, expenses, and liabilities.
            You can add, edit, delete, and view transactions, as well as apply filters to sort your transactions.
            """
        print(about_text)
        self.__back()

    def __add_transaction(self):
        """Add transaction feature."""
        clear()
        # Ask user for a date of a transaction
        transaction_date = self.select_transaction_date()
        clear()
        # Check if date is valid
        if transaction_date is None:
            return
        print(f"Adding a transaction of {transaction_date}")
        # Create new Transaction instance with entered date
        transaction = Transaction(date=transaction_date)
        clear()
        # Ask user if he wants to save currently created transaction
        confirm_save = inquirer.confirm(message="Confirm saving the transaction?", default=True).execute()
        if confirm_save:
            # If yes, then save it to the storage and print status
            self.transactions_manager.append(transaction.__dict__)
            print("Saved successfully!\n")
        else:
            # Else inform that it is not saved
            print("Not saved\n")

    def select_transaction_date(self) -> str | None:
        """Menus of transactions' date selection."""
        year = self.__select_year()
        if year is None:
            return None
        month = self.__select_month()
        if month is None:
            return None
        day = self.__select_day(year, month)
        if day is None:
            return None
        return str(dt(year, month, day))

    @staticmethod
    def __select_year() -> int | None:
        """Menu of year selection."""
        cur_year = dt.today().year
        cmds = ([str(year + 1) for year in range(cur_year - 10, cur_year)] + [(Separator(line=15 * '_'))] + [
            "Back to menu"])
        cmd = inquirer.select("Choose year of the transaction:", choices=cmds, default=cmds[9]).execute()
        if cmd == "Back to menu":
            return None
        return int(cmd)

    @staticmethod
    def __select_month() -> int | None:
        """Menu of month selection."""
        cur_month = dt.today().month
        cmds = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December", Separator(line=15 * '_'), "Back to menu"]
        cmd = inquirer.select("Choose a month of the transaction:", choices=cmds, default=cmds[cur_month - 1]).execute()
        if cmd == "Back to menu":
            return None
        return cmds.index(cmd) + 1

    @staticmethod
    def __select_day(year, month) -> int | None:
        """Menu of day selection."""
        cur_day = dt.today().day
        days_in_month = monthrange(year, month)[1]
        cmds = [i + 1 for i in range(0, days_in_month)] + [Separator(line=15 * '_')] + ["Back to menu"]
        cmd = inquirer.select("Choose a day of the transaction:", choices=cmds, default=cmds[cur_day - 1]).execute()
        if cmd == "Back to menu":
            return None
        return int(cmd)

    def __add_random_transaction(self):
        """Add random transaction feature."""
        clear()
        print("Adding a random transaction\n")
        transaction = Transaction(fill_random=True)
        confirm_save = inquirer.confirm(message="Confirm saving the transaction?", default=True).execute()
        clear()
        if confirm_save:
            self.transactions_manager.append(transaction.__dict__)
            print("Saved successfully!\n")
        else:
            print("Not saved\n")

    def __get_transactions_menu(self, mode):
        """Menu of choosing a category of transaction to deal with."""
        clear()
        cmds = ["All", "Expense", "Income", "Liability", Separator(line=15 * '_'), "Back to menu"]
        msg = None
        if mode == "See":
            msg = "see"
        elif mode == "Delete":
            msg = "delete"
        elif mode == "Edit":
            msg = "edit"
        cmd = inquirer.select(message=f"What category of transactions do you want to {msg}? \n", choices=cmds).execute()
        if cmd == cmds[-1]:
            # If user selected Back to menu
            clear()
            return None
        response = self.__choose_filter(cmd, mode)
        return response

    def __choose_filter(self, transaction_type, mode):
        """Menu of choosing a filter for transactions to deal with."""
        clear()
        cmds = ["None"] + FILTERS + [Separator(line=15 * '_')] + ["Back to menu"]
        if transaction_type != "Expense":
            # If transaction type is not "Expense", then no need to filter by expense type
            cmds.pop(FILTERS.index("Expense Type") + 1)
        cmd = inquirer.select(message="Choose a filter for your transactions?, press Ctrl-z to back\n", choices=cmds,
                              keybindings={"skip": [{"key": ["c-z"]}]}, mandatory=False).execute()
        if cmd is None:
            # If user skipped prompt
            return self.__get_transactions_menu(mode)
        if cmd == cmds[-1]:
            # If user selected "Back to menu"
            clear()
            return None
        response = self.__get_transactions(transaction_type, cmd, mode)
        return response

    def __get_transactions(self, transaction_type, filtered, mode):
        """Outputs a specified filtered category of transaction to deal with."""
        clear()
        print(f"Getting {transaction_type.lower()} transactions...")
        try:
            transactions, total, amount = self.transactions_manager.get_transactions_from_csv(transaction_type,
                                                                                              filtered)
        except Exception as error:
            raise error

        if transactions is None or len(transactions) == 0:
            print("No transactions added yet\n")
            self.__back()
            return self.__get_transactions_menu(mode)

        if mode == "See":
            print("Press any key to go back\n")
        elif mode == "Delete":
            print("Choose a transaction to delete\n")
        elif mode == "Edit":
            print("Choose a transaction to edit\n")

        print(f"Total {amount} {transaction_type.lower()} transactions: {total} USD\n")

        # Proceed to feature menu
        if mode == "See":
            self.__see_transaction_menu(transactions, mode)
        elif mode == "Delete":
            self.__delete_transaction_menu(transactions, mode)
        elif mode == "Edit":
            self.__edit_transaction_menu(transactions, mode)

        return None

    def __see_transaction_menu(self, transactions, mode):
        """Menu of see transactions feature."""
        for transaction in transactions:
            print(transaction)
        print('')
        self.__back()
        return self.__get_transactions_menu(mode)

    def __delete_transaction_menu(self, transactions, mode):
        """Menu of delete transaction feature."""
        selected_transaction = inquirer.select(message="Choose a transaction to delete, press Ctrl-z to back\n",
                                               choices=transactions, keybindings={"skip": [{"key": ["c-z"]}]},
                                               mandatory=False).execute()
        clear()
        if selected_transaction is None:
            return self.__get_transactions_menu(mode)
        print(f"\n{selected_transaction}\n")
        confirm_delete = inquirer.confirm(message="Do you really want to delete the transaction?}",
                                          default=True).execute()
        if confirm_delete:
            response = self.transactions_manager.delete(selected_transaction)
            clear()
            if not response:
                print("No changes applied\n")
            else:
                print("Changed successfully\n")
            self.__back()
        clear()
        return self.__get_transactions_menu(mode)

    def __edit_transaction_menu(self, transactions, mode):
        """Menu of edit transaction feature."""
        selected_transaction = inquirer.select(message="Choose a transaction to edit, press Ctrl-z to back\n",
                                               choices=transactions, keybindings={"skip": [{"key": ["c-z"]}]},
                                               mandatory=False).execute()
        clear()
        if selected_transaction is None:
            return self.__get_transactions_menu(mode)
        print(f"\n{selected_transaction}\n")
        confirm_edit = inquirer.confirm(message="Do you really want to edit the transaction?", default=True).execute()
        if not confirm_edit:
            return self.__get_transactions_menu(mode)
        clear()
        print(f"\n{selected_transaction}\n")
        selected_field = inquirer.select("Select field to be changed, Ctrl-z to back:\n", choices=DATA_KEYS,
                                         keybindings={"skip": [{"key": ["c-z"]}]}, mandatory=False).execute()
        clear()
        if selected_field is not None:
            print(f"\n{selected_transaction}\n")
            response = self.transactions_manager.edit(selected_transaction, selected_field)
            clear()
            if not response:
                print("No changes applied\n")
            else:
                print("Changed successfully\n")
            self.__back()
        return self.__get_transactions_menu(mode)

    @staticmethod
    def __back():
        """This function allows to keep another functions' result in frozen state, so the user can read previous
        output."""
        inquirer.confirm(message="Press any key to go back", default=True, confirm_letter=' ',
                         reject_letter=' ').execute()
        clear()


# Run the script.
if __name__ == '__main__':
    """Create and set up instances with console-set arguments."""
    args = sys.argv
    DEBUG = False
    if len(args) == 2:
        if args[1] in ["--DEBUG", "-d"]:
            DEBUG = True

    app = App()
    app.run()
