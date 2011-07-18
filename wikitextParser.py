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
    LINK_BEGIN              : L_BRACKET{2}                                                          : drop
    LINK_END                : R_BRACKET{2}                                                          : drop

# Protocols

    HTTPS                   : "https://"                                                            : liftValue
    HTTP                    : "http://"                                                             : liftValue
    FTP                     : "ftp://"                                                              : liftValue
    protocol                : HTTPS / HTTP / FTP                                                    : liftValue

# Predefined tags

    NOWIKI_BEGIN            : "<nowiki>"                                                            : drop
    NOWIKI_END              : "</nowiki>"                                                           : drop
    PRE_BEGIN               : "<pre>"                                                               : drop
    PRE_END                 : "</pre>"                                                              : drop
    SPECIAL_TAG             : NOWIKI_BEGIN/NOWIKI_END/PRE_BEGIN/PRE_END

# Characters

    ESC_CHAR                : L_BRACKET/R_BRACKET/protocol/PIPE/L_BRACE/R_BRACE/LT/GT/SLASH/AMP/SEMICOLON
    TITLE_END               : TITLE6_END/TITLE5_END/TITLE4_END/TITLE3_END/TITLE2_END/TITLE1_END
    ESC_SEQ                 : SPECIAL_TAG / ESC_CHAR / TITLE_END
    raw_char                : !ESC_SEQ [\x20..\xff]
    raw_text                : raw_char+                                                             : join render_raw_text
    alpha_num               : [a..zA..Z0..9]
    alpha_num_text          : alpha_num+                                                            : join
    any_char                : [\x20..\xff]
    any_text                : any_char+                                                             : join

# HTML tags

    value_quote             : QUOTE ((!(GT/QUOTE) any_char) / TAB)+ QUOTE                           : join
    value_apostrophe        : APOSTROPHE ((!(GT/APOSTROPHE) any_char) / TAB)+ APOSTROPHE            : join
    value_noquote           : (!(GT/SPACETAB/SLASH) raw_char)+                                      : join
    attribute_value         : (EQUAL (value_quote / value_apostrophe / value_noquote))?             : liftNode
    attribute_name          : (!(EQUAL/SLASH/SPACETAB) raw_char)+                                   : join
    tag_name                : (!(SPACE/SLASH) raw_char)+                                            : join
    optional_attribute      : SPACETABEOL+ attribute_name attribute_value
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

    page_name               : raw_char+                                                             : join
# TODO: allow IPv6 addresses (http://[::1]/etc)
    address                 : (!(QUOTE/R_BRACKET) [\x21..\xff])+                                    : liftValue
    url                     : protocol address                                                      : join

# Links

    allowed_in_link         : (!(R_BRACKET/PIPE) ESC_CHAR)+                                         : restore join
    link_text               : (clean_inline / allowed_in_link)*                                     : liftValue
    link_argument           : PIPE link_text                                                        : liftValue
    link_arguments          : link_argument*
    internal_link           : LINK_BEGIN page_name link_arguments LINK_END                          : liftValue
    optional_link_text      : SPACETAB+ link_text                                                   : liftValue
    external_link           : L_BRACKET url optional_link_text? R_BRACKET 
    link                    : internal_link / external_link

# Pre and nowiki tags

    # Preformatted acts like nowiki (disables wikitext parsing)
    pre_text                : (!PRE_END any_char)*                                                  : join
    preformatted            : PRE_BEGIN pre_text PRE_END                                            : liftValue
    # We allow any char without parsing them as long as the tag is not closed
    eol_to_space            : EOL*                                                                  : replace_by_space
    nowiki_text             : (!NOWIKI_END (any_char/eol_to_space))*                                : join
    nowiki                  : NOWIKI_BEGIN nowiki_text NOWIKI_END                                   : liftValue

# Text types

    styled_text             : link / url / html_comment / tag / entity
    not_styled_text         : preformatted / nowiki
    allowed_char            : ESC_CHAR{1}                                                           : restore liftValue
    allowed_text            : raw_text / allowed_char
    clean_inline            : (not_styled_text / styled_text / raw_text)+                           : @
    inline                  : (not_styled_text / styled_text / allowed_text)+                       : @

# Paragraphs

    special_line_begin      : SPACE/EQUAL/BULLET/HASH/COLON/DASH{4}/TABLE_BEGIN/SEMICOLON
    paragraph_line          : !special_line_begin inline EOL                                        : liftValue
    blank_paragraph         : EOL{2}                                                                : drop keep
    paragraph               : paragraph_line+                                                       : liftValue render_paragraph
    paragraphs              : (blank_paragraph/EOL/paragraph)+

# Titles

    title6                  : TITLE6_BEGIN inline TITLE6_END                                        : liftValue
    title5                  : TITLE5_BEGIN inline TITLE5_END                                        : liftValue
    title4                  : TITLE4_BEGIN inline TITLE4_END                                        : liftValue
    title3                  : TITLE3_BEGIN inline TITLE3_END                                        : liftValue
    title2                  : TITLE2_BEGIN inline TITLE2_END                                        : liftValue render_title2
    title1                  : TITLE1_BEGIN inline TITLE1_END                                        : liftValue
    title                   : title6 / title5 / title4 / title3 / title2 / title1

# Lists

    LIST_CHAR               : BULLET / HASH / COLON / SEMICOLON
    list_leaf_content       : !LIST_CHAR inline EOL                                                 : liftValue

    bullet_list_leaf        : BULLET optional_comment list_leaf_content                             : liftValue
    bullet_sub_list         : BULLET optional_comment list_item                                     : @

    number_list_leaf        : HASH optional_comment list_leaf_content                               : liftValue
    number_sub_list         : HASH optional_comment list_item                                       : @

    colon_list_leaf         : COLON optional_comment list_leaf_content                              : liftValue
    colon_sub_list          : COLON optional_comment list_item                                      : @

    semi_colon_list_leaf    : SEMICOLON optional_comment list_leaf_content                          : liftValue
    semi_colon_sub_list     : SEMICOLON optional_comment list_item                                  : @

    list_leaf               : semi_colon_list_leaf/colon_list_leaf/number_list_leaf/bullet_list_leaf: @
    sub_list                : semi_colon_sub_list/colon_sub_list/number_sub_list/bullet_sub_list    : @
    list_item               : sub_list / list_leaf                                                  : @
    list                    : list_item+

# Preformatted

    EOL_or_not              : EOL{0..1}                                                             : drop
    preformatted_line       : SPACE inline EOL                                                      : liftValue
    preformatted_lines      : preformatted_line+
    preformatted_text       : inline EOL_or_not                                                     : liftValue
    preformatted_paragraph  : PRE_BEGIN EOL preformatted_text PRE_END EOL
    preformatted_group      : preformatted_paragraph / preformatted_lines

# Special lines

    horizontal_rule         : DASH{4} DASH* inline* EOL                                             : liftValue keep

    # This should never happen
    invalid_line            : any_text EOL                                                          : liftValue

# Tables

    HTML_value_quote        : QUOTE ((!(GT/QUOTE) any_char) / TAB)+ QUOTE                           : join
    HTML_value_apostrophe   : APOSTROPHE ((!(GT/APOSTROPHE) any_char) / TAB)+ APOSTROPHE            : join
    HTML_value_noquote      : (!(GT/SPACETAB/SLASH) raw_char)+                                      : join
    HTML_value              : HTML_value_quote / HTML_value_apostrophe / HTML_value_noquote
    HTML_name               : (!(EQUAL/SLASH/SPACETAB) raw_char)+                                   : join
    HTML_attribute          : SPACETAB* HTML_name EQUAL HTML_value SPACETAB*
    HTML_attributes         : HTML_attribute*
    table_parameters_pipe   : (SPACETAB* HTML_attribute+ SPACETAB* PIPE !PIPE)?                     : liftNode
    table_parameters        : (HTML_attribute / clean_inline)+                                      : liftValue
    table_parameter         : table_parameters_pipe{0..1}                                           : liftValue
    table_cell_content      : clean_inline*
    table_first_cell        : table_parameter table_cell_content                                    : liftNode
    table_other_cell        : (PIPE{2} table_first_cell)*                                           : liftValue liftNode
    table_line_cells        : PIPE table_first_cell table_other_cell EOL                            : liftValue
    table_line_header       : BANG table_first_cell table_other_cell EOL                            : liftValue
    table_empty_cell        : PIPE EOL                                                              : keep
    table_param_line_break  : TABLE_NEWLINE table_parameters* EOL                                   : keep liftValue
    table_line_break        : TABLE_NEWLINE EOL                                                     : keep
    table_title             : TABLE_TITLE table_parameter table_cell_content EOL                    : liftValue
    table_special_line      : table_title / table_line_break / table_param_line_break
    table_normal_line       : table_line_cells / table_line_header / table_empty_cell
    table_line              : !TABLE_END (table_special_line / table_normal_line)                   : liftNode
    table_content           : (table_line / table / EOL)*                                           : liftNode
    table_begin             : TABLE_BEGIN table_parameters*                                         : liftValue
    table                   : table_begin SPACETABEOL* table_content TABLE_END EOL                  : @ liftValue

# Top pattern

    wikitext                : list / horizontal_rule / preformatted_group / title / table / EOL / paragraphs
    body                    : optional_comment (wikitext/invalid_line)+                             : liftValue render_body

"""

from pijnu.library import *


def make_parser(actions=None):
    """Return a parser.

    The parser's toolset functions are (optionally) augmented (or overridden)
    by a map of additional ones passed in.

    """
    if actions is None:
        actions = {}

    # Start off with the imported pijnu library functions:
    toolset = globals().copy()

    parser = Parser()
    state = parser.state

### title: wikitext ###
    
    
    def toolset_from_grammar():
        """Return a map of toolset functions hard-coded into the grammar."""
    ###   <toolset>
        def replace_by_space(node):
            node.value = ' '
        
    
        return locals().copy()
    
    toolset.update(toolset_from_grammar())
    toolset.update(actions)
    
    ###   <definition>
    # recursive pattern(s)
    table = Recursive(name='table')
    list_item = Recursive(name='list_item')
    sub_list = Recursive(name='sub_list')
    list_leaf = Recursive(name='list_leaf')
    semi_colon_sub_list = Recursive(name='semi_colon_sub_list')
    colon_sub_list = Recursive(name='colon_sub_list')
    number_sub_list = Recursive(name='number_sub_list')
    bullet_sub_list = Recursive(name='bullet_sub_list')
    inline = Recursive(name='inline')
    clean_inline = Recursive(name='clean_inline')
    # Codes
    
    LF = Char('\n', expression="'\n'", name='LF')
    CR = Char('\n', expression="'\n'", name='CR')
    EOL = Choice([LF, CR], expression='LF / CR', name='EOL')(toolset['drop'])
    L_BRACKET = Word('[', expression='"["', name='L_BRACKET')(toolset['drop'])
    R_BRACKET = Word(']', expression='"\\]"', name='R_BRACKET')(toolset['drop'])
    L_BRACE = Word('{', expression='"{"', name='L_BRACE')(toolset['drop'])
    R_BRACE = Word('}', expression='"}"', name='R_BRACE')(toolset['drop'])
    SPACE = Word(' ', expression='" "', name='SPACE')(toolset['drop'])
    TAB = Word('\t', expression='"\t"', name='TAB')(toolset['drop'])
    SPACETAB = Choice([SPACE, TAB], expression='SPACE / TAB', name='SPACETAB')(toolset['drop'])
    SPACETABEOL = Choice([SPACE, TAB, EOL], expression='SPACE / TAB / EOL', name='SPACETABEOL')(toolset['drop'])
    AMP = Word('&', expression='"&"', name='AMP')(toolset['drop'])
    PIPE = Word('|', expression='"|"', name='PIPE')(toolset['drop'])
    BANG = Word('!', expression='"!"', name='BANG')(toolset['drop'])
    EQUAL = Word('=', expression='"="', name='EQUAL')(toolset['drop'])
    BULLET = Word('*', expression='"*"', name='BULLET')(toolset['drop'])
    HASH = Word('#', expression='"#"', name='HASH')(toolset['drop'])
    COLON = Word(':', expression='":"', name='COLON')(toolset['drop'])
    LT = Word('<', expression='"<"', name='LT')(toolset['drop'])
    GT = Word('>', expression='">"', name='GT')(toolset['drop'])
    SLASH = Word('/', expression='"/"', name='SLASH')(toolset['drop'])
    SEMICOLON = Word(';', expression='";"', name='SEMICOLON')(toolset['drop'])
    DASH = Word('-', expression='"-"', name='DASH')(toolset['drop'])
    TABLE_BEGIN = Word('{|', expression='"{|"', name='TABLE_BEGIN')(toolset['drop'])
    TABLE_END = Word('|}', expression='"|}"', name='TABLE_END')(toolset['drop'])
    TABLE_NEWLINE = Word('|-', expression='"|-"', name='TABLE_NEWLINE')(toolset['drop'])
    TABLE_TITLE = Word('|+', expression='"|+"', name='TABLE_TITLE')(toolset['drop'])
    QUOTE = Word('"', expression='"\\""', name='QUOTE')(toolset['drop'])
    APOSTROPHE = Word("'", expression='"\\\'"', name='APOSTROPHE')(toolset['drop'])
    TITLE6_BEGIN = Repetition(EQUAL, numMin=6, numMax=6, expression='EQUAL{6}', name='TITLE6_BEGIN')(toolset['drop'])
    TITLE5_BEGIN = Repetition(EQUAL, numMin=5, numMax=5, expression='EQUAL{5}', name='TITLE5_BEGIN')(toolset['drop'])
    TITLE4_BEGIN = Repetition(EQUAL, numMin=4, numMax=4, expression='EQUAL{4}', name='TITLE4_BEGIN')(toolset['drop'])
    TITLE3_BEGIN = Repetition(EQUAL, numMin=3, numMax=3, expression='EQUAL{3}', name='TITLE3_BEGIN')(toolset['drop'])
    TITLE2_BEGIN = Repetition(EQUAL, numMin=2, numMax=2, expression='EQUAL{2}', name='TITLE2_BEGIN')(toolset['drop'])
    TITLE1_BEGIN = Repetition(EQUAL, numMin=1, numMax=1, expression='EQUAL{1}', name='TITLE1_BEGIN')(toolset['drop'])
    TITLE6_END = Sequence([Repetition(EQUAL, numMin=6, numMax=6, expression='EQUAL{6}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{6} SPACETAB* EOL', name='TITLE6_END')(toolset['drop'])
    TITLE5_END = Sequence([Repetition(EQUAL, numMin=5, numMax=5, expression='EQUAL{5}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{5} SPACETAB* EOL', name='TITLE5_END')(toolset['drop'])
    TITLE4_END = Sequence([Repetition(EQUAL, numMin=4, numMax=4, expression='EQUAL{4}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{4} SPACETAB* EOL', name='TITLE4_END')(toolset['drop'])
    TITLE3_END = Sequence([Repetition(EQUAL, numMin=3, numMax=3, expression='EQUAL{3}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{3} SPACETAB* EOL', name='TITLE3_END')(toolset['drop'])
    TITLE2_END = Sequence([Repetition(EQUAL, numMin=2, numMax=2, expression='EQUAL{2}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{2} SPACETAB* EOL', name='TITLE2_END')(toolset['drop'])
    TITLE1_END = Sequence([Repetition(EQUAL, numMin=1, numMax=1, expression='EQUAL{1}'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), EOL], expression='EQUAL{1} SPACETAB* EOL', name='TITLE1_END')(toolset['drop'])
    LINK_BEGIN = Repetition(L_BRACKET, numMin=2, numMax=2, expression='L_BRACKET{2}', name='LINK_BEGIN')(toolset['drop'])
    LINK_END = Repetition(R_BRACKET, numMin=2, numMax=2, expression='R_BRACKET{2}', name='LINK_END')(toolset['drop'])
    
    # Protocols
    
    HTTPS = Word('https://', expression='"https://"', name='HTTPS')(toolset['liftValue'])
    HTTP = Word('http://', expression='"http://"', name='HTTP')(toolset['liftValue'])
    FTP = Word('ftp://', expression='"ftp://"', name='FTP')(toolset['liftValue'])
    protocol = Choice([HTTPS, HTTP, FTP], expression='HTTPS / HTTP / FTP', name='protocol')(toolset['liftValue'])
    
    # Predefined tags
    
    NOWIKI_BEGIN = Word('<nowiki>', expression='"<nowiki>"', name='NOWIKI_BEGIN')(toolset['drop'])
    NOWIKI_END = Word('</nowiki>', expression='"</nowiki>"', name='NOWIKI_END')(toolset['drop'])
    PRE_BEGIN = Word('<pre>', expression='"<pre>"', name='PRE_BEGIN')(toolset['drop'])
    PRE_END = Word('</pre>', expression='"</pre>"', name='PRE_END')(toolset['drop'])
    SPECIAL_TAG = Choice([NOWIKI_BEGIN, NOWIKI_END, PRE_BEGIN, PRE_END], expression='NOWIKI_BEGIN/NOWIKI_END/PRE_BEGIN/PRE_END', name='SPECIAL_TAG')
    
    # Characters
    
    ESC_CHAR = Choice([L_BRACKET, R_BRACKET, protocol, PIPE, L_BRACE, R_BRACE, LT, GT, SLASH, AMP, SEMICOLON], expression='L_BRACKET/R_BRACKET/protocol/PIPE/L_BRACE/R_BRACE/LT/GT/SLASH/AMP/SEMICOLON', name='ESC_CHAR')
    TITLE_END = Choice([TITLE6_END, TITLE5_END, TITLE4_END, TITLE3_END, TITLE2_END, TITLE1_END], expression='TITLE6_END/TITLE5_END/TITLE4_END/TITLE3_END/TITLE2_END/TITLE1_END', name='TITLE_END')
    ESC_SEQ = Choice([SPECIAL_TAG, ESC_CHAR, TITLE_END], expression='SPECIAL_TAG / ESC_CHAR / TITLE_END', name='ESC_SEQ')
    raw_char = Sequence([NextNot(ESC_SEQ, expression='!ESC_SEQ'), Klass(u' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x20..\\xff]')], expression='!ESC_SEQ [\\x20..\\xff]', name='raw_char')
    raw_text = Repetition(raw_char, numMin=1, numMax=False, expression='raw_char+', name='raw_text')(toolset['join'], toolset['render_raw_text'])
    alpha_num = Klass(u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', expression='[a..zA..Z0..9]', name='alpha_num')
    alpha_num_text = Repetition(alpha_num, numMin=1, numMax=False, expression='alpha_num+', name='alpha_num_text')(toolset['join'])
    any_char = Klass(u' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x20..\\xff]', name='any_char')
    any_text = Repetition(any_char, numMin=1, numMax=False, expression='any_char+', name='any_text')(toolset['join'])
    
    # HTML tags
    
    value_quote = Sequence([QUOTE, Repetition(Choice([Sequence([NextNot(Choice([GT, QUOTE], expression='GT/QUOTE'), expression='!(GT/QUOTE)'), any_char], expression='!(GT/QUOTE) any_char'), TAB], expression='(!(GT/QUOTE) any_char) / TAB'), numMin=1, numMax=False, expression='((!(GT/QUOTE) any_char) / TAB)+'), QUOTE], expression='QUOTE ((!(GT/QUOTE) any_char) / TAB)+ QUOTE', name='value_quote')(toolset['join'])
    value_apostrophe = Sequence([APOSTROPHE, Repetition(Choice([Sequence([NextNot(Choice([GT, APOSTROPHE], expression='GT/APOSTROPHE'), expression='!(GT/APOSTROPHE)'), any_char], expression='!(GT/APOSTROPHE) any_char'), TAB], expression='(!(GT/APOSTROPHE) any_char) / TAB'), numMin=1, numMax=False, expression='((!(GT/APOSTROPHE) any_char) / TAB)+'), APOSTROPHE], expression='APOSTROPHE ((!(GT/APOSTROPHE) any_char) / TAB)+ APOSTROPHE', name='value_apostrophe')(toolset['join'])
    value_noquote = Repetition(Sequence([NextNot(Choice([GT, SPACETAB, SLASH], expression='GT/SPACETAB/SLASH'), expression='!(GT/SPACETAB/SLASH)'), raw_char], expression='!(GT/SPACETAB/SLASH) raw_char'), numMin=1, numMax=False, expression='(!(GT/SPACETAB/SLASH) raw_char)+', name='value_noquote')(toolset['join'])
    attribute_value = Option(Sequence([EQUAL, Choice([value_quote, value_apostrophe, value_noquote], expression='value_quote / value_apostrophe / value_noquote')], expression='EQUAL (value_quote / value_apostrophe / value_noquote)'), expression='(EQUAL (value_quote / value_apostrophe / value_noquote))?', name='attribute_value')(toolset['liftNode'])
    attribute_name = Repetition(Sequence([NextNot(Choice([EQUAL, SLASH, SPACETAB], expression='EQUAL/SLASH/SPACETAB'), expression='!(EQUAL/SLASH/SPACETAB)'), raw_char], expression='!(EQUAL/SLASH/SPACETAB) raw_char'), numMin=1, numMax=False, expression='(!(EQUAL/SLASH/SPACETAB) raw_char)+', name='attribute_name')(toolset['join'])
    tag_name = Repetition(Sequence([NextNot(Choice([SPACE, SLASH], expression='SPACE/SLASH'), expression='!(SPACE/SLASH)'), raw_char], expression='!(SPACE/SLASH) raw_char'), numMin=1, numMax=False, expression='(!(SPACE/SLASH) raw_char)+', name='tag_name')(toolset['join'])
    optional_attribute = Sequence([Repetition(SPACETABEOL, numMin=1, numMax=False, expression='SPACETABEOL+'), attribute_name, attribute_value], expression='SPACETABEOL+ attribute_name attribute_value', name='optional_attribute')
    optional_attributes = Repetition(optional_attribute, numMin=False, numMax=False, expression='optional_attribute*', name='optional_attributes')
    tag_open = Sequence([LT, tag_name, optional_attributes, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), GT], expression='LT tag_name optional_attributes SPACETABEOL* GT', name='tag_open')
    tag_close = Sequence([LT, SLASH, tag_name, GT], expression='LT SLASH tag_name GT', name='tag_close')
    tag_autoclose = Sequence([LT, tag_name, optional_attributes, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), SLASH, GT], expression='LT tag_name optional_attributes SPACETABEOL* SLASH GT', name='tag_autoclose')
    tag = Choice([tag_autoclose, tag_open, tag_close], expression='tag_autoclose / tag_open / tag_close', name='tag')
    
    # HTML entities
    
    entity = Sequence([AMP, alpha_num_text, SEMICOLON], expression='AMP alpha_num_text SEMICOLON', name='entity')(toolset['liftValue'])
    
    # HTML comments
    
        # HTML comments are totally ignored and do not appear in the final text
    comment_content = Repetition(Choice([Repetition(Sequence([NextNot(Sequence([Repetition(DASH, numMin=2, numMax=2, expression='DASH{2}'), GT], expression='DASH{2} GT'), expression='!(DASH{2} GT)'), Klass(u' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x20..\\xff]')], expression='!(DASH{2} GT) [\\x20..\\xff]'), numMin=1, numMax=False, expression='(!(DASH{2} GT) [\\x20..\\xff])+'), SPACETABEOL], expression='(!(DASH{2} GT) [\\x20..\\xff])+ / SPACETABEOL'), numMin=False, numMax=False, expression='((!(DASH{2} GT) [\\x20..\\xff])+ / SPACETABEOL)*', name='comment_content')
    html_comment = Sequence([LT, BANG, Repetition(DASH, numMin=2, numMax=2, expression='DASH{2}'), comment_content, Repetition(DASH, numMin=2, numMax=2, expression='DASH{2}'), GT], expression='LT BANG DASH{2} comment_content DASH{2} GT', name='html_comment')(toolset['drop'])
    optional_comment = Repetition(html_comment, numMin=False, numMax=False, expression='html_comment*', name='optional_comment')
    
    # Text
    
    page_name = Repetition(raw_char, numMin=1, numMax=False, expression='raw_char+', name='page_name')(toolset['join'])
    # TODO: allow IPv6 addresses (http://[::1]/etc)
    address = Repetition(Sequence([NextNot(Choice([QUOTE, R_BRACKET], expression='QUOTE/R_BRACKET'), expression='!(QUOTE/R_BRACKET)'), Klass(u'!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff', expression='[\\x21..\\xff]')], expression='!(QUOTE/R_BRACKET) [\\x21..\\xff]'), numMin=1, numMax=False, expression='(!(QUOTE/R_BRACKET) [\\x21..\\xff])+', name='address')(toolset['liftValue'])
    url = Sequence([protocol, address], expression='protocol address', name='url')(toolset['join'])
    
    # Links
    
    allowed_in_link = Repetition(Sequence([NextNot(Choice([R_BRACKET, PIPE], expression='R_BRACKET/PIPE'), expression='!(R_BRACKET/PIPE)'), ESC_CHAR], expression='!(R_BRACKET/PIPE) ESC_CHAR'), numMin=1, numMax=False, expression='(!(R_BRACKET/PIPE) ESC_CHAR)+', name='allowed_in_link')(toolset['restore'], toolset['join'])
    link_text = Repetition(Choice([clean_inline, allowed_in_link], expression='clean_inline / allowed_in_link'), numMin=False, numMax=False, expression='(clean_inline / allowed_in_link)*', name='link_text')(toolset['liftValue'])
    link_argument = Sequence([PIPE, link_text], expression='PIPE link_text', name='link_argument')(toolset['liftValue'])
    link_arguments = Repetition(link_argument, numMin=False, numMax=False, expression='link_argument*', name='link_arguments')
    internal_link = Sequence([LINK_BEGIN, page_name, link_arguments, LINK_END], expression='LINK_BEGIN page_name link_arguments LINK_END', name='internal_link')(toolset['liftValue'])
    optional_link_text = Sequence([Repetition(SPACETAB, numMin=1, numMax=False, expression='SPACETAB+'), link_text], expression='SPACETAB+ link_text', name='optional_link_text')(toolset['liftValue'])
    external_link = Sequence([L_BRACKET, url, Option(optional_link_text, expression='optional_link_text?'), R_BRACKET], expression='L_BRACKET url optional_link_text? R_BRACKET', name='external_link')
    link = Choice([internal_link, external_link], expression='internal_link / external_link', name='link')
    
    # Pre and nowiki tags
    
        # Preformatted acts like nowiki (disables wikitext parsing)
    pre_text = Repetition(Sequence([NextNot(PRE_END, expression='!PRE_END'), any_char], expression='!PRE_END any_char'), numMin=False, numMax=False, expression='(!PRE_END any_char)*', name='pre_text')(toolset['join'])
    preformatted = Sequence([PRE_BEGIN, pre_text, PRE_END], expression='PRE_BEGIN pre_text PRE_END', name='preformatted')(toolset['liftValue'])
        # We allow any char without parsing them as long as the tag is not closed
    eol_to_space = Repetition(EOL, numMin=False, numMax=False, expression='EOL*', name='eol_to_space')(toolset['replace_by_space'])
    nowiki_text = Repetition(Sequence([NextNot(NOWIKI_END, expression='!NOWIKI_END'), Choice([any_char, eol_to_space], expression='any_char/eol_to_space')], expression='!NOWIKI_END (any_char/eol_to_space)'), numMin=False, numMax=False, expression='(!NOWIKI_END (any_char/eol_to_space))*', name='nowiki_text')(toolset['join'])
    nowiki = Sequence([NOWIKI_BEGIN, nowiki_text, NOWIKI_END], expression='NOWIKI_BEGIN nowiki_text NOWIKI_END', name='nowiki')(toolset['liftValue'])
    
    # Text types
    
    styled_text = Choice([link, url, html_comment, tag, entity], expression='link / url / html_comment / tag / entity', name='styled_text')
    not_styled_text = Choice([preformatted, nowiki], expression='preformatted / nowiki', name='not_styled_text')
    allowed_char = Repetition(ESC_CHAR, numMin=1, numMax=1, expression='ESC_CHAR{1}', name='allowed_char')(toolset['restore'], toolset['liftValue'])
    allowed_text = Choice([raw_text, allowed_char], expression='raw_text / allowed_char', name='allowed_text')
    clean_inline **= Repetition(Choice([not_styled_text, styled_text, raw_text], expression='not_styled_text / styled_text / raw_text'), numMin=1, numMax=False, expression='(not_styled_text / styled_text / raw_text)+', name='clean_inline')
    inline **= Repetition(Choice([not_styled_text, styled_text, allowed_text], expression='not_styled_text / styled_text / allowed_text'), numMin=1, numMax=False, expression='(not_styled_text / styled_text / allowed_text)+', name='inline')
    
    # Paragraphs
    
    special_line_begin = Choice([SPACE, EQUAL, BULLET, HASH, COLON, Repetition(DASH, numMin=4, numMax=4, expression='DASH{4}'), TABLE_BEGIN, SEMICOLON], expression='SPACE/EQUAL/BULLET/HASH/COLON/DASH{4}/TABLE_BEGIN/SEMICOLON', name='special_line_begin')
    paragraph_line = Sequence([NextNot(special_line_begin, expression='!special_line_begin'), inline, EOL], expression='!special_line_begin inline EOL', name='paragraph_line')(toolset['liftValue'])
    blank_paragraph = Repetition(EOL, numMin=2, numMax=2, expression='EOL{2}', name='blank_paragraph')(toolset['drop'], toolset['keep'])
    paragraph = Repetition(paragraph_line, numMin=1, numMax=False, expression='paragraph_line+', name='paragraph')(toolset['liftValue'], toolset['render_paragraph'])
    paragraphs = Repetition(Choice([blank_paragraph, EOL, paragraph], expression='blank_paragraph/EOL/paragraph'), numMin=1, numMax=False, expression='(blank_paragraph/EOL/paragraph)+', name='paragraphs')
    
    # Titles
    
    title6 = Sequence([TITLE6_BEGIN, inline, TITLE6_END], expression='TITLE6_BEGIN inline TITLE6_END', name='title6')(toolset['liftValue'])
    title5 = Sequence([TITLE5_BEGIN, inline, TITLE5_END], expression='TITLE5_BEGIN inline TITLE5_END', name='title5')(toolset['liftValue'])
    title4 = Sequence([TITLE4_BEGIN, inline, TITLE4_END], expression='TITLE4_BEGIN inline TITLE4_END', name='title4')(toolset['liftValue'])
    title3 = Sequence([TITLE3_BEGIN, inline, TITLE3_END], expression='TITLE3_BEGIN inline TITLE3_END', name='title3')(toolset['liftValue'])
    title2 = Sequence([TITLE2_BEGIN, inline, TITLE2_END], expression='TITLE2_BEGIN inline TITLE2_END', name='title2')(toolset['liftValue'], toolset['render_title2'])
    title1 = Sequence([TITLE1_BEGIN, inline, TITLE1_END], expression='TITLE1_BEGIN inline TITLE1_END', name='title1')(toolset['liftValue'])
    title = Choice([title6, title5, title4, title3, title2, title1], expression='title6 / title5 / title4 / title3 / title2 / title1', name='title')
    
    # Lists
    
    LIST_CHAR = Choice([BULLET, HASH, COLON, SEMICOLON], expression='BULLET / HASH / COLON / SEMICOLON', name='LIST_CHAR')
    list_leaf_content = Sequence([NextNot(LIST_CHAR, expression='!LIST_CHAR'), inline, EOL], expression='!LIST_CHAR inline EOL', name='list_leaf_content')(toolset['liftValue'])
    
    bullet_list_leaf = Sequence([BULLET, optional_comment, list_leaf_content], expression='BULLET optional_comment list_leaf_content', name='bullet_list_leaf')(toolset['liftValue'])
    bullet_sub_list **= Sequence([BULLET, optional_comment, list_item], expression='BULLET optional_comment list_item', name='bullet_sub_list')
    
    number_list_leaf = Sequence([HASH, optional_comment, list_leaf_content], expression='HASH optional_comment list_leaf_content', name='number_list_leaf')(toolset['liftValue'])
    number_sub_list **= Sequence([HASH, optional_comment, list_item], expression='HASH optional_comment list_item', name='number_sub_list')
    
    colon_list_leaf = Sequence([COLON, optional_comment, list_leaf_content], expression='COLON optional_comment list_leaf_content', name='colon_list_leaf')(toolset['liftValue'])
    colon_sub_list **= Sequence([COLON, optional_comment, list_item], expression='COLON optional_comment list_item', name='colon_sub_list')
    
    semi_colon_list_leaf = Sequence([SEMICOLON, optional_comment, list_leaf_content], expression='SEMICOLON optional_comment list_leaf_content', name='semi_colon_list_leaf')(toolset['liftValue'])
    semi_colon_sub_list **= Sequence([SEMICOLON, optional_comment, list_item], expression='SEMICOLON optional_comment list_item', name='semi_colon_sub_list')
    
    list_leaf **= Choice([semi_colon_list_leaf, colon_list_leaf, number_list_leaf, bullet_list_leaf], expression='semi_colon_list_leaf/colon_list_leaf/number_list_leaf/bullet_list_leaf', name='list_leaf')
    sub_list **= Choice([semi_colon_sub_list, colon_sub_list, number_sub_list, bullet_sub_list], expression='semi_colon_sub_list/colon_sub_list/number_sub_list/bullet_sub_list', name='sub_list')
    list_item **= Choice([sub_list, list_leaf], expression='sub_list / list_leaf', name='list_item')
    list = Repetition(list_item, numMin=1, numMax=False, expression='list_item+', name='list')
    
    # Preformatted
    
    EOL_or_not = Repetition(EOL, numMin=0, numMax=1, expression='EOL{0..1}', name='EOL_or_not')(toolset['drop'])
    preformatted_line = Sequence([SPACE, inline, EOL], expression='SPACE inline EOL', name='preformatted_line')(toolset['liftValue'])
    preformatted_lines = Repetition(preformatted_line, numMin=1, numMax=False, expression='preformatted_line+', name='preformatted_lines')
    preformatted_text = Sequence([inline, EOL_or_not], expression='inline EOL_or_not', name='preformatted_text')(toolset['liftValue'])
    preformatted_paragraph = Sequence([PRE_BEGIN, EOL, preformatted_text, PRE_END, EOL], expression='PRE_BEGIN EOL preformatted_text PRE_END EOL', name='preformatted_paragraph')
    preformatted_group = Choice([preformatted_paragraph, preformatted_lines], expression='preformatted_paragraph / preformatted_lines', name='preformatted_group')
    
    # Special lines
    
    horizontal_rule = Sequence([Repetition(DASH, numMin=4, numMax=4, expression='DASH{4}'), Repetition(DASH, numMin=False, numMax=False, expression='DASH*'), Repetition(inline, numMin=False, numMax=False, expression='inline*'), EOL], expression='DASH{4} DASH* inline* EOL', name='horizontal_rule')(toolset['liftValue'], toolset['keep'])
    
        # This should never happen
    invalid_line = Sequence([any_text, EOL], expression='any_text EOL', name='invalid_line')(toolset['liftValue'])
    
    # Tables
    
    HTML_value_quote = Sequence([QUOTE, Repetition(Choice([Sequence([NextNot(Choice([GT, QUOTE], expression='GT/QUOTE'), expression='!(GT/QUOTE)'), any_char], expression='!(GT/QUOTE) any_char'), TAB], expression='(!(GT/QUOTE) any_char) / TAB'), numMin=1, numMax=False, expression='((!(GT/QUOTE) any_char) / TAB)+'), QUOTE], expression='QUOTE ((!(GT/QUOTE) any_char) / TAB)+ QUOTE', name='HTML_value_quote')(toolset['join'])
    HTML_value_apostrophe = Sequence([APOSTROPHE, Repetition(Choice([Sequence([NextNot(Choice([GT, APOSTROPHE], expression='GT/APOSTROPHE'), expression='!(GT/APOSTROPHE)'), any_char], expression='!(GT/APOSTROPHE) any_char'), TAB], expression='(!(GT/APOSTROPHE) any_char) / TAB'), numMin=1, numMax=False, expression='((!(GT/APOSTROPHE) any_char) / TAB)+'), APOSTROPHE], expression='APOSTROPHE ((!(GT/APOSTROPHE) any_char) / TAB)+ APOSTROPHE', name='HTML_value_apostrophe')(toolset['join'])
    HTML_value_noquote = Repetition(Sequence([NextNot(Choice([GT, SPACETAB, SLASH], expression='GT/SPACETAB/SLASH'), expression='!(GT/SPACETAB/SLASH)'), raw_char], expression='!(GT/SPACETAB/SLASH) raw_char'), numMin=1, numMax=False, expression='(!(GT/SPACETAB/SLASH) raw_char)+', name='HTML_value_noquote')(toolset['join'])
    HTML_value = Choice([HTML_value_quote, HTML_value_apostrophe, HTML_value_noquote], expression='HTML_value_quote / HTML_value_apostrophe / HTML_value_noquote', name='HTML_value')
    HTML_name = Repetition(Sequence([NextNot(Choice([EQUAL, SLASH, SPACETAB], expression='EQUAL/SLASH/SPACETAB'), expression='!(EQUAL/SLASH/SPACETAB)'), raw_char], expression='!(EQUAL/SLASH/SPACETAB) raw_char'), numMin=1, numMax=False, expression='(!(EQUAL/SLASH/SPACETAB) raw_char)+', name='HTML_name')(toolset['join'])
    HTML_attribute = Sequence([Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), HTML_name, EQUAL, HTML_value, Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*')], expression='SPACETAB* HTML_name EQUAL HTML_value SPACETAB*', name='HTML_attribute')
    HTML_attributes = Repetition(HTML_attribute, numMin=False, numMax=False, expression='HTML_attribute*', name='HTML_attributes')
    table_parameters_pipe = Option(Sequence([Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), Repetition(HTML_attribute, numMin=1, numMax=False, expression='HTML_attribute+'), Repetition(SPACETAB, numMin=False, numMax=False, expression='SPACETAB*'), PIPE, NextNot(PIPE, expression='!PIPE')], expression='SPACETAB* HTML_attribute+ SPACETAB* PIPE !PIPE'), expression='(SPACETAB* HTML_attribute+ SPACETAB* PIPE !PIPE)?', name='table_parameters_pipe')(toolset['liftNode'])
    table_parameters = Repetition(Choice([HTML_attribute, clean_inline], expression='HTML_attribute / clean_inline'), numMin=1, numMax=False, expression='(HTML_attribute / clean_inline)+', name='table_parameters')(toolset['liftValue'])
    table_parameter = Repetition(table_parameters_pipe, numMin=0, numMax=1, expression='table_parameters_pipe{0..1}', name='table_parameter')(toolset['liftValue'])
    table_cell_content = Repetition(clean_inline, numMin=False, numMax=False, expression='clean_inline*', name='table_cell_content')
    table_first_cell = Sequence([table_parameter, table_cell_content], expression='table_parameter table_cell_content', name='table_first_cell')(toolset['liftNode'])
    table_other_cell = Repetition(Sequence([Repetition(PIPE, numMin=2, numMax=2, expression='PIPE{2}'), table_first_cell], expression='PIPE{2} table_first_cell'), numMin=False, numMax=False, expression='(PIPE{2} table_first_cell)*', name='table_other_cell')(toolset['liftValue'], toolset['liftNode'])
    table_line_cells = Sequence([PIPE, table_first_cell, table_other_cell, EOL], expression='PIPE table_first_cell table_other_cell EOL', name='table_line_cells')(toolset['liftValue'])
    table_line_header = Sequence([BANG, table_first_cell, table_other_cell, EOL], expression='BANG table_first_cell table_other_cell EOL', name='table_line_header')(toolset['liftValue'])
    table_empty_cell = Sequence([PIPE, EOL], expression='PIPE EOL', name='table_empty_cell')(toolset['keep'])
    table_param_line_break = Sequence([TABLE_NEWLINE, Repetition(table_parameters, numMin=False, numMax=False, expression='table_parameters*'), EOL], expression='TABLE_NEWLINE table_parameters* EOL', name='table_param_line_break')(toolset['keep'], toolset['liftValue'])
    table_line_break = Sequence([TABLE_NEWLINE, EOL], expression='TABLE_NEWLINE EOL', name='table_line_break')(toolset['keep'])
    table_title = Sequence([TABLE_TITLE, table_parameter, table_cell_content, EOL], expression='TABLE_TITLE table_parameter table_cell_content EOL', name='table_title')(toolset['liftValue'])
    table_special_line = Choice([table_title, table_line_break, table_param_line_break], expression='table_title / table_line_break / table_param_line_break', name='table_special_line')
    table_normal_line = Choice([table_line_cells, table_line_header, table_empty_cell], expression='table_line_cells / table_line_header / table_empty_cell', name='table_normal_line')
    table_line = Sequence([NextNot(TABLE_END, expression='!TABLE_END'), Choice([table_special_line, table_normal_line], expression='table_special_line / table_normal_line')], expression='!TABLE_END (table_special_line / table_normal_line)', name='table_line')(toolset['liftNode'])
    table_content = Repetition(Choice([table_line, table, EOL], expression='table_line / table / EOL'), numMin=False, numMax=False, expression='(table_line / table / EOL)*', name='table_content')(toolset['liftNode'])
    table_begin = Sequence([TABLE_BEGIN, Repetition(table_parameters, numMin=False, numMax=False, expression='table_parameters*')], expression='TABLE_BEGIN table_parameters*', name='table_begin')(toolset['liftValue'])
    table **= Sequence([table_begin, Repetition(SPACETABEOL, numMin=False, numMax=False, expression='SPACETABEOL*'), table_content, TABLE_END, EOL], expression='table_begin SPACETABEOL* table_content TABLE_END EOL', name='table')(toolset['liftValue'])
    
    # Top pattern
    
    wikitext = Choice([list, horizontal_rule, preformatted_group, title, table, EOL, paragraphs], expression='list / horizontal_rule / preformatted_group / title / table / EOL / paragraphs', name='wikitext')
    body = Sequence([optional_comment, Repetition(Choice([wikitext, invalid_line], expression='wikitext/invalid_line'), numMin=1, numMax=False, expression='(wikitext/invalid_line)+')], expression='optional_comment (wikitext/invalid_line)+', name='body')(toolset['liftValue'], toolset['render_body'])

    symbols = locals().copy()
    symbols.update(actions)
    parser._recordPatterns(symbols)
    parser._setTopPattern("body")
    parser.grammarTitle = "wikitext"
    parser.filename = "wikitextParser.py"

    return parser
