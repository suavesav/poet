from __future__ import absolute_import
import nltk
import re
import random
import sys
import string

from nltk.tokenize.treebank import TreebankWordDetokenizer
# from nltk.corpus import words as worddict
from datamuse import datamuse

from .utils import syllable_counter, basic_words

class Poet(object):
    def __init__(self, context=None):
        """
        context -- context to be parsed and used for context 
                   (can be raw or nltk.Text)
        """
        self.datamuse = datamuse.Datamuse()
        self.syllable_dict = {}
        self.last_seen_word = None
        self.contextual = False

        if context:
            self.context = context
            self.contextual=True
            self._prepare_for_poet()
        print("contextual mode") if self.contextual else print("free mode")

    def toggle_contextual_mode(self):
        self.contextual = not self.contextual
        print("contextual mode") if self.contextual else print("free mode")

    def _prepare_for_poet(self):
        """ Tokenize, get rid of punctuation, lowercase-ify """
        TOKENIZE_PATTERN = re.compile(r"[a-zA-Z]+-?'?[a-zA-Z]*")
        tagged_tokens = None

        text = self.context
        if isinstance(self.context, nltk.Text):
            # detokenize if nltk text passed in
            tagged_tokens = nltk.pos_tag(self.context)
            twd = TreebankWordDetokenizer()
            text = twd.detokenize(self.context)

        self.tokens = [w.lower() for w in TOKENIZE_PATTERN.findall(text)]
        self.text = nltk.Text(self.tokens)
        if not tagged_tokens:
            tagged_tokens = nltk.pos_tag(self.tokens)

        self.tagdict = {}
        for tt in tagged_tokens:
            v,k = tt
            try:
                self.tagdict[k].add(v.lower())
            except KeyError:
                self.tagdict[k] = set([v.lower()])

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
                assert all(i >= 4 for i in meter), \
                'All lines must have 4 or more syllables'

    def compose(self, stanza_data=None, meter=None, num_stanzas=1, force_contextual=False):
        """ Given some raw text, create a poem based on word contexts in the text.
        Arguments:
        stanza_data -- tuple of form (<lines_per_stanza>, <words_per_line>)
        meter -- list of syllable counts specifying the meter of the stanza
            e.g. [5,7,5] for a haiku
        num_stanzas -- the number of stanzas in the poem
        """
        if force_contextual and self.context:
            self.contextual = True
            print("contextual mode\n\n")

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
                self.last_seen_word, word_syllables = self.pick_next_word_by_syllables(
                    syllables_per_line - num_syllables)
                line.append(self.last_seen_word)
                num_syllables += word_syllables

        return ' '.join(line)

    def pick_starting_word(self):
        """ Get a random word from the text """
        if self.contextual:
            return self.get_random_word(self.tokens)
        else:
            return self.get_random_word(basic_words())
    
    def pick_next_word(self):
        if self.contextual:
            concordances = self.text.concordance_list(self.last_seen_word)
            possible_next_words = [c.right[0] for c in concordances]
        else:
            r = self.datamuse.words(lc=self.last_seen_word, max=10)
            possible_next_words = [w['word'] for w in r if w['word'] not in string.punctuation]

        word = self.get_random_word(possible_next_words)
        return word

    def pick_next_word_by_syllables(self, max_syllables):
        if self.contextual:
            concordances = self.text.concordance_list(self.last_seen_word)
            next_words = [c.right[0] for c in concordances]
            possible_next_words = {}
            for w in next_words:
                try:
                    possible_next_words[w] = self.syllable_dict[w]
                except KeyError:
                    num_syllables = syllable_counter(w)
                    possible_next_words[w] = num_syllables
                    self.syllable_dict[w] = num_syllables
            possible_next_words = {k:v for k,v in possible_next_words.items() if v <= max_syllables}

            word = self.get_random_word(possible_next_words.keys())
            return (word, possible_next_words[word])
        else:
            possible_next_words = {}
            r = self.datamuse.words(lc=self.last_seen_word, md='s', max=20)
            for row in r:
                w = row['word']
                if w not in string.punctuation and row['numSyllables'] <= max_syllables:
                    possible_next_words[w] = row

            word = self.get_random_word(possible_next_words.keys())
            return (word, possible_next_words[word]['numSyllables'])

    def get_random_word(self, word_list):
        return random.sample(word_list, 1)[0]

    def print_poem(self):
        """ Prints the poem """
        for line in self.poem:
            print(line)

# eventually want to get get context from POS-tagger
# eventually want to get punctuation from ngram too
# eventually want to get capitalization from original text
# cadence, line length, rhyme scheme
# adj noun alliteration
