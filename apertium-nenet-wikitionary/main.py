#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

import sys
import math


def scrape_word(word_link):
    r = requests.get("http://ru.wiktionary.org"+word_link)
    soup = BeautifulSoup(r.text, 'lxml')
    meaning_index = None
    headlines = soup.select('.mw-headline')
    for i, x in enumerate(headlines):
        if 'Значение' in x.text:
            meaning_index = i
    trans = []
    if meaning_index:
        head = headlines[meaning_index]
        try:
            ol = head.parent.next_sibling.next_sibling
            for tli in ol.select('li'):
                if tli.a:
                    splitted = tli.text.split('◆')
                    trans.append(splitted[0]+' ◆')
        except Exception:
            pass
    return trans


def scrape_data(pos, link):
    print("Fetching category link: ", link, file=sys.stderr)
    r = requests.get(link)
    print("Fetched category link: ", link, file=sys.stderr)
    soup = BeautifulSoup(r.text, 'lxml')

    length = len(soup.select('.mw-category-group a'))
    content = ""

    for i, word_link in enumerate(soup.select('.mw-category-group a')):
        if not word_link.get('href'):
            print("Could not get href for element ",
                  word_link, file=sys.stderr)
            continue

        word = word_link.text
        trans = scrape_word(word_link.get('href'))

        for tr in trans:
            content += "{}; {}; {}\n".format(word, pos, tr)

        xyz = '\r' if i != length-1 else ''
        print(xyz+"Word: "+word.rjust(30)+'; Number: '+str(i).ljust(30)+str(
              str(math.floor((i/length)*100))+'%').rjust(20),
              file=sys.stderr, end='\t')
    print(file=sys.stderr)
    return content


if __name__ == '__main__':
    print('This script scrapes wiktionary nenets words, printing logging data to stderr', file=sys.stderr)
    print('and actual output data to stdout', file=sys.stderr)
    page_links = {
        'Существительное': 'https://ru.wiktionary.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9D%D0%B5%D0%BD%D0%B5%D1%86%D0%BA%D0%B8%D0%B5_%D1%81%D1%83%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5',
        'Существительное': 'https://ru.wiktionary.org/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9D%D0%B5%D0%BD%D0%B5%D1%86%D0%BA%D0%B8%D0%B5_%D1%81%D1%83%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5&pagefrom=%D1%85%D1%8B%D0%BD%D1%83%D0%BC%E2%80%99#mw-pages',
        'Глагол': 'https://ru.wiktionary.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9D%D0%B5%D0%BD%D0%B5%D1%86%D0%BA%D0%B8%D0%B5_%D0%B3%D0%BB%D0%B0%D0%B3%D0%BE%D0%BB%D1%8B',
        'Прилагательное': 'https://ru.wiktionary.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9D%D0%B5%D0%BD%D0%B5%D1%86%D0%BA%D0%B8%D0%B5_%D0%BF%D1%80%D0%B8%D0%BB%D0%B0%D0%B3%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5',
        'наречие': 'https://ru.wiktionary.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9D%D0%B5%D0%BD%D0%B5%D1%86%D0%BA%D0%B8%D0%B5_%D0%BD%D0%B0%D1%80%D0%B5%D1%87%D0%B8%D1%8F'
    }
    content = ""
    for pos, l in page_links.items():
        content += scrape_data(pos, l)

    with open('backup.dat', 'w') as f:
        f.write(content)

    print(content, end='')
