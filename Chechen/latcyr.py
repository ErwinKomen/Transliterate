"""
Transliteration conversion between Latin (academic) script and Cyrillic (standard) script of Chechen

Erwin R. Komen - May 2021
"""
import re
import sys

# This conversion list is orderd long-to-short and contains four elements per unit:
# 1: full latin (lower case) to be recognized
# 2: syllabls (V=vowel, C=consonant, D=diphthong, C#=end-of-syllable consonant)
# 3: cyrillic translation
# 4: cyrillic translation in *open* syllable (usually left blank)
# 5: cyrillic translation: syllable-initial
# 6: cyrillic translation: syllable-initial in *open* syllable
lst_latin_c = [
    "bw_CC_бІ", "b_C_б",
    "cch'_CC_ччІ", "cCh'_CC_цчІ", "ch'_C_чІ", "chw_CC_чхь",
    "cchw_CCC_ччхь","cch_CC_чч", "cCh_CC_цч", "ch_C_ч", "c'_C_цІ", "cw_CC_цхь", "c_C_ц",
    "dw_CC_дІ", "d_C_д",
    "f_C_ф",
    "ggh_CC_ггІ", "gh_C_гІ", "g_C_г", 
    "hhw_CC_ххь", "hw_C_хь", "hh_CC_ххІ", "h_C_хІ",
    "j_C_й",
    "kx_CC_кьх", "kk'_CC_ккІ", "k'_C_кІ", "k_C_к",
    "lhw_CC_лхь", "lh_CC_лхІ", "l_C_л",
    "mw_CC_мІ", "m_C_м",
    "nw_CC_нІ", "n_C_н",
    "p'_C_пІ", "pw_CC_пхь", "p_C_п",
    "qq'_CC_ккъ", "qq_CC_ккх", "q'_C_къ", "q_C_кх",
    "rhw_CC_рхь", "rrh_CC_ррхІ", "rhh_CCC_рххІ", "rh_C_рхІ", "r_C_р",
    "shw_CC_шхь", "ssh_CC_шш", "sh_C_ш", "sw_CC_схь", "s_C_с", 
    "tw_CC_тхь", "t'_C_тІ", "t_C_т",
    "v_C_в",
    "w_C_І",
    "xhw_CC_хъхь", "xw_CC_хъхь", "x_CC_х",
    "zzh_CC_жж", "zhw_CC_жІ", "zw_CC_зхь", "zh_C_ж", "z_C_з",
    ]
any_vowel = "aeiouy"
lst_latin_vs = [
    "aa_VV", "ae_V", "a_V", 
    "ee_VV", "eE_VV", "e_V", 
    "ie_D", "ii_VV", "i_V", 
    "oo_VV", "oe_D", "o_V",
    "uo_D", "uu_VV", "u_V",
    "yy_VV", "ye_D", "y_V"
    ]
lst_latin_v = [
    "aa_VV_а_ā", "aj'ie_VCD_айе", "ae_V_аь", "a_V_а_а",
    "ee_VV_е_ē_э_э̄", "eE_VV_ē__э̄",
    "ie_D_е_е_э_э", "iijie_VVCD_ийе", "iiji_VVCV_ийи", "ii_VV_ий", "i_V_и",
    "jaa_CVV_я_я̄_ъя_ъя̄", "jae_CV_яь__ъяь",          "ja_CV_я__ъя", 
    "jee_CVV_е_ē_ъе_ъē", "je_CV_е__ъе",             "jie_CD_е_иэ_ъе_ъиэ",
    "juu_CVV_ю_ю̄_ъю_ъю̄", "juo_CD_йо_йō_ъйо_ъйуо",   "ju_CV_ю__ъю",
    "jyy_CVV_юьй__ъюьй", "jye_CD_йоь__ъйоь",        "jy_CV_юь__ъюь",
    "j_C_й",
    ]
lst_keep = [
    "doocch_CVVCC_доцч", "voocch_CVVCC_воцч", "joocch_CVVCC_йоцч", "boocch_CVVCC_боцч",
    ]

class ErrHandle:
    """Error handling"""

    # ======================= CLASS INITIALIZER ========================================
    def __init__(self):
        # Initialize a local error stack
        self.loc_errStack = []

    # ----------------------------------------------------------------------------------
    # Name :    Status
    # Goal :    Just give a status message
    # History:
    # 6/apr/2016    ERK Created
    # ----------------------------------------------------------------------------------
    def Status(self, msg):
        """Put a status message on the standard error output"""

        print(msg, file=sys.stderr)

    # ----------------------------------------------------------------------------------
    # Name :    DoError
    # Goal :    Process an error
    # History:
    # 6/apr/2016    ERK Created
    # ----------------------------------------------------------------------------------
    def DoError(self, msg, bExit = False):
        """Show an error message on stderr, preceded by the name of the function"""

        # Append the error message to the stack we have
        self.loc_errStack.append(msg)
        # get the message
        sErr = self.get_error_message()
        # Print the error message for the user
        print("Error: {}\nSystem:{}".format(msg, sErr), file=sys.stderr)
        # Is this a fatal error that requires exiting?
        if (bExit):
            sys.exit(2)
        # Otherwise: return the string that has been made
        return "<br>".join(self.loc_errStack)

    def get_error_message(self):
        """Retrieve just the error message and the line number itself as a string"""

        arInfo = sys.exc_info()
        if len(arInfo) == 3:
            sMsg = str(arInfo[1])
            if arInfo[2] != None:
                sMsg += " at line " + str(arInfo[2].tb_lineno)
            return sMsg
        else:
            return ""

    def get_error_stack(self):
        return " ".join(self.loc_errStack)


class TranslitChe(object):
    lst_trans_c = []
    lst_trans_v = []
    lst_trans_vs = []
    is_latin = re.compile(r"[a-zA-Z']")
    oErr = ErrHandle()

    def __init__(self, **kwargs):
        # Read the list of CONSONANTS into my own list
        for item in lst_latin_c:
            arItem = item.split("_")
            oItem = dict(lat=arItem[0], syl=arItem[1], cyr=arItem[2])
            self.lst_trans_c.append(oItem)

        # Read the list of skip vowels into my own list
        for item in lst_latin_vs:
            arItem = item.split("_")
            oItem = dict(lat=arItem[0], syl=arItem[1])
            self.lst_trans_vs.append(oItem)

        # Read the list of VOWELS into my own list
        for item in lst_latin_v:
            arItem = item.split("_")
            oItem = dict(lat=arItem[0], syl=arItem[1], cyr=arItem[2],
                         cyr_open=None, cyr_ini=None, cyr_ini_open=None)
            num = len(arItem)
            if num > 3:
                oItem['cyr_open'] = arItem[3]
            if num > 4:
                oItem['cyr_ini'] = arItem[4]
            if num > 5:
                oItem['cyr_ini_open'] = arItem[5]
            self.lst_trans_v.append(oItem)

        # Make sure to also do what belongs to this object
        return super(TranslitChe, self).__init__(**kwargs)

    def lat2cyr_word(self, sWord):
        """Perform conversion latin to cyrillic on ONE WORD only"""

        def skip_vowel(jPos, sText):
            for item in lst_trans_vs:
                sLat = item['lat']
                sSyl = item['syl']
                lenItem = len(sLat)
                if sText[jPos:jPos+lenItem] == sLat:
                    # Found it!
                    return jPos + lenItem, item
            # DIdn't find it
            return jPos, None

        sBack = ""
        lWord = []
        iPos = 0
        num = len(sWord)
        try:
            # Walk the whole word
            while iPos < num:
                # Skip any vowels
                if sWord[iPos:1] in any_vowel:
                    iPos, oVowel = skip_vowel(iPos, sWord)
                    if oVowel == None:
                        # Something went wrong
                        iStop = 1
                    else:
                        lWord.append(oVowel)

                # GO to the next position
                iPos += 1
        except:
            msg = self.oErr.get_error_message()
            self.oErr.DoError("lat2cyr_word")

        return sBack
   
    def do_lat2cyr(self, sPart, options=None):
        """COnvert latin in [sPart] to cyrillic"""

        # Get the list of switches
        switches = [] if not 'switches' in options else options['switches']
        bOverbar = (options.get("vowel") == "macron")
        
        # Initialize
        bCons = True        # Start of word is with a consonant (if anything, then glottal stop by default)
        iPos = 0            # Position of current Latin letter in word
        iLen = len(sPart)   # Length of the Latin word
        result = []         # The result is a list of objects, one for each phoneme
        bWord = False
        iStart = 0

        try:

            # Divide the string into words
            while iPos < iLen-1:
                # Are we starting a word or not?
                sThis = sPart[iPos]
                bThisWord = (self.is_latin.match(sThis) != None)
                # Check where we are
                if not bWord and bThisWord:
                    # we were inside a non-word, but this is a word...
                    sChunk = sPart[iStart:iPos]
                    # (1) Add chunk to result
                    result.append(sChunk)
                    # (2) Reset counter
                    iStart = iPos
                elif bWord and not bThisWord:
                    # we were in word, now in non-word
                    sWord = sPart[iStart:iPos]
                    # (1) Convert this word
                    converted = self.lat2cyr_word(sWord)
                    # (2) Add word to result
                    result.append(converted)
                    # (3) Reset counter
                    iStart = iPos
                # Make sure we adapt where we are
                bWord = bThisWord

                # Go to the next position
                iPos += 1
            # Re-combine everything
            sPart = "".join(result)

        except:
            msg = self.oErr.get_error_message()
            self.oErr.DoError("do_lat2cyr")

        # Return the result
        return sPart



