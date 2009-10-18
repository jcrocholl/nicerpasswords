#!/usr/bin/python
# Copyright (C) 2009 Johann C. Rocholl <johann@rocholl.net>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Simple readable random password generator in one Python file

This is a random password generator based on the most common
combinations of vowels and consonants in the German language. It
makes passwords that are simple to read and remember, but safe from
dictionary attacks. You can use this module in your program like this:

>>> from german_passwords import generate_password
>>> generate_password()
'schmiensting'
>>> generate_password(digits=2)
'keuchtucht23'

Known problems:
1. The algorithm may generate words that appear in a German dictionary.
2. The algorithm may generate profanities. To work around these problems,
   check the output against a word list and try again if necessary.
3. Without digits, the current version can generate only 170638
   different passwords. Adding digits is highly recommended, because
   it increases the search space for brute force attacks.

If you run this script on the command line without arguments, it will
generate 100 random passwords for you:

$ python german_passwords.py
schwaechtut     jaehlinn        speeraer        klommallt       snankusst
gierbeibst      chauchticks     slorlauf        zypahlst        porult
spliplal        shachsef        schleigext      spaellellt      prdublept
schneerumpf     khaltsams       gluehrut        haisaubt        pfruetut
skialoels       mbypier         leamtets        spliskach       taeumilms
rhorfohrs       krerpackst      sklastrier      gnotturrt       pfomperkt
maeubegs        slarreisst      sklaheft        beeremmt        smorforps
smontrent       pfaufzun        karlets         geitaul         veichtirr
khanlamt        kuzenkst        snangriffst     rialoch         glaufrert
feuertollst     fleintrots      knaenkarz       khaftecht       throphippt
keugolg         prdutternd      bliertunsch     crenproff       gocki
prichkein       treueraeuft     pfordnefs       leelalls        snafuetzt
tysor           pneuchturm      pneugund        cherwenz        teueraeumst
sklazor         blaeusenk       skladretz       gnaechorts      scheueriels
bluschuenz      feutig          mbympod         phittin         pneureil
nysicht         preidam         gnabwenkt       jintals         veugunkt
dschumgelds     fladrorm        viession        schnaeftells    gluerzieds
teuertab        zweffaph        gaenglix        szekraff        schauftrark
fjohlult        schoessegst     pfrueftil       throppaft       wlattung
stroestauscht   schreimut       wlallin         dioesieht       prduchanks

This file is ready to use with common German letter combinations, but
you can also use it to generate combination dicts for other languages.
Then you can replace the dicts in this file with the new ones, and you
have a password generator for your own language, e.g. Klingon.

$ python german_passwords.py wordlist.txt 700

The file wordlist.txt should contain one lowercase word on each line.
"""

import random


def generate_password(digits=0):
    parts = []
    choice = random.choice(START_VOWEL.keys())
    parts.append(choice)
    choice = random.choice(START_VOWEL[choice])
    parts.append(choice)
    choice = random.choice(VOWEL_CONSONANT[choice])
    parts.append(choice)
    choice = random.choice(CONSONANT_VOWEL[choice])
    parts.append(choice)
    choice = random.choice(VOWEL_END[choice])
    parts.append(choice)
    for d in range(digits):
        parts.append(random.choice(DIGITS))
    return ''.join(parts)


def count_groups(filename='wordlist.txt'):
    groups = {}
    for word in open(filename):
        word = '^' + word.strip().lower() + '$'
        index = 0
        v_group = c_group = ''
        while index < len(word):
            # Find some consonants.
            start = index
            while index < len(word) and word[index] not in VOWELS:
                index += 1
            c_group = word[start:index]
            if v_group and c_group:
                pair = (v_group, c_group)
                groups[pair] = groups.get(pair, 0) + 1
            # Find some vowels.
            start = index
            while index < len(word) and word[index] in VOWELS:
                index += 1
            v_group = word[start:index]
            if c_group and v_group:
                pair = (c_group, v_group)
                groups[pair] = groups.get(pair, 0) + 1
    group_list = []
    for pair, count in groups.iteritems():
        group1, group2 = pair
        group_list.append((count, group1, group2))
    group_list.sort()
    group_list.reverse() # Highest count first.
    return group_list


def build_prefix_dict(groups, group2_allow=None, cutoff=100):
    prefix_dict = {}
    for triple in groups:
        count, group1, group2 = triple
        group1 = group1.lstrip('^')
        group2 = group2.rstrip('$')
        if group2_allow and group2 not in group2_allow:
            continue
        if group1 not in prefix_dict:
            prefix_dict[group1] = []
        prefix_dict[group1].append(group2)
        cutoff -= 1
        if not cutoff:
            break
    return prefix_dict


def print_prefix_dict(name, prefix_dict):
    import textwrap
    prefixes = prefix_dict.keys()
    prefixes.sort()
    print name, '= {'
    for prefix in prefixes:
        suffixes = prefix_dict[prefix]
        line = "    '%s': ['%s']," % (prefix, "', '".join(suffixes))
        indent = line.index('[') + 1
        print textwrap.fill(line, subsequent_indent=' ' * indent)
    print '    }'


def strength(dicts, suffix=None):
    last = dicts[-1]
    first = dicts[:-1]
    sum = 0
    for key in last.keys():
        if suffix is None or suffix in last[key]:
            sum += strength(first, key) if first else 1
    # l = len(dicts)
    # print "%sstrength(%d, '%s'): %d" % ('    ' * (4 - l), l, suffix, sum)
    return sum


def process_wordlist(filename='wordlist.txt', cutoff=100):
    groups = count_groups(filename)
    vowel_end = build_prefix_dict(
        [triple for triple in groups if triple[2].endswith('$')],
        cutoff=cutoff)
    consonant_vowel = build_prefix_dict(
        [triple for triple in groups
         if not triple[1].startswith('^') and not triple[2].endswith('$')],
        vowel_end.keys(), cutoff=cutoff)
    vowel_consonant = build_prefix_dict(
        [triple for triple in groups
         if not triple[1].startswith('^') and not triple[2].endswith('$')],
        consonant_vowel.keys(), cutoff=cutoff)
    start_vowel = build_prefix_dict(
        [triple for triple in groups if triple[1].startswith('^')],
        vowel_consonant.keys(), cutoff=cutoff)
    print "# This version can generate %d different passwords." % strength(
        [start_vowel, vowel_consonant, consonant_vowel, vowel_end])
    print "DIGITS = '%s' # Avoid confusing 0 and 1 with O and I." % DIGITS
    print "VOWELS = '%s' # To split words into groups of letters." % VOWELS
    print_prefix_dict('START_VOWEL', start_vowel)
    print_prefix_dict('VOWEL_CONSONANT', vowel_consonant)
    print_prefix_dict('CONSONANT_VOWEL', consonant_vowel)
    print_prefix_dict('VOWEL_END', vowel_end)
    print
    print "if __name__ == '__main__':"
    print "    main()"


def main():
    import sys
    if len(sys.argv) == 3:
        filename = sys.argv[1] # For example, wordlist.txt with english words.
        cutoff = int(sys.argv[2]) # For example, 10 for the top ten choices.
        process_wordlist(filename, cutoff)
    else:
        for row in range(20):
            for column in range(4):
                print '%-15s' % generate_password(),
            print generate_password()


# This version can generate 170638 different passwords.
DIGITS = '23456789' # Avoid confusing 0 and 1 with O and I.
VOWELS = 'aeiouy' # To split words into groups of letters.
START_VOWEL = {
    '': ['a', 'u', 'e', 'au', 'ei', 'ue', 'i', 'o', 'ae', 'oe', 'eu',
         'aeu', 'ai', 'aue', 'io', 'ia'],
    'b': ['e', 'a', 'u', 'i', 'ei', 'o', 'ue', 'au', 'ea', 'oe', 'ie',
          'eu', 'ee', 'ae', 'aue', 'io', 'y', 'ai', 'ia', 'aeu'],
    'bl': ['u', 'i', 'o', 'a', 'ei', 'e', 'ae', 'oe', 'ue', 'au',
           'ie', 'aue', 'aeu'],
    'br': ['a', 'u', 'e', 'au', 'ue', 'o', 'i', 'ei', 'ie', 'oe',
           'aue', 'aeu', 'ae'],
    'c': ['o', 'a', 'e', 'i', 'u', 'ae'],
    'ch': ['a', 'e', 'i', 'o', 'au', 'u'],
    'chl': ['o'],
    'chr': ['i', 'o', 'y'],
    'cl': ['u', 'o', 'i', 'e', 'ue', 'au'],
    'cr': ['e', 'a'],
    'd': ['u', 'e', 'a', 'i', 'o', 'ie', 'ue', 'aue', 'ia', 'ae',
          'eu', 'oe', 'y', 'ei', 'au', 'ioe', 'io', 'ua', 'ea'],
    'dr': ['ei', 'a', 'e', 'u', 'i', 'o', 'ue', 'ae', 'au', 'oe'],
    'dsch': ['u'],
    'f': ['e', 'a', 'o', 'i', 'u', 'ue', 'ei', 'eue', 'ae', 'oe',
          'au', 'ie', 'eu', 'ee', 'aeu', 'ia', 'ai'],
    'fj': ['o'],
    'fl': ['u', 'a', 'ue', 'ie', 'e', 'i', 'o', 'ei', 'ae', 'oe',
           'aue', 'au', 'eu', 'aeu'],
    'fr': ['ei', 'a', 'ie', 'e', 'o', 'ue', 'eu', 'i', 'aue', 'u',
           'oe', 'au', 'eue', 'ae'],
    'g': ['e', 'a', 'ei', 'u', 'o', 'i', 'ae', 'ue', 'ea', 'oe', 'ie',
          'au', 'ee', 'y', 'eu', 'eue'],
    'gl': ['ei', 'a', 'ue', 'o', 'au', 'i', 'ae', 'aeu', 'ie', 'u',
           'e'],
    'gn': ['a', 'ae', 'o'],
    'gr': ['o', 'u', 'a', 'e', 'ue', 'i', 'oe', 'au', 'ae', 'aue',
           'ei', 'ie', 'ee', 'aeu', 'eu', 'eue'],
    'h': ['e', 'i', 'a', 'o', 'ei', 'au', 'u', 'oe', 'ae', 'ue', 'y',
          'aeu', 'eu', 'ie', 'ee', 'aue', 'ai', 'io', 'eue'],
    'j': ['u', 'a', 'e', 'ae', 'o', 'ue', 'au', 'i', 'ea'],
    'k': ['o', 'a', 'e', 'i', 'u', 'ue', 'au', 'ae', 'oe', 'ei', 'ie',
          'ai', 'eu', 'aeu', 'aue', 'y', 'io'],
    'kh': ['a'],
    'kl': ['a', 'ei', 'i', 'e', 'o', 'ae', 'u', 'oe', 'au', 'ue',
           'aue', 'ee'],
    'kn': ['a', 'o', 'i', 'e', 'u', 'au', 'ie', 'ei', 'oe', 'ue',
           'ae'],
    'kr': ['a', 'e', 'i', 'ie', 'ei', 'ae', 'eu', 'au', 'ue', 'u',
           'o', 'ea', 'oe', 'aeu'],
    'l': ['a', 'e', 'o', 'i', 'ei', 'u', 'ie', 'ae', 'au', 'oe', 'ue',
          'eu', 'ee', 'aeu', 'aue', 'y', 'ai', 'ea'],
    'm': ['i', 'a', 'e', 'o', 'u', 'ue', 'ae', 'ei', 'ie', 'oe', 'au',
          'y', 'ee', 'ai', 'eu', 'aue', 'aeu'],
    'mb': ['y'],
    'n': ['a', 'o', 'e', 'ie', 'eu', 'i', 'ae', 'u', 'eue', 'ue',
          'ei', 'oe', 'ai', 'y', 'ea', 'ua', 'au', 'ia'],
    'p': ['a', 'o', 'e', 'u', 'i', 'au', 'ei', 'ae', 'ue', 'io', 'oe',
          'y', 'ie', 'ia', 'ea'],
    'pf': ['e', 'a', 'i', 'ei', 'ae', 'u', 'o', 'aue', 'oe', 'au'],
    'pfl': ['i', 'e', 'a', 'ue', 'au', 'u'],
    'pfr': ['ue'],
    'ph': ['a', 'o', 'i', 'y', 'ae', 'oe', 'e'],
    'phr': ['a'],
    'pl': ['a', 'u', 'au', 'ae', 'ue', 'ei', 'e', 'oe', 'o'],
    'pn': ['eu'],
    'pr': ['o', 'ae', 'ei', 'i', 'e', 'a', 'ue', 'u', 'ie', 'io',
           'eu'],
    'prd': ['u'],
    'ps': ['y', 'eu'],
    'pt': ['o'],
    'q': ['ua', 'ue'],
    'r': ['e', 'a', 'ei', 'o', 'u', 'i', 'ue', 'au', 'ea', 'ie', 'oe',
          'ae', 'aeu', 'eue', 'ee', 'eu', 'ia', 'ai'],
    'rh': ['ei', 'y', 'o', 'e', 'a'],
    's': ['e', 'o', 'a', 'i', 'u', 'ee', 'ue', 'ie', 'ei', 'y', 'au',
          'aeu', 'ae', 'aue', 'ai', 'eu', 'oe'],
    'sc': ['a'],
    'sch': ['a', 'u', 'i', 'au', 'e', 'ae', 'ie', 'ei', 'ue', 'o',
            'oe', 'eu', 'aue', 'eue', 'aeu'],
    'schl': ['a', 'u', 'i', 'e', 'ue', 'ei', 'ae', 'o', 'eu', 'ie',
             'au', 'aue', 'oe'],
    'schm': ['e', 'a', 'u', 'ie', 'i', 'ei', 'ae', 'o', 'au', 'ue'],
    'schn': ['e', 'a', 'i', 'ee', 'ei', 'u', 'ue', 'au', 'o', 'oe',
             'ie', 'eu', 'ae'],
    'schr': ['ei', 'i', 'e', 'u', 'o', 'a', 'au', 'ae', 'oe', 'ie'],
    'schw': ['e', 'a', 'i', 'ei', 'ae', 'u', 'ie', 'ue', 'oe', 'o'],
    'sh': ['o', 'e', 'a'],
    'sk': ['i', 'a', 'u', 'e', 'o', 'ia', 'y'],
    'skl': ['a'],
    'skr': ['u'],
    'sl': ['o', 'a'],
    'sm': ['a', 'o'],
    'sn': ['a'],
    'sp': ['e', 'a', 'ie', 'o', 'i', 'ei', 'ae', 'u', 'ue', 'io',
           'oe', 'ee'],
    'sph': ['ae'],
    'spl': ['i', 'ee'],
    'spr': ['e', 'a', 'i', 'u', 'ue', 'oe', 'ei', 'ie', 'o', 'eu',
            'ae'],
    'st': ['a', 'e', 'u', 'i', 'ei', 'eue', 'o', 'ue', 'au', 'ae',
           'oe', 'ie', 'aeu', 'aue', 'ea'],
    'str': ['a', 'ei', 'o', 'i', 'e', 'u', 'oe', 'aeu', 'au', 'ae',
            'eu', 'y'],
    'sw': ['i'],
    'sz': ['e'],
    't': ['a', 'o', 'e', 'u', 'i', 'ie', 'au', 'ei', 'ae', 'ue', 'y',
          'oe', 'ee', 'eu', 'aeu', 'eue', 'ai', 'aue', 'ea'],
    'th': ['e', 'ea', 'ue', 'u', 'y', 'ai', 'o'],
    'thr': ['o'],
    'tr': ['a', 'o', 'i', 'e', 'u', 'ue', 'au', 'ae', 'oe', 'eu',
           'ei', 'ie', 'aue', 'aeu', 'ai', 'eue', 'io'],
    'tsch': ['e', 'a'],
    'tw': ['a'],
    'v': ['e', 'o', 'ie', 'i', 'a', 'oe', 'u', 'io', 'ae', 'ei', 'ia',
          'eu'],
    'vd': ['i'],
    'vl': ['ie'],
    'vls': ['i'],
    'w': ['e', 'a', 'i', 'o', 'ei', 'ie', 'u', 'ae', 'ue', 'oe',
          'ai'],
    'wh': ['i'],
    'wl': ['a'],
    'wr': ['i', 'a'],
    'x': ['e', 'i', 'y', 'a'],
    'z': ['u', 'e', 'i', 'a', 'ei', 'ie', 'ue', 'o', 'eu', 'ae', 'y',
          'au', 'oe', 'io', 'ua', 'aeu'],
    'zw': ['ei', 'i', 'e', 'a', 'ie', 'oe', 'ae'],
    }
VOWEL_CONSONANT = {
    'a': ['t', 'r', 'g', 'ss', 'ng', 'nd', 'l', 'lt', 'mm', 'b', 'bg',
          'n', 'd', 'm', 'ft', 'rt', 'cht', 'ch', 'll', 'rb', 'nt',
          'hr', 'p', 'kt', 'nz', 's', 'st', 'tt', 'nk', 'ff', 'sch',
          'hl', 'nn', 'nl', 'ck', 'pp', 'hm', 'br', 'bs', 'nnt', 'k',
          'f', 'bl', 'rk', 'tz', 'rst', 'nst', 'gt', 'bw', 'rm', 'v',
          'chg', 'rr', 'z', 'ns', 'chs', 'nf', 'ndl', 'bst', 'bz',
          'h', 'lk', 'ftl', 'bt', 'bb', 'nsp', 'ndt', 'hn', 'rg',
          'ph', 'th', 'lb', 'nw', 'mst', 'chl', 'sst', 'nr', 'rd',
          'nb', 'mp', 'ntr', 'llt', 'bh', 'nm', 'ckt', 'nsch', 'ngr',
          'nh', 'bk', 'rl', 'mt', 'lst', 'tr', 'ntw', 'hlt', 'rn',
          'lz', 'nschl', 'mpf', 'nch', 'dr', 'x', 'nspr', 'ngl',
          'chb', 'str', 'gn', 'rsch', 'ld', 'fft', 'mml', 'lts',
          'ndg', 'llg', 'nkt', 'hrt', 'sk'],
    'ae': ['nd', 'ss', 'ng', 'g', 'h', 't', 'ft', 'll', 'cht', 'd',
           'r', 'hr', 'tz', 'ch', 'lt', 's', 'rt', 'ndl', 'tt', 'hl',
           'mpf', 'nk', 'rm', 'st', 'gl', 'nn', 'n', 'ngl', 'mm', 'm',
           'rk', 'ngt', 'nz', 'hlt', 'l', 'ltn', 'f'],
    'aeu': ['f', 'm', 's', 'b', 'mt'],
    'ai': ['s'],
    'au': ['sg', 'fg', 't', 'f', 's', 'b', 'ss', 'sl', 'l', 'sb',
           'sr', 'sh', 'st', 'ch', 'fl', 'ff', 'sst', 'g', 'fr', 'm',
           'fz', 'ftr', 'd', 'sch', 'n', 'ft', 'sz', 'cht', 'fn',
           'sk', 'k', 'bt'],
    'aue': ['nd', 'rt'],
    'e': ['r', 'nd', 'n', 't', 'st', 'l', 'rt', 's', 'g', 'h', 'b',
          'w', 'rl', 'm', 'f', 'd', 'rb', 'rh', 'lt', 'sch', 'll',
          'rg', 'rw', 'rs', 'nt', 'rf', 'rk', 'rst', 'rr', 'k', 'rm',
          'rz', 'ng', 'ss', 'tr', 'z', 'rn', 'tt', 'rd', 'rnd',
          'rsch', 'nh', 'rtr', 'lnd', 'nst', 'ck', 'rv', 'nb', 'nk',
          'ns', 'ch', 'kt', 'hr', 'nl', 'br', 'rbr', 'sp', 'tz', 'nn',
          'v', 'p', 'str', 'cht', 'schl', 'nz', 'nf', 'chn', 'gr',
          'nsch', 'hm', 'ld', 'rschl', 'ntr', 'kl', 'nw', 'nr',
          'schw', 'ntw', 'bl', 'nm', 'ntl', 'rbl', 'schr', 'spr',
          'nsw', 'tzt', 'x', 'gt', 'gl', 'rkl', 'nv', 'rdr', 'fr',
          'dr', 'llt', 'rsp', 'chs', 'ckt', 'fl', 'hl', 'mpf', 'ndst',
          'mp', 'rp', 'gg', 'lf', 'rschw', 'lh', 'xp', 'lb', 'kr',
          'pr', 'ntg', 'rkr', 'lm', 'ff', 'bt', 'hrt', 'lg', 'lst',
          'llsch', 'nth', 'np', 'rns', 'lk', 'nschl', 'md', 'q', 'zw',
          'hrl', 'nsp', 'pp', 'gn', 'hnt', 'npr', 'nstr', 'lz', 'mm',
          'rnt', 'nkl', 'pl', 'hn', 'chtl', 'nkt', 'ft', 'ht', 'nntn',
          'ngl'],
    'ea': ['rb', 'mt', 'l'],
    'ee': ['r', 'l'],
    'ei': ['t', 's', 'n', 'd', 'ch', 'g', 'ng', 'l', 'st', 'f', 'b',
           'ss', 'h', 'm', 'nz', 'nh', 'nf', 'chn', 'nl', 'z', 'ns',
           'nb', 'cht', 'lt', 'nk', 'nst', 'nsch', 'nw', 'chst', 'nd',
           'tl', 'nr', 'tr', 'nt', 'ts', 'r', 'ntr', 'gn', 'w', 'chl',
           'ft'],
    'eu': ['t', 'g', 'r', 'd', 'cht', 'l', 'gn'],
    'eue': ['r', 'rt'],
    'i': ['g', 'ch', 'sch', 'n', 't', 'cht', 'gst', 's', 'nd', 'tt',
          'st', 'ng', 'nn', 'd', 'ss', 'v', 'k', 'l', 'chst', 'gt',
          'mm', 'nt', 'z', 'll', 'gk', 'tz', 'ld', 'm', 'ck', 'ff',
          'chk', 'r', 'rtsch', 'schst', 'f', 'nk', 'ns', 'ft', 'rk',
          'b', 'nf', 'nst', 'ckt', 'sm', 'mp', 'nz', 'rm', 'ckl',
          'nh', 'pp', 'dr', 'ndl', 'chtl', 'ttl', 'lf', 'tzt', 'sk',
          'scht', 'ngl', 'rr', 'gn', 'tg', 'vst', 'nv', 'lb', 'mmt',
          'rch', 'kt', 'tl', 'tgl', 'pl', 'p'],
    'ia': ['l'],
    'ie': ['r', 'rt', 'd', 'g', 'b', 'f', 'ss', 'l', 'h', 't', 's',
           'n', 'nst', 'rb', 'll', 'nt', 'lt', 'dl'],
    'io': ['n', 'ns'],
    'ioe': ['s'],
    'o': ['s', 'l', 'r', 'mm', 'n', 't', 'll', 'g', 'b', 'd', 'ss',
          'rg', 'rt', 'm', 'st', 'rm', 'p', 'ch', 'ff', 'rd', 'nt',
          'z', 'gr', 'nn', 'ck', 'nd', 'k', 'hl', 'tt', 'rr', 'lg',
          'llst', 'pp', 'rb', 'rst', 'h', 'v', 'mp', 'hn', 'ns', 'nz',
          'rsch', 'rdn', 'f', 'nf', 'mb', 'pf', 'lt', 'bl', 'rs',
          'rf', 'ntr', 'rtg', 'rh', 'ld', 'ph', 'cht', 'rn', 'hlg',
          'rl', 'nk', 'rk', 'rtr', 'rtl', 'tz', 'pt', 'hr', 'nstr',
          'llt', 'j', 'rz', 'lk'],
    'oe': ['r', 's', 'rm', 'rd', 't', 'pf', 'g', 'rt', 'n', 'st',
           'gl', 'd', 'hn', 'ss', 'ck', 'rs', 'lk', 'h', 'rp', 'b',
           'ch'],
    'u': ['ng', 'nd', 'nt', 'r', 'n', 's', 'g', 'nb', 'l', 't', 'st',
          'f', 'mg', 'ch', 'ngs', 'm', 'd', 'pp', 'kt', 'ck', 'mm',
          'nk', 'ngsv', 'b', 'nv', 'ngsl', 'h', 'lt', 'rchg', 'nkt',
          'str', 'ngsb', 'ld', 'ns', 'cht', 'ss', 'nf', 'tz', 'tt',
          'nr', 'ngsg', 'ngsf', 'z', 'rt', 'ms', 'nw', 'w', 'ssb',
          'sch', 'ngl', 'rs', 'k', 'mf', 'nm', 'ngspr', 'p', 'nz',
          'gz', 'sst', 'rg', 'tr', 'rr', 'mp', 'nn', 'ml', 'rz',
          'nsch', 'ckt', 'tzt', 'bl', 'nst', 'v', 'rst', 'mst'],
    'ua': ['l'],
    'ue': ['b', 'g', 'ck', 'nd', 'hr', 't', 'ss', 'cht', 'st', 'ch',
           'tt', 'ckg', 'r', 'll', 'rd', 'hl', 'ckt', 'rg', 'hrt',
           'tz', 'd', 'h', 'rz', 'rf', 'mm', 'nst', 'ft', 'hn', 'rt',
           'llt', 'f', 'rst', 'l', 's', 'rm', 'gt', 'ckl'],
    'y': ['st', 'p', 's', 'mp'],
    }
CONSONANT_VOWEL = {
    'b': ['e', 'i', 'u', 'a', 'o', 'ie', 'ue', 'au', 'ae'],
    'bb': ['e'],
    'bg': ['e'],
    'bh': ['a'],
    'bk': ['o'],
    'bl': ['i', 'e', 'ie', 'a'],
    'bn': ['i'],
    'br': ['a', 'i', 'au', 'e', 'ue'],
    'bs': ['e', 'a', 'i'],
    'bst': ['e'],
    'bt': ['e', 'ei'],
    'bw': ['e'],
    'bz': ['u'],
    'ch': ['e', 'u', 'i', 'a', 'o'],
    'chb': ['a'],
    'chg': ['e'],
    'chk': ['ei'],
    'chl': ['i'],
    'chn': ['e', 'i', 'u'],
    'chs': ['e'],
    'chst': ['e'],
    'cht': ['e', 'i', 'u'],
    'chtg': ['e'],
    'chtl': ['i'],
    'ck': ['e', 'i', 'u'],
    'ckg': ['e'],
    'ckl': ['i', 'u'],
    'ckt': ['e'],
    'd': ['e', 'i', 'u', 'a', 'ie', 'o', 'io', 'eu', 'ue'],
    'dl': ['i'],
    'dr': ['i', 'e', 'o'],
    'f': ['e', 'a', 'i', 'ue', 'o', 'ae', 'u'],
    'ff': ['e', 'i', 'a'],
    'ffn': ['e'],
    'fft': ['e'],
    'fg': ['e'],
    'fl': ['i', 'e', 'o', 'a'],
    'fn': ['a'],
    'fr': ['i', 'ie', 'e'],
    'ft': ['e', 'i'],
    'ftl': ['i'],
    'ftr': ['a'],
    'fz': ['u'],
    'g': ['e', 'u', 'a', 'i', 'ie', 'o'],
    'gb': ['a'],
    'gg': ['e'],
    'gk': ['ei'],
    'gl': ['i', 'ei'],
    'gn': ['e', 'a', 'i', 'o'],
    'gr': ['a', 'i', 'e'],
    'gs': ['a'],
    'gst': ['e'],
    'gt': ['e'],
    'gz': ['eu'],
    'h': ['e', 'i', 'a', 'ei', 'o', 'u', 'oe', 'ae', 'au'],
    'hb': ['a'],
    'hl': ['e', 'u', 'i'],
    'hlb': ['e'],
    'hlg': ['e'],
    'hlt': ['e'],
    'hm': ['e'],
    'hn': ['e', 'u', 'a'],
    'hnl': ['i'],
    'hnt': ['e'],
    'hr': ['e', 'u', 'i'],
    'hrb': ['a'],
    'hrl': ['i'],
    'hrt': ['e'],
    'ht': ['e'],
    'j': ['a'],
    'k': ['e', 'a', 'o', 'u', 'ue'],
    'kl': ['a', 'e'],
    'kr': ['a'],
    'kt': ['io', 'e', 'i', 'ie', 'o'],
    'l': ['e', 'i', 'a', 'ie', 'o', 'u', 'ei', 'au', 'ae', 'oe', 'y'],
    'lb': ['e', 'a'],
    'ld': ['e', 'u', 'i'],
    'lf': ['e'],
    'lg': ['e'],
    'lh': ['a'],
    'lk': ['e', 'o', 'u'],
    'll': ['e', 'i', 'u', 'a', 'o', 'ie', 'ei'],
    'llg': ['e'],
    'llsch': ['a'],
    'llst': ['e'],
    'llt': ['e'],
    'lm': ['e'],
    'lnd': ['e'],
    'lp': ['e'],
    'lst': ['e'],
    'lt': ['e', 'i', 'u', 'a'],
    'ltn': ['i'],
    'lts': ['a'],
    'lv': ['e'],
    'lz': ['e'],
    'm': ['e', 'a', 'i', 'o', 'ei', 'ae', 'ie', 'ue', 'u'],
    'mb': ['e'],
    'md': ['e'],
    'mf': ['a'],
    'mg': ['e'],
    'ml': ['i'],
    'mm': ['e', 'u', 'i', 'a'],
    'mml': ['i'],
    'mmt': ['e'],
    'mp': ['e', 'o', 'a', 'u'],
    'mpf': ['e', 'i'],
    'mpft': ['e'],
    'ms': ['e'],
    'mst': ['e'],
    'mt': ['e'],
    'n': ['e', 'a', 'i', 'ie', 'o', 'au', 'u', 'ei', 'ae', 'ue',
          'oe'],
    'nb': ['e', 'a', 'i'],
    'nch': ['e'],
    'nd': ['e', 'i', 'u', 'a', 'ie', 'o'],
    'ndb': ['a'],
    'ndg': ['e'],
    'ndl': ['i', 'u', 'e'],
    'ndsch': ['a'],
    'ndst': ['e'],
    'ndt': ['e'],
    'nf': ['a', 'e', 'ae', 'o', 'ue', 'oe', 'i', 'u'],
    'ng': ['e', 'a', 'u', 'i'],
    'ngl': ['i'],
    'ngr': ['i'],
    'ngs': ['a'],
    'ngsb': ['e'],
    'ngsf': ['ae'],
    'ngsg': ['e'],
    'ngsl': ['o'],
    'ngspr': ['o'],
    'ngst': ['e'],
    'ngsv': ['o', 'e'],
    'ngt': ['e'],
    'nh': ['a', 'ei', 'ae', 'e'],
    'nk': ['e', 'o', 'u', 'a'],
    'nkl': ['i'],
    'nkt': ['e', 'io'],
    'nl': ['a', 'o', 'i', 'e', 'ei'],
    'nm': ['a', 'e', 'ae'],
    'nn': ['e', 'i', 'a', 'u'],
    'nnt': ['e'],
    'nntn': ['i'],
    'np': ['a'],
    'npr': ['o'],
    'nr': ['ei', 'e', 'i', 'u'],
    'ns': ['e', 'a', 'i', 'u', 'ie', 'io', 'o'],
    'nsb': ['e'],
    'nsch': ['a', 'e', 'i'],
    'nschl': ['a'],
    'nsg': ['e'],
    'nsp': ['o'],
    'nspr': ['u'],
    'nst': ['e', 'a', 'i', 'ae'],
    'nstr': ['u'],
    'nsw': ['e'],
    'nt': ['e', 'a', 'i', 'ie', 'ei', 'o', 'u'],
    'ntg': ['e'],
    'nth': ['a'],
    'ntl': ['i'],
    'ntr': ['a', 'i', 'o', 'ae', 'e'],
    'ntw': ['i', 'o'],
    'nv': ['e', 'o'],
    'nw': ['e', 'a', 'i', 'ei'],
    'nz': ['e', 'u', 'ie', 'i', 'ei', 'ue'],
    'nzt': ['e'],
    'p': ['e', 'a', 'i', 'ie', 'o', 'u'],
    'pf': ['e', 'i'],
    'pft': ['e'],
    'ph': ['i', 'e'],
    'pl': ['a'],
    'pp': ['e', 'a'],
    'ppt': ['e'],
    'pr': ['o'],
    'pt': ['i'],
    'q': ['ue'],
    'r': ['e', 'i', 'a', 'u', 'ei', 'ue', 'ie', 'au', 'o', 'ae', 'ia',
          'oe', 'aeu', 'eie', 'iu'],
    'rb': ['e', 'ei', 'a', 'i', 'o', 'u', 'ie'],
    'rbl': ['i'],
    'rbr': ['e', 'i', 'au'],
    'rch': ['e'],
    'rchg': ['e'],
    'rd': ['e', 'i', 'a', 'u', 'ie', 'o'],
    'rdn': ['e', 'u'],
    'rdr': ['ue'],
    'rf': ['e', 'a', 'o', 'ue', 'i', 'ae'],
    'rg': ['e', 'a', 'i', 'u', 'ae', 'ie'],
    'rgt': ['e'],
    'rh': ['a', 'e', 'ae', 'ei', 'o', 'oe', 'i'],
    'rk': ['e', 'u', 'o', 'a', 'au', 'ei'],
    'rkl': ['i', 'ae'],
    'rkr': ['a'],
    'rks': ['a'],
    'rkt': ['e'],
    'rl': ['i', 'e', 'a', 'ei', 'o', 'au', 'ie', 'ae', 'u', 'oe'],
    'rm': ['e', 'a', 'i', 'u', 'o', 'oe', 'ie', 'ae', 'ue', 'ei'],
    'rmt': ['e'],
    'rn': ['e', 'a', 'i', 'ie', 'ae'],
    'rnd': ['e'],
    'rns': ['e'],
    'rnt': ['e'],
    'rp': ['e', 'a', 'u'],
    'rr': ['e', 'i', 'a', 'ei', 'o', 'u'],
    'rrt': ['e'],
    'rs': ['e', 'a', 'i', 'o', 'u', 'ae'],
    'rsch': ['a', 'u', 'ie', 'e', 'ei', 'ue'],
    'rschl': ['a'],
    'rschw': ['e'],
    'rsp': ['a', 'ie'],
    'rst': ['e', 'a', 'ae', 'o', 'i', 'ue', 'ei'],
    'rt': ['e', 'i', 'ei', 'u', 'a', 'ie', 'o'],
    'rtg': ['e'],
    'rtl': ['i'],
    'rtr': ['a', 'e', 'ae'],
    'rtsch': ['a'],
    'rv': ['e', 'o', 'ie'],
    'rw': ['a', 'e', 'i', 'ei', 'ae', 'ue', 'u', 'o'],
    'rz': ['e', 'i', 'u', 'ie', 'ei', 'eu', 'ae', 'o'],
    'rzt': ['e'],
    's': ['e', 'a', 'ie', 'i', 'u', 'o', 'ei', 'io', 'ae', 'au'],
    'sb': ['e', 'a', 'i'],
    'sch': ['e', 'ae', 'i', 'a', 'o', 'u', 'ue', 'ei', 'ie'],
    'schl': ['a', 'e', 'o'],
    'schr': ['ie', 'ae'],
    'schst': ['e'],
    'scht': ['e'],
    'schw': ['e', 'i'],
    'sg': ['e', 'a'],
    'sh': ['a'],
    'sk': ['o', 'u', 'e', 'a'],
    'sl': ['a', 'i'],
    'sm': ['u'],
    'sp': ['e', 'ie', 'a', 'o'],
    'spr': ['ae'],
    'sr': ['ei'],
    'ss': ['e', 'i', 'u', 'a', 'ie', 'io'],
    'ssb': ['a'],
    'ssg': ['e'],
    'ssl': ['i'],
    'sst': ['e'],
    'st': ['e', 'i', 'a', 'u', 'o', 'ae', 'ie', 'ue', 'eue', 'au'],
    'stg': ['e'],
    'stl': ['i'],
    'str': ['ie', 'a', 'i', 'ei', 'e', 'o'],
    'sv': ['e'],
    'sz': ['u'],
    't': ['e', 'i', 'io', 'a', 'o', 'u', 'ae', 'ie', 'ei', 'ue',
          'au'],
    'tg': ['e'],
    'tgl': ['ie'],
    'th': ['e', 'o', 'i'],
    'tl': ['i'],
    'tr': ['ie', 'a', 'e', 'o', 'i', 'ae'],
    'ts': ['a'],
    'tsch': ['e'],
    'tscht': ['e'],
    'tsg': ['e'],
    'tst': ['e'],
    'tt': ['e', 'i', 'u', 'ie', 'a'],
    'ttl': ['i'],
    'tz': ['e', 'u', 'i'],
    'tzb': ['a'],
    'tzl': ['i'],
    'tzt': ['e'],
    'v': ['e', 'i', 'o', 'a', 'ie'],
    'vst': ['e'],
    'w': ['e', 'i', 'a', 'o', 'u', 'ei', 'ae', 'ie', 'oe', 'ue'],
    'x': ['e', 'i'],
    'xp': ['o', 'e'],
    'z': ['ie', 'e', 'i', 'ei', 'ia', 'u', 'o', 'a', 'ue'],
    'zt': ['e'],
    'zw': ['i'],
    }
VOWEL_END = {
    'a': ['ft', '', 'nd', 'r', 'g', 't', 'l', 'ng', 'cht', 'n', 'tz',
          'll', 'lt', 'mm', 's', 'hl', 'nn', 'nk', 'd', 'm', 'ch',
          'lls', 'nt', 'hn', 'ss', 'rkt', 'rt', 'hrt', 'ngs', 'ls',
          'nz', 'mt', 'gt', 'tt', 'hr', 'nds', 'mpf', 'nnt', 'gs',
          'ts', 'st', 'dt', 'b', 'ns', 'rf', 'kt', 'rs', 'sst', 'rm',
          'ck', 'rk', 'chs', 'mms', 'hlt', 'f', 'rzt', 'llt', 'ld',
          'ppt', 'fft', 'chst', 'h', 'rsch', 'ngst', 'gst', 'ckt',
          'nns', 'nkt', 'tzt', 'ndt', 'lts', 'rd', 'gd', 'lb', 'bt',
          'ph', 'hns', 'ms', 'k', 'ngt', 'mmt', 'hm', 'rrt', 'rn',
          'nzt', 'nts', 'nkst', 'nks', 'rts', 'rms', 'nnst', 'mts',
          'ht', 'cks', 'tts', 'hrs', 'hls', 'rz', 'rks', 'rfs',
          'mpft', 'mmst', 'kts', 'fts', 'sh', 'rb', 'ps', 'lz', 'hmt',
          'hmst', 'hlst', 'ff', 'ds', 'ckst'],
    'aa': ['t', 'l', 'r', 'ls'],
    'ae': ['t', 'ft', 'r', 'ngt', 'gt', 'ch', 'ss', 'llt', 'hlt',
           'lt', 'fts', 'hrt', 'sst', 'rs', 'ht', 'rts', 'gst', 'ts',
           'rmt', 'ngst', 'mpft', 'ck', 'chst', 'rt', 'rbt', 'nkt',
           'chs', 'n', 'hrst'],
    'aeu': ['mt', 'ft', 'mst', 'fst'],
    'ai': ['', 'l'],
    'ao': ['s'],
    'au': ['', 's', 'f', 'm', 't', 'st', 'sch', 'ch', 'fs', 'ms', 'b',
           'cht', 'ft', 'bt', 'chs', 'scht', 'nt', 'n', 'l', 'gt'],
    'aue': ['n', 'r', 'rn', '', 'nd', 's', 'rt', 'rs', 'rnd', 'm'],
    'auu': ['ng'],
    'ay': [''],
    'e': ['n', '', 'r', 's', 'm', 'nd', 't', 'rn', 'st', 'rs', 'l',
          'ln', 'ns', 'rt', 'lt', 'ls', 'rnd', 'nt', 'lnd', 'rst',
          'lst', 'cht', 'tz', 'rk', 'hr', 'nz', 'ld', 'tt', 'll',
          'ss', 'tzt', 'gt', 'kt', 'llt', 'ht', 'g', 'ckt', 'ck',
          'bt', 'nts', 'hrs', 'chts', 'x', 'f', 'rks', 'ms', 'tts',
          'rg', 'hrt', 'nkt', 'hl', 'rb', 'cks', 'nnt', 'hst', 'lls',
          'gs', 'ts', 'rr', 'rd', 'nds', 'rts', 'nk', 'mmt', 'hn',
          'h', 'ft', 'ckst', 'rns', 'nnst', 'hnt', 'fs', 'rrt', 'pt',
          'k', 'ch', 'bst', 'sts', 'rz', 'nsch', 'md', 'hrst', 'hls',
          'xt', 'nkst', 'ngt', 'd', 'rnt', 'ppt', 'ngst', 'rbt', 'lz',
          'lds', 'kts', 'gst', 'chs', 'rzt', 'rkt', 'nzt', 'lf'],
    'ea': ['l', 'm'],
    'eau': [''],
    'ee': ['', 'r', 'n', 's'],
    'ei': ['t', '', 'n', 's', 'ch', 'l', 'ns', 'st', 'm', 'ls', 'lt',
           'cht', 'd', 'gt', 'ft', 'ts', 'sst', 'ss', 'f', 'chs',
           'ms', 'g', 'bt', 'zt', 'sch', 'chst', 'k', 'nt', 'fst',
           'bst', 'lst', 'ht', 'mt', 'gst', 'z', 'nst', 'ks', 'nd',
           'b'],
    'eie': ['n', 'r', '', 'rn', 's', 'm', 'nd', 'rs'],
    'eu': ['r', 'g', '', 'rs', 'gs', 't', 'st', 'nd', 'm', 'z',
           'cht'],
    'eue': ['r', 'rn', '', 'n', 'rt', 'rs', 's', 'rnd', 'nd'],
    'euu': ['ng'],
    'ey': [''],
    'i': ['g', 'ch', 'n', 'sch', 'k', 's', 'cht', 'ng', '', 'gt',
          'st', 'tt', 'ft', 'ff', 'v', 'gst', 't', 'tz', 'ld', 'ngt',
          'nn', 'nd', 'ngs', 'ck', 'chst', 'chts', 'ckt', 'ns', 'l',
          'mmt', 'ngst', 'tzt', 'ss', 'p', 'ps', 'cks', 'lm', 'nns',
          'chs', 'bt', 'scht', 'ffs', 'tts', 'nkt', 'd', 'z', 'nnt',
          'sst', 'ppt', 'ls', 'r', 'lch', 'f', 'c', 'x', 'rn', 'm',
          'lms', 'vs', 'rr', 'rm', 'fft', 'rt', 'nz', 'mmst', 'ckst',
          'rk', 'lds', 'kt', 'ffst', 'ts', 'll', 'rkt', 'nkst', 'lz',
          'llt', 'gs', 'ttst', 'sts', 'schst', 'nk'],
    'ia': ['l', '', 't', 'n', 's', 'ls'],
    'ie': ['rt', '', 'n', 'rst', 'r', 'l', 'b', 'nst', 'rs', 'g', 't',
           'f', 'd', 'lt', 's', 'ht', 'gt', 'sst', 'ls', 'ss', 'bs',
           'gst', 'nt', 'll', 'rn', 'bt', 'h', 'bst', 'hst', 'gs',
           'st', 'ns', 'fst', 'ts', 'ds', 'lst', 'ft', 'fs'],
    'iee': ['n'],
    'ieu': ['r', 'rs'],
    'io': ['n', '', 's', 'ns'],
    'ioe': ['s'],
    'iu': ['m', 'ms', 's'],
    'o': ['', 's', 'r', 'n', 'rt', 't', 'rs', 'll', 'ss', 'rm', 'f',
          'ff', 'ck', 'g', 'ns', 'm', 'pf', 'rts', 'rd', 'st', 'nt',
          'l', 'hn', 'ch', 'lz', 'mmt', 'lt', 'ts', 'nds', 'rn', 'hr',
          'cks', 'b', 'rf', 'p', 'lg', 'tt', 'hl', 'llt', 'gst',
          'rns', 'lk', 'h', 'd', 'cht', 'ld', 'fs', 'ffs', 'bst',
          'pp', 'ckt', 'tzt', 'rst', 'nd', 'bt', 'x', 'pft', 'lgt',
          'hnt', 'chs', 'w', 'rgt', 'pfs', 'hrs', 'hns', 'tts', 'rps',
          'rb', 'ng', 'ms', 'ht', 'nst', 'ppt', 'llst', 'lls', 'lf',
          'lds', 'gt'],
    'oe': ['rt', 'l', 's', 'st', 'nt', 'pft', 'n', 'sst', 'hnt',
           'rst', 'r', 'ls', 'rs', 'mt', 'hnst', ''],
    'oo': ['t', 'm'],
    'ou': ['r'],
    'u': ['ng', 's', 'ss', 'ch', 'm', 'r', 'g', 't', 'nd', 'cht',
          'ck', 'chs', 'nkt', 'hr', 'st', 'ms', 'rs', 'tz', 'b',
          'nst', '', 'gs', 'f', 'rg', 'rm', 'ngs', 'n', 'ts', 'ckt',
          'h', 'ft', 'cks', 'rf', 'tzt', 'lt', 'sst', 'rt', 'nk',
          'hl', 'rz', 'mpf', 'rms', 'nft', 'ld', 'kt', 'pft', 'p',
          'l', 'gst', 'fs', 'bs', 'rst', 'hs', 'chst', 'pps', 'nsch',
          'nkts', 'tscht', 'tsch', 'scht', 'mpt', 'mpft', 'ckst',
          'rrt', 'ns', 'nks'],
    'ua': ['l'],
    'ue': ['ck', 'ckt', 'hrt', 'r', 'llt', 'hl', 'gt', 'cks', 'll',
           'hlt', '', 'rzt', 'rst', 'ht', 'hr', 'tzt', 'rt', 'n',
           'sst', 'pft', 'nz', 'hls', 'ckst', 'l', 'nscht', 'gst',
           'bt', 'tscht', 'rmt', 'nd', 't', 'rs', 'm', 'hst'],
    'y': ['', 'p', 's', 'd'],
    }

if __name__ == '__main__':
    main()
