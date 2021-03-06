import itertools
from pathlib import Path
import random


wordlist_dir = Path(__file__).parent / 'wordlist'


#: A mapping from class to words
wordlists = {}

#: A mapping from word to class
wordclasses = {}


def _populate_words():
    if wordlists:
        return

    for fname in sorted(wordlist_dir.glob('*.txt')):
        with fname.open('r') as fh:
            words = fh.read().split('\n')
            words = [word for word in words if word]

            # TODO: Put this into the wordlists themselves.
            random.seed(4)
            random.shuffle(words)

            classification = str(fname.name[:-4])
            wordlists[classification] = words
            if classification != 'noun':
                for word in words:
                    # There may be some duplicates between nouns and adjectives.
                    wordclasses.setdefault(word, classification)

adjective_order = ['adjective.quantity',
                   'adjective.condition',
                   'adjective.appearance',
                   'adjective.sound',
                   'adjective.time',
                   'adjective.shape',
                   'adjective.touch',
                   'adjective.color',
                    #Proper adjective (often nationality, other place of origin, or material)
                    #Purpose or qualifier,
                    'adjective.personality']
combinations = {1: list(itertools.combinations(adjective_order, 1)),
                2: list(itertools.combinations(adjective_order, 2)),
                3: list(itertools.combinations(adjective_order, 3)),
                }

def generate(n_words=3):
    rand = random.randint(0, 10000000)
    return encode(rand, n_words=n_words)


def encode(number, n_words=3):
    _populate_words()

    # TODO: Assert number below limit.

    n_adj = n_words - 1

    from collections import OrderedDict
    diagnostics = OrderedDict()

    n_nouns = len(wordlists['noun'])
    noun_ind = diagnostics['noun-index'] = number % n_nouns

    # Identify the noun for the given number.
    noun = wordlists['noun'][noun_ind]
    residual = number // n_nouns

    # Identify the structure for the given number
    struct_ind = diagnostics['structure-index'] = residual % len(combinations[n_adj])
    structure = combinations[n_adj][struct_ind]
    residual = residual // len(combinations[n_adj])

    list_lengths = [len(wordlists[cat]) for cat in structure]

    words = []
    for dim, word_class in reversed(list(zip(list_lengths, structure))):
        v = diagnostics['{}-index'.format(word_class)] = residual % dim
        residual = residual // dim
        words.insert(0, wordlists[word_class][v])

        # Dimension of structure

    words.append(noun)
    namehash = '-'.join(words)

    return namehash


def _identify_structure(words):
    # There are some words in the nouns and the adjectives list (e.g. orange)
    structure = [wordclasses[word] for word in words[:-1]] + ['noun']
    return structure


def decode(namehash):
    _populate_words()

    words = namehash.split('-')
    structure = _identify_structure(words)

    from collections import OrderedDict
    diagnostics = OrderedDict()

    positions = [wordlists[wordclasses[word]].index(word)
                 for word in words[:-1]]
    noun_posn = diagnostics['noun-index-x'] = wordlists['noun'].index(words[-1])
    positions.append(noun_posn)

    list_lengths = [len(wordlists[cat]) for cat in structure]


    list_lengths.insert(-1, len(combinations[len(words) - 1]))
    struct_posn = diagnostics['structure-index'] = combinations[len(words) - 1].index(tuple(structure[:-1]))
    positions.insert(-1, struct_posn)

    factor = 1
    number = 0
    for posn, length in reversed(list(zip(positions, list_lengths))):
        number += posn * factor
        factor *= length
    return number

def roundtrip(n):
    print('Decoding:', n)
    name = encode(n)
    print('Encoding:', name)
    dec = decode(name)
    print("Got:", dec)
    assert dec == n

if __name__ == '__main__':
    _populate_words()

    print(encode(9516072))
    print(decode('thundering-victorious-uncle'))
    for i in range(120, 1880802 * 50, 10023):
        namehash = encode(i, 3)
        print(i, end=' ')
        print(namehash, decode(namehash))

    print(encode(1880802))

    print(decode('abundant-zealous-pulley'))
