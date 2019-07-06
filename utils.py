VOWELS = 'aeiouy'

def syllable_counter(word):
    """ Takes in a word and returns the number of syllables in the word """
    letters = [c for c in list(word.lower()) if c.isalpha()]

    if len(letters) == 0:
        return 0

    if len(letters) in [1, 2]:
        return 1

    num_syllables = 0
    last_syllable_pos = 0
    for i, letter in enumerate(letters):
        if letter not in VOWELS:
            if i and letters[i - 1] in VOWELS:
                num_syllables += 1
                last_syllable_pos = i
                syllable = ''
        elif i == len(letters) - 1:
            if letter != 'e':
                num_syllables += 1
            elif i - last_syllable_pos >= 2:
                num_syllables += 1

    return num_syllables or 1
