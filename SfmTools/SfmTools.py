# ==========================================================================================
# Name:   SfmTools.py
# Goal:   Convert SFM to SFM, allowing for some plug-in filtering, depending on the flags
# Author: Erwin R. Komen
# History:  
# 21/may/2019 - created
# ==========================================================================================
import sys, getopt, os.path, re
import util
from sfm import Sfm, SfmFile

# ============================= LOCAL VARIABLES ====================================
errHandle = util.ErrHandle()

# ----------------------------------------------------------------------------------
# Name :    main
# Goal :    Main body of the function: convert .docx to other .docx
# History:
# 18/dec/2017    ERK Created
# ----------------------------------------------------------------------------------
def main(prgName, argv) :
    flInput = ''        # input file name
    flOutput = ''       # output file name
    flCompare = ''      # comparison (input) file
    action = "none"     # User-definable action: 
                        # 1 - 'simple'  - only retain \c \v \p
                        # 2 - 'compare' - Find the differences between input and compare

    options = {'input': '', 
               'output': '', 
               'compare': '',
               'action': action,
               'oerr': errHandle}

    try:
        # Adapt the program name to exclude the directory
        index = prgName.rfind("\\")
        if (index > 0) :
            prgName = prgName[index+1:]
        sSyntax = prgName + ' [-a action] -i <inputfile> -o <outputfile> -c <comparefile>'
        # get all the arguments
        try:
            # Get arguments and options
            opts, args = getopt.getopt(argv, "hi:o:a:c:", ["-ifile=","-ofile=", "-action=", '-compare='])
        except getopt.GetoptError:
            errHandle.DoError(sSyntax, True)
            
        # Walk all the arguments
        for opt, arg in opts:
            if opt == '-h':
                print(sSyntax)
                sys.exit(0)
            elif opt in ("-i", "--ifile"):
                options['input'] = arg
            elif opt in ("-c", "--compare"):
                options['compare'] = arg
            elif opt in ("-o", "--ofile"):
                options['output'] = arg
            elif opt in ("-a", "--action"):
                # Read the filter
                options['action'] = arg

        # Check if all arguments are there
        if (options['input'] == '' or options['output'] == ''):
            # Give error and exit
            errHandle.DoError(sSyntax, True)

        # Continue with the program
        errHandle.Status('Input is "' + options['input'] + '"')
        errHandle.Status('Compare is "' + options['compare'] + '"')
        errHandle.Status('Output is "' + options['output'] + '"')
        errHandle.Status('Action is "' + options['action'] + '"')

        # Now call the function that converts the input into the output
        if not Sfm.do_action(options):
            errHandle.Status("The conversion could not be completed", True)
        
        # Inform the user that all is well
        errHandle.Status("The conversion is ready")
    except:
        # act
        errHandle.DoError("main")
        return False


# ----------------------------------------------------------------------------------
# Goal :  If user calls this as main, then follow up on it
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    # Call the main function with two arguments: program name + remainder
    main(sys.argv[0], sys.argv[1:])