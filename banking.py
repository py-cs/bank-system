from random import choice
from string import digits
import sqlite3


class Card:
    def __init__(self, number=None, pin=None):
        if number:
            self.from_db(number, pin)
        else:
            self.new_card()

    def new_card(self):
        number = '400000' + ''.join(choice(digits) for _ in range(9))
        last_digit = self.luhn_check(number)
        self.number = number + str(last_digit)
        self.pin = ''.join(choice(digits) for _ in range(4))
        cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (self.number, self.pin))
        conn.commit()
        print(f'Your card has been created\nYour card number:\n{self.number}\nYour card PIN:\n{self.pin}')

    def from_db(self, number, pin):
        cur.execute('SELECT * FROM card WHERE number = ? AND pin = ?', (number, pin))
        data = cur.fetchone()
        if data:
            self.number = data[1]
            self.pin = data[2]
            self.balance = data[3]
            print('You have successfully logged in!')
            return self
        else:
            print('Wrong card number or PIN!')
            return None

    def deposit(self, amount):
        self.balance += amount
        cur.execute('UPDATE card SET balance = ? WHERE number = ?', (self.balance, self.number))
        conn.commit()
        print('Income was added!')

    def transfer(self, dest_number):
        if dest_number == self.number:
            print("You can't transfer money to the same account!")
        elif self.luhn_check(dest_number):
            print('Probably you made mistake in the card number. Please try again!')
        else:
            cur.execute(f'SELECT balance FROM card WHERE number = {dest_number}')
            dest_card = cur.fetchone()
            if dest_card:
                amount = int(input('Enter how much money you want to transfer:'))
                if self.balance < amount:
                    print('Not enough money!')
                else:
                    self.balance -= amount
                    cur.execute('UPDATE card SET balance = ? WHERE number = ?', (self.balance, self.number))
                    cur.execute('UPDATE card SET balance = ? WHERE number = ?', (dest_card[0] + amount, dest_number))
                    conn.commit()
            else:
                print('Such a card does not exist.')

    def close(self):
        cur.execute(f'DELETE FROM card WHERE number = {self.number}')
        conn.commit()
        print('The account has been closed!')

    @staticmethod
    def luhn_check(number):
        digits = [int(c) for c in number]
        for i, digit in enumerate(digits):
            if not i % 2:
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
        return 0 if sum(digits) % 10 == 0 else 10 - sum(digits) % 10


db_name = 'card.s3db'
conn = sqlite3.connect(db_name)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS card 
(id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)''')
conn.commit()

while True:
    print('1. Create an account\n2. Log into account\n0. Exit')
    action = int(input())
    if action == 1:
        card = Card()
    if action == 2:
        card = Card(number=int(input('\nEnter your card number:\n')),
                    pin=input('\nEnter your PIN:\n'))
        if card:
            while True:
                print('1. Balance\n2. Add income\n3. Do transfer'
                      '\n4. Close account\n5. Log out\n0. Exit')
                action = int(input())
                if action == 0:
                    break
                if action == 1:
                    print('Balance:', card.balance)
                if action == 2:
                    card.deposit(int(input('Enter income:')))
                if action == 3:
                    card.transfer(input('Transfer\nEnter card number:'))
                if action == 4:
                    card.close()
                    card = None
                    break
                if action == 5:
                    card = None
                    print('You have successfully logged out!')
                    break
    if action == 0:
        print('Bye!')
        break
