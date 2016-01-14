#!/usr/bin/env python3

import argparse


TAG_FORMAT = '<s n="{}"/>'
E_TAG_FORMAT = '<e><l>{}</l> <r>{}</r></e>'


def get_tags(entry):
    tag_res = ""
    for t in entry.split(".")[1:]:
        tag_res += TAG_FORMAT.format(t)

    return tag_res, entry.split('.')[0].replace(' ', '<b/>')


def rules_to_xml(lines):
    for line in lines:
        if not line:
            continue

        l, r = line.strip().split(':')
        tagl, textl = get_tags(l)
        tagr, textr = get_tags(r)

        print(E_TAG_FORMAT.format(textl+tagl, textr+tagr))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file',
        help="Input file with list of bilingual dictionary entries")
    args = parser.parse_args()

    with open(args.input_file, 'r') as inputf:
        xml = rules_to_xml(inputf.readlines())
