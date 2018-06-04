import sys
import re       # Regular expression 
import util

class convert(object):
    """split texts"""

    errHandle = util.ErrHandle()
    folder = ""

    def __init__(self, **kwargs):
        # No real action here
        return super().__init__(**kwargs)

    def split2texts(self, options):
        """Split one large text into several smaller"""

        try:
            # Get the input file
            sInput = options['input']
            sOutput = options['output']
            self.folder = sOutput

            sHeader = ""    # Name of text
            lText = []      # Lines for a text

            # Open the input
            fInput = open(sInput, 'r', encoding='UTF8')
            # Walk through all the input lines
            for line in fInput.readlines():
                # Check if this identifies the start of a text: ( ICLE-
                if line.startswith("( ICLE-") or line.startswith("(ICLE-"):
                    # Need to chop off the part until the first right bracket
                    iPos = line.find(")")
                    if iPos>=0:
                        self.writetext(sHeader, lText)

                        # Okay, this is the beginning of a text
                        sHeader = line[2:iPos-1].replace(" ", "")
                        line = line[iPos+1:].strip()
                # Add the line to the text
                lText.append(line)
            # After finishing: output the final text
            self.writetext(sHeader, lText)

            return True
        except:
            sMsg = self.errHandle.get_error_message()
            return False

    def writetext(self, sHeader, lText):
        try:
            # If existing, finish and save a previous text
            if sHeader != "":
                # Save current text
                sFile = self.folder + "/" + sHeader + ".txt"
                fOutput = open(sFile, 'w', encoding='UTF8')
                fOutput.writelines(lText)
                #for line_out in lText:
                #    line_out = line_out.replace("\n", "")
                #    line_out = line_out.replace("\r", "")
                #    fOutput.write(line_out + "\n")
                fOutput.close()
                lText.clear()
            return True
        except:
            sMsg = self.errHandle.get_error_message()
            return False
