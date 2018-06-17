import random
import lyrics_retriever as retr
from itertools import cycle
import requests as req
from bs4 import BeautifulSoup as bsoup
import time
import urllib.request as url_req
import json
import re
#import didscraper as dscrap        https://github.com/x41lakazam/didscraper
#import beautifier as bfier         https://github.com/x41lakazam/azlyrics_retriever/blob/master/beautifier.py



band_url = "https://www.azlyrics.com/a/amywinehouse.html"
site_url = "https://www.azlyrics.com"


outfile  = "/home/alakazam/documents/databases/lot_of_lyrics.txt"    # Lyrics text file
writing_mode = 'a'                                                   # Change to 'w' to clear lyrics file each time you run it
logfile  = ".azlyrics-retriever.log"                                 # Save the processed songs
failed_log = ".azlyrics-failed.log"                                  # Save the failed songs



def url_to_title(url):
    title = url.split('/')[5][:-5].capitalize()
    band  = url.split('/')[4].capitalize()
    outline = "{} - {}".format(band, title)
    return outline

def url_to_soup(url, user_agents, proxies):
    proxy = next(proxies)
    ua = random.choice(user_agents)
    print("[Proxy: {}]".format(proxy))
    p = {'http':proxy, 'https':proxy}
    h = {'User-Agent': ua}
    try:
        html = req.get(url, proxies=p, headers=h, timeout=2).text
        soup = bsoup(html, 'html.parser')
        return soup
    except:
        return 0

def find_songs_paths(url):
    urls = []
    html = url_req.urlopen(url)
    soup = bsoup(html, 'html.parser')
    lines = manual_line_retriever(soup)

    # Find the songs titles
    lines_pattern = r'({s:.*, h:.*, c:.*, a:.*},)'
    titles_pattern = r'{s:(.*), h:(.*), c'
    for line in lines:
        o = re.search(lines_pattern, line)
        if str(o) != "None":
            j = str(o.group())
            t = re.search(titles_pattern, j)
            u = t.groups(2)[1]
            urls.append(u.replace('"', ''))
    return urls

def add_path_to_url(url, paths):
    urls = [url+path[2:] for path in paths]
    return urls

def retrieve_log(logfile):
    logs_urls = open(logfile, 'r').read()
    return logs_urls

def log_append(text):
    open(logfile, 'a').write(text)

def soup_parse_lyrics(soup):
    lines = manual_line_retriever(soup)
    lyrics = []
    begin = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
    go = 0
    end = "</div>"
    for line in lines:
        if end in line:
            go = 0
        if go == 1:
            if len(line) and line != "\n":
                lyrics.append(line)
        if begin in line:
            go = 1
    # Make lines Beautifuls
    char_to_replace = ['<br>', '<br/>', '\n', '"', "'"]
    for char in char_to_replace:
        lyrics = [line.replace(char, '') for line in lyrics]
    lyrics = [line for line in lyrics if len(line) and '<' not in line and '[' not in line]
    return lyrics

def manual_line_retriever(data):
    lines = []
    line  = ""
    for char in str(data):
        if char == '\n':
            lines.append(line)
            line = ""
        line += char
    return lines

def failed(url):
    print("[!] Failed to retrieve lyrics of {}".format(url_to_title(url)))
    open(failed_log, 'a').write(url.rstrip()+'\n')

if __name__ == "__main__":

    print("[*] Retrieving paths")
    paths = find_songs_paths(band_url)
    print("[+] {} found.".format(len(paths)))
    # Retrieve urls of songs
    print("[*] Converting to urls")
    urls  = add_path_to_url(site_url, paths)
    # Delete already processed urls
    logs_urls = retrieve_log(logfile)
    urls = [url for url in urls if url not in logs_urls]
    # Process lyrics copying
    lines_counter = 0
    url_counter = 0
    ofile = open(outfile,writing_mode)

    for url in urls:
        print('-------------')
        print("Song: ", url_to_title(url))
        # if url_counter % 70 == 0:
        #     proxies = cycle(set(dscrap.get_proxies()))            Use with didscraper.py
        #     user_agents = dscrap.get_user_agents()                This will actualize proxy list

        while True:
            a=0
            soup = url_to_soup(url, user_agents, proxies)
            if soup != 0 or a == 3:
                break
            a+=1
        if soup != 0:
            url_counter += 1
            lyrics = soup_parse_lyrics(soup)
            for line in lyrics:
                ofile.write(str(line)+"\n")
                lines_counter += 1 # Counter
            log_append(url)
            print("[+] Sucess, total: {} lines for {} urls".format(lines_counter, url_counter))
        else:
            failed(url)

    ofile.close()
    print('[+] Done, {} songs added ({} lines)'.format(url_counter, lines_counter))
    #bfier.beautify(ofile) # use it to beautify your output file 
############################################
