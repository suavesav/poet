from __future__ import absolute_import
import nltk
import re
import random
import sys
import string

from nltk.tokenize.treebank import TreebankWordDetokenizer
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
        """
            Tokenize, get rid of punctuation, derive sentence structures
            from the text, and save basic ones separately. Also create POS
            dict for the text.
        """
        BASIC_TOKENIZE_PATTERN = re.compile(r"[a-zA-Z]+-?'?[a-zA-Z]*")

        self.tokens = []
        self.word_tokens = []
        self.tagged_tokens = []
        self.sentence_structures = []
        self.basic_sentence_structures = []
        self.posdict = {}

        text = self.context
        if isinstance(self.context, nltk.Text):
            # detokenize if nltk text passed in
            twd = TreebankWordDetokenizer()
            text = twd.detokenize(self.context)

        sents = nltk.sent_tokenize(text)
        for sent in sents:
            sentence_structure = []

            sent_tokens = nltk.word_tokenize(sent)
            self.tokens += sent_tokens

            tagged_sent_tokens = nltk.pos_tag(sent_tokens)
            self.tagged_tokens += tagged_sent_tokens

            for word, pos in tagged_sent_tokens:
                sentence_structure.append(pos)
                try:
                    self.posdict[pos].add(word)
                except KeyError:
                    self.posdict[pos] = set([word])

            self.sentence_structures.append(sentence_structure)
            if len(sentence_structure) <= 15:
                self.basic_sentence_structures.append(sentence_structure)

            sent = sent.lower()
            self.word_tokens += [w for w in BASIC_TOKENIZE_PATTERN.findall(sent)]

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
        self.ss = None
        self.ss_loc = None

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
            words_in_line = [self.last_seen_word]
        else:
            line = []
            words_in_line = []

        if words_per_line:
            while len(words_in_line) < words_per_line:
                self.last_seen_word = self.pick_next_word()
                line.append(self.last_seen_word)
                if self.last_seen_word not in string.punctuation:
                    words_in_line.append(self.last_seen_word)

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
            pos = self.get_current_pos()
            possible_words = self.posdict[pos]
            return self.get_random(possible_words)
        else:
            return self.get_random(basic_words())
    
    def pick_next_word(self):
        if self.contextual:
            pos = self.get_current_pos()
            if pos in string.punctuation:
                return pos
            pos_words = self.posdict[pos]
            concordances = self.text.concordance_list(self.last_seen_word)
            concordance_words = [c.right[0] for c in concordances]
            possible_next_words = set(pos_words).intersection(concordance_words)
            if len(possible_next_words) == 0:
                possible_next_words = concordance_words
        else:
            r = self.datamuse.words(lc=self.last_seen_word, max=10)
            possible_next_words = [w['word'] for w in r if w['word'] not in string.punctuation]

        word = self.get_random(possible_next_words)
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

            word = self.get_random(possible_next_words.keys())
            return (word, possible_next_words[word])
        else:
            possible_next_words = {}
            r = self.datamuse.words(lc=self.last_seen_word, md='s', max=20)
            for row in r:
                w = row['word']
                if w not in string.punctuation and row['numSyllables'] <= max_syllables:
                    possible_next_words[w] = row

            word = self.get_random(possible_next_words.keys())
            return (word, possible_next_words[word]['numSyllables'])

    def get_random(self, objs):
        return random.sample(objs, 1)[0]

    def get_current_pos(self):
        if self.ss is None or (self.ss_loc == len(self.ss) - 1):
            self.ss = self.get_random(self.basic_sentence_structures)
            self.ss_loc = 0
        else:
            self.ss_loc += 1
        pos = self.ss[self.ss_loc]
        return pos

    def print_poem(self):
        """ Prints the poem """
        for line in self.poem:
            print(line)

# cadence, line length, rhyme scheme
# adj noun alliteration
