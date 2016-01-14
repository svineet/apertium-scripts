#!/usr/bin/env python3

from xml.dom.minidom import parseString
import sys
import argparse
import re

TAG_RE = re.compile(r'<([^<>]*)>')


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        if hasattr(node, 'tagName'):
            if node.tagName == 'b':
                rc.append(' ')
            if node.tagName == 'g':
                rc.append(getText(node.childNodes))
    return ''.join(rc)


def comment_node(node):
    comment = node.ownerDocument.createComment(node.toxml())
    node.parentNode.replaceChild(comment, node)
    return comment


def search_sprop(node, attr_val):
    for child in node.childNodes:
        if hasattr(child, 'tagName') and child.tagName == 's':
            if child.hasAttribute('n'):
                if child.getAttribute('n') == attr_val:
                    return True
    return False


def go_through(dom, comment_data):
    # Constraints to be aware of:
    # 1. Text must match without tags and replace <b/>s
    # 2. <s> tags with appropriate n attributes must be present
    # 3. groups???
    xdddddd = comment_data.readlines()
    comment_count = 0
    for e in dom.getElementsByTagName('e'):
        if not (e.getElementsByTagName('l') and e.getElementsByTagName('r')):
            continue

        left = e.getElementsByTagName('l')[0]
        right = e.getElementsByTagName('r')[0]

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
                if not search_sprop(right, c):
                    comment_this_line = False

            lwords = TAG_RE.sub('', l).replace('#', '')
            rwords = TAG_RE.sub('', r).replace('#', '')

            word_match = False
            if lwords == getText(left.childNodes) and \
               rwords == getText(right.childNodes):
                word_match = True
            if (not lwords) and rwords and rwords == getText(right.childNodes):
                word_match = True
            if (not rwords) and lwords and lwords == getText(left.childNodes):
                word_match = True
            if (not lwords) and (not rwords):
                word_match = True

            if comment_this_line and word_match:
                comment_count += 1
                comment_node(e)
                break
    return dom.toxml()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="Input file for script")
    args = parser.parse_args()

    xml = sys.stdin.read()
    dom = parseString(xml)
    comment_data = open(args.input_file, 'r')
    commented_dom = go_through(dom, comment_data)
    print(commented_dom)
