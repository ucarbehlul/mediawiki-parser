# -*- coding: utf8 -*-
# get the parser
from pijnu import makeParser
mediawikiGrammar = file("mediawiki.pijnu").read()
mediawikiParser = makeParser(mediawikiGrammar)


print "\n\n== Testing titles =="

test_suite_dict = {
    '=Title 1=\n' : "[title1:[rawText:'Title 1']]",
    '== Title 2 ==\n' : "[title2:[rawText:' Title 2 ']]",
    '===Title 3===                    \n' : "[title3:[rawText:'Title 3']]", # Ignore extra spaces and tabs
    '==== Title 4 ====\n' : "[title4:[rawText:' Title 4 ']]",
    '===== Title 5 =====\n' : "[title5:[rawText:' Title 5 ']]",
    '====== Title 6 ======\n' : "[title6:[rawText:' Title 6 ']]",
    '======= Title 6 =======\n' : "[title6:[rawText:'= Title 6 =']]",
    '= [[a link]] =\n' : "[title1:[rawText:' '  simpleInternalLink:'a link'  rawText:' ']]",
    "== ''italic text'' ==\n" : "[title2:[rawText:' <em>italic text</em> ']]",
    "=== '''bold text''' ===\n" : "[title3:[rawText:' <strong>bold text</strong> ']]",
    "==== ''[[Title 4|formatted link]]'' ====\n" : "[title4:[rawText:' <em></em>'  advancedInternalLink:[templateName:'Title 4'  @cleanInline@:[rawText:'formatted link']]  rawText:'<em> </em>']]",
    '===== {{Title 5}} =====\n' : "[title5:[rawText:' '  simpleTemplate:'Title 5'  rawText:' ']]",
    '====== { Title 6} ======\n' : "[title6:[rawText:' '  allowedChar:'{'  rawText:' Title 6'  allowedChar:'}'  rawText:' ']]",
    '== Title = title ==\n' : "[title2:[rawText:' Title = title ']]",
    '== Title == title ==\n' : "[title2:[rawText:' Title == title ']]", # Allow =* in titles
}

mediawikiParser.testSuite(test_suite_dict)


print "\n\n== Testing nowiki sections =="

test_suite_dict = {
    '<nowiki>some [[text]] that should {{not}} be changed</nowiki>\n' : "[paragraphs:[paragraph:[nowiki:[ignoredInNowiki:'some [[text]] that should {{not}} be changed']]]]",
}

mediawikiParser.testSuite(test_suite_dict)


print "\n\n== Testing links =="

test_suite_dict = {
    '[[article]]' : "[simpleInternalLink:'article']",
    '[[article|alternate]]' : "[advancedInternalLink:[templateName:'article'  @cleanInline@:[rawText:'alternate']]]",
    'An URL: http://www.mozilla.org' : "[rawText:'An URL: '  url:'http://www.mozilla.org']",
    "[http://www.mozilla.org this is an ''external'' link]" : "[externalLink:[url:'http://www.mozilla.org'  @cleanInline@:[rawText:'this is an <em>external</em> link']]]",
    '<a href="http://www.mozilla.org">this is an \'\'external\'\' link</a>' : "[rawText:'<a href=\"'  url:'http://www.mozilla.org'  rawText:'\">this is an <em>external</em> link</a>']"
}

mediawikiParser.inline.testSuite(test_suite_dict)


print "\n\n== Testing italic and bold =="

test_suite_dict = {
    "Here, we have ''italic'' text." : "[rawText:'Here, we have <em>italic</em> text.']",
    "Here, we have '''bold''' text." : "[rawText:'Here, we have <strong>bold</strong> text.']",
    "Here, we have '''''bold and italic''''' text." : "[rawText:'Here, we have <em><strong>bold and italic</strong></em> text.']",
    "Here, we have ''italic only and '''bold and italic''''' text." : "[rawText:'Here, we have <em>italic only and <strong>bold and italic</strong></em> text.']",
    "Here, we have '''bold only and ''bold and italic''''' text." : "[rawText:'Here, we have <strong>bold only and <em>bold and italic</em></strong> text.']",
    "Here, we have '''''bold and italic''' and italic only''." : "[rawText:'Here, we have <em><strong>bold and italic</strong> and italic only</em>.']",
    "Here, we have '''''bold and italic'' and bold only'''." : "[rawText:'Here, we have <strong><em>bold and italic</em> and bold only</strong>.']",
    "Here, we have ''italic, '''bold and italic''' and italic only''." : "[rawText:'Here, we have <em>italic, <strong>bold and italic</strong> and italic only</em>.']",
    "Here, we have '''bold, ''bold and italic'' and bold only'''." : "[rawText:'Here, we have <strong>bold, <em>bold and italic</em> and bold only</strong>.']"
}

mediawikiParser.inline.testSuite(test_suite_dict)


print "\n\n== Testing templates =="

source0 = """{{Template with|1=parameter| 2 = parameters }}"""
result0 = """@inline@:
   advancedTemplate:
      pageName:Template with
      parameters:
         parameter:
            parameterName:1
            optionalValue:
               rawText:parameter
         parameter:
            parameterName:2 
            optionalValue:
               rawText: parameters """
source1 = """{{Template which
 | is = test
 | multi = test
 | lines = test
}}"""
result1 = """@inline@:
   advancedTemplate:
      pageName:Template which
      parameters:
         parameter:
            parameterName:is 
            optionalValue:
               rawText: test
         parameter:
            parameterName:multi 
            optionalValue:
               rawText: test
         parameter:
            parameterName:lines 
            optionalValue:
               rawText: test"""
source2 = """A template {{Template with|1=parameter| 2 = parameters }} inside a text."""
result2 = """@inline@:
   rawText:A template 
   advancedTemplate:
      pageName:Template with
      parameters:
         parameter:
            parameterName:1
            optionalValue:
               rawText:parameter
         parameter:
            parameterName:2 
            optionalValue:
               rawText: parameters 
   rawText: inside a text."""
source3 = """Formatted arguments in a template {{Template with|1='''parameter'''| 2 = ''parameters'' }}."""
result3 = """@inline@:
   rawText:Formatted arguments in a template 
   advancedTemplate:
      pageName:Template with
      parameters:
         parameter:
            parameterName:1
            optionalValue:
               rawText:<strong>parameter</strong>
         parameter:
            parameterName:2 
            optionalValue:
               rawText: <em>parameters</em> 
   rawText:."""
source4 = """A {{Template with|{{other}} |1={{templates}}| 2 = {{nested|inside=1}} }}."""
result4 = """@inline@:
   rawText:A 
   advancedTemplate:
      pageName:Template with
      parameters:
         parameter:
            simpleTemplate:other
            rawText: 
         parameter:
            parameterName:1
            optionalValue:
               simpleTemplate:templates
         parameter:
            parameterName:2 
            optionalValue:
               rawText: 
               advancedTemplate:
                  pageName:nested
                  parameters:
                     parameter:
                        parameterName:inside
                        optionalValue:
                           rawText:1
               rawText: 
   rawText:."""
source5 = """A '''template {{Template with|1=parameter| 2 = parameters }} inside formatted''' text."""
result5 = """@inline@:
   rawText:A <strong>template 
   advancedTemplate:
      pageName:Template with
      parameters:
         parameter:
            parameterName:1
            optionalValue:
               rawText:parameter
         parameter:
            parameterName:2 
            optionalValue:
               rawText: parameters 
   rawText: inside formatted</strong> text.""" # Fails
sources = [source0, source1, source2, source3, source4, source5]
results = [result0, result1, result2, result3, result4, result5]

mediawikiParser.inline.testSuiteMultiline(sources, results)


print "\n\n== Testing table lines =="

test_suite_dict = {
    'style="color:red" | cell 1' : "[<?>:[CSS_attributes:[CSS_text:'style=\"color:red\" ']]  <?>:[@cleanInline@:[rawText:' cell 1']]]"
}

mediawikiParser.wikiTableFirstCell.testSuite(test_suite_dict)

test_suite_dict = {
    '|| cell 1' : "[@cleanInline@:[rawText:' cell 1']]"
}

mediawikiParser.wikiTableOtherCell.testSuite(test_suite_dict)

test_suite_dict = {
    '|-\n' : ""
}

mediawikiParser.wikiTableSpecialLine.testSuite(test_suite_dict)

test_suite_dict = {
    '| style="color:red" | cell 1\n': "[wikiTableLineCells:[<?>:[CSS_attributes:[CSS_text:' style=\"color:red\" ']]  <?>:[@cleanInline@:[rawText:' cell 1']]]]",
    '| cell 1\n': "[wikiTableLineCells:[@cleanInline@:[rawText:' cell 1']]]",
    '|data L2-B\n': "[wikiTableLineCells:[@cleanInline@:[rawText:'data L2-B']]]",
    '| cell 1 || cell 2\n': "[wikiTableLineCells:[wikiTableFirstCell:[@cleanInline@:[rawText:' cell 1 ']]  <?>:[wikiTableOtherCell:[@cleanInline@:[rawText:' cell 2']]]]]",
    '| cell 1 || style="color:red" | cell 2\n': "[wikiTableLineCells:[wikiTableFirstCell:[@cleanInline@:[rawText:' cell 1 ']]  <?>:[wikiTableOtherCell:[<?>:[CSS_attributes:[CSS_text:' style=\"color:red\" ']]  <?>:[@cleanInline@:[rawText:' cell 2']]]]]]",
    '| style="color:red" | cell 1 || cell 2\n': "[wikiTableLineCells:[wikiTableFirstCell:[<?>:[CSS_attributes:[CSS_text:' style=\"color:red\" ']]  <?>:[@cleanInline@:[rawText:' cell 1 ']]]  <?>:[wikiTableOtherCell:[@cleanInline@:[rawText:' cell 2']]]]]",
    '! scope=row | Line 1\n': "[wikiTableLineHeader:[<?>:[CSS_attributes:[CSS_text:' scope=row ']]  <?>:[@cleanInline@:[rawText:' Line 1']]]]",
    '|- style="color:red"\n': "[wikiTableParamLineBreak:[wikiTableParameters:' style=\"color:red\"']]",
}

mediawikiParser.wikiTableLine.testSuite(test_suite_dict)


print "\n\n== Testing tables =="

source0 = """{|
! cellA
! cellB
|- style="color:red"
| cell C
| cell D
|}
"""
result0 = """@wikiTable@:
   <?>:

   <?>:
      wikiTableLine:
         wikiTableLineHeader:
            @cleanInline@:
               rawText: cellA
      wikiTableLine:
         wikiTableLineHeader:
            @cleanInline@:
               rawText: cellB
      wikiTableLine:
         wikiTableParamLineBreak:
            wikiTableParameters: style="color:red"
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText: cell C
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText: cell D"""
source1 = """{|
|+ Table {{title|parameter=yes}}
| cell 1 || cell 2
|-
| cell 3 || cell 4
|}
"""
result1 = """@wikiTable@:
   <?>:

   <?>:
      wikiTableLine:
         wikiTableTitle:
            @inline@:
               rawText: Table 
               advancedTemplate:
                  pageName:title
                  parameters:
                     parameter:
                        parameterName:parameter
                        optionalValue:
                           rawText:yes
      wikiTableLine:
         wikiTableLineCells:
            wikiTableFirstCell:
               @cleanInline@:
                  rawText: cell 1 
            <?>:
               wikiTableOtherCell:
                  @cleanInline@:
                     rawText: cell 2
      wikiTableLine:
         wikiTableLineBreak:
      wikiTableLine:
         wikiTableLineCells:
            wikiTableFirstCell:
               @cleanInline@:
                  rawText: cell 3 
            <?>:
               wikiTableOtherCell:
                  @cleanInline@:
                     rawText: cell 4"""
source2 = """{| class="wikitable" {{prettyTable}}
|+ style="color:red" | Table {{title|parameter}}
|-
|
! scope=col | Title A
! scope=col | Title B
|-
! scope=row | Line 1
|data L1.A
|data L1.B
|-
! scope=row | Line 2
|data L2.A
|data {{template|with|parameters=L2.B}}
|}
"""
result2 = """@wikiTable@:
   wikiTableBegin:
      wikiTableParameters:
         CSS_text: class="wikitable" 
         @cleanInline@:
            simpleTemplate:prettyTable
   <?>:

   <?>:
      wikiTableLine:
         wikiTableTitle:
            <?>:
               CSS_attributes:
                  CSS_text: style="color:red" 
            <?>:
               @inline@:
                  rawText: Table 
                  advancedTemplate:
                     pageName:title
                     parameters:
                        parameter:parameter
      wikiTableLine:
         wikiTableLineBreak:
      wikiTableLine:
         wikiTableLineHeader:
            <?>:
               CSS_attributes:
                  CSS_text: scope=col 
            <?>:
               @cleanInline@:
                  rawText: Title A
      wikiTableLine:
         wikiTableLineHeader:
            <?>:
               CSS_attributes:
                  CSS_text: scope=col 
            <?>:
               @cleanInline@:
                  rawText: Title B
      wikiTableLine:
         wikiTableLineBreak:
      wikiTableLine:
         wikiTableLineHeader:
            <?>:
               CSS_attributes:
                  CSS_text: scope=row 
            <?>:
               @cleanInline@:
                  rawText: Line 1
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText:data L1.A
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText:data L1.B
      wikiTableLine:
         wikiTableLineBreak:
      wikiTableLine:
         wikiTableLineHeader:
            <?>:
               CSS_attributes:
                  CSS_text: scope=row 
            <?>:
               @cleanInline@:
                  rawText: Line 2
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText:data L2.A
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText:data 
               advancedTemplate:
                  pageName:template
                  parameters:
                     parameter:with
                     parameter:
                        parameterName:parameters
                        optionalValue:
                           rawText:L2.B"""
source3 = """{| class="wikitable" {{prettyTable|1=true}}
|+ style="color:red" | Table {{title}}
|-
! scope=col | First (mother)
! scope=col | table
|
{| class="wikitable" {{prettyTable}}
|-
! scope=row | Second (daughter) table
|data L1.A
|data L1.B
|-
! scope=row | in the first one
|data L2.A
|data L2.B
|}
|-
| first
| table
| again
|}
"""
result3 = """@wikiTable@:
   wikiTableBegin:
      wikiTableParameters:
         CSS_text: class="wikitable" 
         @cleanInline@:
            advancedTemplate:
               pageName:prettyTable
               parameters:
                  parameter:
                     parameterName:1
                     optionalValue:
                        rawText:true
   <?>:

   <?>:
      wikiTableLine:
         wikiTableTitle:
            <?>:
               CSS_attributes:
                  CSS_text: style="color:red" 
            <?>:
               @inline@:
                  rawText: Table 
                  simpleTemplate:title
      wikiTableLine:
         wikiTableLineBreak:
      wikiTableLine:
         wikiTableLineHeader:
            <?>:
               CSS_attributes:
                  CSS_text: scope=col 
            <?>:
               @cleanInline@:
                  rawText: First (mother)
      wikiTableLine:
         wikiTableLineHeader:
            <?>:
               CSS_attributes:
                  CSS_text: scope=col 
            <?>:
               @cleanInline@:
                  rawText: table
      @wikiTable@:
         wikiTableBegin:
            wikiTableParameters:
               CSS_text: class="wikitable" 
               @cleanInline@:
                  simpleTemplate:prettyTable
         <?>:

         <?>:
            wikiTableLine:
               wikiTableLineBreak:
            wikiTableLine:
               wikiTableLineHeader:
                  <?>:
                     CSS_attributes:
                        CSS_text: scope=row 
                  <?>:
                     @cleanInline@:
                        rawText: Second (daughter) table
            wikiTableLine:
               wikiTableLineCells:
                  @cleanInline@:
                     rawText:data L1.A
            wikiTableLine:
               wikiTableLineCells:
                  @cleanInline@:
                     rawText:data L1.B
            wikiTableLine:
               wikiTableLineBreak:
            wikiTableLine:
               wikiTableLineHeader:
                  <?>:
                     CSS_attributes:
                        CSS_text: scope=row 
                  <?>:
                     @cleanInline@:
                        rawText: in the first one
            wikiTableLine:
               wikiTableLineCells:
                  @cleanInline@:
                     rawText:data L2.A
            wikiTableLine:
               wikiTableLineCells:
                  @cleanInline@:
                     rawText:data L2.B
      wikiTableLine:
         wikiTableLineBreak:
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText: first
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText: table
      wikiTableLine:
         wikiTableLineCells:
            @cleanInline@:
               rawText: again"""
sources = [source0, source1, source2, source3]
results = [result0, result1, result2, result3]

mediawikiParser.wikiTable.testSuiteMultiline(sources, results)


print "\n\n== Testing special characters =="

test_suite_dict = {
    u"Some Unicode characters: 你好." : u"[rawText:'Some Unicode characters: 你好.']",
    'This # should pass.' : "[rawText:'This # should pass.']",
    'This { should pass.' : "[rawText:'This '  allowedChar:'{'  rawText:' should pass.']",
    'This } should pass.' : "[rawText:'This '  allowedChar:'}'  rawText:' should pass.']",
    'This {{ should pass.' : "[rawText:'This '  allowedChar:'{'  allowedChar:'{'  rawText:' should pass.']",
    'This }} should pass.' : "[rawText:'This '  allowedChar:'}'  allowedChar:'}'  rawText:' should pass.']",
    'This < should pass.' : "[rawText:'This < should pass.']",
    'This > should pass.' : "[rawText:'This > should pass.']",
    'This [ should pass.' : "[rawText:'This '  allowedChar:'['  rawText:' should pass.']",
    'This [[ should pass.' : "[rawText:'This '  allowedChar:'['  allowedChar:'['  rawText:' should pass.']",
    'This ] should pass.' : "[rawText:'This '  allowedChar:']'  rawText:' should pass.']",
    'This ]] should pass.' : "[rawText:'This '  allowedChar:']'  allowedChar:']'  rawText:' should pass.']",
    'This | should pass.' : "[rawText:'This '  allowedChar:'|'  rawText:' should pass.']",
    'This = should pass.' : "[rawText:'This = should pass.']",
    'This "should" pass.' : "[rawText:'This \"should\" pass.']",
    'This - should pass.' : "[rawText:'This - should pass.']",
    'This should be a [[link]] and [[plain text' : "[rawText:'This should be a '  simpleInternalLink:'link'  rawText:' and '  allowedChar:'['  allowedChar:'['  rawText:'plain text']"
}

mediawikiParser.inline.testSuite(test_suite_dict)


print "\n\n== Testing lists =="

test_suite_dict = {
    '* text\n' : "[list:[bulletListLeaf:[rawText:' text']]]",
    '** other text\n' : "[list:[@bulletSubList@:[bulletListLeaf:[rawText:' other text']]]]",
    '*** other text\n' : "[list:[@bulletSubList@:[@bulletSubList@:[bulletListLeaf:[rawText:' other text']]]]]",
    '# text\n' : "[list:[numberListLeaf:[rawText:' text']]]",
    "## ''more text''\n" : "[list:[@numberSubList@:[numberListLeaf:[rawText:' <em>more text</em>']]]]",
    "### ''other text''\n" : "[list:[@numberSubList@:[@numberSubList@:[numberListLeaf:[rawText:' <em>other text</em>']]]]]",
    ": '''more text'''\n" : "[list:[colonListLeaf:[rawText:' <strong>more text</strong>']]]",
    ":::: '''more text'''\n" : "[list:[@colonSubList@:[@colonSubList@:[@colonSubList@:[colonListLeaf:[rawText:' <strong>more text</strong>']]]]]]",    
    '; still more [[text]]\n' : "[list:[semiColonListLeaf:[rawText:' still more '  simpleInternalLink:'text']]]",
    ';; still more [[text]]\n' : "[list:[@semiColonSubList@:[semiColonListLeaf:[rawText:' still more '  simpleInternalLink:'text']]]]",
    ':* more complicated case\n' : "[list:[@colonSubList@:[bulletListLeaf:[rawText:' more complicated case']]]]",
    ';* same as previous line\n' : "[list:[@semiColonSubList@:[bulletListLeaf:[rawText:' same as previous line']]]]",
    '::** another complicated case\n' : "[list:[@colonSubList@:[@colonSubList@:[@bulletSubList@:[bulletListLeaf:[rawText:' another complicated case']]]]]]",
    '*: one more\n' : "[list:[@bulletSubList@:[colonListLeaf:[rawText:' one more']]]]",
    "*:*;#*: this is '''correct''' syntax!\n" : "[list:[@bulletSubList@:[@colonSubList@:[@bulletSubList@:[@semiColonSubList@:[@numberSubList@:[@bulletSubList@:[colonListLeaf:[rawText:' this is <strong>correct</strong> syntax!']]]]]]]]]"
}

mediawikiParser.testSuite(test_suite_dict)

source0 = """* This example...
** shows the shape...
*** of the resulting ...
** AST
"""
result0 = """body:
   list:
      bulletListLeaf:
         rawText: This example...
      @bulletSubList@:
         bulletListLeaf:
            rawText: shows the shape...
      @bulletSubList@:
         @bulletSubList@:
            bulletListLeaf:
               rawText: of the resulting ...
      @bulletSubList@:
         bulletListLeaf:
            rawText: AST"""

sources = [source0]
results = [result0]

mediawikiParser.testSuiteMultiline(sources, results)


print "\n\n== Testing paragraphs =="

source0 = """This is a paragraph.
"""
result0 = """body:
   paragraphs:
      paragraph:
         rawText:This is a paragraph."""
source1 = """This is a paragraph.
With a newline in the middle.
"""
result1 = """body:
   paragraphs:
      paragraph:
         paragraphLine:
            rawText:This is a paragraph.
         paragraphLine:
            rawText:With a newline in the middle."""
source2 = """This is a paragraph.

Followed by another one.
"""
result2 = """body:
   paragraphs:
      paragraph:
         rawText:This is a paragraph.
      paragraph:
         rawText:Followed by another one."""
source3 = """This is a paragraph.


Followed a blank line and another paragraph.
"""
result3 = """body:
   paragraphs:
      paragraph:
         rawText:This is a paragraph.
      blankParagraph:
      paragraph:
         rawText:Followed a blank line and another paragraph."""
source4 = """Styled text such as ''italic'', '''bold''', {{templates}} also work.
"""
result4 = """body:
   paragraphs:
      paragraph:
         rawText:Styled text such as <em>italic</em>, <strong>bold</strong>, 
         simpleTemplate:templates
         rawText: also work."""

sources = [source0, source1, source2, source3, source4]
results = [result0, result1, result2, result3, result4]

mediawikiParser.testSuiteMultiline(sources, results)

print "\n\n== Testing preformatted paragraphs =="

source0 = """ This is a preformatted paragraph.
"""
result0 = """body:
   preformattedLines:
      preformattedLine:
         rawText:This is a preformatted paragraph."""
source1 = """ This is a preformatted paragraph.
Followed by a "normal" one.
"""
result1 = """body:
   preformattedLines:
      preformattedLine:
         rawText:This is a preformatted paragraph.
   paragraphs:
      paragraph:
         rawText:Followed by a "normal" one."""
source2 = """ This is a multiline
 preformatted paragraph.
"""
result2 = """body:
   preformattedLines:
      preformattedLine:
         rawText:This is a multiline
      preformattedLine:
         rawText:preformatted paragraph."""
source3 = """ Styled text such as ''italic'', '''bold''', {{templates}} also work.
"""
result3 = """body:
   preformattedLines:
      preformattedLine:
         rawText:Styled text such as <em>italic</em>, <strong>bold</strong>, 
         simpleTemplate:templates
         rawText: also work."""
source4 = """<pre>
Preformatted paragraph.
</pre>
"""
result4 = """body:
   preformattedParagraph:
      preformattedText:
         rawText:Preformatted paragraph."""
source5 = """Normal paragraph <pre>Preformatted one</pre> Normal one.
"""
result5 = """body:
   paragraphs:
      paragraph:
         rawText:Normal paragraph 
         preformatted:
            rawText:Preformatted one
         rawText: Normal one."""
source6 = """{|
|-
! <pre>Text</pre>
|}
"""  # Preformatted "paragraphs" should also be allowed in other structures.
result6 = """body:
   @wikiTable@:
      <?>:

      <?>:
         wikiTableLine:
            wikiTableLineBreak:
         wikiTableLine:
            wikiTableLineHeader:
               @cleanInline@:
                  rawText: 
                  preformatted:
                     rawText:Text"""

sources = [source0, source1, source2, source3, source4, source5, source6]
results = [result0, result1, result2, result3, result4, result5, result6]

mediawikiParser.testSuiteMultiline(sources, results)

#sources = [source1, source2, source3, source4]
#mediawikiParser.testSuiteDict(sources, method_name="parse", multiline=True)
