# turbo_chopper.py
#
# License: MIT: https://www.monitis.com/blog/software-licensing-types-explained/
#
# Copyright (C) 2019 Kristine Conley & Richard Brockie
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the “Software”), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute,
# sub-license, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

"""! @brief Example Python script with Doxygen style comments."""

##
# @mainpage About Turbochopper
#
# @section description_main What does Turbochopper do?
# Turbochopper is a python script that takes one long HTML file and grossly prepares it for use with a DITA publishing tool. 
# Turbochopper wraps the content of one H1 tag and its p tags in a valid XML topic element. It also names each file and outputs the topics in a directory.
#
# @section description_rationale Why use Turbochopper?
# Turbochopper can save you time for proof of concept projects. 
# For example, when working with a team of developers who already were collaborating to produce documentation using
# Google Docs, I exported the user guide as HTML, ran Turbochopper, and then groomed the topics in Structured FrameMaker (DITA). 
# Next, I made a DITA map and output these docmentation deliverables: 
#   - PDF
#   - HTML
#
# Even though Turbochopper's capabilities are quite limited, it did save me a significant amount of file preparation time.
#
# @section description_start Getting Started
#   -# Get Turbochopper from GitHub (@ref https://github.com/dumpydog212/turbochopper)
#   -# Set these variables in turbo_chopper.py:
#       - _filename_, which is the name of the HTML source file.
#       - _source_folder_, which is the relative path to the location of the HTML source file.
#       - _output_root_, which is the location to which you want tubochopper to write.
#   -# Run the script.
#
# (c) 2021 Kristi Conley. All rights reserved.

# Imports
import os
import sys

from slugify import slugify

from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4.element import Comment
from bs4.element import NavigableString

DUPLICATES_TRIGGERS_ERROR = False

VALID_ELEMENTS = ['p']

XMLNS_DITAARCH = "http://dita.oasis-open.org/architecture/2005/"
EXTN_XML = '.xml'

filename = 'example.html'
source_folder = '/Users/kconley/poc_md2xml'

full_path = os.path.join(source_folder, filename)

output_root = '/Users/kconley/Desktop/xfer to Win 10 VM/turbo_chopper_output'


def parse_this(html):
    return BeautifulSoup(html, features="lxml")
    # return BeautifulSoup(html, features="html.parser")


class ElementStatisticsClass(object):
    def __init__(self):
        self.element_count = 0
        self.parsed_tag_count = 0
        self.invalid_tag_count = 0

        self.valid_tag_dict = {}
        self.invalid_tag_dict = {}

    @staticmethod
    def _order_tags_dict(the_dict):
        in_order = {}
        for key, value in sorted(the_dict.items(), key=lambda item: item[1], reverse=True):
            in_order[key] = value
        return in_order

    @property
    def ordered_valid_tags(self):
        return self._order_tags_dict(self.valid_tag_dict)

    @property
    def ordered_invalid_tags(self):
        return self._order_tags_dict(self.invalid_tag_dict)


the_stats = ElementStatisticsClass()


class ChoppedH1(object):
    def __init__(self, h1_tag, index):
        self.h1_tag = h1_tag
        self.string = self.h1_tag.string.strip()
        self.slug = slugify(self.string, separator="_")
        self.index = index

        self.soup = BeautifulSoup('<topic></topic>', features='xml')
        the_topic = self.soup.topic
        the_topic['id'] = 'tbd__{:05d}'.format(self.index)
        the_topic['xmlns:ditaarch'] = XMLNS_DITAARCH

        title_tag = self.soup.new_tag("title")
        title_tag.string = self.string
        the_topic.append(title_tag)

        # add short description element after title element
        shortdesc_tag = self.soup.new_tag("shortdesc")
        shortdesc_tag.string = ""
        the_topic.append(shortdesc_tag)

        # add the prolog element with author string
        prolog_tag = self.soup.new_tag("prolog")
        the_topic.append(prolog_tag)

        author_tag = self.soup.new_tag("author")
        author_tag.string = "TurboChopper!"
        prolog_tag.append(author_tag)

        self.body_tag = self.soup.new_tag("body")
        the_topic.append(self.body_tag)

    def __str__(self):
        return "{:>5}  {}".format(self.index, self.slug)

    @staticmethod
    def _count_this_tag(stats_dict, the_element):
        try:
            stats_dict[the_element.name] += 1
        except KeyError:
            stats_dict[the_element.name] = 1

    def add_this_element(self, this_element):
        the_stats.element_count += 1

        if this_element.name not in VALID_ELEMENTS:
            the_stats.invalid_tag_count += 1
            self._count_this_tag(the_stats.invalid_tag_dict, this_element)
            return

        the_stats.parsed_tag_count += 1
        self._count_this_tag(the_stats.valid_tag_dict, this_element)

        if this_element.name == 'p':
            # is this valid for all <p> tags?
            add_this_tag = self.soup.new_tag(this_element.name)

            # builds the new string from the strings in the children of this_element

            string_list = []
            for this_child in this_element.children:
                if this_child.string is not None:
                    string_list.append(this_child.string.strip())
                    self._count_this_tag(the_stats.valid_tag_dict, this_child)

            add_this_tag.string = ' '.join(string_list)

            # this is the same as the 6 (commented) lines above!
            # add_this_tag.string = ' '.join([c.string.strip() for c in this_element.children if c.string is not None])

        else:
            print("Unexpected tag received!")
            exit(-1)

        # finally, add the new tag!
        self.body_tag.append(add_this_tag)

    def write_to_file(self, output_path):
        output_file = os.path.join(output_path, self.slug + EXTN_XML)

        print("{:>5}  {}".format(self.index, output_file))
        with open(output_file, 'w') as fptr:
            fptr.write(self.soup.prettify())


def main():
    this_script = os.path.basename(sys.argv[0])
    print('running {}:'.format(this_script))
    print(full_path)

    with open(full_path) as fptr:
        soup = parse_this(fptr)

    soup_as_a_list = list(soup)

    type_tests = [type(soup_as_a_list[0]) == Comment,
                  type(soup_as_a_list[1]) == Tag,
                  ]

    if not all(type_tests):
        print('Unexpected xml structure!')
        exit(-1)

    the_comment = soup_as_a_list[0]
    the_html = soup_as_a_list[1]

    print('Elements in <body>: {}'.format(len(the_html.body)))

    promote_these = ['h2', 'h3', 'h4', 'h5']

    for promotion_needed in promote_these:
        to_promote = soup.find_all(promotion_needed)
        print("Promoting: {} - {} found".format(promotion_needed, len(to_promote)))

        for promote_this in to_promote:
            promote_this.name = 'h1'

    the_h1s = soup.find_all('h1')

    # suppressing any h1 tags that only have whitespace in their string
    # h1_strings = [h.string for h in the_h1s if not h.string.isspace()]

    h1_strings = []
    for this_h1 in the_h1s:
        if this_h1.string is None:
            continue

        if not this_h1.string.isspace():
            h1_strings.append(this_h1.string.strip())

    if DUPLICATES_TRIGGERS_ERROR:
        if not len(h1_strings) == len(set(h1_strings)):
            print('Duplicated text in h1 tags!')
            exit(-1)

    # where to put the output...
    doc_title = slugify(h1_strings[0], separator="_")
    output_folder = os.path.join(output_root, doc_title)
    os.makedirs(output_folder, exist_ok=True)

    chopped_list = []
    h1_index = 0
    # for this_h1 in the_h1s[89:90]:
    for this_h1 in the_h1s:
        if this_h1.string is None:
            continue

        the_tests = [this_h1.string.isspace(),
                     slugify(this_h1.string, separator="_") == doc_title,
                     ]
        if any(the_tests):
            continue

        h1_index += 1

        chopped_thing = ChoppedH1(this_h1, h1_index)
        print(chopped_thing)

        # print('^^^', h1_index, this_h1.name, type(this_h1))
        # print('Next element count: {}'.format(len(list(this_h1.next_elements))))

        for n_index, this_element in enumerate(this_h1.next_elements):
            if not type(this_element) == Tag:
                continue

            assert isinstance(this_element, Tag)
            # print(n_index, type(this_element), this_element.name)

            if this_element.name == 'h1':
                # print("====== next h1 found! {}".format(this_element.string))
                break

            # add element to the topic
            chopped_thing.add_this_element(this_element)

        # add to array for looping later...
        chopped_list.append(chopped_thing)

    print('\nWriting XML to file:')
    for chopped_thing in chopped_list:
        chopped_thing.write_to_file(output_folder)
        print(chopped_thing.soup.prettify())

    print('')
    print('   Valid tag list: {}'.format(VALID_ELEMENTS))
    print('  Total tag count: {}'.format(the_stats.element_count))
    print(' Parsed tag count: {}'.format(the_stats.parsed_tag_count))
    for key, value in the_stats.ordered_valid_tags.items():
        if key is None:
            key = 'None'
        print('{:>16} {:>4}'.format(key, value))

    print('Invalid tag count: {}'.format(the_stats.invalid_tag_count))
    for key, value in the_stats.ordered_invalid_tags.items():
        print('{:>16} {:>4}'.format(key, value))


def test_fn(a, b, c=None):
    print(a, b, c)


if __name__ == "__main__":
    main()

    # test_fn(a=45, b=76, c=89)
# turbo_chopper.py
#
# License: MIT: https://www.monitis.com/blog/software-licensing-types-explained/
#
# Copyright (C) 2019 Kristine Conley & Richard Brockie
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the “Software”), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute,
# sub-license, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

"""! @brief Example Python script with Doxygen style comments."""

##
# @mainpage About Turbochopper
#
# @section description_main What does Turbochopper do?
# Turbochopper is a python script that takes one long HTML file and grossly prepares it for use with a DITA publishing tool. 
# Turbochopper wraps the content of one H1 tag and its p tags in a valid XML topic element. It also names each file and outputs the topics in a directory.
#
# @section description_rationale Why use Turbochopper?
# Turbochopper can save you time for proof of concept projects. 
# For example, when working with a team of developers who already were collaborating to produce documentation using
# Google Docs, I exported the user guide as HTML, ran Turbochopper, and then groomed the topics in Structured FrameMaker (DITA). 
# Next, I made a DITA map and output these docmentation deliverables: 
#   - PDF
#   - HTML
#
# Even though Turbochopper's capabilities are quite limited, it did save me a significant amount of file preparation time.
#
# @section description_start Getting Started
#   -# Get Turbochopper from GitHub (@ref https://github.com/dumpydog212/turbochopper)
#   -# Set these variables in turbo_chopper.py:
#       - _filename_, which is the name of the HTML source file.
#       - _source_folder_, which is the relative path to the location of the HTML source file.
#       - _output_root_, which is the location to which you want tubochopper to write.
#   -# Run the script.
#
# (c) 2021 Kristi Conley. All rights reserved.

# Imports
import os
import sys

from slugify import slugify

from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4.element import Comment
from bs4.element import NavigableString

DUPLICATES_TRIGGERS_ERROR = False

VALID_ELEMENTS = ['p']

XMLNS_DITAARCH = "http://dita.oasis-open.org/architecture/2005/"
EXTN_XML = '.xml'

filename = 'example.html'
source_folder = '/Users/kconley/poc_md2xml'

full_path = os.path.join(source_folder, filename)

output_root = '/Users/kconley/Desktop/xfer to Win 10 VM/turbo_chopper_output'


def parse_this(html):
    return BeautifulSoup(html, features="lxml")
    # return BeautifulSoup(html, features="html.parser")


class ElementStatisticsClass(object):
    def __init__(self):
        self.element_count = 0
        self.parsed_tag_count = 0
        self.invalid_tag_count = 0

        self.valid_tag_dict = {}
        self.invalid_tag_dict = {}

    @staticmethod
    def _order_tags_dict(the_dict):
        in_order = {}
        for key, value in sorted(the_dict.items(), key=lambda item: item[1], reverse=True):
            in_order[key] = value
        return in_order

    @property
    def ordered_valid_tags(self):
        return self._order_tags_dict(self.valid_tag_dict)

    @property
    def ordered_invalid_tags(self):
        return self._order_tags_dict(self.invalid_tag_dict)


the_stats = ElementStatisticsClass()


class ChoppedH1(object):
    def __init__(self, h1_tag, index):
        self.h1_tag = h1_tag
        self.string = self.h1_tag.string.strip()
        self.slug = slugify(self.string, separator="_")
        self.index = index

        self.soup = BeautifulSoup('<topic></topic>', features='xml')
        the_topic = self.soup.topic
        the_topic['id'] = 'tbd__{:05d}'.format(self.index)
        the_topic['xmlns:ditaarch'] = XMLNS_DITAARCH

        title_tag = self.soup.new_tag("title")
        title_tag.string = self.string
        the_topic.append(title_tag)

        # add short description element after title element
        shortdesc_tag = self.soup.new_tag("shortdesc")
        shortdesc_tag.string = ""
        the_topic.append(shortdesc_tag)

        # add the prolog element with author string
        prolog_tag = self.soup.new_tag("prolog")
        the_topic.append(prolog_tag)

        author_tag = self.soup.new_tag("author")
        author_tag.string = "TurboChopper!"
        prolog_tag.append(author_tag)

        self.body_tag = self.soup.new_tag("body")
        the_topic.append(self.body_tag)

    def __str__(self):
        return "{:>5}  {}".format(self.index, self.slug)

    @staticmethod
    def _count_this_tag(stats_dict, the_element):
        try:
            stats_dict[the_element.name] += 1
        except KeyError:
            stats_dict[the_element.name] = 1

    def add_this_element(self, this_element):
        the_stats.element_count += 1

        if this_element.name not in VALID_ELEMENTS:
            the_stats.invalid_tag_count += 1
            self._count_this_tag(the_stats.invalid_tag_dict, this_element)
            return

        the_stats.parsed_tag_count += 1
        self._count_this_tag(the_stats.valid_tag_dict, this_element)

        if this_element.name == 'p':
            # is this valid for all <p> tags?
            add_this_tag = self.soup.new_tag(this_element.name)

            # builds the new string from the strings in the children of this_element

            string_list = []
            for this_child in this_element.children:
                if this_child.string is not None:
                    string_list.append(this_child.string.strip())
                    self._count_this_tag(the_stats.valid_tag_dict, this_child)

            add_this_tag.string = ' '.join(string_list)

            # this is the same as the 6 (commented) lines above!
            # add_this_tag.string = ' '.join([c.string.strip() for c in this_element.children if c.string is not None])

        else:
            print("Unexpected tag received!")
            exit(-1)

        # finally, add the new tag!
        self.body_tag.append(add_this_tag)

    def write_to_file(self, output_path):
        output_file = os.path.join(output_path, self.slug + EXTN_XML)

        print("{:>5}  {}".format(self.index, output_file))
        with open(output_file, 'w') as fptr:
            fptr.write(self.soup.prettify())


def main():
    this_script = os.path.basename(sys.argv[0])
    print('running {}:'.format(this_script))
    print(full_path)

    with open(full_path) as fptr:
        soup = parse_this(fptr)

    soup_as_a_list = list(soup)

    type_tests = [type(soup_as_a_list[0]) == Comment,
                  type(soup_as_a_list[1]) == Tag,
                  ]

    if not all(type_tests):
        print('Unexpected xml structure!')
        exit(-1)

    the_comment = soup_as_a_list[0]
    the_html = soup_as_a_list[1]

    print('Elements in <body>: {}'.format(len(the_html.body)))

    promote_these = ['h2', 'h3', 'h4', 'h5']

    for promotion_needed in promote_these:
        to_promote = soup.find_all(promotion_needed)
        print("Promoting: {} - {} found".format(promotion_needed, len(to_promote)))

        for promote_this in to_promote:
            promote_this.name = 'h1'

    the_h1s = soup.find_all('h1')

    # suppressing any h1 tags that only have whitespace in their string
    # h1_strings = [h.string for h in the_h1s if not h.string.isspace()]

    h1_strings = []
    for this_h1 in the_h1s:
        if this_h1.string is None:
            continue

        if not this_h1.string.isspace():
            h1_strings.append(this_h1.string.strip())

    if DUPLICATES_TRIGGERS_ERROR:
        if not len(h1_strings) == len(set(h1_strings)):
            print('Duplicated text in h1 tags!')
            exit(-1)

    # where to put the output...
    doc_title = slugify(h1_strings[0], separator="_")
    output_folder = os.path.join(output_root, doc_title)
    os.makedirs(output_folder, exist_ok=True)

    chopped_list = []
    h1_index = 0
    # for this_h1 in the_h1s[89:90]:
    for this_h1 in the_h1s:
        if this_h1.string is None:
            continue

        the_tests = [this_h1.string.isspace(),
                     slugify(this_h1.string, separator="_") == doc_title,
                     ]
        if any(the_tests):
            continue

        h1_index += 1

        chopped_thing = ChoppedH1(this_h1, h1_index)
        print(chopped_thing)

        # print('^^^', h1_index, this_h1.name, type(this_h1))
        # print('Next element count: {}'.format(len(list(this_h1.next_elements))))

        for n_index, this_element in enumerate(this_h1.next_elements):
            if not type(this_element) == Tag:
                continue

            assert isinstance(this_element, Tag)
            # print(n_index, type(this_element), this_element.name)

            if this_element.name == 'h1':
                # print("====== next h1 found! {}".format(this_element.string))
                break

            # add element to the topic
            chopped_thing.add_this_element(this_element)

        # add to array for looping later...
        chopped_list.append(chopped_thing)

    print('\nWriting XML to file:')
    for chopped_thing in chopped_list:
        chopped_thing.write_to_file(output_folder)
        print(chopped_thing.soup.prettify())

    print('')
    print('   Valid tag list: {}'.format(VALID_ELEMENTS))
    print('  Total tag count: {}'.format(the_stats.element_count))
    print(' Parsed tag count: {}'.format(the_stats.parsed_tag_count))
    for key, value in the_stats.ordered_valid_tags.items():
        if key is None:
            key = 'None'
        print('{:>16} {:>4}'.format(key, value))

    print('Invalid tag count: {}'.format(the_stats.invalid_tag_count))
    for key, value in the_stats.ordered_invalid_tags.items():
        print('{:>16} {:>4}'.format(key, value))


def test_fn(a, b, c=None):
    print(a, b, c)


if __name__ == "__main__":
    main()

    # test_fn(a=45, b=76, c=89)
