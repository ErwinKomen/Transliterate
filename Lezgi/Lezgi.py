# ==============================================================================
# Author: Sarah Ruth Moeller
# Date:   January 2017
# ==============================================================================

# import regex library for searching verb endings and NLTK for tokenizing
import re
from nltk.tokenize import RegexpTokenizer

# Store transliteration correspondences of Cyrillic : Latin characters.
# Dict is easier to edit than if statements later.
translit = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "ye",
    "ё": "yo", "ж": "j", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о":
    "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "xh", "ц": "ts", "ч": "ç",
    "ш": "ş", "ы": "ı", "э": "e", "ю": "yu",
    "я": "ə",
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е":
    "Ye", "Ё": "Yo", "Ж": "J", "З": "Z",
    "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M", "Н":
    "N", "О": "O", "П": "P", "Р": "R", "С": "S",
    "Т": "T", "У": "U", "Ф": "F", "Х": "Xh", "Ц": "Ts",
    "Ч": "Ç", "Ш": "Ş", "Ы": "I", "Э": "E",
    "Ю": "Yu", "Я": "Ə"}
digraphs = {"гъ": "ğ", "гь": "h", "къ": "g'", "кь": "q'", "кI": "k'",
    "пI": "p'", "тI": "t'", "уь": "ü", "хъ": "q","хь": "x",
    "цI": "ts'", "чI": "ç'", "ве": "ö", "аъ": "a'", "еъ": "ye'",
    "ёъ": "yo'", "иъ": "i'", "оъ": "o'", "уъ": "u'",
    "ыъ": "ı'", "эъ": "e'", "юъ": "yu'", "яъ": "ə'",
    "Гъ": "Ğ", "Гь": "H", "Къ": "G'", "Кь": "Q'", "КI": "K'",
    "ПI": "P'", "ТI": "T'", "Уь": "Ü", "Хъ": "Q", "Хь": "X",
    "ЦI": "Ts'", "ЧI": "Ç'", "Ве": "Ö", "Аъ": "A'", "Еъ": "Ye'",
    "Ёъ": "Yo'", "Иъ": "İ'", "Оъ": "O'", "Уъ": "U'",
    "Ыъ": "I'", "Эъ": "E'", "Юъ": "Yu'", "Яъ": "Ə'",
    "<<": '"', ">>": '"'}
# chars that need to be included without changing
nonalphanum = ('"', ',', '-', '?', '!', ':', '.', '(', ')', '[', ']', ' ', '\n')
# files with cyrillic orthography
#Cyr_files = ['Text1.txt', 'Text2.txt', 'Text3.txt', 'Text6.txt',
#    'Text7.txt', 'Text10.txt', 'Text12.txt', 'Text13.txt',
#    'Text14.txt', 'Text15.txt', 'Text17.txt', 'Text18.txt',
#    'Text19.txt', 'Text20.txt', 'Text25.txt', 'Text26.txt',
#    'Text28.txt']
Cyr_files = ['Text1.txt']
# list of finite verbal inflection endings and full copula forms; transliterated
Vendings = ["ray(ni)?(t’a)?\\b", "za?vay?(ç|çir)?(ni)?(t’a)?\\b",
    "zmay?(ç|çir)?(ni)?(t’a)?\\b", "mir(ni)?(t’a)?\\b",
    "na?vay?(ç|çir)?(ni)?(t’a)?\\b",
    "nmay?(ç|çir)?(ni)?(t’a)?\\b",
    # 'da', 'n', and 'na" are "bad" endings, too short to distinguish from other POS. These endings eliminate them.
    "day(ç|çir)?(ni)?(t’a)?\\b","nt’a\\b",
    "nay(ç|çir)?(ni)?(t’a)?\\b",
    #copulae
    "\\bya(ni)?(t’a)?\\b", "\\btir(ni)?(t’a)?\\b",
    "\\btu?(ir)?(ni)?(t’a)?\\b", "\\bavay?(ç|çir)?(ni)?(t’a)?\\b",
    "\\bgvay?(ç|çir)?(ni)?(t’a)?\\b",
    "\\bgalay?(ç|çir)?(ni)?(t’a)?\\b", "\\bkvay?(ç|çir)?(ni)?(t’a)?\\b",
    "\\balay?(ç|çir)?(ni)?(t’a)?\\b",
    "\\balay?(ç|çir)?(ni)?(t’a)?\\b", "\\bgumay?(ç|çir)?(ni)?(t’a)?\\b",
    "\\bgalamay?(ç|çir)?(ni)?(t’a)?\\b",
    "\\bkumay?(ç|çir)?(ni)?(t’a)?\\b", "\\balamay?(ç|çir)?(ni)?(t’a)?\\b"]
    # non-finite endings - "z\\b", "daldi(ni)?(t’a)?\\b", "rdavay(ni)?(t’a)?\\b", "nmaz(di)?(ni)?(t’a)?\\b"

# Transliterates list of files.
# Returns list of list of transliterated files
def transliterate(files, transliteration, digphs, punct):
    # transliterated files
    lat_files = []
    for file in files:
        # Get the absolute path
        cyrFile = open(file, 'r', encoding='UTF8')
        # Create new file for Latin transliteration
        filename = 'Latin_' + file
        latinFile = open (filename, 'a', encoding='UTF8')
        # Readlines of Cyrillic file, put in list
        lines = cyrFile.readlines()
        #Look at each item in list of lines
        for line in lines:
            # keep track of index, declare string to combine two chars
            max = len(line)
            x = 0
            combo = ''
            # look at each char in each line
            for i in line:
                # first keep chars that are the same, increase index counter
                if i in punct:
                    latinFile.write(i)
                    x+=1
                # Combine i with next letter if i is not end of line
                else:
                    if x < max-1:
                        j = line[x + 1]
                        combo = i + j
                    # if i and next letter == digraph key, append value
                    if combo in digphs:
                        latinFile.write(digphs[combo])
                    # transliterate single Cyrillic chars
                    elif i in transliteration:
                        latinFile.write(transliteration[i])
                    # skip character "?", 2nd letters of digraphs, Latin characters, or numerals and increase index count
                    else:
                        x += 1
                        continue
                    # increase index count
                    x += 1
        #Close new and old file
        cyrFile.close()
        latinFile.close()
        #add Latin file to list
        lat_files.append(filename)
    return lat_files

# Takes list of Latin files and list of morphemes
# Returns dict with occurrences of each ending/aux
def vCount(files, endings):
    #store endings with count
    verbs = {}
    # loop thru Latin files
    for file in files:
        f = open(file, 'r', encoding='UTF8')
        lines = f.readlines()
        # search each line
        for line in lines:
            # for each ending/aux
            for ending in endings:
                # make it a regex
                pattern = re.compile(ending)
                # search for each ending
                found = re.finditer(pattern, line)
                if found:
                    for find in found:
                        item = find.group()
                        if item not in verbs:
                            #add to dict
                            verbs[item] = 1
                        else:
                            #increase value
                            verbs[item] += 1
            f.close()
    return verbs

# Takes iterable of strings, adds . ? !.
# Returns list of new strings
def add_punct(endings):
    li = []
    for ending in endings:
        # add punct and add 3 patterns to list
        new_item = ending + '\.'
        li.append(new_item)
        new_item = ending + '\?'
        li.append(new_item)
        new_item = ending + '\!'
        li.append(new_item)
    return li

#Takes two dicts of endings, one with periods/commas, one without
#Returns dict with occurrences of endings that are NOT sentence final (wo periods)
def nonFVCalculate(woPuncts, wPuncts):
    # dict for count of non-sentence final occurrences
    nonSentFinalCount = {}
    for wPunct in wPuncts:
        #remove period from each key
        x = wPunct[:-1]
        for woPunct in woPuncts:
            # if ending in both dicts, subtract # of sentence final occurrences from total occurrences
            if x == woPunct:
                difference = woPuncts[woPunct] - wPuncts[wPunct]
                # add to dict only if there is at least one non-sentencefinal occurrence
                if difference > 0:
                    nonSentFinalCount[x] = difference
    return nonSentFinalCount

# Takes dict of verbs w counts as values.
# Returns sum of values
def sum_values(dict):
    total = 0
    # Puts values of dictionary in list
    counts = dict.values()
    for i in counts:
        total += i
    return total

# Takes list of files, tokenizes each, and count tokens.
# Return total token count for corpus of files.
def countwords(files):
    # number of tokens in file
    wc = 0
    # Only allow words as tokens, not punctuation or numerals
    tokenizer = RegexpTokenizer(r'\w+')
    # count tokens in each file, add to total word count
    for file in files:
        current = open(file, 'r', encoding= 'UTF8')
        lines = current.read()
        tokens = tokenizer.tokenize(f)
        wc += len(tokens)
        current.close()
    return wc

#Takes list of morphemes and files, adds elements for regex searching, searches in file and adds results to file.
#Adds list of verbs + post-verbal elements to new file
def getPVE(files, verbs):
    # create new file for results
    new = open('post_verbal_elements.txt', 'a', encoding='UTF8')
    # loop thru Latin files
    for file in files:
        # Append name of file being searched separated by new lines
        marker = '\n' + file + '\n\n'
        new.write(marker)
        f = open(file, 'r', encoding='UTF8')
        lines = f.read()
        # for each ending/aux
        for verb in verbs:
            # change search pattern to get post verbal elements, up to next . ? or !
            pat = re.compile(verb + '\\b' + '([^.?!]*)\.?\??!?')
            # search for each ending
            results = re.finditer(pat, lines)
            if results:
                for result in results:
                    str_result = result.group(1)
                    # Add search results on new line in file if not empty string
                    if str_result != '':
                        new.write(str_result + '\n')
    new.close()


#main program
newFiles = transliterate(Cyr_files, translit, digraphs, nonalphanum)
verbs = vCount(newFiles, Vendings)
totalV = sum_values(verbs)
last_verbs = add_punct(Vendings)
sent_fin_Vs = vCount(newFiles, last_verbs)
totalSFV = sum_values(sent_fin_Vs)
nonFinal = nonFVCalculate(verbs, sent_fin_Vs)
wordCount = countwords(newFiles)
#turn nonFV verbs into list
nonFmorph = nonFinal.keys()
#file of post-verbal elements
getPVE(newFiles, nonFmorph)

print("All Verbs:", verbs)
print("Clause-final verbs:", sent_fin_Vs)
print("Total number of verbs in text:", totalV)
print("Total number of non-clause-final verbs:", totalSFV)
print("Total number of words:", wordCount)
print("Non-clause-final verbs:")
for x in nonFinal:
    print(x,'\t',nonFinal[x])

