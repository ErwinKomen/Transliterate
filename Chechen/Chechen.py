# ==========================================================================================
# Name:   Chechen.py
# Goal:   Convert Chechen from Academic Latin into Phonemic (for the Caucasian Handbook)
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
# Goal :    Main body of the function: convert .docx to other .docx
# History:
# 18/dec/2017    ERK Created
# ----------------------------------------------------------------------------------
def main(prgName, argv) :
    flInput = ''        # input file name
    flOutput = ''       # output file name
    lStyleIn = []       # List of styles to watch
    sStyleOut = ""      # THe one output style needed
                        # The parameters we pass on
    options = {'input': '', 
               'output': '', 
               'styles': [],
               'target': '',
               'convert': '',
               'switches': [],
               'oerr': errHandle}        

    try:
        # Adapt the program name to exclude the directory
        index = prgName.rfind("\\")
        if (index > 0) :
            prgName = prgName[index+1:]
        sSyntax = prgName + ' [-s styles, -t target, -w switches] -i <inputfile> -o <outputfile>'
        # get all the arguments
        try:
            # Get arguments and options
            opts, args = getopt.getopt(argv, "hi:o:s:t:c:w:", ["-inputfile=","-outputfile=", "-styles=", "-target=", "-convert=", "-switches="])
        except getopt.GetoptError:
            errHandle.DoError(sSyntax, True)
            
        # Walk all the arguments
        for opt, arg in opts:
            if opt == '-h':
                print(sSyntax)
                sys.exit(0)
            elif opt in ("-i", "--ifile"):
                options['input'] = arg
            elif opt in ("-o", "--ofile"):
                options['output'] = arg
            elif opt in ("-s", "--styles"):
                # Styles is a semicolon-separated list of styles
                options['styles'] = re.split(r"\s*;\s*", arg)
            elif opt in ("-w", "--switches"):
                # Switches is a semicolon-separated list of switches
                options['switches'] = re.split(r"\s*;\s*", arg)
            elif opt in ("-t", "--target"):
                options['target'] = arg
            elif opt in ("-c", "--convert"):
                options['convert'] = arg

        # Check if all arguments are there
        if (options['input'] == '' or options['output'] == ''):
            # Give error and exit
            errHandle.DoError(sSyntax, True)
        if len(options['styles']) == 0:
            options['styles'].append("Chechen")
            options['styles'].append("Vernacular")

        # Continue with the program
        errHandle.Status('Input is "' + options['input'] + '"')
        errHandle.Status('Output is "' + options['output'] + '"')
        errHandle.Status('Styles is "' + ", ".join(options['styles']) + '"')
        if options['target'] != "":
            errHandle.Status("Target is '"+options['target']+"'")


        # Now call the function that converts the input into the output
        if not convert.academic2phonemic(options):
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