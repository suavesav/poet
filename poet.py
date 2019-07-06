import nltk
import re
import random
import sys

from nltk.tokenize.treebank import TreebankWordDetokenizer

from utils import syllable_counter

class Poet:
    def __init__(self, context):
        """
        context -- context to be parsed and used for context 
                   (can be raw or nltk.Text)
        """
        self.context = context
        self.syllable_dict = {}
        self.last_seen_word = None
        self._prepare_for_poet()

    def _prepare_for_poet(self):
        """ Tokenize, get rid of punctuation, lowercase-ify """
        TOKENIZE_PATTERN = re.compile(r"[a-zA-Z]+-?'?[a-zA-Z]*")

        text = self.context
        if isinstance(self.context, nltk.Text):
            # detokenize if nltk text passed in
            twd = TreebankWordDetokenizer()
            text = twd.detokenize(self.context)
            # text = ' '.join(list(twd.detokenize(self.context)))

        self.tokens = [w.lower() for w in TOKENIZE_PATTERN.findall(text)]
        self.text = nltk.Text(self.tokens)

    def _validate_input(self, stanza_data, meter):
        STANZA_DATA_TYPE_ERROR = 'stanza_data should be an iterator containing lines_per_stanza, words_per_line'
        METER_TYPE_ERROR = 'meter should be an iterator of syllable counts specifying the meter of the stanza'

        assert (stanza_data or meter) and (not(stanza_data and meter)), \
                'Must have either meter or stanza_data'
        if stanza_data:
            try:
                iterable = iter(stanza_data)
            except TypeError:
                raise TypeError(STANZA_DATA_TYPE_ERROR)
            else:
                assert len(stanza_data) == 2, STANZA_DATA_TYPE_ERROR
        if meter:
            try:
                iterable = iter(meter)
            except TypeError:
                raise TypeError(METER_TYPE_ERROR)
            else:
                assert all(i >= 4 for i in meter), 'All lines must have 4 or more syllables'

    def contextual_poet(self, stanza_data=None, meter=None, num_stanzas=1):
        """ Given some raw text, create a poem based on word contexts in the text.
        Arguments:
        stanza_data -- tuple of form (<lines_per_stanza>, <words_per_line>)
        meter -- list of syllable counts specifying the meter of the stanza
            e.g. [5,7,5] for a haiku
        num_stanzas -- the number of stanzas in the poem
        """
        self._validate_input(stanza_data, meter)
        self.poem = []
        while num_stanzas:
            self.stanza_generator(stanza_data, meter)
            self.poem.append('')
            num_stanzas -= 1
        self.print_poem()

    def stanza_generator(self, stanza_data=None, meter=None):
        if stanza_data:
            lines_per_stanza, words_per_line = stanza_data
            while len(self.poem) < lines_per_stanza:
                line = self.line_generator(words_per_line=words_per_line)
                self.poem.append(line)

        elif meter:
            for syllable_count in meter:
                line = self.line_generator(syllables_per_line=syllable_count)
                self.poem.append(line)

    def line_generator(self, words_per_line=None, syllables_per_line=None):
        """ Generate a line of the poem based on the text
        Arguments:
        words_per_line -- the number of words per line
        syllables_per_line -- the number of syllables in this line
        """
        assert words_per_line or syllables_per_line

        if self.last_seen_word is None:
            self.last_seen_word = self.pick_starting_word()
            line = [self.last_seen_word]
        else:
            line = []

        if words_per_line:
            while len(line) < words_per_line:
                self.last_seen_word = self.pick_next_word()
                line.append(self.last_seen_word)

        elif syllables_per_line:
            num_syllables = 0
            while num_syllables < syllables_per_line:
                self.last_seen_word = self.pick_next_word_by_syllables(
                    syllables_per_line - num_syllables)
                line.append(self.last_seen_word)
                num_syllables += self.syllable_dict[self.last_seen_word]

        return ' '.join(line)

    def pick_starting_word(self):
        """ Get a random word from the text """
        loc = random.randint(0, len(self.tokens) - 1)
        return self.tokens[loc]
    
    def pick_next_word(self):
        concordances = self.text.concordance_list(self.last_seen_word)
        loc = random.randint(0, len(concordances) - 1)
        word = concordances[loc].right[0]
        return word

    def pick_next_word_by_syllables(self, max_syllables):
        concordances = self.text.concordance_list(self.last_seen_word)
        possible_next_words = [c.right[0] for c in concordances]
        unseen_words = set(possible_next_words) - set(self.syllable_dict.keys())
        for w in unseen_words:
            self.syllable_dict[w] = syllable_counter(w) 

        word_syllable_count = sys.maxint
        while word_syllable_count > max_syllables:
            loc = random.randint(0, len(possible_next_words) - 1)
            word = possible_next_words[loc]
            word_syllable_count = self.syllable_dict[word]
        return word

    def print_poem(self):
        """ Prints the poem """
        for line in self.poem:
            print line

# eventually want to get get context from POS-tagger
# eventually want to get punctuation from ngram too
# eventually want to get capitalization from original text
# cadence, line length, rhyme scheme
