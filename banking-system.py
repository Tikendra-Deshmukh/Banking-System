import random
import re
from datetime import datetime
from abc import ABC, abstractmethod

class Account(ABC):
    next_account_id = 1
    def __init__(self, id, account_type, balance):
        self.id = id
        self.account_type = account_type
        self.balance = balance
        self.transactions = []

    def save_account_info(self):
        try:
           with open(f"{self.id}.txt", "a+") as file:
               if isinstance(self, SavingsAccount):
                  file.write(f"{self.id},{self.account_type},{self.balance}\n")
               elif isinstance(self, CheckingAccount):
                  file.write(f"{self.id},{self.account_type},{self.balance}\n")
               elif isinstance(self, LoanAccount):
                  file.write(f"{self.id},{self.account_type},{self.balance}\n")
        #IOError is basically a error of input & output ocuuring for many reasons
        except IOError as e:
            print(f"Error occurred while saving account info: {e}")
        #Exception is a base class which contains all types of exception
        except Exception as e:
            print(f"An error occurred: {e}")


    def deposit(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            print("Please Enter amount in digits")
            return
        self.balance += amount
        self.save_account_info()
        transaction = f"Deposited: {amount}"
        self.transactions.append(transaction)
        with open("Trasaction_history.txt", "a") as f:
            f.write(f"{self.id} deposited {amount} rupees on ({datetime.now()})\n")

    @abstractmethod
    def withdraw(self, amount):
        pass

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def balance_enquiry(self):
        print(f"Account Type: {self.account_type}")
        print(f"Balance: {self.balance}")

    def transfer_funds(self, recipient_account, amount):
        try:
            if self.balance >= amount:
                self.balance -= amount
                recipient_account.balance += amount
                self.save_account_info()
                recipient_account.save_account_info()
                transaction = f"Transferred: {amount} to {recipient_account.id}"
                self.transactions.append(transaction)
                recipient_account.transactions.append(transaction)
                with open("Trasaction_history.txt", "a") as f:
                    f.write(f"{self.id} transferred {amount} rupees to {recipient_account.id} on ({datetime.now()})\n")
                return True
            else:
                raise ValueError("Insufficient balance.")
        except:
            print("Insufficient balance.")
            return False


class CheckingAccount(Account):
    def __init__(self, id, balance):
        super().__init__(id, "Checking", balance)
        self.credit_limit =(self.balance*0.5)*(-1)
        self.overdraft_fee= abs(self.balance) * 0.02


    def withdraw(self, amount):
        try:
            if self.balance - amount >= self.credit_limit:
                if self.balance - amount> 0:
                    self.balance -= amount
                    transaction = f"Withdrawn: {amount}"
                    self.transactions.append(transaction)
                    print("Amount withdrawn successfully!")
                    self.save_account_info()
                    with open("Trasaction_history.txt", "a") as f:
                        f.write(f"{self.id} withdrawed {amount} rupees on ({datetime.now()})\n")
                elif self.balance - amount < 0:
                    self.balance -= (self.overdraft_fee + amount)
                    transaction = f"overdraft fee deducted: {self.overdraft_fee}"
                    self.transactions.append(transaction)
                    self.save_account_info()
                    with open("Trasaction_history.txt", "a") as f:
                        f.write(f"{self.id} withdrawed {amount} rupees on ({datetime.now()})\n")
        #as (e) means it prints the actual error rather than the user defined message
        except ValueError as e:
            print(e)


class SavingsAccount(Account):
    def __init__(self, id, balance):
        super().__init__(id, "Savings", balance)
        self.interest_rate = (self.balance*0.1)

    def deposit(self, amount):
        try:
            self.balance += (amount+self.interest_rate)
            self.save_account_info()
            transaction = f"Deposited: {amount}"
            self.transactions.append(transaction)
            with open("Trasaction_history.txt", "a") as f:
                f.write(f"{self.id} deposited {amount} rupees on ({datetime.now()})\n")
        except ValueError as e:
            print(e)

    def withdraw(self, amount):
        try:
            if self.balance >= amount:
                self.balance -= amount
                self.save_account_info()
                transaction = f"Withdrawn: {amount}"
                self.transactions.append(transaction)
                with open("Trasaction_history.txt", "a") as f:
                    f.write(f"{self.id} withdrawed {amount} rupees on ({datetime.now()})\n")
                return True
            else:
                print("Insufficient balance.")
                return False
        except ValueError as e:
            print(e)


class LoanAccount(Account):
    def __init__(self, id, balance):
        super().__init__(id, "Loan", balance)
        # self.loanDuration = int(input("Enter current month of loan taken: "))
    def withdraw(self, amount):
        try:
            if self.balance >= amount:
                loanDuration = int(input("Enter current month of loan taken: "))
                intrestRate = self.balance*(loanDuration // 0.08)
                self.balance -= round(amount + intrestRate)
                self.save_account_info()
                transaction = f"Withdrawn: {amount}"
                self.transactions.append(transaction)
                with open("Trasaction_history.txt", "a") as f:
                    f.write(f"{self.id} withdrawed {amount} rupees on ({datetime.now()})\n")
                return True
            else:
                print("Insufficient balance.")
                return False
        except ValueError as e:
            if "Insufficient funds" in str(e):
                print("Insufficient balance.")
            else:
                print(e)
        #TypeError when the type of input is not match with the condition
        except TypeError as e:
            print("LoanDuration required an integer value.")

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
            with open("customerinfo.txt", "a") as file:
                file.write(f"{self.id},{self.password},{self.first_name},{self.last_name},{self.address}\n")
        except IOError as e:
            print(f"Error occurred while saving customer info: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

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
        self.admin_password = self.load_admin_password("admin_password.txt")

    def load_admin_password(self, filename):
        try:
            with open(filename, "r") as file:
                return file.read().strip()
        #FileNotFoundError when the required file doesn't exist or the directory is different
        except FileNotFoundError:
            return None

    def change_admin_password(self):
        n = input("\nEnter previous password: ")
        with open("admin_password.txt", "r") as f:
            if n == f.read():
                o = input("Set new password: ")
                with open("admin_password.txt", "w") as g:
                    g.write(o)
            else:
                print("Invalid Password!!")
                self.change_admin_password()


    def load_customers_from_file(self):
        with open("customerinfo.txt", "r") as file:
            for line in file:
                id, password, first_name, last_name, address = line.strip().split(",")
                customer = Customer(id, password, first_name, last_name, address)
                self.customers.append(customer)
                self.load_customer_accounts(customer)


    def load_customer_accounts(self, customer):
            with open(f"{customer.id}.txt", "r") as file:
                for line in file:
                    k = line.strip().split(",")
                    id, account_type, balance = k[0],k[1],k[2]
                    if account_type == "Checking":
                        account = CheckingAccount(id, float(balance))
                    elif account_type == "Savings":
                        account = SavingsAccount(id, float(balance))
                    elif account_type == "Loan":
                        account = LoanAccount(id, float(balance))
                    customer.add_account(account)


    def save_customer_accounts(self, customer):
        try:
            with open(f"{customer.id}.txt", "a") as file:
                for account in customer.accounts:
                   if isinstance(account, CheckingAccount):
                      file.write(f"{account.id},Checking,{account.balance},{account.credit_limit}\n")
                   elif isinstance(account, SavingsAccount):
                      file.write(f"{account.id},Savings,{account.balance},{account.interest_rate}\n")
                   elif isinstance(account, LoanAccount):
                      file.write(f"{account.id},Loan,{account.balance}\n")
                      account.save_account_info()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)
            print("Something went wrong. Please try again.")

    def customer_login(self, ID, PSword):
        self.load_customers_from_file()
        for customer in self.customers:
            if customer.id == ID and customer.password == PSword:
                return customer
        return None

    def admin_login(self, password):
        try:
           if password == self.admin_password:
              return True
           return False
        except Exception as e:
           print(f"An error occurred during admin login: {e}")


    def create_customer(self, password, first_name, last_name, address):
        try:
           id =random.randint(100,999)+random.randint(1000,9999)+ random.randint(1000000,9999999)
           print(f'your Account ID is : {id}')
           customer = Customer(id, password, first_name, last_name, address)
           # Check password length and digit presence
           if len(password) < 6 or not re.search(r'\d', password):
               print("Password must be at least 6 characters long and contain a digit.")
               return False
           self.customers.append(customer)
           Customer.save_customer_info(customer)
           f = open(f"{id}.txt", "w")
           f.close()
           # self.prompt_account_type(customer)
           return True

        except Exception as e:
           print(f"An error occurred while creating customer: {e}")

    def prompt_account_type(self, customer):
        try:
            print("Select an account type:")
            print("1. Checking Account")
            print("2. Savings Account")
            print("3. Loan Account")
            choice = input("Enter your choice: ")
            if choice == "1":
               self.create_checking_account(customer)
            elif choice == "2":
               self.create_savings_account(customer)
            elif choice == "3":
               self.create_loan_account(customer)
            else:
               print("Invalid choice.")
        except Exception as e:
             print(f"An error occurred while prompting account type: {e}")

    def create_checking_account(self, customer):
        try:
           balance = float(input("Enter initial balance: "))
           account = CheckingAccount(customer.id, balance)
           account.save_account_info()
           customer.accounts.append(account)
           print("Checking account created successfully.")
        except ValueError:
           print("Invalid input. Please enter a valid balance.")
        except Exception as e:
           print(f"An error occurred while creating checking account: {e}")

    def create_savings_account(self, customer):
        try:
           balance = float(input("Enter initial balance: "))
           account = SavingsAccount(customer.id, balance)
           account.save_account_info()
           customer.accounts.append(account)
           print("Savings account created successfully.")
        except ValueError:
           print("Invalid input. Please enter a valid balance.")
        except Exception as e:
           print(f"An error occurred while creating savings account: {e}")

    def create_loan_account(self, customer):
        try:
           balance = float(input("Enter initial balance: "))
           account = LoanAccount(customer.id, balance)
           account.save_account_info()
           customer.accounts.append(account)
           print("Loan account created successfully.")
        except ValueError:
           print("Invalid input. Please enter a valid balance.")
        except Exception as e:
           print(f"An error occurred while creating loan account: {e}")

    def print_all_customers_info(self):
        try:
           print("All Customers Information")
           for customer in self.customers:
               print(f"Account ID: {customer.id}")
               print(f"Name: {customer.first_name} {customer.last_name}")
               print(f"Address: {customer.address}")
               print("Accounts:")
               for account in customer.accounts:
                   if isinstance(account, CheckingAccount):
                      print(f"- Account Type: Checking")
                      print(f"  Balance: {account.balance}")
                      print(f"  Credit Limit: {account.credit_limit}")
                   elif isinstance(account, SavingsAccount):
                      print(f"- Account Type: Savings")
                      print(f"  Balance: {account.balance}")
                      print(f"  Interest Rate: 10%")
                   elif isinstance(account, LoanAccount):
                      print(f"- Account Type: Loan")
                      print(f"  Balance: {account.balance}")
                      print(f"  Interest Rate: 8% with respect to loan duration")
                      print(f"  Loan Duration: maximum 6 months")
        except Exception as e:
           print(f"An error occurred while printing customer information: {e}")

    def select_customer_by_username(self, id):
        try:
           for customer in self.customers:
              if customer.id == id:
                 return customer
           return None
        except Exception as e:
           print(e)

# Helper function to select an account from a customer's accounts list
def select_account(customer):
    if not customer.accounts:
        print("No accounts found.")
        return None

    print("Select an account:")
    for i, account in enumerate(customer.accounts):
        print(f"{i+1}. Account Type: {account.account_type}")
        print(f"   Balance: {account.balance}")
    try:
        choice = int(input("Enter account number: ")) - 1
    except ValueError:
        print("Please enter a valid account number.")
        return None

    if 0 <= choice < len(customer.accounts):
        return customer.accounts[choice]
    else:
        print("Invalid account number.")
        return None

def pretty_print_interface(func):
    def wrapper(*args, **kwargs):
        print("\n=========================================================================================\n=========================================================================================")
        func(*args, **kwargs)
        print("=========================================================================================\n=========================================================================================\n")

    return wrapper

def pretty(func):
    def wrapper(*args, **kwargs):
        print("╔═══════════════════════════════════════════╗")
        print("║             CUSTOMER INTERFACE            ║")
        print("╠═══════════════════════════════════════════╣")
        print("╚═══════════════════════════════════════════╝")
        func(*args, **kwargs)
        print()
    return wrapper

def pretty_print(func):
    def wrapper(*args, **kwargs):
        print("╭───────────────────────────────────────╮")
        print("│         WELCOME TO OUR BANK           │")
        print("│                                       │")
        print("╰───────────────────────────────────────╯")
        func(*args, **kwargs)
        print('\n=========================================================================================\n')

    return wrapper


def pretty_admin(func):
    def wrapper(*args, **kwargs):
        print("╔═══════════════════════════════════════════╗")
        print("║              ADMIN INTERFACE              ║")
        print("╚═══════════════════════════════════════════╝")
        func(*args, **kwargs)
        print()

    return wrapper

# Main function
@pretty_print
def main():
    banking_system = BankingSystem()
    banking_system.load_customers_from_file()

    while True:
        print("\n*** Main Interface ***")
        print("Press[1] for Customer Login")
        print("Press[2] for Admin Login")
        print("Press[3] for Quit")
        try:
            choice = input("Enter your choice: ")
        except ValueError:
            print("Please enter a valid choice!")
            continue

        if choice == "1":
            print("\n Press '1' to Login to your account\n Press '2' to Register Yourself.")
            choice2 = int(input())
            if choice2 == 1:
                customer_id = input("Enter your Account ID: ")
                customer_password = input("Enter your password: ")
                customerA = banking_system.customer_login(customer_id, customer_password)
                if customerA:
                    customer_interface(banking_system, customerA)
                else:
                    print("Invalid username or password.")
            elif choice2 == 2:
                print('password must be :\n *six characters in length\n *must contain at least one digit\n')
                password = input("Set password: ")
                first_name = input("Enter first name: ")
                last_name = input("Enter last name: ")
                address = input("Enter address: ")
                if banking_system.create_customer(password, first_name, last_name, address):
                    print("Registered successfully.")
                else:
                    print("Failed to create customer. Please check password requirements.")
            else:
                print("\nPlease Enter Right Choice!!")

        elif choice == "2":
            admin_interface(banking_system)

        elif choice == "3":
            print("Goodbye!!")
            break
        else:
            print("Invalid choice. Please try again.")


# Update the customer_interface function
@pretty_print_interface
@pretty
def customer_interface(banking_system, customer):
    print(f"\nWelcome, {customer.first_name} {customer.last_name}!")

    while True:
        try:
            print("\nCustomer Interface")
            print("1. Create Account")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Balance Enquiry")
            print("5. Transfer Funds")
            print("6. Back")
            choice = input("Enter your choice: ")

            if choice == "1":
                banking_system.prompt_account_type(customer)

            elif choice == "2":
                account = select_account(customer)
                if account:
                    amount = float(input("Enter amount to deposit: "))
                    account.deposit(amount)
                    print("Amount deposited successfully.")

            elif choice == "3":
                account = select_account(customer)
                if account:
                    amount = float(input("Enter amount to withdraw: "))
                    account.withdraw(amount)
                    print("Amount withdrawn successfully.")

            elif choice == "4":
                account = select_account(customer)
                if account:
                    account.balance_enquiry()

            elif choice == "5":
                account = select_account(customer)
                if account:
                    recipient_username = input("Enter recipient ID: ")
                    recipient_customer = banking_system.select_customer_by_username(recipient_username)
                    if recipient_customer:
                        recipient_account = select_account(recipient_customer)
                        if recipient_account:
                            amount = float(input("Enter amount to transfer: "))
                            account.transfer_funds(recipient_account, amount)
                            print("Funds transferred successfully.")
                        else:
                            print("Recipient account not found.")
                    else:
                        print("Recipient username not found.")

            elif choice == "6":
                print("Going back to the main menu.")
                break

            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid choice or amount.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Update the admin_interface function
@pretty_admin
@pretty_print_interface
def admin_interface(banking_system):
    # username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    if banking_system.admin_login(password):
        while True:
            print("\nAdmin Interface")
            print("1. Create Customer")
            print("2. Print All Customers Information")
            print("3. balance Enquiry")
            print("4. transaction history")
            print("5. Transfer funds")
            print("6. Change admin password")
            print("7. Back")
            try:
                choice = input("Enter your choice: ")
            except ValueError:
                print("Please enter a valid choice.")
                continue

            if choice == "1":
                print('password must be :\n *six characters in length\n *must contain at least one digit\n')
                password = input("Enter password: ")
                first_name = input("Enter first name: ")
                last_name = input("Enter last name: ")
                address = input("Enter address: ")
                if banking_system.create_customer( password, first_name, last_name, address):
                    print("Customer created successfully.")
                else:
                    print("Failed to create customer. Please check password requirements.")

            elif choice == "2":
                banking_system.print_all_customers_info()

            elif choice == "3":
                ID = input("Enter customer Account ID: ")
                customer = banking_system.select_customer_by_username(ID)
                if customer:
                    account = select_account(customer)
                    if account:
                        account.balance_enquiry()

            elif choice == "4":
                with open("Trasaction_history.txt", "r") as f:
                    g = f.readlines()
                for line in g:
                    print(line)

            elif choice == "5":
                ID = input("Enter customer Account ID: ")
                customer = banking_system.select_customer_by_username(ID)
                if customer:
                    account = select_account(customer)
                    if account:
                        recipient_username = input("Enter recipient ID: ")
                        recipient_customer = banking_system.select_customer_by_username(recipient_username)
                        if recipient_customer:
                            recipient_account = select_account(recipient_customer)
                            if recipient_account:
                                amount = float(input("Enter amount to transfer: "))
                                account.transfer_funds(recipient_account, amount)
                                print("Funds transferred successfully.")
                        else:
                            print("Recipient username not found.")

            elif choice == "6":
                banking_system.change_admin_password()

            elif choice == "7":
                print("Going back to the main menu.")
                break

            else:
                print("Invalid choice. Please try again.")

    else:
        print("Invalid username or password.")

if __name__ == "__main__":
    main()



h