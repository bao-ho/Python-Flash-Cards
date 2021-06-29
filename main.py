import pandas
import tkinter
from tkinter import messagebox
import random
import gtts
import os

#---------------- CONSTANTS --------------------------------------------------#
BG = "#AAAAAA"
WIDTH = 800
HEIGHT = 526
FONT = "Arial"
DELAY = 3000  # miliseconds
FRONT_TEXT_COLOR = "#394867"
BACK_TEXT_COLOR = "#F1F6F9"
LEARNING_WINDOW = 9
REPETITION = 3
DATABASE = "Swedish_10.csv"
PROGRESS = "Swedish_10_progress.csv"
INSTRUCTION = """Press ✅ if you remember the word, ❌ if you do not
\n\nHot keys: s (sound), space (flip), right (✅), left (❌), escape (quit)"""

#---------------- GLOBAL VARIABLES -------------------------------------------#
is_startup = True
current_word_index = None
current_word = None
sound_on = True
card_front = True

#---------------- CALLBACK FUNCTIONS -----------------------------------------#


def pick_new_word(is_last_word_passed):
    global current_word_index, current_word, card_front
    card_front = True
    if is_last_word_passed:
        passes_list[current_word_index] += 1

    # Pick a word among the first LEARNING_WINDOW words that have not been 
    # checked (passed) REPETITION times.
    word_indicis = []
    for i in range(len(swedish_list)):
        if passes_list[i] < REPETITION:
            word_indicis.append(i)
        if len(word_indicis) > LEARNING_WINDOW:
            break

    # Corner case: the user has learnt all the words
    if len(word_indicis) <= LEARNING_WINDOW:
        messagebox.showinfo(title="Great job!", messagebox="You have learnt them all!")
        return    
    index = random.randint(0, LEARNING_WINDOW)
    current_word_index = word_indicis[index]
    current_word = swedish_list[current_word_index]
    show_front_card(current_word)


def on_key_press(event):
    if event.keysym == 'Right':
        pick_new_word(is_last_word_passed=True)
    elif event.keysym == 'Left':
        pick_new_word(is_last_word_passed=False)
    elif event.keysym == 'Escape':
        save_and_quit()
    elif event.keysym == 'space':
        flip_card(current_word)
    elif event.keysym == 's':
        flip_sound_status()

#---------------- NORMAL FUNCTIONS ------------#


def show_front_card(word):
    canvas.itemconfig(canvas_image, image=front_image)
    canvas.itemconfig(canvas_language, text="Swedish", fill=FRONT_TEXT_COLOR)
    grammar = "" if word['Grammar'] == "" else f"{word['Grammar']} "
    swedish_word = f"{grammar}{word['Swedish']}"
    canvas.itemconfig(canvas_word, text=swedish_word, fill=FRONT_TEXT_COLOR)
    pronounce(swedish_word, "sv")
    global is_startup
    if is_startup:
        canvas.itemconfig(subtitles, text=INSTRUCTION)
        is_startup = False
    else:
        example = "" if word['Examples'] == "" else f", {word['Examples']}"
        item = f"{word['Type']}{example}"
        canvas.itemconfig(subtitles, text=item)


def show_back_card(word):
    canvas.itemconfig(canvas_image, image=back_image)
    canvas.itemconfig(canvas_language, text="English", fill=BACK_TEXT_COLOR)
    english_word = word["English"]
    if word["Grammar"] == "en" or word["Grammar"] == "ett":
        if english_word[0] in ["a", "e", "i", "o", "u"]:
            english_word = f'an {english_word}'
        else:
            english_word = f'a {english_word}'
    elif word["Grammar"] == "att":
        english_word = f'to {english_word}'
    canvas.itemconfig(canvas_word, text=english_word, fill=BACK_TEXT_COLOR)
    canvas.itemconfig(subtitles, text="")
    pronounce(english_word, "en")


def flip_card(word):
    global card_front
    card_front = not card_front
    if card_front:
        show_front_card(word)
    else:
        show_back_card(word)


def flip_sound_status():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        sound_button.config(image=sound_on_image)
    else:
        sound_button.config(image=sound_off_image)


def pronounce(word, lang):
    if sound_on and not is_startup:
        window.after(100, load_and_play, word, lang)


def load_and_play(word, lang):
    audio_output = gtts.gTTS(text=word, lang=lang)
    audio_output.save("sound.mp3")
    os.system("afplay sound.mp3")


def read_progress():
    try:
        progress_df = pandas.read_csv(PROGRESS)
    except FileNotFoundError:
        list = [0 for i in range(0, len(data_frame))]
        progress_df = pandas.DataFrame({"passes": list})
        progress_df.to_csv(PROGRESS, index=False)
    return progress_df["passes"].to_list()


def update_progress():
    progress_df = pandas.DataFrame({"passes": passes_list})
    progress_df.to_csv(PROGRESS, index=False)


def save_and_quit():
    # Prompt user for confirmation
    choice = messagebox.askyesnocancel(
        title="Goodbye", message="Update your progress from this session?")
    if choice is True:
        update_progress()
        window.destroy()
    elif choice is False:
        window.destroy()


#---------------- READ DATA --------------------------------------------------#
data_frame = pandas.read_csv(DATABASE, na_filter=False)
swedish_list = data_frame.to_dict(orient="records")
passes_list = read_progress()

#---------------- UI --------------------------#
window = tkinter.Tk()
window.title("Flash card game")
window.config(width=900, height=726, padx=50, pady=50, background=BG)

canvas = tkinter.Canvas()
canvas.config(width=WIDTH, height=HEIGHT,
              background=BG, highlightthickness=0)
canvas.grid(column=0, row=0, columnspan=4)
front_image = tkinter.PhotoImage(file="images/card_front.png")
back_image = tkinter.PhotoImage(file="images/card_back.png")
canvas_image = canvas.create_image(WIDTH/2, HEIGHT/2)
canvas_language = canvas.create_text(
    WIDTH/2, HEIGHT/3, font=(FONT, 40, "italic"))
canvas_word = canvas.create_text(WIDTH/2, HEIGHT/2, font=(FONT, 60, "bold"))
subtitles = canvas.create_text(
    WIDTH/2, HEIGHT*3/4, font=(FONT, 20, "normal"), fill=FRONT_TEXT_COLOR, justify='center')

wrong_image = tkinter.PhotoImage(file="images/wrong.png")
wrong_button = tkinter.Button(image=wrong_image)
wrong_button.config(highlightthickness=0,
                    command=lambda: pick_new_word(is_last_word_passed=False))
wrong_button.grid(column=2, row=1)

right_image = tkinter.PhotoImage(file="images/right.png")
right_button = tkinter.Button(image=right_image)
right_button.config(highlightthickness=0,
                    command=lambda: pick_new_word(is_last_word_passed=True))
right_button.grid(column=3, row=1)

flip_image = tkinter.PhotoImage(file="images/flip.png")
flip_button = tkinter.Button(image=flip_image)
flip_button.config(highlightthickness=0,
                   command=lambda: flip_card(current_word))
flip_button.grid(column=1, row=1)

sound_on_image = tkinter.PhotoImage(file="images/sound_on.png")
sound_off_image = tkinter.PhotoImage(file="images/sound_off.png")
sound_button = tkinter.Button(image=sound_on_image)
sound_button.config(highlightthickness=0, command=lambda: flip_sound_status())
sound_button.grid(column=0, row=1)

# Show the first word and instructions
pick_new_word(is_last_word_passed=False)

window.bind('<KeyPress>', on_key_press)
window.protocol("WM_DELETE_WINDOW", save_and_quit)
window.mainloop()
