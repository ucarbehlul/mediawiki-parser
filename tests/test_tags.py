# -*- coding: utf8 -*-

from mediawiki_parser.tests import ParserTestCase


class Tags_tests(ParserTestCase):
    def test_url_in_tag(self):
        source = '<a href="http://www.mozilla.org" style="color:red">'
        result = """tag_open:
   tag_name:a
   optionalAttributes:
      optionalAttribute:
         attribute_name:href
         value_quote:http://www.mozilla.org
      optionalAttribute:
         attribute_name:style
         value_quote:color:red"""
        self.parsed_equal_tree(source, result, 'tag')

    def test_multi_tags(self):
        source = 'a <tag name="mytag" attribute=value /> and <span style=\'color: red\'>text</span>...'
        result = """@inline@:
   rawText:a 
   tag_autoclose:
      tag_name:tag
      optionalAttributes:
         optionalAttribute:
            attribute_name:name
            value_quote:mytag
         optionalAttribute:
            attribute_name:attribute
            value_noquote:value
   rawText: and 
   tag_open:
      tag_name:span
      optionalAttributes:
         attribute_name:style
         value_apostrophe:color: red
   rawText:text
   tag_close:
      tag_name:span
   rawText:..."""
        self.parsed_equal_tree(source, result, 'inline')
