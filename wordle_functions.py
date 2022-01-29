import string
import csv


SOLUTION_FILE = "solutions.csv"
DICTIONARY_FILE = "dictionary.csv"

# Additional filters for searching.


def has_no_doubles(w): return len(set(w)) == len(w)


def nothing_in_common_with(diff_word): 
    return lambda w: all([c not in diff_word for c in w])


# Applies a list of filter functions to a list of words.
def filter_word_list(filters, word_list):
    for f in filters:
        word_list = list(filter(f, word_list))

    return word_list


# Loads word list from specified filename.
def load_word_list(filename):
    with open(filename, newline='') as f:
        word_list = csv.reader(f, delimiter=',')
        word_list = next(word_list)  # Get row from filestream.
    return word_list


# Counts letter frequencies and positions in a list of words.
# Returns dict with letter and frequency at each position.
def count_letter_frequencies(word_list):
    # Set up counts for each character.
    letters = string.ascii_lowercase
    letter_counts = {char: [0, 0, 0, 0, 0] for char in letters}

    # Iterate each word and store counts.
    for word in word_list:
        for (index, char) in enumerate(word):
            letter_counts[char][index] += 1

    return letter_counts


# Returns dictionary of scores for all words in list which meet conditions.
def score_word_list(word_list, letter_counts, filters):

    def score_word(word):
        score = 0
        for (index, char) in enumerate(word):
            score += letter_counts[char][index]
        return score

    if filters:
        if callable(filters): filters = [filters]  # Handle a single passed filter function.
        scores_dict = {word: score_word(word) for word in word_list if all([f(word) for f in filters])}
    else:
        scores_dict = {word: score_word(word) for word in word_list}

    return scores_dict


# Prints top ten scores.
def get_best_words(scores_dict):
    max_n = 10
    print("Most likely words:")
    scored_words = sorted(scores_dict, key=scores_dict.get, reverse=True)

    num_words = min(max_n, len(scored_words))
    if num_words == 0:
        print("No valid words!")
    else:
        for i in range(num_words):
            print(f"#{i+1}", scored_words[i])

    print()

    return scored_words[0:num_words]


# Returns outcome (e.g. "g-y--") given a known solution and played word.
def evaluate_played_word(played_word, solution_word):

    # First, identify any green letters.
    outcome = ['g' if played_word[i] == solution_word[i] else '-' for i in range(5)]

    remaining_indices = [i for (i, c) in enumerate(outcome) if c == '-']

    # No more 'char's should be yellow/green than are present in solution.
    # This list contains remaining characters from solution that can be coloured yellow in outcome.
    uncoloured_chars = [solution_word[i] for i in remaining_indices]

    # Next, iterate remaining characters and determine if they should be yellow.
    for i in remaining_indices:
        if played_word[i] in uncoloured_chars:
            # Char in solution, and can still place a yellow for this char.
            outcome[i] = 'y'
            uncoloured_chars.remove(played_word[i])

        else:
            # Either char is not in solution, or we have already placed a yellow/green for every instance in solution.
            outcome[i] = '-'

    return ''.join(outcome)



# Plays through game of Wordle, scoring words with letter_counts dict.
# If solution word is known, can automatically evaluate words.
def play_game(letter_counts, strategy={}, solution_word=None):
    # Play up to 6 rounds.
    num_rounds = 6

    all_words = load_word_list(SOLUTION_FILE) + load_word_list(DICTIONARY_FILE)
    remaining_words = all_words.copy()
    played_words = []

    filters = []
    
    round = 0
    game_won = None  # state = None if game still in progress.
    while game_won is None:
        round += 1
        print(f"\n{'-'*10}[{round}/{num_rounds}]{'-'*10}")

        # Suggest best words for this round, applying strategy if present.
        strategy_filters = {}  # Filters for this round only, does not edit remaining words list.
        if round in strategy.keys():
            strategy_filters = strategy[round]
        scores_dict = score_word_list(remaining_words, letter_counts, strategy_filters)
        best_words = get_best_words(scores_dict)

        # Win / Lose conditions.
        if len(best_words) == 1:  # Auto-win if one valid word remains.
            game_won = True
            [final_word] = best_words
            played_words.append(final_word)
        elif len(best_words) == 0 or round > num_rounds:
            game_won = False

        if game_won is None:  # Game still in progress!
            # Retrieve played word (typed, or number from previous best words list).
            played_word = ''

            if 'choose_word' in strategy:
                # Pre-defined pick.
                played_word = str(strategy['choose_word'])
            else:
                # User input pick.
                def isvalid(w): return (w in all_words) or (
                    w.isnumeric() and int(w) <= len(best_words))
                while not isvalid(played_word):
                    played_word = input("What word was played?\t")


            # Handle numerical selection.
            if played_word.isnumeric():
                index = int(played_word) - 1
                played_word = best_words[index]
                print(f"({played_word})")
            
            played_words.append(played_word)

            # Evaluate played word
            if played_word == solution_word:
                #  Win game immediately if guess is correct.
                game_won = True
            else:
                outcome = ''
                if solution_word: 
                    outcome = evaluate_played_word(played_word, solution_word)
                    print("Result:\t" + outcome)
                else:
                    def isvalid(w): return len(w) == 5 and all(
                        [c.lower() in "gy-" for c in w])

                    while not isvalid(outcome):
                        outcome = input(
                            "What was the outcome? ('g' = green, 'y' = yellow, '-' = none)\t")

                # Parse outcome and create filters for next round.
                filters = []
                for (i, char) in enumerate(outcome):
                    match char.lower():
                        case 'g':  # Green
                            def new_filter(w, p=played_word, i=i):
                                return w[i] == p[i]

                        case 'y':  # Yellow
                            def new_filter(w, p=played_word, i=i):
                                return p[i] in w and w[i] != p[i]

                        case '-':  # None
                            def new_filter(w, p=played_word, i=i):
                                if p.count(p[i]) == 1:
                                    # Single occurence of char in played word - char not in word anywhere.
                                    return p[i] not in w
                                else:
                                    char_indices = [i for (i, c) in enumerate(p) if p[i] == c]
                                    char_outcomes = [outcome[i] for i in char_indices]

                                    # If the duplicate letter is always 'none', it is not present anywhere in the word.
                                    if all([c == '-' for c in char_outcomes]):
                                        return p[i] not in w

                                    # If the duplicate letter is not always 'none', we know is this letter is not at this location (but green or yellow elsewhere).
                                    else:
                                        return w[i] != p[i]

                    filters.append(new_filter)

                remaining_words = filter_word_list(filters, remaining_words)

        if game_won is not None:  # Game over!
            if game_won:
                print("You've wordled it!")
            else:
                print("You've completely wordled it up. Try again.")
            return (round, played_words, game_won)

