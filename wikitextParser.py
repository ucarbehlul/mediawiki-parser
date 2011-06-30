""" wikitext
<definition>
# Codes

    LF                      : '
'
    CR                      : '
'
    EOL                     : LF / CR                                                               : drop
    L_BRACKET               : "["                                                                   : drop
    R_BRACKET               : "\]"                                                                  : drop
    L_BRACE                 : "{"                                                                   : drop
    R_BRACE                 : "}"                                                                   : drop
    SPACE                   : " "                                                                   : drop
    TAB                     : "	"                                                                   : drop
    SPACETAB                : SPACE / TAB                                                           : drop
    SPACETABEOL             : SPACE / TAB / EOL                                                     : drop
    AMP                     : "&"                                                                   : drop
    PIPE                    : "|"                                                                   : drop
    BANG                    : "!"                                                                   : drop
    EQUAL                   : "="                                                                   : drop
    BULLET                  : "*"                                                                   : drop
    HASH                    : "#"                                                                   : drop
    COLON                   : ":"                                                                   : drop
    LT                      : "<"                                                                   : drop
    GT                      : ">"                                                                   : drop
    SLASH                   : "/"                                                                   : drop
    SEMICOLON               : ";"                                                                   : drop
    DASH                    : "-"                                                                   : drop
    TABLE_BEGIN             : "{|"                                                                  : drop
    TABLE_END               : "|}"                                                                  : drop
    TABLE_NEWLINE           : "|-"                                                                  : drop
    TABLE_TITLE             : "|+"                                                                  : drop
    QUOTE                   : "\""                                                                  : drop
    APOSTROPHE              : "\'"                                                                  : drop
    TITLE6_BEGIN            : EQUAL{6}                                                              : drop
    TITLE5_BEGIN            : EQUAL{5}                                                              : drop
    TITLE4_BEGIN            : EQUAL{4}                                                              : drop
    TITLE3_BEGIN            : EQUAL{3}                                                              : drop
    TITLE2_BEGIN            : EQUAL{2}                                                              : drop
    TITLE1_BEGIN            : EQUAL{1}                                                              : drop
    TITLE6_END              : EQUAL{6} SPACETAB* EOL                                                : drop
    TITLE5_END              : EQUAL{5} SPACETAB* EOL                                                : drop
    TITLE4_END              : EQUAL{4} SPACETAB* EOL                                                : drop
    TITLE3_END              : EQUAL{3} SPACETAB* EOL                                                : drop
    TITLE2_END              : EQUAL{2} SPACETAB* EOL                                                : drop
    TITLE1_END              : EQUAL{1} SPACETAB* EOL                                                : drop
    TEMPLATE_BEGIN          : L_BRACE{2}                                                            : drop
    TEMPLATE_END            : R_BRACE{2}                                                            : drop
    LINK_BEGIN              : L_BRACKET{2}                                                          : drop
    LINK_END                : R_BRACKET{2}                                                          : drop

    HTTPS                   : "https://"                                                            : liftValue
    HTTP                    : "http://"                                                             : liftValue
    FTP                     : "ftp://"                                                              : liftValue
    protocol                : HTTPS / HTTP / FTP                                                    : liftValue

# Predefined tags

    NOWIKI_BEGIN            : "<nowiki>"                                                            : drop
    NOWIKI_END              : "</nowiki>"                                                           : drop
    PRE_BEGIN               : "<pre>"                                                               : drop
    PRE_END                 : "</pre>"                                                              : drop
    special_tag             : NOWIKI_BEGIN/NOWIKI_END/PRE_BEGIN/PRE_END

# Characters

    escChar                 : L_BRACKET/R_BRACKET/protocol/PIPE/L_BRACE/R_BRACE/LT/GT/SLASH/AMP/SEMICOLON
    titleEnd                : TITLE6_END/TITLE5_END/TITLE4_END/TITLE3_END/TITLE2_END/TITLE1_END
    escSeq                  : special_tag / escChar / titleEnd
    rawChar                 : !escSeq [\x20..\xff]
    rawText                 : rawChar+                                                              : join parseAllQuotes
    alpha_num               : [a..zA..Z0..9]
    alpha_num_text          : alpha_num+                                                            : join
    anyChar                 : [\x20..\xff]
    anyText                 : anyChar+                                                              : join

# HTML tags

    value_quote             : QUOTE ((!(GT/QUOTE) anyChar) / TAB)+ QUOTE                            : join
    value_apostrophe        : APOSTROPHE ((!(GT/APOSTROPHE) anyChar) / TAB)+ APOSTROPHE             : join
    value_noquote           : (!(GT/SPACETAB/SLASH) rawChar)+                                       : join
    attribute_value         : value_quote / value_apostrophe / value_noquote
    attribute_name          : (!(EQUAL/SLASH/SPACETAB) rawChar)+                                    : join
    tag_name                : (!(SPACE/SLASH) rawChar)+                                             : join
    optional_attribute      : SPACETABEOL+ attribute_name EQUAL attribute_value
    optional_attributes     : optional_attribute*
    tag_open                : LT tag_name optional_attributes SPACETABEOL* GT
    tag_close               : LT SLASH tag_name GT
    tag_autoclose           : LT tag_name optional_attributes SPACETABEOL* SLASH GT
    tag                     : tag_autoclose / tag_open / tag_close

# HTML entities

    entity                  : AMP alpha_num_text SEMICOLON                                          : liftValue

# HTML comments

    # HTML comments are totally ignored and do not appear in the final text
    comment_content         : ((!(DASH{2} GT) [\x20..\xff])+ / SPACETABEOL)*
    html_comment            : LT BANG DASH{2} comment_content DASH{2} GT                            : drop
    optional_comment        : html_comment*

# Text

    page_name               : rawChar+                                                              : join
# TODO: allow IPv6 addresses (http://[::1]/etc)
    address                 : (!(SPACE/QUOTE/R_BRACKET) [\x21..\xff])+                              : liftValue
    url                     : protocol address                                                      : join

# Links

    allowed_in_link         : (!(R_BRACKET/PIPE) escChar)+                                          : restore liftValue join
    link_text               : (cleanInline / allowed_in_link)*                                      : liftValue
    link_argument           : PIPE link_text
    link_arguments          : link_argument*
    internal_link           : LINK_BEGIN page_name link_arguments LINK_END                          : liftValue
    optional_link_text      : SPACETAB+ link_text                                                   : liftValue
    external_link           : L_BRACKET url optional_link_text? R_BRACKET 
    link                    : internal_link / external_link

# Templates

    value                   : EQUAL cleanInline                                                     : liftValue
    optional_value          : value*                                                                : liftValue
    parameter_name          : (!EQUAL rawChar)+                                                     : join
    parameter_with_value    : parameter_name optional_value                                         : liftValue
    parameter               : SPACETABEOL* PIPE SPACETABEOL* (parameter_with_value / cleanInline)   : liftValue
    parameters              : parameter*
    template                : TEMPLATE_BEGIN page_name parameters SPACETABEOL* TEMPLATE_END

# Preformatted and nowiki

    # Preformatted acts like nowiki (disables wikitext parsing)
    pre_text                : (!PRE_END anyChar)*                                                   : join
    preformatted            : PRE_BEGIN pre_text PRE_END                                            : liftValue
    # We allow any char without parsing them as long as the tag is not closed
    nowiki_text             : (!NOWIKI_END anyChar)*                                                : join
    nowiki                  : NOWIKI_BEGIN nowiki_text NOWIKI_END                                   : liftValue

# Text types

    styledText              : preformatted / link / url / template
    allowedChar             : escChar{1}                                                            : restore liftValue
    allowedText             : rawText / allowedChar
    cleanInline             : (nowiki / styledText / rawText)+                                      : @
    inline                  : (nowiki / styledText / html_comment / tag / entity / allowedText)+    : @

# Line types

    specialLineBegin        : SPACE/EQUAL/BULLET/HASH/COLON/DASH/TABLE_BEGIN/SEMICOLON

    title6                  : TITLE6_BEGIN inline TITLE6_END                                        : liftValue
    title5                  : TITLE5_BEGIN inline TITLE5_END                                        : liftValue
    title4                  : TITLE4_BEGIN inline TITLE4_END                                        : liftValue
    title3                  : TITLE3_BEGIN inline TITLE3_END                                        : liftValue
    title2                  : TITLE2_BEGIN inline TITLE2_END                                        : liftValue
    title1                  : TITLE1_BEGIN inline TITLE1_END                                        : liftValue
    title                   : title6 / title5 / title4 / title3 / title2 / title1

    paragraphLine           : !specialLineBegin inline EOL                                          : liftValue
    blankParagraph          : EOL{2}                                                                : setNullValue
    paragraph               : paragraphLine+                                                        : liftValue
    paragraphs              : (blankParagraph/EOL/paragraph)+


    listChar                : BULLET / HASH / COLON / SEMICOLON
    listLeafContent         : !listChar inline EOL                                                  : liftValue

    bulletListLeaf          : BULLET optional_comment listLeafContent                               : liftValue
    bulletSubList           : BULLET optional_comment listItem                                      : @

    numberListLeaf          : HASH optional_comment listLeafContent                                 : liftValue
    numberSubList           : HASH optional_comment listItem                                        : @

    colonListLeaf           : COLON optional_comment listLeafContent                                : liftValue
    colonSubList            : COLON optional_comment listItem                                       : @

    semiColonListLeaf       : SEMICOLON optional_comment listLeafContent                            : liftValue
    semiColonSubList        : SEMICOLON optional_comment listItem                                   : @

    listLeaf                : semiColonListLeaf / colonListLeaf / numberListLeaf / bulletListLeaf   : @
    subList                 : semiColonSubList / colonSubList / numberSubList / bulletSubList       : @
    listItem                : subList / listLeaf                                                    : @
    list                    : listItem+

    EOL_or_not              : EOL{0..1}                                                             : drop
    preformattedLine        : SPACE inline EOL                                                      : liftValue
    preformattedLines       : preformattedLine+
    preformattedText        : inline EOL_or_not                                                     : liftValue
    preformattedParagraph   : PRE_BEGIN EOL preformattedText PRE_END EOL
    preformattedGroup       : preformattedParagraph / preformattedLines

    horizontalRule          : DASH{4} DASH* inline EOL                                              : liftValue

    invalidLine             : anyText EOL                                                           : liftValue

# Tables

# TODO: replace CSS attributes with classic tag attributes
    CSS_chars               : !(PIPE/BANG/L_BRACE) anyChar
    CSS_text                : CSS_chars+                                                            : join
    CSS_attributes          : CSS_text+ PIPE !PIPE                                                  : liftValue
    wikiTableParameters     : (CSS_text / cleanInline)+                                             : liftValue
    wikiTableFirstCell      : CSS_attributes{0..1} cleanInline*                                     : liftValue
    wikiTableOtherCell      : PIPE{2} wikiTableFirstCell                                            : liftValue
    wikiTableLineCells      : PIPE wikiTableFirstCell wikiTableOtherCell* EOL                       : liftValue
    wikiTableLineHeader     : BANG wikiTableFirstCell wikiTableOtherCell* EOL                       : liftValue
    wikiTableEmptyCell      : PIPE EOL                                                              : setNullValue
    wikiTableParamLineBreak : TABLE_NEWLINE wikiTableParameters* EOL                                : liftValue
    wikiTableLineBreak      : TABLE_NEWLINE EOL                                                     : setNullValue
    wikiTableTitle          : TABLE_TITLE CSS_attributes{0..1} inline* EOL                          : liftValue
    wikiTableSpecialLine    : wikiTableTitle / wikiTableLineBreak / wikiTableParamLineBreak
    wikiTableNormalLine     : wikiTableLineCells / wikiTableLineHeader / wikiTableEmptyCell
    wikiTableLine           : !TABLE_END (wikiTableSpecialLine / wikiTableNormalLine)
    wikiTableContent        : wikiTableLine / wikiTable / EOL
    wikiTableBegin          : TABLE_BEGIN wikiTableParameters*                                      : liftValue
    wikiTable               : wikiTableBegin EOL* wikiTableContent* TABLE_END EOL                   : @ liftValue

# Top pattern

    body                    : optional_comment (list / horizontalRule / preformattedGroup / title / wikiTable / EOL / paragraphs / invalidLine / EOL)+ : liftValue

"""



from pijnu.library import *

wikitextParser = Parser()
state = wikitextParser.state



### title: wikitext ###


###   <toolset>
def setNullValue(node):
    node.value = ''
def parseAllQuotes(node):
    from apostrophes import parseQuotes
    node.value = parseQuotes(node.value)

###   <definition>
# recursive pattern(s)
wikiTable = Recursive(name='wikiTable')
listItem = Recursive(name='listItem')
subList = Recursive(name='subList')
listLeaf = Recursive(name='listLeaf')
semiColonSubList = Recursive(name='semiColonSubList')
colonSubList = Recursive(name='colonSubList')
numberSubList = Recursive(name='numberSubList')
bulletSubList = Recursive(name='bulletSubList')
inline = Recursive(name='inline')
cleanInline = Recursive(name='cleanInline')
# Codes

LF = Char('\n', expression="'\n'", name='LF')
CR = Char('\n', expression="'\n'", name='CR')
EOL = Choice([LF, CR], expression='LF / CR', name='EOL')(drop)
L_BRACKET = Word('[', expression='"["', name='L_BRACKET')(drop)
R_BRACKET = Word(']', expression='"\\]"', name='R_BRACKET')(drop)
L_BRACE = Word('{', expression='"{"', name='L_BRACE')(drop)
R_BRACE = Word('}', expression='"}"', name='R_BRACE')(drop)
SPACE = Word(' ', expression='" "', name='SPACE')(drop)
TAB = Word('\t', expression='"\t"', name='TAB')(drop)
SPACETAB = Choice([SPACE, TAB], expression='SPACE / TAB', name='SPACETAB')(drop)
SPACETABEOL = Choice([SPACE, TAB, EOL], expression='SPACE / TAB / EOL', name='SPACETABEOL')(drop)
AMP = Word('&', expression='"&"', name='AMP')(drop)
PIPE = Word('|', expression='"|"', name='PIPE')(drop)
BANG = Word('!', expression='"!"', name='BANG')(drop)
EQUAL = Word('=', expression='"="', name='EQUAL')(drop)
BULLET = Word('*', expression='"*"', name='BULLET')(drop)
HASH = Word('#', expression='"#"', name='HASH')(drop)
COLON = Word(':', expression='":"', name='COLON')(drop)
LT = Word('<', expression='"<"', name='LT')(drop)
GT = Word('>', expression='">"', name='GT')(drop)
SLASH = Word('/', expression='"/"', name='SLASH')(drop)
SEMICOLON = Word(';', expression='";"', name='SEMICOLON')(drop)
DASH = Word('-', expression='"-"', name='DASH')(drop)
TABLE_BEGIN = Word('{|', expression='"{|"', name='TABLE_BEGIN')(drop)
TABLE_END = Word('|}', expression='"|}"', name='TABLE_END')(drop)
TABLE_NEWLINE = Word('|-', expression='"|-"', name='TABLE_NEWLINE')(drop)
TABLE_TITLE = Word('|+', expression='"|+"', name='TABLE_TITLE')(drop)
QUOTE = Word('"', expression='"\\""', name='QUOTE')(drop)
APOSTROPHE = Word("'", expression='"\\\'"', name='APOSTROPHE')(drop)
TITLE6_BEGIN = Repetition(EQUAL, numMin=6, numMax=6, expression='EQUAL{6}', name='TITLE6_BEGIN')(drop)
TITLE5_BEGIN = Repetition(EQUAL, numMin=5, numMax=5, expression='EQUAL{5}', name='TITLE5_BEGIN')(drop)
TITLE4_BEGIN = Repetition(EQUAL, numMin=4, numMax=4, expression='EQUAL{4}', name='TITLE4_BEGIN')(drop)
TITLE3_BEGIN = Repetition(EQUAL, numMin=3, numMax=3, expression='EQUAL{3}', name='TITLE3_BEGIN')(drop)
TITLE2_BEGIN = Repetition(EQUAL, numMin=2, numMax=2, expression='EQUAL{2}', name='TITLE2_BEGIN')(drop)
TITLE1_BEGIN = Repetition(EQUAL, numMin=1, numMax=1, expression='EQUAL{1}', name='TITLE1_BEGIN')(drop)
TITLE6_END = Sequence([Repetition(EQUAL, numMin=6, numMax=6, expression='EQUAL{6}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{6} SPACETAB* EOL', name='TITLE6_END')(drop)
TITLE5_END = Sequence([Repetition(EQUAL, numMin=5, numMax=5, expression='EQUAL{5}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{5} SPACETAB* EOL', name='TITLE5_END')(drop)
TITLE4_END = Sequence([Repetition(EQUAL, numMin=4, numMax=4, expression='EQUAL{4}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{4} SPACETAB* EOL', name='TITLE4_END')(drop)
TITLE3_END = Sequence([Repetition(EQUAL, numMin=3, numMax=3, expression='EQUAL{3}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{3} SPACETAB* EOL', name='TITLE3_END')(drop)
TITLE2_END = Sequence([Repetition(EQUAL, numMin=2, numMax=2, expression='EQUAL{2}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{2} SPACETAB* EOL', name='TITLE2_END')(drop)
TITLE1_END = Sequence([Repetition(EQUAL, numMin=1, numMax=1, expression='EQUAL{1}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{1} SPACETAB* EOL', name='TITLE1_END')(drop)
TEMPLATE_BEGIN = Repetition(L_BRACE, numMin=2, numMax=2, expression='L_BRACE{2}', name='TEMPLATE_BEGIN')(drop)
TEMPLATE_END = Repetition(R_BRACE, numMin=2, numMax=2, expression='R_BRACE{2}', name='TEMPLATE_END')(drop)
LINK_BEGIN = Repetition(L_BRACKET, numMin=2, numMax=2, expression='L_BRACKET{2}', name='LINK_BEGIN')(drop)
LINK_END = Repetition(R_BRACKET, numMin=2, numMax=2, expression='R_BRACKET{2}', name='LINK_END')(drop)

HTTPS = Word('https://', expression='"https://"', name='HTTPS')(liftValue)
HTTP = Word('http://', expression='"http://"', name='HTTP')(liftValue)
FTP = Word('ftp://', expression='"ftp://"', name='FTP')(liftValue)
protocol = Choice([HTTPS, HTTP, FTP], expression='HTTPS / HTTP / FTP', name='protocol')(liftValue)

# Predefined tags

NOWIKI_BEGIN = Word('<nowiki>', expression='"<nowiki>"', name='NOWIKI_BEGIN')(drop)
NOWIKI_END = Word('</nowiki>', expression='"</nowiki>"', name='NOWIKI_END')(drop)
PRE_BEGIN = Word('<pre>', expression='"<pre>"', name='PRE_BEGIN')(drop)
PRE_END = Word('</pre>', expression='"</pre>"', name='PRE_END')(drop)
special_tag = Choice([NOWIKI_BEGIN, NOWIKI_END, PRE_BEGIN, PRE_END], expression='NOWIKI_BEGIN/NOWIKI_END/PRE_BEGIN/PRE_END', name='special_tag')

# Characters

escChar = Choice([L_BRACKET, R_BRACKET, protocol, PIPE, L_BRACE, R_BRACE, LT, GT, SLASH, AMP, SEMICOLON], expression='L_BRACKET/R_BRACKET/protocol/PIPE/L_BRACE/R_BRACE/LT/GT/SLASH/AMP/SEMICOLON', name='escChar')
titleEnd = Choice([TITLE6_END, TITLE5_END, TITLE4_END, TITLE3_END, TITLE2_END, TITLE1_END], expression='TITLE6_END/TITLE5_END/TITLE4_END/TITLE3_END/TITLE2_END/TITLE1_END', name='titleEnd')
escSeq = Choice([special_tag, escChar, titleEnd], expression='special_tag / escChar / titleEnd', name='escSeq')
rawChar = Sequence([NextNot(escSeq, expression='!escSeq'), Klass(u' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x20..\\xff]')], expression='!escSeq [\\x20..\\xff]', name='rawChar')
rawText = Repetition(rawChar, numMin=1, numMax=False, expression='rawChar+', name='rawText')(join, parseAllQuotes)
alpha_num = Klass(u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', expression='[a..zA..Z0..9]', name='alpha_num')
alpha_num_text = Repetition(alpha_num, numMin=1, numMax=False, expression='alpha_num+', name='alpha_num_text')(join)
anyChar = Klass(u' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x20..\\xff]', name='anyChar')
anyText = Repetition(anyChar, numMin=1, numMax=False, expression='anyChar+', name='anyText')(join)

# HTML tags

value_quote = Sequence([QUOTE, Repetition(Choice([Sequence([NextNot(Choice([GT, QUOTE], expression='GT/QUOTE'), expression='!(GT/QUOTE)'), anyChar], expression='!(GT/QUOTE) anyChar'), TAB], expression='(!(GT/QUOTE) anyChar) / TAB'), numMin=1, numMax=False, expression='((!(GT/QUOTE) anyChar) / TAB)+'), QUOTE], expression='QUOTE ((!(GT/QUOTE) anyChar) / TAB)+ QUOTE', name='value_quote')(join)
value_apostrophe = Sequence([APOSTROPHE, Repetition(Choice([Sequence([NextNot(Choice([GT, APOSTROPHE], expression='GT/APOSTROPHE'), expression='!(GT/APOSTROPHE)'), anyChar], expression='!(GT/APOSTROPHE) anyChar'), TAB], expression='(!(GT/APOSTROPHE) anyChar) / TAB'), numMin=1, numMax=False, expression='((!(GT/APOSTROPHE) anyChar) / TAB)+'), APOSTROPHE], expression='APOSTROPHE ((!(GT/APOSTROPHE) anyChar) / TAB)+ APOSTROPHE', name='value_apostrophe')(join)
value_noquote = Repetition(Sequence([NextNot(Choice([GT, SPACETAB, SLASH], expression='GT/SPACETAB/SLASH'), expression='!(GT/SPACETAB/SLASH)'), rawChar], expression='!(GT/SPACETAB/SLASH) rawChar'), numMin=1, numMax=False, expression='(!(GT/SPACETAB/SLASH) rawChar)+', name='value_noquote')(join)
attribute_value = Choice([value_quote, value_apostrophe, value_noquote], expression='value_quote / value_apostrophe / value_noquote', name='attribute_value')
attribute_name = Repetition(Sequence([NextNot(Choice([EQUAL, SLASH, SPACETAB], expression='EQUAL/SLASH/SPACETAB'), expression='!(EQUAL/SLASH/SPACETAB)'), rawChar], expression='!(EQUAL/SLASH/SPACETAB) rawChar'), numMin=1, numMax=False, expression='(!(EQUAL/SLASH/SPACETAB) rawChar)+', name='attribute_name')(join)
tag_name = Repetition(Sequence([NextNot(Choice([SPACE, SLASH], expression='SPACE/SLASH'), expression='!(SPACE/SLASH)'), rawChar], expression='!(SPACE/SLASH) rawChar'), numMin=1, numMax=False, expression='(!(SPACE/SLASH) rawChar)+', name='tag_name')(join)
optional_attribute = Sequence([Repetition(SPACETABEOL, numMin=1, numMax=False, expression='SPACETABEOL+'), attribute_name, EQUAL, attribute_value], expression='SPACETABEOL+ attribute_name EQUAL attribute_value', name='optional_attribute')
optional_attributes = Repetition(optional_attribute, numMin=False, numMax=False, expression='optional_attribute*', name='optional_attributes')
tag_open = Sequence([LT, tag_name, optional_attributes, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), GT], expression='LT tag_name optional_attributes SPACETABEOL* GT', name='tag_open')
tag_close = Sequence([LT, SLASH, tag_name, GT], expression='LT SLASH tag_name GT', name='tag_close')
tag_autoclose = Sequence([LT, tag_name, optional_attributes, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), SLASH, GT], expression='LT tag_name optional_attributes SPACETABEOL* SLASH GT', name='tag_autoclose')
tag = Choice([tag_autoclose, tag_open, tag_close], expression='tag_autoclose / tag_open / tag_close', name='tag')

# HTML entities

entity = Sequence([AMP, alpha_num_text, SEMICOLON], expression='AMP alpha_num_text SEMICOLON', name='entity')(liftValue)

# HTML comments

    # HTML comments are totally ignored and do not appear in the final text
comment_content = Repetition(Choice([Repetition(Sequence([NextNot(Sequence([Repetition(DASH, numMin=2, numMax=2, expression='DASH{2}'), GT], expression='DASH{2} GT'), expression='!(DASH{2} GT)'), Klass(u' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x20..\\xff]')], expression='!(DASH{2} GT) [\\x20..\\xff]'), numMin=1, numMax=False, expression='(!(DASH{2} GT) [\\x20..\\xff])+'), SPACETABEOL], expression='(!(DASH{2} GT) [\\x20..\\xff])+ / SPACETABEOL'), numMin=False, numMax=False, expression='((!(DASH{2} GT) [\\x20..\\xff])+ / SPACETABEOL)*', name='comment_content')
html_comment = Sequence([LT, BANG, Repetition(DASH, numMin=2, numMax=2, expression='DASH{2}'), comment_content, Repetition(DASH, numMin=2, numMax=2, expression='DASH{2}'), GT], expression='LT BANG DASH{2} comment_content DASH{2} GT', name='html_comment')(drop)
optional_comment = Repetition(html_comment, numMin=False, numMax=False, expression='html_comment*', name='optional_comment')

# Text

page_name = Repetition(rawChar, numMin=1, numMax=False, expression='rawChar+', name='page_name')(join)
# TODO: allow IPv6 addresses (http://[::1]/etc)
address = Repetition(Sequence([NextNot(Choice([SPACE, QUOTE, R_BRACKET], expression='SPACE/QUOTE/R_BRACKET'), expression='!(SPACE/QUOTE/R_BRACKET)'), Klass(u'!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x21..\\xff]')], expression='!(SPACE/QUOTE/R_BRACKET) [\\x21..\\xff]'), numMin=1, numMax=False, expression='(!(SPACE/QUOTE/R_BRACKET) [\\x21..\\xff])+', name='address')(liftValue)
url = Sequence([protocol, address], expression='protocol address', name='url')(join)

# Links

allowed_in_link = Repetition(Sequence([NextNot(Choice([R_BRACKET, PIPE], expression='R_BRACKET/PIPE'), expression='!(R_BRACKET/PIPE)'), escChar], expression='!(R_BRACKET/PIPE) escChar'), numMin=1, numMax=False, expression='(!(R_BRACKET/PIPE) escChar)+', name='allowed_in_link')(restore, liftValue, join)
link_text = Repetition(Choice([cleanInline, allowed_in_link], expression='cleanInline / allowed_in_link'), numMin=False, numMax=False, expression='(cleanInline / allowed_in_link)*', name='link_text')(liftValue)
link_argument = Sequence([PIPE, link_text], expression='PIPE link_text', name='link_argument')
link_arguments = Repetition(link_argument, numMin=False, numMax=False, expression='link_argument*', name='link_arguments')
internal_link = Sequence([LINK_BEGIN, page_name, link_arguments, LINK_END], expression='LINK_BEGIN page_name link_arguments LINK_END', name='internal_link')(liftValue)
optional_link_text = Sequence([Repetition(SPACETAB, numMin=1, numMax=False, expression='SPACETAB+'), link_text], expression='SPACETAB+ link_text', name='optional_link_text')(liftValue)
external_link = Sequence([L_BRACKET, url, Option(optional_link_text, expression='optional_link_text?'), R_BRACKET], expression='L_BRACKET url optional_link_text? R_BRACKET', name='external_link')
link = Choice([internal_link, external_link], expression='internal_link / external_link', name='link')

# Templates

value = Sequence([EQUAL, cleanInline], expression='EQUAL cleanInline', name='value')(liftValue)
optional_value = Repetition(value, numMin=False, numMax=False, expression='value*', name='optional_value')(liftValue)
parameter_name = Repetition(Sequence([NextNot(EQUAL, expression='!EQUAL'), rawChar], expression='!EQUAL rawChar'), numMin=1, numMax=False, expression='(!EQUAL rawChar)+', name='parameter_name')(join)
parameter_with_value = Sequence([parameter_name, optional_value], expression='parameter_name optional_value', name='parameter_with_value')(liftValue)
parameter = Sequence([Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), PIPE, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), Choice([parameter_with_value, cleanInline], expression='parameter_with_value / cleanInline')], expression='SPACETABEOL* PIPE SPACETABEOL* (parameter_with_value / cleanInline)', name='parameter')(liftValue)
parameters = Repetition(parameter, numMin=False, numMax=False, expression='parameter*', name='parameters')
template = Sequence([TEMPLATE_BEGIN, page_name, parameters, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), TEMPLATE_END], expression='TEMPLATE_BEGIN page_name parameters SPACETABEOL* TEMPLATE_END', name='template')

# Preformatted and nowiki

    # Preformatted acts like nowiki (disables wikitext parsing)
pre_text = Repetition(Sequence([NextNot(PRE_END, expression='!PRE_END'), anyChar], expression='!PRE_END anyChar'), numMin=False, numMax=False, expression='(!PRE_END anyChar)*', name='pre_text')(join)
preformatted = Sequence([PRE_BEGIN, pre_text, PRE_END], expression='PRE_BEGIN pre_text PRE_END', name='preformatted')(liftValue)
    # We allow any char without parsing them as long as the tag is not closed
nowiki_text = Repetition(Sequence([NextNot(NOWIKI_END, expression='!NOWIKI_END'), anyChar], expression='!NOWIKI_END anyChar'), numMin=False, numMax=False, expression='(!NOWIKI_END anyChar)*', name='nowiki_text')(join)
nowiki = Sequence([NOWIKI_BEGIN, nowiki_text, NOWIKI_END], expression='NOWIKI_BEGIN nowiki_text NOWIKI_END', name='nowiki')(liftValue)

# Text types

styledText = Choice([preformatted, link, url, template], expression='preformatted / link / url / template', name='styledText')
allowedChar = Repetition(escChar, numMin=1, numMax=1, expression='escChar{1}', name='allowedChar')(restore, liftValue)
allowedText = Choice([rawText, allowedChar], expression='rawText / allowedChar', name='allowedText')
cleanInline **= Repetition(Choice([nowiki, styledText, rawText], expression='nowiki / styledText / rawText'), numMin=1, numMax=False, expression='(nowiki / styledText / rawText)+', name='cleanInline')
inline **= Repetition(Choice([nowiki, styledText, html_comment, tag, entity, allowedText], expression='nowiki / styledText / html_comment / tag / entity / allowedText'), numMin=1, numMax=False, expression='(nowiki / styledText / html_comment / tag / entity / allowedText)+', name='inline')

# Line types

specialLineBegin = Choice([SPACE, EQUAL, BULLET, HASH, COLON, DASH, TABLE_BEGIN, SEMICOLON], expression='SPACE/EQUAL/BULLET/HASH/COLON/DASH/TABLE_BEGIN/SEMICOLON', name='specialLineBegin')

title6 = Sequence([TITLE6_BEGIN, inline, TITLE6_END], expression='TITLE6_BEGIN inline TITLE6_END', name='title6')(liftValue)
title5 = Sequence([TITLE5_BEGIN, inline, TITLE5_END], expression='TITLE5_BEGIN inline TITLE5_END', name='title5')(liftValue)
title4 = Sequence([TITLE4_BEGIN, inline, TITLE4_END], expression='TITLE4_BEGIN inline TITLE4_END', name='title4')(liftValue)
title3 = Sequence([TITLE3_BEGIN, inline, TITLE3_END], expression='TITLE3_BEGIN inline TITLE3_END', name='title3')(liftValue)
title2 = Sequence([TITLE2_BEGIN, inline, TITLE2_END], expression='TITLE2_BEGIN inline TITLE2_END', name='title2')(liftValue)
title1 = Sequence([TITLE1_BEGIN, inline, TITLE1_END], expression='TITLE1_BEGIN inline TITLE1_END', name='title1')(liftValue)
title = Choice([title6, title5, title4, title3, title2, title1], expression='title6 / title5 / title4 / title3 / title2 / title1', name='title')

paragraphLine = Sequence([NextNot(specialLineBegin, expression='!specialLineBegin'), inline, EOL], expression='!specialLineBegin inline EOL', name='paragraphLine')(liftValue)
blankParagraph = Repetition(EOL, numMin=2, numMax=2, expression='EOL{2}', name='blankParagraph')(setNullValue)
paragraph = Repetition(paragraphLine, numMin=1, numMax=False, expression='paragraphLine+', name='paragraph')(liftValue)
paragraphs = Repetition(Choice([blankParagraph, EOL, paragraph], expression='blankParagraph/EOL/paragraph'), numMin=1, numMax=False, expression='(blankParagraph/EOL/paragraph)+', name='paragraphs')


listChar = Choice([BULLET, HASH, COLON, SEMICOLON], expression='BULLET / HASH / COLON / SEMICOLON', name='listChar')
listLeafContent = Sequence([NextNot(listChar, expression='!listChar'), inline, EOL], expression='!listChar inline EOL', name='listLeafContent')(liftValue)

bulletListLeaf = Sequence([BULLET, optional_comment, listLeafContent], expression='BULLET optional_comment listLeafContent', name='bulletListLeaf')(liftValue)
bulletSubList **= Sequence([BULLET, optional_comment, listItem], expression='BULLET optional_comment listItem', name='bulletSubList')

numberListLeaf = Sequence([HASH, optional_comment, listLeafContent], expression='HASH optional_comment listLeafContent', name='numberListLeaf')(liftValue)
numberSubList **= Sequence([HASH, optional_comment, listItem], expression='HASH optional_comment listItem', name='numberSubList')

colonListLeaf = Sequence([COLON, optional_comment, listLeafContent], expression='COLON optional_comment listLeafContent', name='colonListLeaf')(liftValue)
colonSubList **= Sequence([COLON, optional_comment, listItem], expression='COLON optional_comment listItem', name='colonSubList')

semiColonListLeaf = Sequence([SEMICOLON, optional_comment, listLeafContent], expression='SEMICOLON optional_comment listLeafContent', name='semiColonListLeaf')(liftValue)
semiColonSubList **= Sequence([SEMICOLON, optional_comment, listItem], expression='SEMICOLON optional_comment listItem', name='semiColonSubList')

listLeaf **= Choice([semiColonListLeaf, colonListLeaf, numberListLeaf, bulletListLeaf], expression='semiColonListLeaf / colonListLeaf / numberListLeaf / bulletListLeaf', name='listLeaf')
subList **= Choice([semiColonSubList, colonSubList, numberSubList, bulletSubList], expression='semiColonSubList / colonSubList / numberSubList / bulletSubList', name='subList')
listItem **= Choice([subList, listLeaf], expression='subList / listLeaf', name='listItem')
list = Repetition(listItem, numMin=1, numMax=False, expression='listItem+', name='list')

EOL_or_not = Repetition(EOL, numMin=0, numMax=1, expression='EOL{0..1}', name='EOL_or_not')(drop)
preformattedLine = Sequence([SPACE, inline, EOL], expression='SPACE inline EOL', name='preformattedLine')(liftValue)
preformattedLines = Repetition(preformattedLine, numMin=1, numMax=False, expression='preformattedLine+', name='preformattedLines')
preformattedText = Sequence([inline, EOL_or_not], expression='inline EOL_or_not', name='preformattedText')(liftValue)
preformattedParagraph = Sequence([PRE_BEGIN, EOL, preformattedText, PRE_END, EOL], expression='PRE_BEGIN EOL preformattedText PRE_END EOL', name='preformattedParagraph')
preformattedGroup = Choice([preformattedParagraph, preformattedLines], expression='preformattedParagraph / preformattedLines', name='preformattedGroup')

horizontalRule = Sequence([Repetition(DASH, numMin=4, numMax=4, expression='DASH{4}'), Repetition(DASH, numMin=False, numMax=False, expression='DASH*'), inline, EOL], expression='DASH{4} DASH* inline EOL', name='horizontalRule')(liftValue)

invalidLine = Sequence([anyText, EOL], expression='anyText EOL', name='invalidLine')(liftValue)

# Tables

# TODO: replace CSS attributes with classic tag attributes
CSS_chars = Sequence([NextNot(Choice([PIPE, BANG, L_BRACE], expression='PIPE/BANG/L_BRACE'), expression='!(PIPE/BANG/L_BRACE)'), anyChar], expression='!(PIPE/BANG/L_BRACE) anyChar', name='CSS_chars')
CSS_text = Repetition(CSS_chars, numMin=1, numMax=False, expression='CSS_chars+', name='CSS_text')(join)
CSS_attributes = Sequence([Repetition(CSS_text, numMin=1, numMax=False, expression='CSS_text+'), PIPE, NextNot(PIPE, expression='!PIPE')], expression='CSS_text+ PIPE !PIPE', name='CSS_attributes')(liftValue)
wikiTableParameters = Repetition(Choice([CSS_text, cleanInline], expression='CSS_text / cleanInline'), numMin=1, numMax=False, expression='(CSS_text / cleanInline)+', name='wikiTableParameters')(liftValue)
wikiTableFirstCell = Sequence([Repetition(CSS_attributes, numMin=0, numMax=1, expression='CSS_attributes{0..1}'), Repetition(cleanInline, numMin=False, numMax=False, expression='cleanInline*')], expression='CSS_attributes{0..1} cleanInline*', name='wikiTableFirstCell')(liftValue)
wikiTableOtherCell = Sequence([Repetition(PIPE, numMin=2, numMax=2, expression='PIPE{2}'), wikiTableFirstCell], expression='PIPE{2} wikiTableFirstCell', name='wikiTableOtherCell')(liftValue)
wikiTableLineCells = Sequence([PIPE, wikiTableFirstCell, Repetition(wikiTableOtherCell, numMin=False, numMax=False, expression='wikiTableOtherCell*'), EOL], expression='PIPE wikiTableFirstCell wikiTableOtherCell* EOL', name='wikiTableLineCells')(liftValue)
wikiTableLineHeader = Sequence([BANG, wikiTableFirstCell, Repetition(wikiTableOtherCell, numMin=False, numMax=False, expression='wikiTableOtherCell*'), EOL], expression='BANG wikiTableFirstCell wikiTableOtherCell* EOL', name='wikiTableLineHeader')(liftValue)
wikiTableEmptyCell = Sequence([PIPE, EOL], expression='PIPE EOL', name='wikiTableEmptyCell')(setNullValue)
wikiTableParamLineBreak = Sequence([TABLE_NEWLINE, Repetition(wikiTableParameters, numMin=False, numMax=False, expression='wikiTableParameters*'), EOL], expression='TABLE_NEWLINE wikiTableParameters* EOL', name='wikiTableParamLineBreak')(liftValue)
wikiTableLineBreak = Sequence([TABLE_NEWLINE, EOL], expression='TABLE_NEWLINE EOL', name='wikiTableLineBreak')(setNullValue)
wikiTableTitle = Sequence([TABLE_TITLE, Repetition(CSS_attributes, numMin=0, numMax=1, expression='CSS_attributes{0..1}'), Repetition(inline, numMin=False, numMax=False, expression='inline*'), EOL], expression='TABLE_TITLE CSS_attributes{0..1} inline* EOL', name='wikiTableTitle')(liftValue)
wikiTableSpecialLine = Choice([wikiTableTitle, wikiTableLineBreak, wikiTableParamLineBreak], expression='wikiTableTitle / wikiTableLineBreak / wikiTableParamLineBreak', name='wikiTableSpecialLine')
wikiTableNormalLine = Choice([wikiTableLineCells, wikiTableLineHeader, wikiTableEmptyCell], expression='wikiTableLineCells / wikiTableLineHeader / wikiTableEmptyCell', name='wikiTableNormalLine')
wikiTableLine = Sequence([NextNot(TABLE_END, expression='!TABLE_END'), Choice([wikiTableSpecialLine, wikiTableNormalLine], expression='wikiTableSpecialLine / wikiTableNormalLine')], expression='!TABLE_END (wikiTableSpecialLine / wikiTableNormalLine)', name='wikiTableLine')
wikiTableContent = Choice([wikiTableLine, wikiTable, EOL], expression='wikiTableLine / wikiTable / EOL', name='wikiTableContent')
wikiTableBegin = Sequence([TABLE_BEGIN, Repetition(wikiTableParameters, numMin=False, numMax=False, expression='wikiTableParameters*')], expression='TABLE_BEGIN wikiTableParameters*', name='wikiTableBegin')(liftValue)
wikiTable **= Sequence([wikiTableBegin, Repetition(EOL, numMin=False, numMax=False, expression='EOL*'), Repetition(wikiTableContent, numMin=False, numMax=False, expression='wikiTableContent*'), TABLE_END, EOL], expression='wikiTableBegin EOL* wikiTableContent* TABLE_END EOL', name='wikiTable')(liftValue)

# Top pattern

body = Sequence([optional_comment, Repetition(Choice([list, horizontalRule, preformattedGroup, title, wikiTable, EOL, paragraphs, invalidLine, EOL], expression='list / horizontalRule / preformattedGroup / title / wikiTable / EOL / paragraphs / invalidLine / EOL'), numMin=1, numMax=False, expression='(list / horizontalRule / preformattedGroup / title / wikiTable / EOL / paragraphs / invalidLine / EOL)+')], expression='optional_comment (list / horizontalRule / preformattedGroup / title / wikiTable / EOL / paragraphs / invalidLine / EOL)+', name='body')(liftValue)



wikitextParser._recordPatterns(vars())
wikitextParser._setTopPattern("body")
wikitextParser.grammarTitle = "wikitext"
wikitextParser.filename = "wikitextParser.py"
