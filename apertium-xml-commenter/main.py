#!/usr/bin/env python3

from lxml import etree
import sys
import argparse
import re

TAG_RE = re.compile(r'<([^<>]*)>')


def getText(node):
    all_text = [node.text] if node.text else []
    for n in node:
        if n.tag == 'b':
            all_text.append(' ')
        if n.tag == 'g':
            all_text.append(getText(n))
        if n.tail:
            all_text.append(n.tail)
    return "".join(all_text)


def comment_node(node):
    comment = etree.Comment(etree.tostring(node))
    comment.tail = node.tail
    node.getparent().replace(node, comment)
    return comment


def search_sprop(node, attr_val):
    for child in node.findall("s"):
        if child.get("n") == attr_val:
            return True
    return False


def go_through(dom, comment_data):
    # Constraints to be aware of:
    # 1. Text must match without tags and replace <b/>s
    # 2. <s> tags with appropriate n attributes must be present
    # 3. groups
    xdddddd = comment_data.readlines()
    for e in dom.xpath('//e'):
        if e.find('p') is None:
            continue

        if e.find('p').find('l') is None or e.find('p').find('r') is None:
            continue

        left = e.find('p').find('l')
        right = e.find('p').find('r')
        for line in xdddddd:
            constraint = {'l': [], 'r': []}
            line = line.strip()
            l, r = line.split(":")

            comment_this_line = True
            for key in ['l', 'r']:
                if not TAG_RE.findall(l if key == 'l' else r):
                    continue

                for tag in TAG_RE.findall(l if key == 'l' else r):
                    constraint[key].append(tag)

            for c in constraint['l']:
                if not search_sprop(left, c.strip()):
                    comment_this_line = False

            for c in constraint['r']:
                if not search_sprop(right, c.strip()):
                    comment_this_line = False

            lwords = TAG_RE.sub('', l).replace('#', '')
            rwords = TAG_RE.sub('', r).replace('#', '')

            word_match = False
            if lwords == getText(left) and \
               rwords == getText(right):
                word_match = True
            if (not lwords) and rwords and rwords == getText(right):
                word_match = True
            if (not rwords) and lwords and lwords == getText(left):
                word_match = True
            if (not lwords) and (not rwords):
                word_match = True

            if comment_this_line and word_match:
                comment_node(e)
                break
    return etree.tostring(dom, encoding='utf8', method='xml')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="Input file for script")
    args = parser.parse_args()

    dom = etree.parse(sys.stdin)
    comment_data = open(args.input_file, 'r')
    commented_dom = go_through(dom, comment_data)
    print(commented_dom.decode('utf-8'))
