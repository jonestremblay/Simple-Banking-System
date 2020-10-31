import math
import random
import sqlite3

# Connect to database and create a cursor instance.
conn = sqlite3.connect("card.s3db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS card (
        id INTEGER ,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
         )""")


def gen_acc_number() -> str:
    acc_number = ""
    while len(acc_number) < 9:
        acc_number += str(random.randint(0, 9))
    return acc_number


def gen_pin_code() -> str:
    pin_code = ""
    while len(pin_code) < 4:
        pin_code += str(random.randint(0, 9))
    return pin_code


class CardNumber:

    def __init__(self, bin, acc_number, pin_code):
        self.bin = bin
        self.acc_number = acc_number
        self.pin_code = pin_code
        self.card_number_no_check_digit = self.bin + self.acc_number
        self.balance = 0

    @staticmethod
    def gen_check_digit() -> str:
        """
        Luhn's algorithm: all numbers % 10 == 0
        so sum of all numbers of the card number - without check digit - (sum)
        (sum + x) % 10 == 0
        """
        count_list = list(account.bin) + list(account.acc_number)
        int_count_list = [int(i) for i in count_list]
        new_list = []

        for a in range(0, len(int_count_list), 2):
            new_list.append(int_count_list[a] * 2)
        for b in range(1, len(int_count_list), 2):
            new_list.append(int_count_list[b])
        c = 0
        for i in new_list:
            if i > 9:
                c += 9
        int_sum = sum(new_list) - c
        poss_check_digits = []
        for x in range(10):
            if (int_sum + x) % 10 == 0:
                # poss_check_digits.append(x)
                check_digit = str(x)
        # check_digit = str(random.choice(poss_check_digits))
        return check_digit


iin_bin = "400000"

choice = -1
while choice != 0:
    choice = input("1. Create an account\n"
                   "2. Log into account\n"
                   "0. Exit\n")
    if choice == "1":
        account = CardNumber(iin_bin, gen_acc_number(), gen_pin_code())
        check_sum = CardNumber.gen_check_digit()
        card_number = account.bin + account.acc_number + check_sum
        card_pin = account.pin_code
        print("\nYour card has been created\n"
              "Your card number:\n" +
              card_number + "\n"
              "Your card PIN:\n" +
              card_pin + "\n")
        card_balance = account.balance
        card_id = account.bin
        card = (card_id, card_number, card_pin, card_balance)
        c.execute("INSERT INTO card VALUES (?, ?, ?, ?)", card)
        conn.commit()
        print("New card added to the card\'s database.")
        print(c.fetchall())
        continue
    elif choice == "2":
        # Log into acc
        log_in = False
        user = input("Enter you card number:\n")
        pin = input("Enter your PIN:\n")

        if user == (account.card_number_no_check_digit + CardNumber.gen_check_digit()) \
                and pin == account.pin_code:
            print("\nYou have successfully logged in!")
            log_in = True
            while log_in:
                choice = input("\n1. Balance\n"
                               "2. Log out\n"
                               "0. Exit\n")
                if choice == "1":
                    balance = account.balance
                    print("\nBalance: ", balance)
                    continue
                elif choice == "2":
                    print("\nYou have successfully logged out!\n")
                    log_in = False
                elif choice == "0":
                    print("\nBye!")
                    conn.close()
                    exit()
        else:
            print("\nWrong card number or PIN!\n")
            continue
    elif choice == "0":
        # Exit
        print("Bye!")
        conn.close()
        exit()
    else:
        print("Incorrect parameter.")
