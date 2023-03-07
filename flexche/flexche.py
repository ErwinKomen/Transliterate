"""
Convert the latin chechen interlinear line (FLEX) into phonemic script

This version created by Erwin R. Komen
Date: 2/dec/2020

Example:
    python interche.py  -m "test1" 
                        -i "d:/data files/elpash/stories.xml" 
                        -o "d:/data files/elpash/stories_phon.xml"
"""

import sys, getopt, os.path, importlib
import re
from lxml import etree


trans_phonemic = [
    {"latin": "ae", "phoneme": "æ"},
    {"latin": "a", "phoneme": "a"},
    {"latin": "b", "phoneme":  "b"},
    {"latin": "ch'", "phoneme":  "ʧ’"},
    {"latin": "chw", "phoneme":  "ʧħ"}, 
    {"latin": "ch", "phoneme":  "ʧ"},
    {"latin": "c'", "phoneme":  "ʦ’"},
    {"latin": "cw", "phoneme":  "ʦħ"},
    {"latin": "c", "phoneme":  "ʦ"},
    {"latin": "d", "phoneme":  "d"},
    {"latin": "ev", "phoneme":  "ey", "following": "#bcdghklmnpqrstwxz'"},  # context: / _#  or / _[cons]
    {"latin": "e", "phoneme":  "e"},
    {"latin": "gh", "phoneme":  "ʁ"},
    {"latin": "g", "phoneme":  "g"},
    {"latin": "hhw", "phoneme":  "ħħ"}, #
    {"latin": "hw", "phoneme":  "ħ"}, #
    {"latin": "h", "phoneme":  "h"},
    {"latin": "i", "phoneme":  "i"},
    {"latin": "j", "phoneme":  "j"},
    {"latin": "k'", "phoneme":  "k’"},
    {"latin": "k", "phoneme":  "k"},
    {"latin": "l", "phoneme":  "l"},
    {"latin": "m", "phoneme":  "m"},
    {"latin": "n", "phoneme":  "n"},
    {"latin": "ov", "phoneme":  "ou"},
    {"latin": "o", "phoneme":  "o"},
    {"latin": "p'", "phoneme":  "p’"},
    {"latin": "pw", "phoneme":  "pħ"},
    {"latin": "p", "phoneme":  "p"},
    {"latin": "q'", "phoneme":  "q’"},
    {"latin": "q", "phoneme":  "q"},
    {"latin": "rh", "phoneme":  "r̥"},
    {"latin": "r", "phoneme":  "r"},
    {"latin": "shw", "phoneme":  "ʃħ"}, 
    {"latin": "ssh", "phoneme":  "ʃʃ"},
    {"latin": "sh", "phoneme":  "ʃ"},
    {"latin": "sw", "phoneme":  "sħ"},  
    {"latin": "s", "phoneme":  "s"},
    {"latin": "t'", "phoneme":  "t’"},
    {"latin": "tw", "phoneme":  "tħ"},  
    {"latin": "t", "phoneme":  "t"},
    {"latin": "u", "phoneme":  "u"},
    {"latin": "v", "phoneme":  "v"},
    {"latin": "w", "phoneme":  "ʕ"},
    {"latin": "x", "phoneme":  "χ"},
    {"latin": "zh", "phoneme":  "ʒ"},
    {"latin": "z", "phoneme":  "z"},
    {"latin": "'", "phoneme":  "ʔ"}
    ]



# ================== General helper functions =============================
def get_error_message():
    arInfo = sys.exc_info()
    if len(arInfo) == 3:
        sMsg = str(arInfo[1])
        if arInfo[2] != None:
            sMsg += " at line " + str(arInfo[2].tb_lineno)
        return sMsg
    else:
        return ""

def Status( msg):
    # Just print the message
    print(msg, file=sys.stderr)

def DoError(msg, bExit = False):
    # get the message
    sErr = get_error_message()
    # Print the error message for the user
    print("Error: {}\nSystem:{}".format(msg, sErr), file=sys.stderr)
    # Is this a fatal error that requires exiting?
    if (bExit):
        sys.exit(2)
    # Otherwise: return the string that has been made
    return msg


# ----------------------------------------------------------------------------------
# Name :    main
# Goal :    Main body of the function
# History:
# 31/jan/2019    ERK Created
# ----------------------------------------------------------------------------------
def main(prgName, argv) :
    flInput = ''        # input file name: XML with author definitions
    flOutput = ''       # output file name
    method = 'test1'    # Method used

    try:
        sSyntax = prgName + ' -i <FLEX interlinear> -o <FLEX interlinear>'
        # get all the arguments
        try:
            # Get arguments and options
            opts, args = getopt.getopt(argv, "hi:o:m:", ["-ifile=", "-ofile", "method"])
        except getopt.GetoptError:
            print(sSyntax)
            sys.exit(2)
        # Walk all the arguments
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(sSyntax)
                sys.exit(0)
            elif opt in ("-i", "--ifile"):
                flInput = arg
            elif opt in ("-o", "--ofile"):
                flOutput = arg
            elif opt in ("-m", "--method"):
                method = arg
        # Check if all arguments are there
        if (flInput == '' or flOutput == ''):
            DoError(sSyntax)

        # Continue with the program
        Status('Input is "' + flInput + '"')
        Status('Output is "' + flOutput + '"')
        Status('Method: "' + method + '"')

        oArgs = dict(input=flInput, output=flOutput, method=method)

        # Call the function that actually does the work
        if not interlinear2phonemic(oArgs):
            DoError("Could not complete conversion", True)

        Status("Ready")
    except:
        DoError("main")


# ----------------------------------------------------------------------------------
# Name :    interlinear2phonemic
# Goal :    Convert the FLEX interlinear into phonemic
# History:
# 16/nov/2020    ERK Created
# ----------------------------------------------------------------------------------
def interlinear2phonemic(oArgs):
    """Read the CorpusSearch results and convert into Excel"""

    # Defaults
    flInput = ""
    flOutput = ""
    method = "test1"
    rBreak =re.compile( r'[\-\:\.]')
    namespaces = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
                  'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    try:
        # Recover the arguments
        if "input" in oArgs: flInput = oArgs["input"]
        if "output" in oArgs: flOutput = oArgs["output"]
        if "method" in oArgs: method = oArgs['method']

        trans_phon = trans_phonemic

        # Check input file
        if not os.path.isfile(flInput):
            Status("Please specify an input FILE")
            return False

        namespacestyle = 'xmlns:m="{}" xmlns:w="{}"'.format(namespaces['m'], namespaces['w'])
        
        # Read the text file into an array
        xmldoc = etree.parse(flInput)
        

        # Find all the Interlinear lines in [ce-Latn]
        phoneme_lines = xmldoc.xpath("//m:t[parent::m:r[child::w:rPr/child::w:rStyle[contains(@w:val, 'ce-Latn')]]]", namespaces=namespaces)
        for el in phoneme_lines:
            # Get the text of this line
            line = el.text.strip()
            # Convert
            # el.text = convert_word(line)
            el.text = do_convert(line)


        # Find all [Interlin Word Gloss en] lines
        gloss_lines = xmldoc.xpath("//m:e[descendant::w:rStyle[contains(@w:val, 'Word Gloss')]]", namespaces=namespaces)
        for gloss in gloss_lines:
            # Get the text  of this gloss
            text_lst = gloss.xpath("./descendant::m:t", namespaces=namespaces)
            gloss_txt = text_lst[0].text
            Status("Gloss = [{}]".format(gloss_txt))

            # Split on period
            # OLD gloss_parts = gloss_txt.split(".")

            # Find a list of all splittable elements:'-','.'
            gloss_break = rBreak.findall(gloss_txt)
            gloss_parts = rBreak.split(gloss_txt)

            # Remove the current <m:r> child
            for mr in gloss.getchildren():
                gloss.remove(mr)
            # Walk the parts and add children respecively
            for idx, gloss_part in enumerate(gloss_parts):
                style = "Interlin Word Gloss en"
                if gloss_part != gloss_part.lower():
                    gloss_part = gloss_part.lower()
                    style = "Interlin Morpheme Gloss en"
                # Add the period for anything but the first element
                if idx > 0: 
                    # gloss_part = "." + gloss_part
                    gloss_part = gloss_break[idx-1] + gloss_part
                # Create a child
                child_mr = etree.fromstring('<m:r {}><m:rPr><m:nor /></m:rPr><w:rPr><w:rStyle w:val="{}" /></w:rPr><m:t>{}</m:t></m:r>'.format(
                    namespacestyle, style, gloss_part))
                # Add the child to the <m:e> gloss
                gloss.append(child_mr)

        # Find all the <m:rSp m:val="3" /> instances and change the value into 2 (vertical spacing within formula's)
        vert_spacing = xmldoc.xpath("//m:rSp[@m:val]", namespaces=namespaces)
        for vert in vert_spacing:
            # Change the value of the m:val attribute
            vert.attrib['{' + namespaces['m'] + '}val'] = '2'

        # Write the result to the new XML file
        str_output = etree.tostring(xmldoc, xml_declaration=True, encoding="utf-8", pretty_print=True).decode("utf-8")
        with open(flOutput, "w", encoding="utf-8") as fp:
            fp.write(str_output)

        # Return positively
        return True
    except:
        sMsg = get_error_message()
        DoError("interlinear2phonemic")
        return False

def convert_word(word):

    def trans_fits(oTrans, word, idx):
        """Check if the word at index idx fits oTrans"""

        bFound = False
        trans = ""
        ln = 0
        try:
            # Every line must have the Latin symbol(s) and the phoneme translation
            k = oTrans['latin']
            trans = oTrans['phoneme']
            # Possibly get a following context
            foll_context = oTrans.get("following")

            ln = len(k)
            # Check if line fits at all
            bFound = (word[idx:idx+ln] == k)

            # The letter fits, but is there a context?
            if bFound and not foll_context is None:
                # Check if the following context fits
                foll_letter = "#" if (idx+ln) >= len(word) else word[idx+ln]
                bFound = (foll_letter in foll_context)
        except:
            sMsg = get_error_message()
            DoError("convert_word")

        return bFound, trans, ln

    sBack = ""
    try:
        # Convert to lower-case
        word = word.lower()
        # Visit all characters of the word
        letter = []
        idx = 0
        while idx < len(word):
            bFound = False
            # Action depends on the character
            for oTrans in trans_phonemic:
                # Check if this one fits
                bFound, trans, ln = trans_fits(oTrans, word, idx)
                if bFound:
                    # Use the result
                    letter.append(trans)
                    idx += ln
                    bFound = True
                    break
            if not bFound:
                letter.append(word[idx:idx+1])
                idx += 1
        sBack = "".join(letter)
    except:
        sMsg = get_error_message()
        DoError("convert_word")
    return sBack

def do_convert(sPart, options={}):
    """Convert the string in [sPart] according to the rules for the Caucasian handbook"""

    try:
        # Get the list of switches
        switches = [] if not 'switches' in options else options['switches']
        bGeminateV = ('vv' in switches)
        bGeminateC = ('cc' in switches)
        bIngush = ('ingush' in switches)
        bHw = ('hw' in switches)
        bGh = ('gh' in switches)
        bIpa = ('ipa' in switches)
        bOld = False

        # Treat the 'w' where it is a hw occurring after: c, ch, k, p, sh, s, t
        sPart = re.sub(r"(ch|c|k|p|sh|s|t)w", r"\g<1>ħ",sPart)

        if bGeminateC:
            # Treat 'ww'
            sPart = sPart.replace("ww", "ʕʕ")
            if not bGh:
                # Convert gh > ʁ (long and short variant)
                sPart = sPart.replace("ggh", "ʁː").replace("gh", "ʁ").replace("Gh", "ʁ")
            # Convert ch > č (long and short variant)
            sPart = sPart.replace("cch", "čč").replace("ch", "č").replace("Ch", "č")
            # Convert zh > ž (long and short variant)
            sPart = sPart.replace("zzh", "žž").replace("zh", "ž").replace("Zh", "ž")
            # Convert sh > š (long and short variant)
            sPart = sPart.replace("ssh", "šš").replace("sh", "š").replace("Sh", "š")
            if not bHw:
                # Convert hw > ħ (long and short variant)
                sPart = sPart.replace("hhw", "ħħ").replace("hw", "ħ").replace("Hw", "ħ")
        else:
            # Treat 'ww'
            sPart = sPart.replace("ww", "ʕː")
            if not bGh:
                # Convert gh > ʁ (long and short variant)
                sPart = sPart.replace("ggh", "ʁː").replace("gh", "ʁ").replace("Gh", "ʁ")
            # Convert ch > č (long and short variant)
            sPart = sPart.replace("cch", "čː").replace("ch", "č").replace("Ch", "č")
            # Convert zh > ž (long and short variant)
            sPart = sPart.replace("zzh", "žː").replace("zh", "ž").replace("Zh", "ž")
            # Convert sh > š (long and short variant)
            sPart = sPart.replace("ssh", "šː").replace("sh", "š").replace("Sh", "š")
            if not bHw:
                # Convert hw > ħ (long and short variant)
                sPart = sPart.replace("hhw", "ħː").replace("hw", "ħ").replace("Hw", "ħ")
        # Convert g > ɡ (any variant)
        sPart = sPart.replace("g", "ɡ")
        # Convert x > χ (any variant)
        sPart = sPart.replace("x", "χ")
        # Treat the 'w' where it occurs in other places
        sPart = re.sub(r"[Ww]", r"ʕ",sPart)
        # Treat double glottal stop
        if bGeminateC:
            sPart = sPart.replace("''", "ʔʔ")
            sPart = sPart.replace("’’", "ʔʔ")
        else:
            sPart = sPart.replace("''", "ʔː")
            sPart = sPart.replace("’’", "ʔː")
        # Treat single glottal stop
        sPart = re.sub(r"([aeiuoy])(['’])", r"\g<1>ʔ", sPart)
        # Treat [rh]
        sPart = sPart.replace("rh", "r̥")

        # The [v] does NOT change!!!
    
        # Make sure that ejectives have the correct apostrophe
        sPart = sPart.replace("'", "’")
        if bGeminateV:
            if not bIngush:
                sPart = sPart.replace("Yy", "üː").replace("yy", "üː")
        else:
            # Long vowels
            sPart = sPart.replace("Aa", "aː").replace("aa", "aː")
            sPart = sPart.replace("Ee", "eː").replace("ee", "eː")
            sPart = sPart.replace("Ii", "iː").replace("ii", "iː")
            sPart = sPart.replace("Oo", "oː").replace("oo", "oː")
            sPart = sPart.replace("Uu", "uː").replace("uu", "uː")
            if not bIngush:
                sPart = sPart.replace("Yy", "üː").replace("yy", "üː")
        # Diphthong
        if bOld:
            sPart = sPart.replace("Ye", "üe").replace("ye", "üe")
            sPart = sPart.replace("Oe", "üe").replace("oe", "üe")   # So /ye/ and /oe/ coincide
            sPart = sPart.replace("Ov", "ou").replace("ov", "ou")
            sPart = sPart.replace("Ev", "eü").replace("ev", "eü")
            sPart = sPart.replace("Av", "au").replace("av", "au")
        else:
            sPart = re.sub(r"Ye(?:^[aeiouy])", r"üe", sPart)
            sPart = re.sub(r"Oe(?:^[aeiouy])", r"üe", sPart)
            sPart = re.sub(r"Ov(?:^[aeiouy])", r"ou", sPart)
            sPart = re.sub(r"Ev(?:^[aeiouy])", r"eü", sPart)
            sPart = re.sub(r"Av(?:^[aeiouy])", r"au", sPart)
            sPart = re.sub(r"ye(?:^[aeiouy])", r"üe", sPart)
            sPart = re.sub(r"oe(?:^[aeiouy])", r"üe", sPart)
            sPart = re.sub(r"ov(?:^[aeiouy])", r"ou", sPart)
            sPart = re.sub(r"ev(?:^[aeiouy])", r"eü", sPart)
            sPart = re.sub(r"av(?:^[aeiouy])", r"au", sPart)
            pass
        # SHort vowels
        if not bIngush:
            sPart = sPart.replace("Y", "ü").replace("y", "ü")
        # Long consonants
        if not bGeminateC:
            sPart = sPart.replace("bb", "bː").replace("dd", "dː").replace("gg", "gː")
            sPart = sPart.replace("hh", "hː").replace("kk", "kː").replace("ll", "lː")
            sPart = sPart.replace("mm", "mː").replace("nn", "nː").replace("pp", "pː")
            sPart = sPart.replace("qq", "qː").replace("rr", "rː").replace("ss", "sː")
            sPart = sPart.replace("tt", "tː").replace("vv", "vː").replace("xx", "xː")
            sPart = sPart.replace("zz", "zː")

        # Should we do IPA?
        if bIpa:
            sPart = sPart.replace("ü", "y")
            sPart = sPart.replace("š", "ʃ")
            sPart = sPart.replace("ž", "ʒ")
            sPart = sPart.replace("č", "ʧ")
            sPart = sPart.replace("c", "ʦ")
    except:
        sMsg = get_error_message()
        DoError("do_convert")

    # Return what we have made of it
    return sPart
 



# ----------------------------------------------------------------------------------
# Goal :  If user calls this as main, then follow up on it
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    # Call the main function with two arguments: program name + remainder
    main(sys.argv[0], sys.argv[1:])

