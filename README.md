# Overview
This Personal Finance Management Console App helps you manage your personal finances by tracking your income, expenses, and liabilities. You can add, edit, delete, and view transactions. The app also allows you to filter and sort transactions to better analyze your financial activities.

# Features
Add new transactions with details such as date, category, expense type, title, amount, currency, and description.
View all transactions with options to filter and sort by date, amount, or expense type.
Edit existing transactions to update any field.
Delete transactions to remove them from your records.
Display total amounts and transaction counts for better financial insights.
# Installation
1. Clone the repository:  

  ```bash 
  git clone https://github.com/kharlamovilya/PersonalFinanceManagementApp
  ```

  ```bash 
  cd PersonalFinanceManagementApp/
  ```

2. Make sure you have Python installed. Then, install the required packages using pip:e

  ```bash
  pip install -r requirements.txt
  ```

3. Run the application:

  ```bash 
  python main.py
  ```
# Usage
### Main Menu
When you run the application, you will be presented with a main menu where you can choose the following options:

- Show Transactions: View and filter your transactions.
- Add Transaction: Add a new transaction to your records.
- Delete Transaction: Remove a transaction from your records.
- Edit Transaction: Edit details of an existing transaction.
- About: Learn more about the application. 
- Exit: Exit the application.
 ### Adding a Transaction
To add a transaction, select the "Add Transaction" option from the main menu. You will be prompted to enter the following details:
- Category: Select whether the transaction is an "Income", "Expense", or "Liability".
- Expense Type: If the transaction is an expense, choose the type of expense (e.g., Housing, Transportation).
- Title: Enter a title for the transaction.
- Amount: Enter the amount of money for the transaction.
- Currency: Select the currency for the transaction (e.g., USD, EUR).
- Description: Provide a brief description of the transaction.
### Viewing and Filtering Transactions
To view your transactions, select the "Show Transactions" option. You can filter the transactions based on:
- Newest: Show transactions from newest to oldest.
- Oldest: Show transactions from oldest to newest.
- Amount Increases: Sort transactions by increasing amount.
- Amount Decreases: Sort transactions by decreasing amount.
- Expense Type: If viewing expenses, sort them by expense type.
### Editing and Deleting Transactions
To edit or delete a transaction, you must first select the transaction from the list. You can then choose to either delete the transaction or edit specific fields.

# Development
### Requirements
- Python 3.6+
- InquirerPy

### Contact
For any questions or suggestions, feel free to contact the project maintainer:

Email: iluhasupergames@gmail.com
