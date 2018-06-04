# ==========================================================================================
# Name:   SplitText.py
# Goal:   Split a text into multiple texts, based on [...] contents
# Author: Erwin R. Komen
# History:  
# 18/dec/2017 - created
# ==========================================================================================
import sys, getopt, os.path, re
import util
import convert

# ============================= LOCAL VARIABLES ====================================
errHandle = util.ErrHandle()

# ----------------------------------------------------------------------------------
# Name :    main
# Goal :    Main body of the function: split one large text file into several smaller
# History:
# 18/dec/2017    ERK Created
# ----------------------------------------------------------------------------------
def main(prgName, argv) :
    flInput = ''        # input file name
    flOutput = ''       # output directory name
    batch = None

    # The parameters we pass on
    options = {'input': '', 
               'output': '', 
               'oerr': errHandle}        

    try:
        # Adapt the program name to exclude the directory
        index = prgName.rfind("\\")
        if (index > 0) :
            prgName = prgName[index+1:]
        sSyntax = prgName + ' -i <inputfile> -o <outputfolder>'
        # get all the arguments
        try:
            # Get arguments and options
            opts, args = getopt.getopt(argv, "hi:o:", ["-inputfile=","-outputfolder="])
        except getopt.GetoptError:
            errHandle.DoError(sSyntax, True)
            
        # Walk all the arguments
        for opt, arg in opts:
            if opt == '-h':
                print(sSyntax)
                sys.exit(0)
            elif opt in ("-i", "--ifile"):
                options['input'] = arg
            elif opt in ("-o", "--ofolder"):
                options['output'] = arg

        # Check if all arguments are there
        if (options['input'] == '' or options['output'] == ''):
            # Give error and exit
            errHandle.DoError(sSyntax, True)

        # Continue with the program
        errHandle.Status('Input is "' + options['input'] + '"')
        errHandle.Status('Output is "' + options['output'] + '"')

        # Now call the function that splits the input
        batch = convert.convert()
        if not batch.split2texts(options):
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
