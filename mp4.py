import subprocess

audio = "youtube-dl --rm-cache-dir "

with open('yt-urls.txt', 'r') as f:
    i = 0
    urls = []
    for l in f:
        url = l.split('\n')[0]
        urls.append(audio + url)
        i += 1
        print(i)
    print(urls)
    processes = [subprocess.Popen(program) for program in urls]
    
