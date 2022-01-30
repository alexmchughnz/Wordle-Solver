from wordle_functions import *


def solve_wordle():
    # Count word frequencies.
    solution_list = load_word_list(SOLUTION_FILE)
    letter_counts = count_letter_frequencies(solution_list)

    strategy = {
        'choose_word': 1,
        1: {'filters': has_no_doubles},
        2: {'filters': [has_no_doubles, shares_yellows_with_previous],
            'words': 'all'}
    }

    play_game(letter_counts, strategy)


if __name__ == "__main__":
    solve_wordle()
