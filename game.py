import json
import os
from random import randint
import sqlite3



logged_in = False


class Database:
    def __init__(self):
        self.con = sqlite3.connect("players.db")
        self.cur = self.con.cursor()
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS players (
                            name TEXT PRIMARY KEY,
                            balance INTEGER
                        )
                         """)
        self.con.commit()

    def logout(self):
        global logged_in
        tempVal = self.currentPlayer[0]
        self.currentPlayer = None
        logged_in = False
        if self.currentPlayer == None:
            print(f"Successfully logged out of account {tempVal}!")

    
    def login(self, playerName):
        global logged_in
        result = self.cur.execute("SELECT name, balance FROM players WHERE name = ?", (playerName,)).fetchone()
        if result:
            self.currentPlayer = result
            print(f"Successfully logged in as {self.currentPlayer[0]}")
            logged_in = True
        else:
            print("Invalid user!\n")           


    def update_balance(self, playerName, newBalance):
        result = self.cur.execute("SELECT name FROM players WHERE name = ?", (playerName,)).fetchone()

        if result:
            self.cur.execute("UPDATE players SET balance = ? WHERE name = ?", (newBalance, playerName))
            self.con.commit()
            print(f"{playerName}'s balance has been updated to {newBalance}!")
        else:
            print(f"Player {playerName} does not exist!")


    def printAllPlayers(self):
        for row in self.cur.execute("SELECT name, balance FROM players"):
            print(f'Player Name: {row[0]} | Balance: {row[1]}')

    def createPlayer(self, name, balance):
        if not logged_in:
            try:
                self.cur.execute("INSERT INTO players VALUES (?, ?)", (name, balance))
                self.con.commit()
                print(f"Player {name} with balance {balance} successfully created!")

            except sqlite3.IntegrityError:
                print("This player already exists.")
        else:
            print("You must be logged out to create a player!")

    def stealMoney(self, playerName, opponentName):

        player = self.cur.execute("SELECT name, balance FROM players WHERE name = ?",(playerName,)).fetchone()
        opponent = self.cur.execute("SELECT name, balance FROM players WHERE name = ?",(opponentName,)).fetchone()
        if not player or not opponent:
            print("Error one or more users does not exist!")
        else: 
            probability = randint(1, 3)
            if probability == 3:
                print(f'{player[0]} successfully stole {opponent[1]} from {opponent[0]}!')
                self.cur.execute("UPDATE players SET balance = balance + ? where name = ?",(opponent[1], playerName))
                self.cur.execute("UPDATE players SET balance = 0 where name = ?",(opponent[0],))
                self.con.commit()
            else:
                print(f'{player[0]} failed to steal {opponent[0]}\'s money, he ended up losing his balance of {player[1]} to {opponent[0]}!')
                self.cur.execute("UPDATE players SET balance = balance + ? where name = ?",(player[1], opponentName))
                self.cur.execute("UPDATE players SET balance = 0 where name = ?",(player[0],))
                self.con.commit()
    def removePlayer(self, playerName):
        result = self.cur.execute("SELECT name, balance FROM players WHERE name = ?", (playerName,)).fetchone()
        if result:
            self.cur.execute("DELETE FROM players WHERE name = ?", (playerName,))
            self.con.commit()
            print(f"Player {playerName} has been removed")
            if logged_in and self.currentPlayer[0] == playerName:
                self.logout()
        else:
            print(f"Player {playerName} doesn't exist.")
            

if __name__ == "__main__":
    db = Database()
    print("Welcome!\n[create] to create a new"
              "player\n[login] to login as a" 
              "player that exists\n[steal] to" \
              " steal money from a player\n[update]" \
              "to update balance for a player\n" \
              "[printp] to print all players\n[quit]" \
              "to quit the session\n" \
              "[logout] to logout\n" \
              "[remove] to remove a player from database" \
              "[status] see if you're logged in or not")

    while True:
        choice = input(">")

        if choice == "quit":
            break
        elif choice == "create":
            try:
                name = input("Enter player name: ")
                balance = int(input("Enter player balance: "))
                db.createPlayer(name, balance)
            except sqlite3.IntegrityError:
                continue
        elif choice == "steal":
            if logged_in:
                victim = input("Enter victim: ")
                db.stealMoney(db.currentPlayer[0], victim)
            else:
                player = input("Enter user who wants to steal: ")
                victim = input("Enter victim: ")
                db.stealMoney(player, victim)
        elif choice == "update":
            if logged_in:
                newBalance = int(input("Enter new balance: "))
                db.update_balance(db.currentPlayer[0], newBalance)
            else:
                name = input("Enter name: ")
                newBalance = int(input("Enter new balance: "))
                db.update_balance(name, newBalance)
        elif choice == "printp":
            db.printAllPlayers()
        elif choice == "login":
            name = input("Enter player name: ")
            if name == "back":
                continue
            else:
                db.login(name)
        elif choice == "logout":
            if logged_in:
                db.logout()
            else:
                print("You are not logged in..")
                continue
        elif choice == "remove":
            player = input("Enter player name: ")
            db.removePlayer(player)
            continue
        elif choice == "status":
            if logged_in:
                print(f"Logged in as {db.currentPlayer[0]}")
            else:
                print("Not logged in.")
            continue
        else:
            print("Enter a valid option!")
            continue