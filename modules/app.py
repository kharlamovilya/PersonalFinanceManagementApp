"""
This module provides with a Personal Finance Management
console based app with user-friendly prompts.
"""
import os
import sys

from InquirerPy import inquirer
from InquirerPy.separator import Separator

from modules.dateSelection import select_transaction_date
from modules.transactions import TransactionManager, Transaction, DATA_KEYS, FILTERS


def clear():
    """Clears console."""
    os.system('cls' if os.name == 'nt' else 'clear')


# noinspection PyMethodMayBeStatic
class App:
    """This class provides with console interactions with Transactions object."""

    def __init__(self, DEBUG: bool):
        """Initializes an App object.
        :param DEBUG: turns on DEBUG mode and its features.
        """
        self.debug = DEBUG
        self.transactions_manager = TransactionManager()

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
            self.mode = "See"
            self.__get_transactions_menu()
        elif cmd == "delete":
            self.mode = "Delete"
            self.__get_transactions_menu()
        elif cmd == "edit":
            self.mode = "Edit"
            self.__get_transactions_menu()
        elif cmd == 'exit':
            self.__exit()
        elif cmd == "random":
            self.__add_random_transaction()
        elif cmd == "about":
            self.__show_about()

    def __exit(self):
        clear()
        print("Goodbye!")
        sys.exit()

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
        transaction_date = select_transaction_date()
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
            self.transactions_manager.append(transaction)
            print("Saved successfully!\n")
        else:
            # Else inform that it is not saved
            print("Not saved\n")

    def __add_random_transaction(self):
        """Add random transaction feature."""
        clear()
        print("Adding a random transaction\n")
        transaction = Transaction(fill_random=True)
        confirm_save = inquirer.confirm(message="Confirm saving the transaction?", default=True).execute()
        clear()
        if confirm_save:
            self.transactions_manager.append(transaction)
            print("Saved successfully!\n")
        else:
            print("Not saved\n")

    def __get_transactions_menu(self):
        """Menu of choosing a category of transaction to deal with."""
        clear()
        cmds = ["All", "Expense", "Income", "Liability", Separator(line=15 * '_'), "Back to menu"]
        msg = None
        if self.mode == "See":
            msg = "see"
        elif self.mode == "Delete":
            msg = "delete"
        elif self.mode == "Edit":
            msg = "edit"
        cmd = inquirer.select(message=f"What category of transactions do you want to {msg}? \n", choices=cmds).execute()
        if cmd == cmds[-1]:
            # If user selected Back to menu
            clear()
            return None
        response = self.__choose_filter(cmd)
        return response

    def __choose_filter(self, transaction_type: str):
        """Menu of choosing a filter for transactions to deal with.
        :param transaction_type: a category of a transaction (Income, Expense etc.).
        """
        clear()
        cmds = ["None"] + FILTERS + [Separator(line=15 * '_')] + ["Back to menu"]
        if transaction_type != "Expense":
            # If transaction type is not "Expense", then no need to filter by expense type
            cmds.pop(FILTERS.index("Expense Type") + 1)
        cmd = inquirer.select(message="Choose a filter for your transactions?, press Ctrl-z to back\n", choices=cmds,
                              keybindings={"skip": [{"key": ["c-z"]}]}, mandatory=False).execute()
        if cmd is None:
            # If user skipped prompt
            return self.__get_transactions_menu()
        if cmd == cmds[-1]:
            # If user selected "Back to menu"
            clear()
            return None
        response = self.__get_transactions(transaction_type, cmd)
        return response

    def __get_transactions(self, transaction_type, filtered):
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
            return self.__get_transactions_menu()

        if self.mode == "See":
            print("Press any key to go back\n")
        elif self.mode == "Delete":
            print("Choose a transaction to delete\n")
        elif self.mode == "Edit":
            print("Choose a transaction to edit\n")

        print(f"Total {amount} {transaction_type.lower()} transactions: {total} USD\n")

        # Proceed to feature menu
        if self.mode == "See":
            self.__see_transaction_menu(transactions)
        elif self.mode == "Delete":
            self.__delete_transaction_menu(transactions)
        elif self.mode == "Edit":
            self.__edit_transaction_menu(transactions)

        return None

    def __see_transaction_menu(self, transactions: list[Transaction]):
        """Menu of see transactions feature.
        :param transactions: a list of transactions.
        :return:
        """
        for transaction in transactions:
            print(transaction)
        print('')
        self.__back()
        return self.__get_transactions_menu()

    def __delete_transaction_menu(self, transactions: list[Transaction]):
        """Menu of delete transaction feature.
        :param transactions: a list of transactions.
        """
        selected_transaction = inquirer.select(message="Choose a transaction to delete, press Ctrl-z to back\n",
                                               choices=transactions, keybindings={"skip": [{"key": ["c-z"]}]},
                                               mandatory=False).execute()
        clear()
        if selected_transaction is None:
            return self.__get_transactions_menu()
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
        return self.__get_transactions_menu()

    def __edit_transaction_menu(self, transactions: list[Transaction]):
        """Menu of edit transaction feature.
        :param transactions: a list of transactions.
        """
        selected_transaction = inquirer.select(message="Choose a transaction to edit, press Ctrl-z to back\n",
                                               choices=transactions, keybindings={"skip": [{"key": ["c-z"]}]},
                                               mandatory=False).execute()
        clear()
        if selected_transaction is None:
            return self.__get_transactions_menu()
        print(f"\n{selected_transaction}\n")
        confirm_edit = inquirer.confirm(message="Do you really want to edit the transaction?", default=True).execute()
        if not confirm_edit:
            return self.__get_transactions_menu()
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
        return self.__get_transactions_menu()

    @staticmethod
    def __back():
        """This function allows to keep another functions' result in frozen state, so the user can read previous
        output."""
        inquirer.confirm(message="Press any key to go back", default=True, confirm_letter=' ',
                         reject_letter=' ').execute()
        clear()
