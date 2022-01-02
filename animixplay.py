import os
from os.path import isfile, join
import sys
import json
import subprocess

from threading import Thread
from time import sleep

from bs4 import BeautifulSoup as BS
import requests

args = sys.argv[1:]

#set arguments
temp = {}
if(len(args) > 1):
    temp["start"] = int(args[1]) - 1
if(len(args) > 2):
    temp["end"] = int(args[2]) - 1
temp["url"] = args[0]

ttt = args[0].split('/')
temp['title'] = (args[0].split('/')[-2].replace('-', ' ') if len(ttt[-2]) > len(ttt[-1]) else ttt[-1]) + ' Episode '
args = temp
print(args)

#scrape site for episodes
print("Getting episodes...")
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
src = requests.get(args['url'], headers=headers).text
soup = BS(src, 'lxml')


eplist = json.loads(soup.find('div', {"id": 'epslistplace'}).text)
eplist.pop('eptotal', None)

for k in eplist:
    eplist[k] = str(eplist[k]).split('=')[1].split('&')[0]
#get episode download page
#download url = https://gogoplay1.com/download?id={ID}

eps = []
if(args.get('end')):
    for i in range(args['start'], args['end'] + 1):
        eps.append(i)
else: eps = [args['start']]
print("Got episodes")

res = []
names = {}

def fnc(i):
    global res, names
    id = int(i)
    
    src = requests.get("https://gogoplay1.com/download?id={}".format(eplist[str(i)]), headers=headers).text
    soup = BS(src, 'lxml')

    for l in soup.find_all('div', {'class':'mirror_link'})[1]:
        if(l == '\n'): continue
        if("fembed" in str(l)):
            dat = requests.post('https://fembed-hd.com/api/source/{}'.format(str(l.a.get('href')).split('/')[-1]))
            quals = json.loads(dat.text).get('data')#[-2]['file']
            chose = ''
            for f in quals:
               if(f['label'] == '720p'):
                   found = True
                   res.append(f['file'])
                   chose = f['file']
            if chose == '':
                res.append(quals[0]['file'])
                chose = quals[0]['file']
            names[str(requests.get(chose, timeout=10, allow_redirects=False).headers['Location']).split('/')[-1].split('.')[0]] = i
                
def dl(u):
    process = subprocess.Popen('youtube-dl ' + u).wait()
    print('done ' + u)
            
threads = []

print("Scraping for download links...")
#run scrape on different threads
for ep in eps:
    thread = Thread(target=fnc, args=(ep, ))
    thread.start()
    threads.append(thread)
    
for thread in threads:
    thread.join()

print('finished scraping')
print('starting downloads...')

threads = []
#get videos
#processes = [subprocess.Popen('youtube-dl ' + program).wait() for program in res]
for u in res:
    thread = Thread(target=dl, args=(u, ))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print('finished downloading')
print('renaming files...')

root = os.path.dirname(os.path.realpath(__file__))
files = [f for f in os.listdir(root) if isfile(join(root, f))]
for file in files:
    for n in names:
        if(n in file):
            os.rename(file, str(args['title']) + str(int(names[n]) + 1) + '.' + file.split('.')[-1])
            break

