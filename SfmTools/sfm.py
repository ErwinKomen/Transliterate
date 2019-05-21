# ----------------------------------------------------------------------------------
# Name :    sfm
# Goal :    SFM related functions
# History:
# 18/dec/2017    ERK Created
# ----------------------------------------------------------------------------------

import io, sys, os, os.path
import util
import re

class SfmFile():
    """One SFM file read as dictionary"""

    chapters = None
    oerr = None

    def __init__(self, oerr, **kwargs):
        self.oerr = oerr
        return super(SfmFile, self).__init__(**kwargs)

    def read(self, file):
        try:
            # Read the file as string
            with open(file, "r", encoding="utf8") as f:
                sContents = f.read()

            # Split the file into \c
            lst_c = sContents.split("\\c")
            self.chapters = []
            for one_c in lst_c:
                # Normalize
                one_c = one_c.strip()
                # Split chaper into verses
                lst_v = one_c.split("\\v")
                verses = []
                for one_v in lst_v:
                    # Normalize
                    one_v = one_v.strip()
                    verses.append(one_v)
                # Add to chapters
                self.chapters.append(verses)

            return True
        except:
            msg = self.oerr.get_error_message()
            self.oerr.DoError("sfmfile read")
            return False

    def write(self, file, chapters):
        try:
            # Convert the file into a string
            lst_c = []
            for one_c in chapters:
                # Combine the verses into a string
                verses = "\\v ".join(one_c)
                lst_c.append(verses)
            # Combine chapters
            text = "\n\\c ".join(lst_c)

            # Write the string
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)

            return True
        except:
            msg = self.oerr.get_error_message()
            self.oerr.DoError("sfmfile read")
            return False


class Sfm():
    """Standard Format Marker related procedures"""

    oerr = None

    def do_action(options):
        """Act upon the indicated type"""

        finput = options['input']
        foutput = options['output']
        fcompare = options['compare']
        action = options['action']
        oerr = util.ErrHandle()

        result = None
        if action == "simple":
            result = Sfm.filter(finput, foutput, "simple")
        elif action == "compare":
            result = Sfm.compare(finput, fcompare, foutput)

        # Return the result
        return result

    def compare(finput, fcompare, foutput):
        """Compare two SFM files and return the result"""

        oerr = util.ErrHandle()

        def pre_process(sInput):
            sOutput = re.sub(r'\s\-+\s', " ", sInput)
            sOutput = sOutput.replace(u'\u0406', '\u04c0')
            sOutput = sOutput.replace("„", "<")
            sOutput = sOutput.replace('“', ">")
            sOutput = sOutput.replace('–', "")
            sOutput = sOutput.replace(".", "")
            sOutput = sOutput.replace(",", "")
            sOutput = sOutput.lower()
            return sOutput

        try:
            # Read both files
            sfminput = SfmFile(oerr)
            sfmcompare = SfmFile(oerr)

            bInput = sfminput.read(finput)
            bCompare = sfmcompare.read(fcompare)

            oInput = sfminput.chapters
            oCompare = sfmcompare.chapters

            lst_diff = []

            # Compare chapters
            for idx_c, ch_input in enumerate(oInput):
                # Get the corresponding comparison chapter
                ch_compare = oCompare[idx_c]
                # Compare verses
                for idx_v, vs_input in enumerate(ch_input):
                    vs_compare = ch_compare[idx_v]

                    # A bit more pre-processing on the verse contents
                    vs_input = pre_process(vs_input)
                    vs_compare = pre_process(vs_compare)

                    # Convert both verses into arrays
                    w_input = re.split(r'\s+', vs_input)
                    w_compare = re.split(r'\s+', vs_compare)

                    length = min(len(w_input), len(w_compare))
                    for idx in range(length):
                        if w_input[idx] != w_compare[idx]:
                            # Found the first difference
                            msg = "{}:{} at word #{} [{}] versus [{}]".format(idx_c, idx_v, idx, w_input[idx], w_compare[idx])
                            lst_diff.append(msg)
                            break
            # Combine the comparison
            sText = "\n".join(lst_diff)

            # Write as output
            with open(foutput, "w", encoding="utf-8") as f:
                f.write(sText)

            result = True
        except:
            msg = oerr.get_error_message()
            oerr.DoError("compare")
            result = False

        return result

    def filter(finput, foutput, ftype):
        """Filter according to the indicated filter type"""

        oerr = util.ErrHandle()

        try:
            # r_sfm = re.compile(r"\\\w+[\s\*]")
            r_sfm = re.compile(r"\\\w+((\s)|(\*)|$)")

            # Read the input
            sfmfile = SfmFile(oerr)
            result = sfmfile.read(finput)

            if result:
                # Filter the input according to filter type
                lst_c = []
                for one_c in sfmfile.chapters:
                    verses = []
                    for one_v in one_c:
                        # Perform the filtering
                        if ftype == "none":
                            new_v = one_v
                        elif ftype == "simple":
                            # Perform simple filtering
                            new_v = r_sfm.sub("", one_v)
                            # Replace quotation marks
                            new_v = new_v.replace("«", "<<")
                            new_v = new_v.replace("»", ">>")
                            # Remove *g**
                            new_v = new_v.replace("*g**", "")
                        verses.append(new_v)
                    # Process the verses
                    lst_c.append(verses)

                # Write the new list as a file
                result = sfmfile.write(foutput, lst_c)
        except:
            msg = oerr.get_error_message()
            oerr.DoError("filter")
            result = False

        return result


    
