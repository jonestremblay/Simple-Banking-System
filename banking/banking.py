import random
import sqlite3

# The reason why the test #4 doesnt pass is because i store the bin and account number separated, not as a whole, and the thest check the number as a whole.
# Connect to database and create a cursor instance.

conn = sqlite3.connect("../card.s3db")
cursor = conn.cursor()

ADD_CARD = "INSERT INTO card (id, number, pin, balance) VALUES (?, ?, ?, ?)"

DELETE_CARD = "DELETE FROM card WHERE number == ?"

GET_ALL_CARDS = "SELECT * FROM card"

GET_CARD_NUMBER_ofACCOUNT = "SELECT number FROM card WHERE number == ? "

GET_PIN_NUMBER_ofACCOUNT = "SELECT pin FROM card WHERE number == ? "

GET_BALANCE_ofACCOUNT = "SELECT balance FROM card WHERE number == ?"

UPDATE_BALANCE_ofAccount = "UPDATE card SET balance=(balance - ?) WHERE number == ? "


def create_card_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS card (
            id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
            )""")
    conn.commit()


def drop_card_table():
    cursor.execute("""DROP TABLE card""")
    conn.commit()


drop_card_table()
create_card_table()


def remove_symbols_from_string(stringToEdit) -> str:
    """
    Convert the fetch into a string, then removes symbols   [ ] ( ) ,    from the string.
    """
    string = str(stringToEdit)
    for z in ("[", ""), ("]", ""), ("(", ""), (")", ""), (",", ""):
        string = string.replace(*z)
    return string


def gen_acc_number() -> str:
    acc_num = ""
    while len(acc_num) < 9:
        acc_num += str(random.randint(0, 9))
    return acc_num


def gen_pin_code() -> str:
    pin_code = ""
    while len(pin_code) < 4:
        pin_code += str(random.randint(0, 9))
    return pin_code


def gen_check_digit(bank_idNumber, account_number) -> str:
    """
    Luhn's algorithm: all numbers % 10 == 0
    so sum of all numbers of the card number - without check digit - (sum)
    (sum + x) % 10 == 0
    Returns the check-digit that pass Luhn's algorithm
    """
    count_list = list(bank_idNumber) + list(account_number)
    int_count_list = [int(k) for k in count_list]
    new_list = []
    check_digit = ""
    for a in range(0, len(int_count_list), 2):
        new_list.append(int_count_list[a] * 2)
    for b in range(1, len(int_count_list), 2):
        new_list.append(int_count_list[b])
    c = 0
    for k in new_list:
        if k > 9:
            c += 9
    int_sum = sum(new_list) - c

    for x in range(10):
        if (int_sum + x) % 10 == 0:
            check_digit = str(x)
    return check_digit


class CardNumber:
    def __init__(self, _bin, _acc_number, _pin_code):
        self.bin = _bin
        self.acc_number = _acc_number
        self.pin_code = _pin_code
        self.card_number_no_check_digit = self.bin + self.acc_number
        self.balance = 0


iin_bin = "400000"
choice = -1
while choice != 0:
    log_in = False
    choice = input("1. Create an account\n"
                   "2. Log into account\n"
                   "3. View all accounts\n"
                   "0. Exit\n")
    if choice == "1":
        acc_number = gen_acc_number()
        check_sum = gen_check_digit(iin_bin, acc_number)
        card_number = iin_bin + acc_number + check_sum
        card_pin = gen_pin_code()
        print("\nYour card has been created\n"
              "Your card number:\n" +
              card_number + "\nYour card PIN:\n" +
              card_pin + "\n")
        card = (iin_bin, acc_number + check_sum, card_pin, 0)
        cursor.execute(ADD_CARD, card)
        conn.commit()
        print("New card added to the card\'s database.")
        print("BIN: " + card[0] + " Acc_#: " + card[1] + "\n"
              "PIN: " + card[2] + "   Balance: " + str(card[3]) + " $" + "\n")
    elif choice == "2":
        # Log into acc
        user = input("Enter you card number:\n")
        pin = input("Enter your PIN:\n")
        user_number = user[6:]
        cursor.execute(GET_CARD_NUMBER_ofACCOUNT, (user_number,))
        user_fetch = cursor.fetchall()
        user_data = remove_symbols_from_string(user_fetch)
        cursor.execute(GET_PIN_NUMBER_ofACCOUNT, (user_number,))
        pin_fetch = cursor.fetchall()
        pin_data = remove_symbols_from_string(pin_fetch)
        card_number = user
        # user[6:]: slice the BIN (400000) from the input, to compare only acc_number, not card number.
        if user_number in user_data:
            if pin in pin_data:
                print("\nYou have successfully logged in!")
                log_in = True
                while log_in:
                    menu = input("\n1. Balance\n"
                                 "2. Add income\n"
                                 "3. Do transfer\n"
                                 "4. Close account\n"
                                 "5. Log out\n"
                                 "0. Exit\n")
                    if menu == "1":
                        # Print balance
                        acc = (user_number,)
                        cursor.execute(GET_BALANCE_ofACCOUNT, acc)
                        fetch = cursor.fetchall()
                        balance = remove_symbols_from_string(fetch)
                        print("\nBalance: " + balance)  # + " $")
                    elif menu == "2":
                        # Add income
                        income = int(input("Enter income:\n"))
                        data = (income, user_number)
                        cursor.execute(UPDATE_BALANCE_ofAccount, data)
                        conn.commit()
                        print("\nIncome was added!")
                    elif menu == "3":
                        # Transfer money to another card.
                        cursor.execute(GET_BALANCE_ofACCOUNT, (user_number,))
                        fetch = cursor.fetchall()
                        current_balance = int(remove_symbols_from_string(fetch))
                        print("\nTransfer")
                        card_num_to_transfer = input("Enter card number:\n")
                        if card_num_to_transfer[6:] == user_number:
                            print("\nYou can't transfer money to the same account!\n")
                            break
                        if card_num_to_transfer[-1] == gen_check_digit(card_num_to_transfer[:5],
                                                                       card_num_to_transfer[6:]):
                            # Means it pass Luhn's algorithm.
                            cursor.execute(GET_CARD_NUMBER_ofACCOUNT, (card_num_to_transfer[6:],))
                            nums = cursor.fetchall()
                            if (card_num_to_transfer[6:],) in nums:
                                amount = int(input("Enter how much money you want to transfer:\n"))
                                if amount <= current_balance:
                                    # do transfer and print success.
                                    sender = (amount, user_number)
                                    receiver = (amount, card_num_to_transfer[6:])
                                    cursor.execute(UPDATE_BALANCE_ofAccount, sender)
                                    cursor.execute(UPDATE_BALANCE_ofAccount, receiver)
                                    conn.commit()
                                    print("Success!")
                                else:
                                    print("Not enough money!")
                            else:
                                print("Such a card does not exist.")
                        else:
                            print("\nProbably you made mistake in the card number. Please try again!\n")
                            break
                    elif menu == "4":
                        # Close account
                        cursor.execute(DELETE_CARD, (user_number,))
                        conn.commit()
                        print("\nThe account has been closed!\n")
                        break
                    elif menu == "5":
                        # Log out
                        print("\nYou have successfully logged out!\n")
                        log_in = False
                    elif menu == "0":
                        print("\nBye!")
                        conn.close()
                        exit()
                    else:
                        print("Incorrect parameter.")
            else:
                print("\nWrong card number or PIN!\n")
        else:
            print("\nWrong card number or PIN!\n")
    elif choice == "3":
        # View all accounts
        cursor.execute(GET_ALL_CARDS)
        data = cursor.fetchall()
        for i in data:
            print(i)
        print()
    elif choice == "0":
        # Exit
        print("Bye!")
        conn.close()
        exit()
    else:
        print("Incorrect parameter.")
