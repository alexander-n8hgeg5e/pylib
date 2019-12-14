#!/usr/bin/python3
height=8
approx_wide=9
parts = {
        'top_of_P' :
                [
                    "||*\\\\\\",
                    "||    \\\\",
                    "||    ||",
                    "||   //",
                    "||*//",
                ],
        }
chars = {
        'start_space' :
                [
                "   "
                ],
        'P' :   [
                    *parts['top_of_P'],
                    "||",
                    "||",
                    "**",
                ],

        'N' :   [
                    "|\\     *|",
                    "||\\    ||",
                    "||\\\\   ||",
                    "|| \\\\  ||",
                    "||  \\\\ ||",
                    "||   \\\\||",
                    "||    \\||",
                    "|*     \\|",
                ],

        'S' :   [
                    "   _==*   ",
                    " //     ",
                    "||      ",
                    "  \\\\    ",
                    "    \\\\  ",
                    "      || ",
                    "     //  ",
                    " *=-F    ",
                ],

        'O' :   [
                    "    _==_   ",
                    "  //    \\\\ ",
                    " //      \\*",
                    "||       ||",
                    "|*       ||",
                    " \\\\      //",
                    "  \\\\    //",
                    "   `-=-\"    ",
                ],

        'G' :   [
                    "    _==_   ",
                    "  //    \\*",
                    ' //      "',
                    "||         ",
                    "||     *===+",
                    " \\\\      //",
                    "  \\\\    //",
                    "   `-=-\"    ",
                ],

        'Y' :   [
                    "*\\       /*",
                    " \\\\     //",
                    "  \\\\   //",
                    "   \\\\ //",
                    "    \\//",
                    "    //",
                    "   //",
                    "  */",
            
                ],

        'E' :   [
                    "||====* ",
                    "||",
                    "||",
                    "||____ ",
                    "||====* ",
                    "||",
                    "||",
                    "||====* ",
                ],
        '.' :
                [
                     *[""]*(height-2),
                    "  __",
                    " |**|   ",

                ],
        'I' :   [
                     "**",
                     *["||"]*(height-2),
                     "**",
                ],

        'R' :   [
                *parts['top_of_P'][:-1],
                    "||==\\\\",
                    "||   \\\\",
                    "||    \\\\",
                    "||     \\*",
                ],
        ' ' :   [
                " "*approx_wide
                ]
        }

######################
###   char funcs   ###
######################
def square_char(c): #{{{
    m=0#{{{
    for j in c:
        m=max(len(j),m)
    for j in range(len(c)):
        c[j]+=' '* (m - len(c[j]))
    c+= (height-len(c)) * [(" "*m )]
    return c  #}}}

def chars2lines(charkeystring,h_spaceing=" ",upper=True,start_space=True):
    global chars#{{{
    lines=[]
    if upper:
        charkeystring=charkeystring.upper()
    for i in range(height):
        line=""
        if start_space:
            line+=chars["start_space"][i]
        for c in charkeystring[:-1]:
            line+=chars[c][i]+h_spaceing
        line+=chars[charkeystring[-1]][i]
        lines.append(line)
    return lines#}}}

def square_chars(chars):
    for k,v in chars.items():#{{{
        chars[k]=square_char(v)
    return chars#}}}

def charformat(charkeystring,h_spaceing=" ",upper=True):
    #{{{
    lines=chars2lines(charkeystring,h_spaceing=h_spaceing,upper=upper)
    return "\n".join(lines)#}}}
#}}}

chars=square_chars(chars)

# vim: set foldmethod=marker foldlevel=0    :
