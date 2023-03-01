import requests
from bs4 import BeautifulSoup
import time
import random
import os
import json
import re
import yaml

class LyricsRub:
    def __init__(self):
        self.headers={
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        #for crawling
        with open('config.yml', "r") as f:
            client = yaml.safe_load(f)
        self.apikey = client['apikey']
        self.ss = requests.Session()

    def get_lyrics_link(self, q):
        '''Using web crawling to search and locate to track'''
        req = self.ss.get(f'http://api.musixmatch.com/ws/1.1/track.search?apikey={self.apikey}&q={q}&page_size=3&page=1&s_track_rating=desc')
        reqt= json.loads(req.text)
        track_name = reqt['message']['body']['track_list'][0]['track']['track_name'].replace('-','')
        track_artist = reqt['message']['body']['track_list'][0]['track']['artist_name'].replace('-','')
        track_share_url = reqt['message']['body']['track_list'][0]['track']['track_share_url']
        track_name = re.sub(' +','-',track_name)
        track_artist = re.sub(' +','-',track_artist)
        time.sleep(random.uniform(0.8, 0.2))
        return track_name,track_artist,track_share_url
            
    def get_lyrics(self, q='space%20oddity%20david%20bowie'):
        '''Using web crawling to get the lyrics of the destinated track'''
        track_name,track_artist,track_share_url = self.get_lyrics_link(q)
        # trackname = path.split('/')[2:]
        trackname = track_artist+'_'+track_name
        filename = f"lyrics/{trackname}.txt"
        # if file does not exist:
        if not os.path.exists(filename):
        #   os.remove(filename)
            # write lyrics titles
            f = open(filename, "w")
            f.write(trackname+'\n')
            #get lyrics from musixmatch
            req = self.ss.get(track_share_url, headers=self.headers)
            soup = BeautifulSoup(req.text, features="lxml")
            spans = soup.find_all('span', attrs={'class':'lyrics__content__ok'})
            for span in spans:
                f.write(span.string)
            time.sleep(random.uniform(0.8, 0.2))
            f.close()
        return filename

    def process_lyrics(self,filename):
        """ 
        Processing lyrics and get those objects:
        filenames: ['', '']    
        lyrics_line_lst: [['',''],['','']]
        lyrics_str_lst: ['','']
        comp_lyrics_line_lst:['','']
        comp_lyrics_str: ''
        """
        lyrics_line_lst = []
        if os.path.exists(filename):
            with open(filename) as f:
                lyrics_line_lst = f.read().splitlines()
                lyrics_line_lst = [i for i in lyrics_line_lst if i != '']
                lyrics_str='. '.join(lyrics_line_lst)
        else:
            lyrics_line_lst = None
            lyrics_str = None


        return  lyrics_str, lyrics_line_lst
