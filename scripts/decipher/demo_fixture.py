"""demo_fixture.py — a SYNTHETIC cipher/plain vocabulary with a KNOWN ground-truth map.

So the engine is runnable and self-verifying TODAY (no external corpus dependency). We take a
plain vocabulary (real English words over a small Latin alphabet, so letter frequencies are
natural / Zipfian), invent a DISJOINT cipher alphabet (one opaque symbol per plain letter),
draw a random-FREE bijection ``truth_map`` (cipher-symbol -> plain-letter), and ENCODE each
plain word into a cipher word by applying the inverse map. The engine must then RECOVER
``truth_map`` and the cognate pairings from cipher text + the plain wordlist alone.

Expected on CLEAN controlled data: the map is recovered at ~100% and cognate accuracy is
~100%, proving the E-step alignment + M-step assignment + EM loop are correctly implemented.
(With the ``frequency`` cold start, see :func:`maplearn.frequency_init`, recovery is exact
modulo frequency ties; with the ``identity`` cold start the result depends on the length
distribution and is reported honestly by ``decipher.py --demo``.)

Determinism: the bijection is built from a fixed seed string (no RNG) and the wordlist is
hard-coded, so the fixture is byte-reproducible.
"""

from typing import Dict, List, Tuple

# A small Latin alphabet (natural, Zipf-skewed frequencies once real words are filtered).
PLAIN_ALPHABET = "theanirousldk"  # 13 letters

# Disjoint cipher symbols (Linear-A-flavoured opaque labels). One per plain letter.
CIPHER_ALPHABET = [f"A{i:02d}" for i in range(len(PLAIN_ALPHABET))]  # A00..A12

# A curated English wordlist; build_fixture FILTERS it to PLAIN_ALPHABET, so any stray
# letter outside the alphabet is dropped harmlessly (asserted in code).
_ENGLISH = """
the and that than this sand hand land read dead head said sail nail rain
train brain drain trail soil road load toad dark lark mark bark shark
milk silk drink stink think thank tank rank sank bank dusk husk musk tusk
disk risk hike bike like dike dime lime time tame same name dame shade
blade trade grade mist list fist wrist roast toast hoist moist round mound
hound sound storm short shirt skirt snort thorn horn born torn worn lord
sword word north south mouth mouse house horse worse husk thorn thorn
road side hide ride tide slate plate crane trace trade theft theft
laden laden notion notion noise noise roast roast
donation isolation roasted roasted
""".split()


def _filter_words(words, alphabet, min_len=3, max_len=8):
    allowed = set(alphabet)
    out = []
    seen = set()
    for w in words:
        w = w.lower()
        if min_len <= len(w) <= max_len and all(ch in allowed for ch in w):
            t = tuple(w)
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def build_fixture(
    plain_alphabet: str = PLAIN_ALPHABET,
    cipher_alphabet=None,
    english_words=_ENGLISH,
    n_words: int = 80,
) -> Dict[str, object]:
    """Construct the synthetic cipher/plain vocabulary + ground truth.

    Returns a dict with::

        plain_words   : list[tuple[str,...]]   the shared plain wordlist (token = char)
        cipher_words  : list[tuple[str,...]]   each plain word encoded via inv_truth
        truth_map     : dict cipher_symbol -> plain_letter   (the map the engine must learn)
        inv_truth     : dict plain_letter -> cipher_symbol   (used to encode; == inverse)
        true_pairs    : dict cipher_word_tuple -> plain_word_tuple

    The cipher alphabet is zipped to the plain alphabet positionally (cipher[i] <-> plain[i]).
    ``n_words`` caps the vocabulary (after filtering + dedup) so the demo stays fast.
    """
    if cipher_alphabet is None:
        cipher_alphabet = [f"A{i:02d}" for i in range(len(plain_alphabet))]
    elif isinstance(cipher_alphabet, tuple):
        cipher_alphabet = list(cipher_alphabet)
    assert len(cipher_alphabet) == len(plain_alphabet), (
        f"cipher alphabet ({len(cipher_alphabet)}) must match plain alphabet "
        f"({len(plain_alphabet)})"
    )

    plain_words = _filter_words(english_words, plain_alphabet)
    if n_words:
        plain_words = plain_words[:n_words]
    assert plain_words, "no English words survived the alphabet filter"

    # Bijection: cipher_symbol[i] <-> plain_letter[i]. Deterministic, no RNG.
    truth_map: Dict[str, str] = {}
    inv_truth: Dict[str, str] = {}
    for p_letter, c_sym in zip(plain_alphabet, cipher_alphabet):
        truth_map[c_sym] = p_letter
        inv_truth[p_letter] = c_sym

    cipher_words: List[Tuple[str, ...]] = []
    true_pairs: Dict[Tuple, Tuple] = {}
    for pw in plain_words:
        cw = tuple(inv_truth[ch] for ch in pw)
        cipher_words.append(cw)
        true_pairs[cw] = pw

    return dict(
        plain_alphabet=list(plain_alphabet),
        cipher_alphabet=list(cipher_alphabet),
        plain_words=plain_words,
        cipher_words=cipher_words,
        truth_map=truth_map,
        inv_truth=inv_truth,
        true_pairs=true_pairs,
    )


def default_fixture() -> Dict[str, object]:
    """The fixture ``decipher.py --demo`` runs: PLAIN_ALPHABET + CIPHER_ALPHABET."""
    return build_fixture(PLAIN_ALPHABET, tuple(CIPHER_ALPHABET))
