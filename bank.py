# Bank Management System
import mysql.connector
from decimal import Decimal

# database se connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arman",
    database="bank_management"
)

# database par SQL query chalane ka tool
cursor = conn.cursor()

def create_customer():

    print("\n====== CREATE CUSTOMER ======")

    name = input("Enter your name: ")
    age = int(input("Enter your age: "))
    mobile = input("Enter your mobile number: ")
    email = input("Enter your email: ")
    address = input("Enter your address: ")

    customer_query = """
        INSERT INTO customers(name, age, mobile, email, address)
        VALUES(%s, %s, %s, %s, %s)
    """

    customer_values = (name, age, mobile, email, address)

    cursor.execute(customer_query, customer_values)

    conn.commit()

    customer_id = cursor.lastrowid

    print("Customer Created Successfully")
    print("Customer ID:", customer_id)

    print("\n====== CREATE ACCOUNT ======")

    account_type = input("Enter account type (Savings/Current): ")
    initial_balance = Decimal(input("Enter initial balance: "))
    pin = input("Set 4-digit PIN: ")

    account_query = """
        INSERT INTO accounts
        (customer_id, account_type, balance, pin)
        VALUES(%s, %s, %s, %s)
    """

    account_values = (
        customer_id,
        account_type,
        initial_balance,
        pin
    )

    cursor.execute(account_query, account_values)

    conn.commit()

    print("Account Created Successfully")
    print("Account Number:", cursor.lastrowid)

def customer_dashboard(account):

    while True:
        print("\n========== CUSTOMER DASHBOARD ==========")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Transaction History")
        print("6. View Profile")
        print("7. Change PIN")
        print("8. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            account_no = account[0]

            query = """
            SELECT balance FROM accounts
            where account_no = %s
            """
            cursor.execute(query,(account_no,))
            result = cursor.fetchone()
            print("Current Balance: ",result[0])

        elif choice == "2":
            amount = float(input("Enter amount to deposite: "))

            if amount<=0:
                print("Please enter valid Amount")
            else:
                account_no = account[0]
                query = """
                   UPDATE accounts set balance = balance + %s
                   where account_no = %s
                """
                values = (amount,account_no)
                cursor.execute(query,values)
                conn.commit()
                transaction_query = """
                    INSERT INTO transactions
                    (account_no,transaction_type,amount,balance_after)
                    values(%s,%s,%s,
                    (SELECT balance from accounts where account_no = %s))
                """
                transaction_values = (account_no,"Deposit",amount,account_no)
                cursor.execute(transaction_query,transaction_values)
                conn.commit()
                print("Amount Deposited Successfully")

        elif choice == "3":
            amount = Decimal(input("Enter Amount to withrow: "))
            if amount<=0:
                print("Please Enter a Valid Amount")
            else:
                account_no = account[0]
                query = """
                    SELECT balance from accounts 
                    where account_no = %s
                """
                cursor.execute(query,(account_no,))
                result = cursor.fetchone()
                balance =  result[0]
                if amount>balance:
                    print("Insufficient balance")
                else:
                    new_balance = balance-amount
                    update_query = """
                        UPDATE accounts
                        set balance = %s
                        where account_no = %s
                    """
                    cursor.execute(update_query,(new_balance,account_no))
                    transaction_query = """
                        INSERT INTO transactions (account_no,transaction_type,amount,balance_after)
                        values (%s, %s, %s, %s)
                    """
                    transaction_values = (
                        account_no,
                        "withdrow",
                        amount,
                        new_balance
                    )
                    cursor.execute(transaction_query,transaction_values)
                    conn.commit()
                    print("Amount Withdrow Successfully")
                    print("Remaining Balance: ",new_balance)

        elif choice == "4":
            receiver_account = int(input("Enter receiver account number: "))
            amount = Decimal(input("Enter Amount to Transafer: "))

            if amount<=0:
                print("Please Enter Valid Amount")
            else:
                sender_account = account[0]

                if sender_account == receiver_account:
                    print("You Can not Transfer Money to your Own Account")
                else:
                    balance_query = """
                        SELECT balance from accounts
                        where account_no = %s   
                    """

                    cursor.execute(balance_query,(sender_account,))
                    sender_result = cursor.fetchone()
                    sender_balance = sender_result[0]

                    if amount>sender_balance:
                        print("Insufficient Balance")
                    else:
                        receiver_query = """
                            select account_no from accounts
                            where account_no = %s and status = 'Active'
                         """
                        cursor.execute(receiver_query,(receiver_account,))

                        receiver_result = cursor.fetchone()

                        if receiver_result is None:
                            print("Receiver Amount not found")
                        else:
                            new_sender_balance = sender_balance - amount

                            receiver_balance_query = """
                                    SELECT balance from accounts
                                    where account_no = %s
                                """
                            cursor.execute(receiver_balance_query,(receiver_account,))

                            receiver_result = cursor.fetchone()
                            receiver_balance = receiver_result[0]
                            new_receiver_balance = receiver_balance + amount

                            update_sender = """
                                 UPDATE accounts 
                                 set balance = %s
                                 where account_no = %s
                            """

                            cursor.execute(update_sender,(new_sender_balance,sender_account))

                            update_receiver = """
                                      UPDATE accounts
                                      SET balance = %s
                                      WHERE account_no = %s
                                    """

                            cursor.execute(update_receiver,(new_receiver_balance,receiver_account))
                              # Sender transaction
                            sender_transaction = """
                                 INSERT INTO transactions
                                 (account_no, transaction_type, amount, balance_after)
                                  VALUES (%s, %s, %s, %s)
                                """
                            cursor.execute(sender_transaction,(sender_account,"Transfer sent",amount,new_sender_balance))
                             # Receiver transaction
                            receiver_transaction = """
                                  INSERT INTO transactions
                                  (account_no, transaction_type, amount, balance_after)
                                  VALUES (%s, %s, %s, %s)
                                  """

                            cursor.execute(receiver_transaction,(receiver_account,"Transfer Received",amount,new_receiver_balance))
                            conn.commit()
                            print("Transfer Successfull")
                            print("Amount Transferred: ",amount)
                            print("Remaining Balance: ",new_sender_balance)


        elif choice == "5":
            account_no = account[0]
            transaction_query = """
                select transaction_type,amount,balance_after,transaction_date
                from transactions
                where account_no = %s
                order by transaction_date desc
            """
            cursor.execute(transaction_query,(account_no,))
            transactions =  cursor.fetchall()
            if not transactions:
                print("Not Transactions Found")
            else:
                print("\n========== Transaction History ==========")
                print("Type\t\tAmount\t\tBalance\t\tDate")
                for transaction in transactions:
                    print(transaction[0],"\t",transaction[1],"\t",transaction[2],"\t",transaction[3])


        elif choice == "6":
            customer_id = account[1]
            profile_query = """
                 select customers.customer_id,customers.name,customers.age,customers.mobile,customers.email,customers.address,accounts.account_no,accounts.account_type,accounts.balance from customers join accounts on customers.customer_id = accounts.customer_id where customers.customer_id = %s
             """
            cursor.execute(profile_query,(customer_id,))
            profile = cursor.fetchone()
            if profile:
                print("\n========== Profile ===========")
                print("Customer ID: ",profile[0])
                print("Name: ",profile[1])
                print("Age: ",profile[2])
                print("Mobile: ",profile[3])
                print("Email: ",profile[4])
                print("Address: ",profile[5])
                print("Account No: ",profile[6])
                print("Account Type: ",profile[7])
                print("Balance: ",profile[8])

        elif choice == "7":
            old_pin = input("Enter Old Pin: ")
            if old_pin != account[4]:
                print("Incorrect Old pin")
            else:
                new_pin = input("Enter new 4-digit pin: ")
                confirm_pin = input("Confirm new pin: ")

                if len(new_pin) != 4 or not new_pin.isdigit():
                    print("PIN must be exactly 4 digits")
                elif new_pin != confirm_pin:
                    print("New Pin and cofirm pin do not match")
                else:
                    account_no = account[0]
                    update_pin_query = """
                           update accounts 
                           set pin = %s
                           where account_no = %s
                      """
                    cursor.execute(update_pin_query,(new_pin,account_no))
                    conn.commit()
                    print("Pin changed successfully")
                    account = list(account)
                    account[4] = new_pin
                    account = tuple(account)

        elif choice == "8":
            print("Logged out successfully!")
            break

        else:
            print("Invalid choice!")

def customer_login():
    print("\n ====== Customer Login ======")

    account_no = int(input("Enter Account Number: "))
    pin = input("Enter Pin: ")

    query = """
    SELECT * FROM accounts
    where account_no = %s and pin = %s
    """

    values = (account_no,pin)
    cursor.execute(query,values)

    account = cursor.fetchone()

    if account:
        print("Login Successfull")
        print("Welcome")
        customer_dashboard(account)
    else:
        print("Invalid Account Number or pin")

# customer_login()

def admin_dashboard():

    while True:
        print("\n========== ADMIN DASHBOARD ==========")
        print("1. View All Customers")
        print("2. Search Customer")
        print("3. View All Accounts")
        print("4. View All Transactions")
        print("5. Total Bank Balance")
        print("6. Block Account")
        print("7. Unblock Account")
        print("8. Delete Account")
        print("9. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            query = """
              select customer_id,name,age,mobile,email,address
              from customers
              """
            cursor.execute(query)
            customers = cursor.fetchall()
            if not customers:
                print("No Customers Found")
            else:
                print("\n========== ALL CUSTOMERS ==========")
                for customer in customers:
                    print("--------------------------------")
                    print("Customer ID :", customer[0])
                    print("Name        :", customer[1])
                    print("Age         :", customer[2])
                    print("Mobile      :", customer[3])
                    print("Email       :", customer[4])
                    print("Address     :", customer[5])


        elif choice == "2":
            customer_id = int(input("Enter Customer ID: "))
            search_query = """
                 select customer_id,name,age,mobile,email,address
                 from customers
                 where customer_id = %s
              """
            cursor.execute(search_query,(customer_id,))
            customer = cursor.fetchone()
            if customer is None:
                print("Customer Not Found")
            else:
                print("\n========== CUSTOMER DETAILS ==========")
                print("Customer ID :", customer[0])
                print("Name        :", customer[1])
                print("Age         :", customer[2])
                print("Mobile      :", customer[3])
                print("Email       :", customer[4])
                print("Address     :", customer[5])

        elif choice == "3":
            query = """
            SELECT account_no, customer_id, account_type, balance, status
            FROM accounts
            ORDER BY account_no
             """
            cursor.execute(query)
            accounts = cursor.fetchall()
            if not accounts:
                print("No Accounts Found")
            else:
                print("\n========== ALL ACCOUNTS ==========")
                print("Account No\tCustomer ID\tType\t\tBalance\t\tStatus")
                for acc in accounts:
                    print(acc[0],"\t\t",acc[1],"\t\t",acc[2],"\t",acc[3],"\t",acc[4])

        elif choice == "4":
            query = """
               select transaction_id,account_no,transaction_type,amount,balance_after,transaction_date from transactions order by transaction_date desc
            """
            cursor.execute(query)
            transactions = cursor.fetchall()
            if not transactions:
                print("Not Transactions Found")
            else:
                print("\n========== ALL TRANSACTIONS ==========")
                for transaction in transactions:
                    print("----------------------------------------")
                    print("Transaction ID :", transaction[0])
                    print("Account No     :", transaction[1])
                    print("Type           :", transaction[2])
                    print("Amount         :", transaction[3])
                    print("Balance After  :", transaction[4])
                    print("Date           :", transaction[5])


        elif choice == "5":
            query = """
                SELECT COUNT(account_no), SUM(balance)
                FROM accounts
                WHERE status = 'Active'
            """
            cursor.execute(query)
            result = cursor.fetchone()
            total_accounts = result[0]
            total_balance = result[1]
    
            if total_balance is None:
                total_balance = 0

            print("\n========== BANK SUMMARY ==========")
            print("Total Active Accounts :", total_accounts)
            print("Total Bank Balance    :", total_balance)

        elif choice == "6":
            account_no = int(input("Enter Account Number To Block: "))
            check_query = """
                  select status from accounts where account_no = %s
              """
            cursor.execute(check_query,(account_no,))
            result = cursor.fetchone()

            if result is None:
                print("Account Not Found")
            elif result[0] == "Blocked":
                print("Account is already blocked")
            else:
                block_query = """
                    Update accounts set status = 'Blocked'
                    where account_no = %s
                """ 
                cursor.execute(block_query,(account_no,))
                conn.commit()
                print("Account Blocked Successfully")
                
        elif choice == "7":
            account_no = int(input("Enter Account Number To Unblock: "))
            check_query = """
                  select status from accounts where account_no = %s
              """
            cursor.execute(check_query,(account_no,))
            result = cursor.fetchone()

            if result is None:
                print("Account Not Found")
            elif result == "Active":
                print("Account Is already Active")
            else:
                unblock_query = """
                      update accounts set status = 'Active' where account_no = %s
                  """
                cursor.execute(unblock_query,(account_no,))
                conn.commit()
                print("Account Unblock Successfully")

        elif choice == "8":
            account_no = int(input("Enter Account Number to Close: "))
            check_query = """
                    select status,balance from accounts 
                    where account_no = %s
               """
            cursor.execute(check_query,(account_no,))
            result = cursor.fetchone()
            if result is None:
                print("Account Not Found")
            elif result[0] == "Closed":
                print("Account is already closed")
            elif result[1]>0:
                print("Account Cannot be closed")
                print("Please withdrow or transafer the remaining balance first")
            else:
                close_query = """
                    update accounts set status = 'Closed'
                    where account_no = %s
                  """
                cursor.execute(close_query,(account_no,))
                conn.commit()
                print("Account Closed Successfully")

        elif choice == "9":
            print("Admin logged out successfully!")
            break

        else:
            print("Invalid choice!")

def admin_login():
    print("\n======== Admin Login =========")

    username = input("Enter Admin Username: ")
    password = input("Enter Adin Password: ")

    if username == "admin" and password == "admin123":
        print("Admin Login Successfull")
        admin_dashboard()
    else:
        print("Invalid Admin credentials")


def main_menu():
    while True:
        print("\n========================================")
        print("       BANK MANAGEMENT SYSTEM")
        print("========================================")
        print("1. Create Customer Account")
        print("2. Customer Login")
        print("3. Admin Login")
        print("4. Exit")

        choice = int(input("Enter Your Choice: "))
        if choice == 1:
            create_customer()
        elif choice == 2:
            customer_login()
        elif choice == 3:
            admin_login()
        elif choice == 4:
            print("Thank For Using Bank Management System")
            break
        else:
            print("Invalid Choice ! Please try again.")

main_menu()

