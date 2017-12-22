# ----------------------------------------------------------------------------------
# Name :    academic2phonemic
# Goal :    Convert a .docx
# History:
# 18/dec/2017    ERK Created
# ----------------------------------------------------------------------------------

import util
import re
from docx import Document

def academic2phonemic(options):
    """COnvert the file in options"""

    # Validate
    if not ('input' in options and 'output' in options):
        return False
    # Make sure we have an error object
    oErr = options['oerr']

    try:
        # Get the options
        lStyles = options['styles']
        sTarget = options['target']
        # Get the input and the output file names
        sInput = options['input']
        sOutput = options['output']

        # Create a document object
        doc = Document(sInput)
        # Get the styles in the document
        styles = doc.styles
        # Get target style
        target = next((item for item in styles if item.name == sTarget), None )
        
        iPar = 0
        # Walk through all the paragraphs of the document
        oErr.Status("Walking paragraphs...")
        for par in doc.paragraphs:
            iPar += 1
            # Show where we are
            oErr.Status("  paragraph #{}".format(iPar), True)
            # Check paragraph
            if par.style.name in lStyles:
                oErr.Status("Convert par within document")
                # Convert this part
                t = do_convert(par.text)
                # Replace it
                par.text = t
            for run in par.runs:
                s = run.style.name
                if s in lStyles:
                    # Convert this part
                    t = do_convert(run.text)
                    # Replace it
                    run.text = t
                    # if needed change style name
                    if target:
                        run.style = target
        # Next visit all TABLES in the document
        iTbl = 0
        oErr.Status("Walking tables...")
        for tbl in doc.tables:
            iTbl += 1
            # Show where we are
            oErr.Status("  table #{}".format(iTbl), True)
            # Visit all rows
            iRow = 0
            for row in tbl.rows:
                iRow += 1
                iCel = 0
                lstCells = []
                # And then all the cells in this row
                for cell in row.cells:
                    # Check if the cell is already there
                    if not cell in lstCells:
                        lstCells.append(cell)
                        iCel += 1
                        iPar = 0
                        # Check the paragraphs in this cell
                        for par in cell.paragraphs:
                            iPar += 1
                            if par.style.name in lStyles:
                                oErr.Status("Convert par within table-cell")
                                # Convert this part
                                t = do_convert(par.text)
                                # Replace it
                                par.text = t
                            for run in par.runs:
                                s = run.style.name
                                if s in lStyles:
                                    # Convert this part
                                    t = do_convert(run.text)
                                    # Replace it
                                    run.text = t
                                    # if needed change style name
                                    if target:
                                        run.style = target


        # Save the document under the new name
        doc.save(sOutput)

        # Return okay
        return True
    except:
        oErr.DoError("academic2phonemic")
        return False


def do_convert(sPart):
    """Convert the string in [sPart] according to the rules for the Caucasian handbook"""

    if "umar" in sPart:
        iStop = 1
    # Treat the 'w' where it is a hw occurring after: c, ch, k, p, sh, s, t
    sPart = re.sub(r"(ch|c|k|p|sh|s|t)w", r"\g<1>ħ",sPart)
    # Treat 'ww'
    sPart = sPart.replace("ww", "ʕː")
    # Convert gh > ʁ (long and short variant)
    sPart = sPart.replace("ggh", "ʁː").replace("gh", "ʁ").replace("Gh", "ʁ")
    # Convert ch > č (long and short variant)
    sPart = sPart.replace("cch", "čː").replace("ch", "č").replace("Ch", "č")
    # Convert zh > ž (long and short variant)
    sPart = sPart.replace("zzh", "žː").replace("zh", "ž").replace("Zh", "ž")
    # Convert sh > š (long and short variant)
    sPart = sPart.replace("ssh", "šː").replace("sh", "š").replace("Sh", "š")
    # Convert hw > ħ (long and short variant)
    sPart = sPart.replace("hhw", "ħː").replace("hw", "ħ").replace("Hw", "ħ")
    # Treat the 'w' where it occurs in other places
    sPart = re.sub(r"[Ww]", r"ʕ",sPart)
    # Treat double glottal stop
    sPart = sPart.replace("''", "ʔː")
    # Treat single glottal stop
    sPart = re.sub(r"([aeiuoy])(')", r"\g<1>ʔ", sPart)
    # Treat [rh]
    sPart = sPart.replace("rh", "r̥")
    # Treat [v]
    sPart = re.sub(r"[Vv]", r"w",sPart)
    # Make sure that ejectives have the correct apostrophe
    sPart = sPart.replace("'", "’")
    # Long vowels
    sPart = sPart.replace("Aa", "aː").replace("aa", "aː")
    sPart = sPart.replace("Ee", "eː").replace("ee", "eː")
    sPart = sPart.replace("Ii", "iː").replace("ii", "iː")
    sPart = sPart.replace("Oo", "oː").replace("oo", "oː")
    sPart = sPart.replace("Uu", "uː").replace("uu", "uː")
    sPart = sPart.replace("Yy", "üː").replace("yy", "üː")
    # Diphthong
    sPart = sPart.replace("Ye", "üe").replace("ye", "üe")
    # SHort vowels
    sPart = sPart.replace("Y", "ü").replace("y", "ü")
    # Long consonants
    sPart = sPart.replace("bb", "bː").replace("dd", "dː").replace("gg", "gː")
    sPart = sPart.replace("hh", "hː").replace("kk", "kː").replace("ll", "lː")
    sPart = sPart.replace("mm", "mː").replace("nn", "nː").replace("pp", "pː")
    sPart = sPart.replace("qq", "qː").replace("rr", "rː").replace("ss", "sː")
    sPart = sPart.replace("tt", "tː").replace("vv", "vː").replace("xx", "xː")
    sPart = sPart.replace("zz", "zː")

    # Return what we have made of it
    return sPart
    
