import pygame
pygame.mixer.init()

from tkinter import *
from dictionary_data import dictionary_data

import random, time, os, json
from PIL import Image, ImageTk

# ------------ CONSTANTS ---------------- #
THEME_COLOR = "#C5CFDC"
MYFONT = ("Bahnschrift", 14)
BUTTON_BG = "#FFA9C6"
TEXTBOX_BG = "#FFFFFB"
GUESS_BT = "#FFC145"
END_BT = "#FF6B6C"
FONT_COLOR = "#1C1C1C"
RETRY_BT = "#AEC0DA"
BUTTON_FG = "#292929"
HINT_BT = "#FDFF8B"
INSTRUCTION_BT = "#F79DFF"
SCOREBOARD_BT = "#828EDB"
MEDIUM_BT = "#DFA15E"
EASY_BT ="#AAD160"
HARD_BT ="#CD5959"
TITLE_FONT = ("Bahnschrift", 20, "bold")

def load_logo(parent, width=400, height=200):

    try:
        img = Image.open("logo.png")
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label = Label(parent, image=photo, bg=THEME_COLOR)
        label.image = photo
        return label
    except:
        return Label(parent, text="Logo Not Found", font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR)

# ------------ GLOBAL STATE TRACKER ---------------- #
MAXIMIZED_STATE = 0

# ------------ UTILITY FUNCTIONS ---------------- #
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    window.geometry(f'{width}x{height}+{x}+{y}')

def check_maximized_state(window):
    global MAXIMIZED_STATE
    if window.winfo_ismapped():
        if window.state() == 'zoomed':
            MAXIMIZED_STATE = 1
        else:
            MAXIMIZED_STATE = 0

# ------------ STACK ADT ---------------- #
class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self): return len(self.items) == 0

    def push(self, item): self.items.append(item)

    def pop(self): return self.items.pop() if not self.is_empty() else None

    def peek(self): return self.items[-1] if not self.is_empty() else None

    def size(self): return len(self.items)

# ------------ LEADERBOARD SYSTEM ---------------- #
class Scoreboard:
    FILE = "Scoreboard.json" #API
    def __init__(self):
        self.data = self.load()
    def load(self):
        if os.path.exists(self.FILE):
            try:
                return json.load(open(self.FILE, "r"))
            except:
                return {"easy": [], "medium": [], "hard": []}
        return {"easy": [], "medium": [], "hard": []}
    def save(self):
        with open(self.FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_score(self, level, score):
        if score <= 0:
            return

        if level not in self.data:
            self.data[level] = []

        self.data[level].append(score)
        self.data[level] = sorted(self.data[level], reverse=True)[:10]
        self.save()

    def get_scores(self, level):
        return self.data.get(level, [])


# ------------ SCOREBOARD UI ---------------- #
class ScoreboardUI:
    def __init__(self):
        self.window = Tk()
        self.window.title("Scoreboard")

        center_window(self.window, 500, 800)
        if MAXIMIZED_STATE == 1:
            self.window.state('zoomed')
        self.window.configure(bg=THEME_COLOR)
        load_logo(self.window).pack(pady=10)

        try:
            self.snd_button = pygame.mixer.Sound(
                "button.MP3")
        except:
            self.snd_button = None

        Label(self.window, text="Scoreboard", font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady= 0)

        button_frame = Frame(self.window, bg=THEME_COLOR)
        button_frame.pack()

        Button(button_frame, text="Easy", bg=BUTTON_BG, fg=BUTTON_FG, font=MYFONT,
               command=lambda: (self.play_button(), self.show_scores("easy"))).grid(row=0, column=0, padx=5)
        Button(button_frame, text="Medium", bg=BUTTON_BG, fg=BUTTON_FG, font=MYFONT,
               command=lambda: (self.play_button(), self.show_scores("medium"))).grid(row=0, column=1, padx=5)
        Button(button_frame, text="Hard", bg=BUTTON_BG, fg=BUTTON_FG, font=MYFONT,
               command=lambda: (self.play_button(), self.show_scores("hard"))).grid(row=0, column=2, padx=5)

        # ---- SCOREBOARD CANVAS ----
        canvas_frame = Frame(self.window, bg=THEME_COLOR)
        canvas_frame.pack(pady=20)

        self.score_canvas = Canvas(canvas_frame, width=330, height=400,
                                   bg=TEXTBOX_BG, highlightthickness=0)
        self.score_canvas.pack(side=LEFT, fill="both", expand=True)

        scrollbar = Scrollbar(canvas_frame, orient="vertical",
                              command=self.score_canvas.yview)
        scrollbar.pack(side=RIGHT, fill="y")

        self.score_canvas.configure(yscrollcommand=scrollbar.set)
        self.score_canvas.bind('<Configure>', lambda e:
        self.score_canvas.configure(scrollregion=self.score_canvas.bbox("all")))

        self.score_frame = Frame(self.score_canvas, bg=TEXTBOX_BG)
        self.score_canvas.create_window((0, 0), window=self.score_frame, anchor="nw")

        Button(self.window, text="Back to Menu", bg=RETRY_BT, fg=BUTTON_FG,
               font=MYFONT, command=lambda: (self.play_button(), self.back())).pack()

        self.Scoreboard = Scoreboard()
        self.show_scores("easy")

        self.window.mainloop()

    def play_button(self):
        if self.snd_button:
            self.snd_button.play()

    def show_scores(self, level):
        scores = self.Scoreboard.get_scores(level)
        scores = [s for s in scores if s != 0]

        for widget in self.score_frame.winfo_children():
            widget.destroy()

        Label(self.score_frame, text=f"Top Scores - {level.capitalize()}",
              font=MYFONT, bg=TEXTBOX_BG, fg=FONT_COLOR).pack(pady=5)

        if not scores:
            Label(self.score_frame, text="No scores yet.",
                  font=MYFONT, bg=TEXTBOX_BG, fg=FONT_COLOR).pack(pady=5)
            return

        for i, s in enumerate(scores, 1):
            Label(self.score_frame, text=f"{i}. {s}",
                  font=MYFONT, bg=TEXTBOX_BG, fg=FONT_COLOR).pack(anchor="w", padx=10)

    def back(self):
        check_maximized_state(self.window)
        self.window.destroy()
        MainMenu()

# ------------ LEVEL SELECTION UI ---------------- #
class LevelSelection:
    def __init__(self):
        self.window = Tk()
        self.window.title("SYGE-Select Difficulty")

        center_window(self.window, 400, 700)

        if MAXIMIZED_STATE == 1:
            self.window.state('zoomed')

        self.window.configure(bg=THEME_COLOR)
        load_logo(self.window).pack(pady=10)

        try:
            self.snd_button = pygame.mixer.Sound(
                "button.MP3")
        except:
            self.snd_button = None

        Label(self.window, text="Select Difficulty", font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady=20)

        button_width = 12
        button_height = 1

        Button(self.window, text="Easy (60s)", bg=EASY_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.select_level("easy"))).pack(pady=10)

        Button(self.window, text="Medium (45s)", bg=MEDIUM_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.select_level("medium"))).pack(pady=10)

        Button(self.window, text="Hard (30s)", bg=HARD_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.select_level("hard"))).pack(pady=10)

        Button(self.window, text="Back to Menu", bg=RETRY_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.back_to_menu())).pack(pady=20)

        self.window.mainloop()

    def play_button(self):
        if self.snd_button:
            self.snd_button.play()

    def select_level(self, level):
        check_maximized_state(self.window)
        self.window.destroy()
        Dictionary_UI(mode="guess", level=level)
        load_logo(self.window).pack(pady=10)

    def back_to_menu(self):
        check_maximized_state(self.window)
        self.window.destroy()
        MainMenu()

# ------------ GAME OVER UI ---------------- #
class GameOver:
    def __init__(self, score, high_score):
        self.window = Tk()
        self.window.title("Game Over")

        center_window(self.window, 400, 700)

        if MAXIMIZED_STATE == 1:
            self.window.state('zoomed')

        self.window.configure(bg=THEME_COLOR)
        load_logo(self.window).pack(pady=10)

        try:
            self.snd_button = pygame.mixer.Sound(
                "button.MP3")
        except:
            self.snd_button = None

        try:
            self.snd_gameover = pygame.mixer.Sound(
                "gameover.mp3")
        except:
            self.snd_gameover = None

        Label(self.window, text="Game Over", font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady=20)
        Label(self.window, text=f"Your Score: {score}", font=MYFONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady=10)
        Label(self.window, text=f"High Score: {high_score}", font=MYFONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady=10)

        if score <= high_score and self.snd_gameover:
            self.snd_gameover.play()

        Button(self.window, text="Back to Menu", bg=RETRY_BT, font=MYFONT, fg=BUTTON_FG,
               command=lambda: (self.play_button(), self.back())).pack(pady=20)

        self.window.mainloop()

    def play_button(self):
        if self.snd_button:
            self.snd_button.play()

    def back(self):
        check_maximized_state(self.window)
        self.window.destroy()
        MainMenu()


# ------------ INFO POPUP WINDOW ---------------- #
class InfoPopup:
    def __init__(self, parent_window, snd_button):
        self.parent_window = parent_window
        self.snd_button = snd_button
        self.window = Toplevel(self.parent_window)
        self.window.title("Game Information")

        center_window(self.window, 400, 500)
        self.window.configure(bg=THEME_COLOR)
        self.window.grab_set()

        Label(self.window, text="SYGE's VocabVentures Info💡", font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(
            pady=10)

        info_text = (
            "This is a vocabulary game to test your knowledge of words.\n\n"
            "FUNCTIONS:\n\n"
            "• DICTIONARY: Look up definitions or terms for any word in the list.\n\n"
            "• PLAY GAME: Guess the word based on the definition given.\n\n"
            "   - Goal: Guess as many words as possible before the timer runs out.\n\n"
            "   - Difficulty: Select Easy (60s), Medium (45s), or Hard (30s).\n\n"
            "   - Hints: You get hints per level (First hint reveals the first letter).\n\n"
            "• SCOREBOARD: See the top 10 scores for each difficulty level."
            "\n\n"
            "\n\nENJOY!"
        )

        canvas_frame = Frame(self.window, bg=THEME_COLOR)
        canvas_frame.pack(pady=10)

        self.info_canvas = Canvas(canvas_frame, width=360, height=350,
                                  bg=TEXTBOX_BG, highlightthickness=0)
        self.info_canvas.pack(side=LEFT, fill="both", expand=True)

        scrollbar = Scrollbar(canvas_frame, orient="vertical",
                              command=self.info_canvas.yview)
        scrollbar.pack(side=RIGHT, fill="y")

        self.info_canvas.configure(yscrollcommand=scrollbar.set)
        self.info_canvas.bind('<Configure>', lambda e:
        self.info_canvas.configure(scrollregion=self.info_canvas.bbox("all")))

        self.info_frame = Frame(self.info_canvas, bg=TEXTBOX_BG)
        self.info_canvas.create_window((0, 0), window=self.info_frame, anchor="nw")

        Label(self.info_frame, text=info_text, font=("Bahnschrift", 12),
              bg=TEXTBOX_BG, fg=FONT_COLOR, justify=LEFT,
              wraplength=330, padx=10, pady=10).pack()

        Button(self.window, text="Close", bg=RETRY_BT, font=MYFONT, fg=BUTTON_FG,
               command=lambda: (self.play_button(), self.window.destroy())).pack(pady=20)

    def play_button(self):
        if self.snd_button:
            self.snd_button.play()

# ------------ MAIN MENU UI ---------------- #
class MainMenu:
    def __init__(self):
        self.window = Tk()
        self.window.title("SYGE VocabVentures - Main Menu")

        center_window(self.window, 400, 700)

        global MAXIMIZED_STATE
        if MAXIMIZED_STATE == 1:
            self.window.state('zoomed')

        self.window.configure(bg=THEME_COLOR)
        try:
            self.snd_button = pygame.mixer.Sound(
                "button.MP3")
        except:
            self.snd_button = None

        try:
            self.logo_image = Image.open("logo.png")
            self.logo_image = self.logo_image.resize((400, 200), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            Label(self.window, image=self.logo_photo, bg=THEME_COLOR).pack(pady=20)
        except:
            Label(self.window, text="Logo Not Found", font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady=20)

        button_width = 10
        button_height = 1

        Button(self.window, text="Play Game", bg=GUESS_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.open_guess_game())).pack(pady=10)

        Button(self.window, text="Dictionary", bg=BUTTON_BG, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.open_dictionary())).pack(pady=10)

        Button(self.window, text="Scoreboard", bg=SCOREBOARD_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.open_Scoreboard())).pack(pady=10)

        Button(self.window, text="Instruction", bg=INSTRUCTION_BT, font=MYFONT, fg=BUTTON_FG,
               width=button_width, height=button_height,
               command=lambda: (self.play_button(), self.open_info())).pack(pady=10)

        self.window.mainloop()

    def play_button(self):
        if self.snd_button:
            self.snd_button.play()

    def play_gameover(self):
        if self.snd_gameover:
            self.snd_gameover.play()

    def open_info(self):
        InfoPopup(self.window, self.snd_button)

    def open_dictionary(self):
        check_maximized_state(self.window)
        self.window.destroy()
        Dictionary_UI(mode="dictionary")

    def open_guess_game(self):
        check_maximized_state(self.window)
        self.window.destroy()
        LevelSelection()

    def open_Scoreboard(self):
        check_maximized_state(self.window)
        self.window.destroy()
        ScoreboardUI()

# ------------ MAIN UI ---------------- #
class Dictionary_UI:
    def load_sounds(self):
        try:
            self.snd_gameover = pygame.mixer.Sound("gameover.mp3")

        except:
            self.snd_gameover = None
        try:
            self.snd_button = pygame.mixer.Sound(
                "button.MP3")
        except:
            self.snd_button = None
        try:
            self.snd_correct = pygame.mixer.Sound(
                "correct!.MP3")
        except:
            self.snd_correct = None
        try:
            self.snd_wrong = pygame.mixer.Sound(
                "wrong.MP3")
        except:
            self.snd_wrong = None
        try:
            self.snd_highscore = pygame.mixer.Sound(
                "wow.MP3")
        except:
            self.snd_highscore = None
        try:
            pygame.mixer.music.load("background music.MP3")
            pygame.mixer.music.play(-1)
        except:
            pass

    def play_button(self):
        if self.snd_button: self.snd_button.play()
    def play_gameover(self):
        if self.snd_gameover: self.snd_gameover.play()
    def play_correct(self):
        if self.snd_correct: self.snd_correct.play()
    def play_wrong(self):
        if self.snd_wrong: self.snd_wrong.play()
    def play_highscore(self):
        if self.snd_highscore: self.snd_highscore.play()
    def __init__(self, mode, level=None):
        self.dictionary_data = dictionary_data
        self.score = 0
        self.game_mode = (mode == "guess")
        self.level = level
        self.time_limit = {"easy": 60, "medium": 45, "hard": 30}.get(level, 30)
        self.remaining_time = self.time_limit
        self.timer_running = False
        self.after_id = None
        self.current_word = None
        self.initial_start = True

        if self.level == "easy":
            self.hints_to_show = [1, 2, 3, 4, 5]
        elif self.level == "medium":
            self.hints_to_show = [1, 2, 3]
        else:
            self.hints_to_show = [1]

        self.hint_count = len(self.hints_to_show)

        self.available_words = list(self.dictionary_data.keys())
        random.shuffle(self.available_words)

        self.load_sounds()

        self.window = Tk()
        self.window.title("SYGE-Dictionary")

        window_width = 400
        window_height = 700
        center_window(self.window, window_width, window_height)

        if MAXIMIZED_STATE == 1:
            self.window.state('zoomed')

        self.window.configure(bg=THEME_COLOR)

        title = "Dictionary Game" if self.game_mode else "Dictionary"
        Label(self.window, text=title, font=TITLE_FONT, bg=THEME_COLOR, fg=FONT_COLOR).pack(pady=15)

        input_frame = Frame(self.window, bg=THEME_COLOR)
        input_frame.pack(pady=5)

        self.entry_word = Entry(input_frame, font=MYFONT, bg=TEXTBOX_BG)
        self.entry_word.pack(side=LEFT, padx=13)

        button_text = "Guess" if self.game_mode else "Search"
        self.action_button = Button(input_frame, text=button_text, bg=BUTTON_BG, font=MYFONT, fg=BUTTON_FG,
                                    command=lambda: (self.play_button(), self.search_or_guess()))
        self.action_button.pack(side=LEFT, padx=10)

        if self.game_mode:
            self.timer_label = Label(
                self.window,
                text=f"Time: {self.remaining_time}",
                font=MYFONT,
                bg=THEME_COLOR,
                fg=FONT_COLOR
            )

            self.timer_label.place(relx=0.1, rely=0.20, anchor='w')

            Button(self.window, text="Retry", bg=GUESS_BT, font=MYFONT, fg=BUTTON_FG,
                   command=lambda: (self.play_button(), self.retry_game())).pack(pady=5)

        self.entry_definition = Text(self.window, width=30, height=10, bg=TEXTBOX_BG, font=MYFONT)
        self.entry_definition.pack(pady=10)
        self.entry_definition.config(state=DISABLED)
        self.label_result = Label(self.window, text="", font=MYFONT, bg=THEME_COLOR, fg=FONT_COLOR)
        self.label_result.pack(pady=10, padx=20)

        if self.game_mode:
            self.label_score = Label(self.window, text="Score: 0", font=MYFONT, bg=THEME_COLOR, fg=FONT_COLOR)
            self.label_score.pack(pady=5)
            self.hint_label = Label(self.window, text="Hints: ", font=MYFONT, bg=THEME_COLOR, fg=FONT_COLOR)
            self.hint_label.pack(pady=5)
            Button(self.window, text="Hint", bg=HINT_BT, font=MYFONT, fg=BUTTON_FG,
                   command=lambda: (self.play_button(), self.use_hint())).pack(pady=5)
            bottom_frame = Frame(self.window, bg=THEME_COLOR)
            bottom_frame.pack(pady=10)
            Button(bottom_frame, text="End Game", bg=END_BT, font=MYFONT, fg=BUTTON_FG,
                   command=lambda: (self.play_button(), self.end_game())).pack(side=LEFT, padx=5)
            Button(bottom_frame, text="Back to Menu", bg=RETRY_BT, font=MYFONT, fg=BUTTON_FG,
                   command=lambda: (self.play_button(), self.back_to_menu())).pack(side=LEFT, padx=5)
        else:
            Button(self.window, text="Back to Menu", bg=RETRY_BT, font=MYFONT, fg=BUTTON_FG,
                   command=lambda: (self.play_button(), self.back_to_menu())).pack(pady=10)

        if self.game_mode:
            self.start_game()

        self.window.mainloop()

    # ------------------ GAME FUNCTIONS ------------------ #
    def start_ready_set_go(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        self.action_button.config(state=DISABLED)
        self.entry_word.config(state=DISABLED)

        self.label_result.config(text="Ready...", fg="blue")
        self.window.after(900, lambda: self.label_result.config(text="Set...", fg="orange"))

        def go():
            self.label_result.config(text="Go!", fg="green")
            self.window.after(500, lambda: self.label_result.config(text="Guess the word", fg="purple"))
            self.timer_running = True
            if self.initial_start:
                self.update_timer()
            self.action_button.config(state=NORMAL)
            self.entry_word.config(state=NORMAL)
            self.next_word()

        self.window.after(2000, go)

    def start_game(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        if self.initial_start:
            self.score = 0
            self.hint_count = len(self.hints_to_show)
            if hasattr(self, "label_score"):
                self.label_score.config(text="Score: 0")

            self.remaining_time = self.time_limit
            self.timer_running = False
            self.start_ready_set_go()
            self.initial_start = False

    def retry_game(self):
        if self.timer_running and self.remaining_time > 0:
            self.score = 0
            self.hint_count = len(self.hints_to_show)
            self.label_score.config(text="Score: 0")
            self.hint_label.config(text="Hints: ")
            self.label_result.config(text="Guess the word", fg="purple")
            self.action_button.config(state=NORMAL)
            self.entry_word.config(state=NORMAL)
            self.entry_word.delete(0, END)
            self.next_word()
        else:
            self.initial_start = True
            self.start_game()
    def start_game(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        self.score = 0
        self.hint_count = 3
        if hasattr(self, "label_score"):
            self.label_score.config(text="Score: 0")
        self.remaining_time = self.time_limit
        self.timer_running = False
        self.start_ready_set_go()

    def update_timer(self):
        if self.timer_running and self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Time: {self.remaining_time}")
            self.after_id = self.window.after(1000, self.update_timer)
        elif self.remaining_time == 0:
            self.timer_running = False
            self.end_game()

    def next_word(self):
        if not self.available_words:
            self.available_words = list(self.dictionary_data.keys())
            random.shuffle(self.available_words)
        self.current_word = self.available_words.pop()

        self.entry_definition.config(state=NORMAL)
        self.entry_definition.delete(1.0, END)

        self.entry_word.delete(0, END)
        self.label_result.config(text="")

        definition = self.dictionary_data[self.current_word].strip()
        self.entry_definition.insert(END, definition)

        self.entry_definition.config(state=DISABLED)

        self.hint_label.config(text="Hints: ")
        self.hint_count = len(self.hints_to_show)

    def search_or_guess(self):
        if self.game_mode:
            self.guess_word()
        else:
            self.get_definition()

    def get_definition(self):
        word = self.entry_word.get().strip().lower()

        if word == "":
            self.label_result.config(text="Please enter a word.", fg="red")
            return

        mapping = {k.lower().strip(): k.strip() for k in self.dictionary_data}

        self.entry_definition.config(state=NORMAL)
        self.entry_definition.delete(1.0, END)

        if word in mapping:
            real = mapping[word]
            self.entry_definition.insert(END, self.dictionary_data[real].strip())
            self.label_result.config(text="", fg="black")
        else:
            self.entry_definition.insert(END, "Word not found.")
            self.label_result.config(text="Word not found.", fg="red")

        self.entry_definition.config(state=DISABLED)

    def guess_word(self):
        guess = self.entry_word.get().strip().lower()

        if guess == "":
            self.label_result.config(text="Please enter a word first.", fg="red")
            return

        self.entry_word.delete(0, END)

        correct_word = self.current_word.strip()
        correct_word_lower = correct_word.lower()

        if guess == correct_word_lower:
            self.play_correct()
            self.score += 1
            self.label_score.config(text=f"Score: {self.score}")
            self.label_result.config(text="Correct!", fg="green")

            self.window.after(500, self.next_word)
            return

        self.play_wrong()
        self.label_result.config(text=f"Wrong! Correct was: {correct_word}", fg="red")

        self.entry_definition.config(state=NORMAL)
        self.entry_definition.delete(1.0, END)
        self.entry_definition.insert(END, self.dictionary_data[correct_word].strip())
        self.entry_definition.config(state=DISABLED)

        self.window.after(1005, self.next_word)

    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            self.hint_count = 5
            self.hints_to_show = [1, 2, 3, 4, 5]
        elif difficulty == "medium":
            self.hint_count = 3
            self.hints_to_show = [1, 2, 3]
        elif difficulty == "hard":
            self.hint_count = 1
            self.hints_to_show = [1]

    def use_hint(self):
        if self.hint_count > 0 and self.current_word:
            current_word_stripped = self.current_word.strip()

            hint_index = len(self.hints_to_show) - self.hint_count
            hint_type = self.hints_to_show[hint_index]

            new_hint = ""

            if hint_type == 1:
                new_hint = f"Starts with {current_word_stripped[0].upper()}"
            elif hint_type == 2:
                new_hint = f"Length is {len(current_word_stripped)} characters"
            elif hint_type == 3:
                new_hint = f"Ends with {current_word_stripped[-1].lower()}"
            elif hint_type == 4:
                vowels = sum(1 for char in current_word_stripped if char.lower() in 'aeiou')
                new_hint = f"Has {vowels} vowels"
            elif hint_type == 5:
                new_hint = f"First two letters: {current_word_stripped[:2].upper()}"

            self.hint_label.config(text=f"Hints: {new_hint}")
            self.hint_count -= 1

        elif self.current_word:
            self.hint_label.config(text="No hints left.")
        else:
            self.hint_label.config(text="Start the game first.")

    def end_game(self):
        self.timer_running = False
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        lb = Scoreboard()
        lb.add_score(self.level, self.score)
        high = self.load_high_score()
        if self.score > high:
            self.save_high_score(self.score)
            self.play_highscore()

        check_maximized_state(self.window)
        self.window.destroy()
        GameOver(self.score, max(self.score, high))

    def back_to_menu(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        check_maximized_state(self.window)
        self.window.destroy()
        MainMenu()

    # ------------------ SAVE SYSTEM ------------------ #
    def load_high_score(self):
        if os.path.exists("high_score.txt"):
            try:
                return int(open("high_score.txt", "r").read())
            except:
                return 0
        return 0

    def save_high_score(self, score):
        open("high_score.txt", "w").write(str(score))

# ------------ START PROGRAM ------------ #
if __name__ == "__main__":
    MainMenu()

