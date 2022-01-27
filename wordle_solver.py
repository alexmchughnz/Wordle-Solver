import string
import csv

CHEAT = True  # If True, will only suggest known solution words.

solution_file = "solutions.csv"
dictionary_file = "dictionary.csv"

# Additional filters for searching.
def has_no_doubles(w): return len(set(w)) == len(w)


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

    return {word: score_word(word) for word in word_list if all([f(word) for f in filters])}


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

    return scored_words[0:num_words]


def main():
    # Count word frequencies.
    sol_words = load_word_list(solution_file)
    letter_counts = count_letter_frequencies(sol_words)

    # Find best starting word.
    if CHEAT:
        all_words = sol_words
    else:
        all_words = load_word_list(dictionary_file) + sol_words

    initial_filters = [has_no_doubles]

    scores_dict = score_word_list(all_words, letter_counts, initial_filters)
    best_words = get_best_words(scores_dict)

    # Play up to 6 rounds.
    num_rounds = 6
    remaining_words = all_words.copy()
    for round in range(1, num_rounds+1):
        print(f"\n{'-'*10}[{round}/{num_rounds}]{'-'*10}")

        # Retrieve played word (typed, or number from previous best words list).
        played_word = ''

        def isvalid(w): return (w in all_words) or (
            w.isnumeric() and int(w) <= len(best_words))
        while not isvalid(played_word):
            played_word = input("What word was played?\t")

        # Handle numerical selection.
        if played_word.isnumeric():
            index = int(played_word) - 1
            played_word = best_words[index]

        # Retrieve outcome of played word.
        outcome = ''

        def isvalid(w): return len(w) == 5 and all(
            [c.lower() in "gy-" for c in w])
        while not isvalid(outcome):
            outcome = input(
                "What was the outcome? ('g' = green, 'y' = yellow, '-' = none)\t")

        # Parse outcome and create filters for next word.
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
                            char_indices = [
                                i for (i, c) in enumerate(p) if p[i] == c]
                            char_outcomes = [outcome[i] for i in char_indices]

                            # If the duplicate letter is always 'none', it is not present anywhere in the word.
                            if all([c == '-' for c in char_outcomes]):
                                return p[i] not in w

                            # If the duplicate letter is not always 'none', we know is this letter is not at this location (but green or yellow elsewhere).
                            else:
                                return w[i] != p[i]

            filters.append(new_filter)

        # Suggest best words for next round.
        scores_dict = score_word_list(remaining_words, letter_counts, filters)
        remaining_words = scores_dict.keys()
        best_words = get_best_words(scores_dict)

        # Win / Lose conditions.
        if len(best_words) == 1:
            print("You've wordled it!")
            return
        elif len(best_words) == 0:
            print("You've completely wordled it up. Try again.")
            return


if __name__ == "__main__":
    main()
