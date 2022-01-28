from wordle_functions import *


def solve_wordle():
    # Count word frequencies.
    sol_words = load_word_list(SOLUTION_FILE)
    letter_counts = count_letter_frequencies(sol_words)

    play_game(letter_counts)


if __name__ == "__main__":
    solve_wordle()
