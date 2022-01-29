from wordle_functions import *


def solve_wordle():
    # Count word frequencies.
    sol_words = load_word_list(SOLUTION_FILE)
    letter_counts = count_letter_frequencies(sol_words)

    strategy = {1: has_no_doubles}

    play_game(letter_counts, strategy)


if __name__ == "__main__":
    solve_wordle()
