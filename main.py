import random
import sqlite3
import hashlib


def connect_db():
    conn = sqlite3.connect('hangman_scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS scores (name TEXT, score INTEGER)''')
    conn.commit()
    return conn, c


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup(conn, c):
    while True:
        name = input("Enter a username: ").strip().lower()
        password = input("Enter a password: ").strip()
        c.execute("SELECT * FROM users WHERE name=?", (name,))
        if c.fetchone():
            print("Username already exists. Try another one.")
        else:
            hashed_password = hash_password(password)
            c.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, hashed_password))
            conn.commit()
            print("Signup successful!")
            return name  # Proceed to game


def login(conn, c):
    while True:
        name = input("Enter your username: ").strip().lower()
        password = input("Enter your password: ").strip()
        c.execute("SELECT password FROM users WHERE name=?", (name,))
        result = c.fetchone()
        if result and result[0] == hash_password(password):
            print(f"Welcome back, {name}!")
            return name
        else:
            print("Invalid username or password. Please try again.")


def update_scores(conn, c, name, score):
    c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()


def restart_game(conn, c, user):
    while True:
        restart = input("Do you want to restart the game? (yes/no): ").lower()
        if restart == "yes":
            start_game(conn, c, user)
            break
        elif restart == "no":
            print("Thanks for playing! Goodbye.")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def choose_difficulty():
    while True:
        difficulty = input("Choose your difficulty level (easy, medium, hard): ").lower()
        if difficulty == "easy":
            return easy_words, 8
        elif difficulty == "medium":
            return medium_words, 6
        elif difficulty == "hard":
            return hard_words, 4
        else:
            print("Invalid input. Please choose easy, medium, or hard.")


def start_game(conn, c, user):
    word_list, max_attempts = choose_difficulty()
    chosen_word = list(random.choice(word_list))
    blank_list = ['_'] * len(chosen_word)
    attempts = 0
    hints_used = False

    print("Starting Hangman!")
    while attempts < max_attempts:
        print(HANGMANPICS[attempts])
        print(f"Word: {' '.join(blank_list)}")
        guess = input("Make a guess or type 'hint' for a hint: ").lower()

        if guess == "hint" and not hints_used:
            for i, letter in enumerate(chosen_word):
                if blank_list[i] == '_':
                    blank_list[i] = letter
                    hints_used = True
                    break
        elif len(guess) == 1 and guess in chosen_word:
            for i, letter in enumerate(chosen_word):
                if letter == guess:
                    blank_list[i] = letter
        else:
            attempts += 1
            print(f"Wrong guess! Attempts left: {max_attempts - attempts}")

        if "_" not in blank_list:
            print("YOU WIN!")
            update_scores(conn, c, user, max_attempts - attempts)
            restart_game(conn, c, user)
            return

    print(HANGMANPICS[-1])
    print(f"GAME OVER. The word was: {''.join(chosen_word)}")
    restart_game(conn, c, user)


HANGMANPICS = ['''
  +---+
  |   |
      |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========''']


easy_words = ["cat", "dog", "fish", "tree", "bird", "ball", "bag", "home", "light", "word", "watch"]
medium_words = ["python", "mountain", "flower", "castle", "planet", "animal", "shift", "google", "laptop"]
hard_words = ["astronaut", "philosophy", "hangman", "amphibious", "transcendent", "processor", "codetantra"]


if __name__ == "__main__":
    conn, c = connect_db()

    print("Welcome to Hangman!")
    logged_in_user = None
    while not logged_in_user:
        choice = input("Do you want to (1) Sign Up or (2) Log In? Enter 1 or 2: ")
        if choice == "1":
            logged_in_user = signup(conn, c)
        elif choice == "2":
            logged_in_user = login(conn, c)
        else:
            print("Invalid input. Please enter 1 or 2.")

    start_game(conn, c, logged_in_user)
    conn.close()
