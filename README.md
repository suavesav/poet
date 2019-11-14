# poet
context-based poetry generator

Ingests and parses text to create 'poetry'. A project for learning basic NLP and experimenting with nltk. It parses text, tokenizes it based on our needs and then uses some input stanza or meter data to generate new text based on words and concordances from the input text. Punctuation would have been nice.

A sonnet based on sense and sensibility:
```
father fanny should you say in law and
who for the son of the whole of
the sake tell you may give away towards
elinor if they think so large party is
very comfortable as their poor thing as to
them but the cheerfulness which brings in such
a piece with all live the bequest mr
dashwood to a child ought to his life
```

A poem based on the Wall Street Journal Corpus:
```
higher prices and has no one
that darrell phillips drew in

stronger advances in the workers
auto dealers said it attached to

the substance abuse would remain in
our research program in the researchers

believe her war-damaged husband as the
filters were aware of boston's dana-farber
```

Furthermore it uses the datamuse API to generate poetry without any input context. It likes to be original sometimes. Generating gems such as:
```
shown him up my lord
was born from time it has been
said of those cases
```

and
```
with her and the other side
in the two days later he
had the time he could not
the first two men to do

you know how it would like
that there was a large amount
that the first two men and
in his hand side effects upon
```

I started experimenting with figuring out parts of speech to provide sentence structure and paragraph structure but that is a work in progress...
