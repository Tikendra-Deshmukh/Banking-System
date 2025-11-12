import random
import re
from datetime import datetime
from abc import ABC, abstractmethod
import csv
import os

class Account(ABC):
    next_account_id = 1
    
    def __init__(self, id, account_type, balance):
        self.id = id
        self.account_type = account_type
        self.balance = float(balance)
        self.transactions = []

    def save_account_info(self):
        try:
            # Read existing accounts
            accounts = []
            if os.path.exists("accounts.csv"):
                with open("accounts.csv", "r", newline='') as file:
                    reader = csv.DictReader(file)
                    accounts = list(reader)
            
            # Update or add account with ALL details
            account_found = False
            for acc in accounts:
                if acc['account_id'] == self.id and acc['account_type'] == self.account_type:
                    acc['balance'] = str(self.balance)
                    # ADDED: Extra fields based on account type
                    if isinstance(self, SavingsAccount):
                        acc['interest_rate'] = str(self.interest_rate)
                    elif isinstance(self, CheckingAccount):
                        acc['credit_limit'] = str(self.credit_limit)
                        acc['overdraft_fee'] = str(self.overdraft_fee)
                    elif isinstance(self, LoanAccount):
                        acc['interest_rate'] = str(self.interest_rate)
                    account_found = True
                    break
            
            if not account_found:
                new_account = {
                    'account_id': self.id,
                    'account_type': self.account_type,
                    'balance': str(self.balance)
                }
                # ADDED: Extra fields
                if isinstance(self, SavingsAccount):
                    new_account['interest_rate'] = str(self.interest_rate)
                elif isinstance(self, CheckingAccount):
                    new_account['credit_limit'] = str(self.credit_limit)
                    new_account['overdraft_fee'] = str(self.overdraft_fee)
                elif isinstance(self, LoanAccount):
                    new_account['interest_rate'] = str(self.interest_rate)
                
                accounts.append(new_account)
            
            # Write back to CSV with ALL fields
            with open("accounts.csv", "w", newline='') as file:
                # DYNAMIC FIELDNAMES - sab fields include karo
                fieldnames = ['account_id', 'account_type', 'balance', 'interest_rate', 'credit_limit', 'overdraft_fee']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for acc in accounts:
                    # Ensure all fields have values
                    for field in fieldnames:
                        if field not in acc:
                            acc[field] = ''  # Empty for missing fields
                    writer.writerow(acc)
                    
        except Exception as e:
            print(f"Error saving account info: {e}")

    def deposit(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            print("Please Enter amount in digits")
            return
        
        self.balance += amount
        self.save_account_info()
        
        # Save transaction
        transaction_data = {
            'account_id': self.id,
            'transaction_type': 'deposit',
            'amount': amount,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'balance_after': self.balance
        }
        self.save_transaction(transaction_data)
        print(f"Deposited {amount} successfully. New balance: {self.balance}")

    @abstractmethod
    def withdraw(self, amount):
        pass

    def save_transaction(self, transaction_data):
        try:
            file_exists = os.path.exists("transactions.csv")
            
            # COMPLETE FIELDNAMES - sab possible fields
            fieldnames = [
                'account_id', 'transaction_type', 'amount', 'timestamp', 
                'balance_after', 'interest_earned', 'overdraft_fee', 
                'loan_duration', 'related_account'
            ]
            
            with open("transactions.csv", "a", newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                # Ensure all fields are present in transaction_data
                for field in fieldnames:
                    if field not in transaction_data:
                        transaction_data[field] = ''
                
                writer.writerow(transaction_data)
        except Exception as e:
            print(f"Error saving transaction: {e}")

    def balance_enquiry(self):
        print(f"Account Type: {self.account_type}")
        print(f"Balance: {self.balance}")

    def transfer_funds(self, recipient_account, amount):
        try:
            amount = float(amount)
            if self.balance >= amount:
                self.balance -= amount
                recipient_account.balance += amount
                
                self.save_account_info()
                recipient_account.save_account_info()
                
                # Save transactions for both accounts
                self_transaction = {
                    'account_id': self.id,
                    'transaction_type': 'transfer_out',
                    'amount': amount,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': self.balance,
                    'related_account': recipient_account.id
                }
                recipient_transaction = {
                    'account_id': recipient_account.id,
                    'transaction_type': 'transfer_in',
                    'amount': amount,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': recipient_account.balance,
                    'related_account': self.id
                }
                
                self.save_transaction(self_transaction)
                recipient_account.save_transaction(recipient_transaction)
                
                print(f"Transferred {amount} to {recipient_account.id} successfully!")
                return True
            else:
                print("Insufficient balance.")
                return False
        except Exception as e:
            print(f"Error during transfer: {e}")
            return False

class CheckingAccount(Account):
    def __init__(self, id, balance):
        super().__init__(id, "Checking", balance)
        self.credit_limit = (self.balance * 0.5) * (-1)
        self.overdraft_fee = abs(self.balance) * 0.02

    def withdraw(self, amount):
        try:
            amount = float(amount)
            if self.balance - amount >= self.credit_limit:
                if self.balance - amount >= 0:
                    self.balance -= amount
                    transaction_data = {
                        'account_id': self.id,
                        'transaction_type': 'withdrawal',
                        'amount': amount,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'balance_after': self.balance
                    }
                    print(f"Withdrew {amount} successfully!")
                else:
                    # Overdraft case
                    total_deduction = amount + self.overdraft_fee
                    self.balance -= total_deduction
                    transaction_data = {
                        'account_id': self.id,
                        'transaction_type': 'withdrawal_overdraft',
                        'amount': amount,
                        'overdraft_fee': self.overdraft_fee,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'balance_after': self.balance
                    }
                    print(f"Withdrew {amount} with overdraft fee {self.overdraft_fee}")
                
                self.save_transaction(transaction_data)
                self.save_account_info()
            else:
                print("Insufficient funds - exceeds credit limit")
        except ValueError as e:
            print(f"Invalid amount: {e}")

class SavingsAccount(Account):
    def __init__(self, id, balance):
        super().__init__(id, "Savings", balance)
        self.interest_rate = 0.02  # 2% interest

    def deposit(self, amount):
        try:
            amount = float(amount)
            interest_earned = amount * self.interest_rate
            self.balance += (amount + interest_earned)
            
            transaction_data = {
                'account_id': self.id,
                'transaction_type': 'deposit_with_interest',
                'amount': amount,
                'interest_earned': interest_earned,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'balance_after': self.balance
            }
            self.save_transaction(transaction_data)
            self.save_account_info()
            print(f"Deposited {amount} with interest {interest_earned}. New balance: {self.balance}")
        except ValueError as e:
            print(f"Invalid amount: {e}")

    def withdraw(self, amount):
        try:
            amount = float(amount)
            if self.balance >= amount:
                self.balance -= amount
                transaction_data = {
                    'account_id': self.id,
                    'transaction_type': 'withdrawal',
                    'amount': amount,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': self.balance
                }
                self.save_transaction(transaction_data)
                self.save_account_info()
                print(f"Withdrew {amount} successfully!")
                return True
            else:
                print("Insufficient balance.")
                return False
        except ValueError as e:
            print(f"Invalid amount: {e}")
            return False

class LoanAccount(Account):
    def __init__(self, id, balance):
        super().__init__(id, "Loan", balance)
        self.interest_rate = 0.08  # 8% annual interest

    def withdraw(self, amount):
        try:
            amount = float(amount)
            if self.balance >= amount:
                try:
                    loan_duration = int(input("Enter loan duration in months: "))
                    if loan_duration <= 0:
                        print("Loan duration must be positive")
                        return False
                    
                    monthly_interest_rate = self.interest_rate / 12
                    total_interest = amount * monthly_interest_rate * loan_duration
                    total_amount = amount + total_interest
                    
                    if self.balance >= total_amount:
                        self.balance -= total_amount
                        
                        transaction_data = {
                            'account_id': self.id,
                            'transaction_type': 'loan_disbursement',
                            'amount': amount,
                            'interest_charged': total_interest,
                            'loan_duration': loan_duration,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'balance_after': self.balance
                        }
                        self.save_transaction(transaction_data)
                        self.save_account_info()
                        
                        print(f"Loan of {amount} disbursed! Total with interest: {total_amount}")
                        return True
                    else:
                        print("Insufficient balance for loan with interest.")
                        return False
                except ValueError:
                    print("Please enter valid number for loan duration.")
                    return False
            else:
                print("Insufficient balance.")
                return False
        except ValueError as e:
            print(f"Invalid amount: {e}")
            return False

class Customer:
    def __init__(self, id, password, first_name, last_name, address):
        self.id = id
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.accounts = []

    def save_customer_info(self):
        try:
            file_exists = os.path.exists("customers.csv")
            with open("customers.csv", "a", newline='') as file:
                fieldnames = ['customer_id', 'password', 'first_name', 'last_name', 'address']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    'customer_id': self.id,
                    'password': self.password,
                    'first_name': self.first_name,
                    'last_name': self.last_name,
                    'address': self.address
                })
        except Exception as e:
            print(f"Error saving customer info: {e}")

    def add_account(self, account):
        self.accounts.append(account)

    def get_account_by_type(self, account_type):
        for account in self.accounts:
            if account.account_type == account_type:
                return account
        return None

    def get_account_balance(self, account_type):
        account = self.get_account_by_type(account_type)
        if account:
            return account.balance
        return None

    def deposit(self, account_type, amount):
        account = self.get_account_by_type(account_type)
        if account:
            return account.deposit(amount)
        return False

    def withdraw(self, account_type, amount):
        account = self.get_account_by_type(account_type)
        if account:
            return account.withdraw(amount)
        return False

class BankingSystem:
    def __init__(self):
        self.customers = []
        self.admin_password = self.load_admin_password()

    def load_admin_password(self):
        try:
            if os.path.exists("admin.csv"):
                with open("admin.csv", "r") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        return row['password']
            # Default password agar file nahi hai
            return "admin123"
        except:
            return "admin123"

    def change_admin_password(self):
        current_pwd = input("\nEnter current admin password: ")
        if current_pwd == self.admin_password:
            new_pwd = input("Enter new admin password: ")
            try:
                with open("admin.csv", "w", newline='') as file:
                    fieldnames = ['password']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow({'password': new_pwd})
                self.admin_password = new_pwd
                print("Admin password changed successfully!")
            except Exception as e:
                print(f"Error changing password: {e}")
        else:
            print("Invalid current password!")

    def load_customers_from_file(self):
        try:
            if os.path.exists("customers.csv"):
                with open("customers.csv", "r", newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        customer = Customer(
                            row['customer_id'],
                            row['password'],
                            row['first_name'],
                            row['last_name'],
                            row['address']
                        )
                        self.customers.append(customer)
                        self.load_customer_accounts(customer)
        except Exception as e:
            print(f"Error loading customers: {e}")

    def load_customer_accounts(self, customer):
        try:
            if os.path.exists("accounts.csv"):
                with open("accounts.csv", "r", newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['account_id'] == customer.id:
                            balance = float(row['balance'])
                            if row['account_type'] == "Checking":
                                account = CheckingAccount(customer.id, balance)
                                if row['credit_limit']:
                                    account.credit_limit = float(row['credit_limit'])
                                if row['overdraft_fee']:
                                    account.overdraft_fee = float(row['overdraft_fee'])
                            elif row['account_type'] == "Savings":
                                account = SavingsAccount(customer.id, balance)
                                if row['interest_rate']:
                                    account.interest_rate = float(row['interest_rate'])
                            elif row['account_type'] == "Loan":
                                account = LoanAccount(customer.id, balance)
                                if row['interest_rate']:
                                    account.interest_rate = float(row['interest_rate'])
                            customer.add_account(account)
        except Exception as e:
            print(f"Error loading accounts for customer {customer.id}: {e}")

    def customer_login(self, customer_id, password):
        self.load_customers_from_file()
        for customer in self.customers:
            if customer.id == customer_id and customer.password == password:
                return customer
        return None

    def admin_login(self, password):
        return password == self.admin_password

    def create_customer(self, password, first_name, last_name, address):
        try:
            # Password validation
            if len(password) < 6 or not re.search(r'\d', password):
                print("Password must be at least 6 characters long and contain a digit.")
                return False
            
            # Generate unique ID
            customer_id = str(random.randint(100, 999) + random.randint(1000, 9999) + random.randint(1000000, 9999999))
            print(f'Your Customer ID is: {customer_id}')
            
            customer = Customer(customer_id, password, first_name, last_name, address)
            self.customers.append(customer)
            customer.save_customer_info()
            
            print("Customer registered successfully!")
            return True

        except Exception as e:
            print(f"Error creating customer: {e}")
            return False

    def prompt_account_type(self, customer):
        try:
            print("\nSelect account type:")
            print("1. Checking Account")
            print("2. Savings Account") 
            print("3. Loan Account")
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                self.create_checking_account(customer)
            elif choice == "2":
                self.create_savings_account(customer)
            elif choice == "3":
                self.create_loan_account(customer)
            else:
                print("Invalid choice!")
        except Exception as e:
            print(f"Error: {e}")

    def create_checking_account(self, customer):
        try:
            balance = float(input("Enter initial balance: "))
            account = CheckingAccount(customer.id, balance)
            account.save_account_info()
            customer.accounts.append(account)
            print("Checking account created successfully!")
        except ValueError:
            print("Please enter valid amount!")
        except Exception as e:
            print(f"Error creating checking account: {e}")

    def create_savings_account(self, customer):
        try:
            balance = float(input("Enter initial balance: "))
            account = SavingsAccount(customer.id, balance)
            account.save_account_info()
            customer.accounts.append(account)
            print("Savings account created successfully!")
        except ValueError:
            print("Please enter valid amount!")
        except Exception as e:
            print(f"Error creating savings account: {e}")

    def create_loan_account(self, customer):
        try:
            balance = float(input("Enter initial balance: "))
            account = LoanAccount(customer.id, balance)
            account.save_account_info()
            customer.accounts.append(account)
            print("Loan account created successfully!")
        except ValueError:
            print("Please enter valid amount!")
        except Exception as e:
            print(f"Error creating loan account: {e}")

    def print_all_customers_info(self):
        try:
            print("\n" + "="*60)
            print("ALL CUSTOMERS INFORMATION")
            print("="*60)
            
            if not self.customers:
                print("No customers found!")
                return
                
            for customer in self.customers:
                print(f"\nCustomer ID: {customer.id}")
                print(f"Name: {customer.first_name} {customer.last_name}")
                print(f"Address: {customer.address}")
                print("Accounts:")
                
                if customer.accounts:
                    for account in customer.accounts:
                        if isinstance(account, CheckingAccount):
                            print(f"  - Checking Account: Balance: {account.balance}, Credit Limit: {account.credit_limit}")
                        elif isinstance(account, SavingsAccount):
                            print(f"  - Savings Account: Balance: {account.balance}, Interest Rate: {account.interest_rate*100}%")
                        elif isinstance(account, LoanAccount):
                            print(f"  - Loan Account: Balance: {account.balance}, Interest Rate: {account.interest_rate*100}%")
                else:
                    print("  No accounts")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error displaying customers: {e}")

    def select_customer_by_id(self, customer_id):
        for customer in self.customers:
            if customer.id == customer_id:
                return customer
        return None

    def view_transaction_history(self, account_id=None):
        try:
            if not os.path.exists("transactions.csv"):
                print("No transactions found!")
                return
                
            with open("transactions.csv", "r", newline='') as file:
                reader = csv.DictReader(file)
                transactions = list(reader)
                
            if not transactions:
                print("No transactions found!")
                return
                
            print("\n" + "="*80)
            print("TRANSACTION HISTORY")
            print("="*80)
            
            for transaction in transactions:
                if account_id is None or transaction['account_id'] == account_id:
                    print(f"Account: {transaction['account_id']} | "
                          f"Type: {transaction['transaction_type']} | "
                          f"Amount: {transaction['amount']} | "
                          f"Time: {transaction['timestamp']}")
                    if transaction['interest_earned'] and float(transaction['interest_earned']) > 0:
                        print(f"  Interest Earned: {transaction['interest_earned']}")
                    if transaction['overdraft_fee'] and float(transaction['overdraft_fee']) > 0:
                        print(f"  Overdraft Fee: {transaction['overdraft_fee']}")
                    if transaction['loan_duration']:
                        print(f"  Loan Duration: {transaction['loan_duration']} months")
                    if transaction['related_account']:
                        print(f"  Related Account: {transaction['related_account']}")
                    print("-" * 50)
                    
        except Exception as e:
            print(f"Error viewing transactions: {e}")

# Helper function to select account
def select_account(customer):
    if not customer.accounts:
        print("No accounts found for this customer!")
        return None

    print("\nSelect an account:")
    for i, account in enumerate(customer.accounts):
        if isinstance(account, CheckingAccount):
            print(f"{i+1}. Checking Account - Balance: {account.balance}")
        elif isinstance(account, SavingsAccount):
            print(f"{i+1}. Savings Account - Balance: {account.balance}")
        elif isinstance(account, LoanAccount):
            print(f"{i+1}. Loan Account - Balance: {account.balance}")
    
    try:
        choice = int(input("Enter account number: ")) - 1
        if 0 <= choice < len(customer.accounts):
            return customer.accounts[choice]
        else:
            print("Invalid account number!")
            return None
    except ValueError:
        print("Please enter a valid number!")
        return None

# Decorators for UI
def pretty_print(func):
    def wrapper(*args, **kwargs):
        print("\n╔═══════════════════════════════════════════╗")
        print("║           ONLINE BANKING SYSTEM           ║")
        print("╚═══════════════════════════════════════════╝")
        func(*args, **kwargs)
    return wrapper

def pretty_customer(func):
    def wrapper(*args, **kwargs):
        print("\n╔═══════════════════════════════════════════╗")
        print("║             CUSTOMER PORTAL               ║")
        print("╚═══════════════════════════════════════════╝")
        func(*args, **kwargs)
    return wrapper

def pretty_admin(func):
    def wrapper(*args, **kwargs):
        print("\n╔═══════════════════════════════════════════╗")
        print("║               ADMIN PORTAL                ║")
        print("╚═══════════════════════════════════════════╝")
        func(*args, **kwargs)
    return wrapper

# Main function
@pretty_print
def main():
    banking_system = BankingSystem()
    
    while True:
        print("\nMAIN MENU")
        print("1. Customer Login")
        print("2. Customer Registration") 
        print("3. Admin Login")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            customer_login_interface(banking_system)
        elif choice == "2":
            customer_registration_interface(banking_system)
        elif choice == "3":
            admin_interface(banking_system)
        elif choice == "4":
            print("Thank you for using our banking system! Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

def customer_login_interface(banking_system):
    print("\n--- CUSTOMER LOGIN ---")
    customer_id = input("Enter Customer ID: ")
    password = input("Enter Password: ")
    
    customer = banking_system.customer_login(customer_id, password)
    if customer:
        customer_interface(banking_system, customer)
    else:
        print("Invalid Customer ID or Password!")

def customer_registration_interface(banking_system):
    print("\n--- CUSTOMER REGISTRATION ---")
    print("Password must be:")
    print("- At least 6 characters long") 
    print("- Contain at least one digit")
    
    password = input("Set your password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    address = input("Enter address: ")
    
    if banking_system.create_customer(password, first_name, last_name, address):
        print("Registration successful! You can now login.")
    else:
        print("Registration failed! Please check password requirements.")

@pretty_customer
def customer_interface(banking_system, customer):
    print(f"Welcome, {customer.first_name} {customer.last_name}!")
    
    while True:
        print("\nCUSTOMER MENU")
        print("1. Create New Account")
        print("2. Deposit Money")
        print("3. Withdraw Money") 
        print("4. Check Balance")
        print("5. Transfer Funds")
        print("6. View My Transactions")
        print("7. Logout")
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == "1":
            banking_system.prompt_account_type(customer)
        elif choice == "2":
            account = select_account(customer)
            if account:
                amount = float(input("Enter deposit amount: "))
                account.deposit(amount)
        elif choice == "3":
            account = select_account(customer)
            if account:
                amount = float(input("Enter withdrawal amount: "))
                account.withdraw(amount)
        elif choice == "4":
            account = select_account(customer)
            if account:
                account.balance_enquiry()
        elif choice == "5":
            account = select_account(customer)
            if account:
                recipient_id = input("Enter recipient Customer ID: ")
                recipient = banking_system.select_customer_by_id(recipient_id)
                if recipient:
                    recipient_account = select_account(recipient)
                    if recipient_account:
                        amount = float(input("Enter transfer amount: "))
                        account.transfer_funds(recipient_account, amount)
                    else:
                        print("Recipient has no accounts!")
                else:
                    print("Recipient not found!")
        elif choice == "6":
            banking_system.view_transaction_history(customer.id)
        elif choice == "7":
            print("Logged out successfully!")
            break
        else:
            print("Invalid choice!")

@pretty_admin
def admin_interface(banking_system):
    password = input("Enter admin password: ")
    
    if not banking_system.admin_login(password):
        print("Invalid admin password!")
        return
        
    print("Admin login successful!")
    
    while True:
        print("\nADMIN MENU")
        print("1. View All Customers")
        print("2. Create New Customer")
        print("3. View Transaction History")
        print("4. Change Admin Password")
        print("5. Logout")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            banking_system.print_all_customers_info()
        elif choice == "2":
            customer_registration_interface(banking_system)
        elif choice == "3":
            print("\n1. View All Transactions")
            print("2. View Specific Customer Transactions")
            sub_choice = input("Enter choice (1-2): ")
            if sub_choice == "1":
                banking_system.view_transaction_history()
            elif sub_choice == "2":
                customer_id = input("Enter Customer ID: ")
                banking_system.view_transaction_history(customer_id)
            else:
                print("Invalid choice!")
        elif choice == "4":
            banking_system.change_admin_password()
        elif choice == "5":
            print("Admin logged out!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    # Create necessary CSV files if they don't exist
    if not os.path.exists("admin.csv"):
        with open("admin.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['password'])
            writer.writeheader()
            writer.writerow({'password': 'admin123'})
    
    main()