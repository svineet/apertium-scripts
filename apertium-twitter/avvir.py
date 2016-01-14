#!/usr/bin/env python3

import tweepy

from pprint import pprint
import re
import json
import time
import pickle
import urllib.parse

from settings import consumer_secret, consumer_key
from settings import access_token, access_token_secret

from bs4 import BeautifulSoup


URL_REGEX = re.compile(r'(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})')
STATUS_URL = "https://twitter.com/statuses/{}"
APY_URL = "http://apy.projectjj.com/beta/translate?{}"
LIMIT = 1200

USE_PICKLE = True


def authenticate():
    print ("Authenticating.")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    print ("Authenticated.")
    print ("Now fetching tweets.")

    return api


def translate(text, flavour):
    if not text: return ""
    url = APY_URL.format(urllib.parse.urlencode({
        'q': text,
        'langpair': ('sme|'+flavour),
        'markUnknown': 0
        }))
    data = urllib.request.urlopen(url).read()
    jsoned = json.loads(data.decode('utf-8'))
    return jsoned['responseData']['translatedText']


def fetch_data(api):
    i = 1
    data = []
    for status in tweepy.Cursor(api.user_timeline, id="avviraviisa").items(LIMIT):
        prev = time.time()
        data.append(( status.text, translate(status.text, 'fin'),
            translate(status.text, 'nob'), STATUS_URL.format(status.id) ))

        print (i)
        print(status.text)
        print ("Time profile: {} to {} -> Delta {}".format(
            prev, time.time(), time.time()-prev))
        print("-"*80)
        i+=1

    return data


def compile_card_fragment(data):
    card_fragment = open('card_fragment.html', 'r').read()
    compiled = ""
    for (i, didata) in enumerate(data):
        original_text = didata['original_text']
        trans_text = didata['translated_text1']
        trans2_text = didata['translated_text2'] 
        permalink = didata['permalink']
        summary = didata['summary']
        img_src = didata['img_src']
        summary_trans1 = didata['summary_trans1']
        summary_trans2 = didata['summary_trans2']

        trans_text = URL_REGEX.sub(r'<a href="\1">\1</a>', trans_text)
        trans2_text = URL_REGEX.sub(r'<a href="\1">\1</a>', trans2_text)
        original_text = URL_REGEX.sub(r'<a href="\1">\1</a>', original_text)

        compiled += card_fragment.format(tweet_translated=trans_text,
                                         tweet_translated2=trans2_text,
                                         tweet_original=original_text,
                                         tweet_id=(i+1),
                                         permalink=permalink,
                                         summary=summary,
                                         summary_trans1=summary_trans1,
                                         summary_trans2=summary_trans2,
                                         img_src=img_src)
    return compiled


def compile_webpage(card_data):
    page = open('template.html', 'r').read()
    compiled = page.format(content=card_data)
    return compiled


def scrape_links(data):
    data2 = []
    i = 1
    for ((orig, trans, trans2, perm)) in data:
        prev = time.time()
        if URL_REGEX.search(orig):
            url_taken_out = URL_REGEX.search(orig).group(1)
        else:
            data2.append((
                orig, trans, trans2, perm, "", ""
                ))
            continue

        print(i)
        print('fetching '+orig)
        try:
            html = urllib.request.urlopen(url_taken_out).read()
        except Exception:
            print('epic fail fetching data')
            data2.append((
                orig, trans, trans2, perm, "", ""
                ))
            continue
        print('fetched, extracting.')
        s = BeautifulSoup(html, 'lxml')

        img_src, summary = '', ''
        try:
            img_src = s.select('.field.field-name-field-image.field-type-image.field-label-hidden')[0].img['src']
        except Exception:
            print('couldnt find image for ', i)
        
        try:
            summary = s.select('div.field.field-name-field-intro-text.field-type-text-long.field-label-hidden')[0].get_text()
        except Exception:
            print('couldnt find summary for ', i)

        print('found ', img_src, summary)
        print('delta ', time.time()-prev)
        print('-'*80)
        i += 1
        data2.append((
                orig, trans, trans2, perm, summary, img_src
                ))
    
    return data2


def translate_all(data2):
    data3 = []
    i = 1
    for ((orig, trans, trans2, perm, summary, img_src)) in data2:
        didata = {}
        print(i)
        print('doing ', orig)
        prev = time.time()

        didata['original_text'] = orig
        didata['translated_text1'] = trans
        didata['translated_text2'] = trans2
        didata['permalink'] = perm
        didata['summary'] = summary
        didata['img_src'] = img_src
        didata['summary_trans1'] = translate(summary, 'fin')
        didata['summary_trans2'] = translate(summary, 'nob')
        data3.append(didata)

        print('done in delta: ', time.time()-prev)
        print('-'*80)
        i+=1
    return data3


if __name__ == '__main__':
    data = None
    if USE_PICKLE:
        data = pickle.load(open('translated_data_dual.dat', 'rb'))
    else:
        api = authenticate()
        data = fetch_data(api)
        pickle.dump(data, open('translated_data_dual.dat', 'wb'))

    data3 = pickle.load(open('final_scraped_pickle.dat', 'rb'))
    
    card_data = compile_card_fragment(data3)
    final_data = compile_webpage(card_data)

    open('output.html', 'w').write(final_data)
    print('\a')
