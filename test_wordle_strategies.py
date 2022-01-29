from statistics import mean
from wordle_functions import *
from disable_printing import *

def test_wordle_strategies():
    # Count word frequencies.
    sol_words = load_word_list(SOLUTION_FILE)
    letter_counts = count_letter_frequencies(sol_words)

    strategies = []
    strategies.append({'choose_word': 1})
    strategies.append({'choose_word': 1,
                       1: has_no_doubles})
          
    average_rounds = {}
    for (n, strategy) in enumerate(strategies):
        print(f"{'='*10} \nStrategy {n}\n{'='*10} ")
        num_rounds = []
        for (i, solution) in enumerate(sol_words):
            num_words = len(sol_words)
            if i % (num_words // 10) == 0:
                print(f"[{i+1}/{len(sol_words)}] {solution}")
            round, words, won = disable_printing(play_game)(letter_counts, strategy, solution)
            num_rounds.append(round)
        average_rounds[n] = mean(num_rounds)

    print()
    for (n, r) in average_rounds.items():
        print(f"Strategy {n}: {r:.2f} rounds")


if __name__ == "__main__":
    print("Testing")
    test_wordle_strategies()
