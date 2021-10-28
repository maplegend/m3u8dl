import requests
import sys
import re
from urllib.parse import urlparse
import json
import os
import shutil

def download_ep(base_url, ep, server, res):
    main_page = requests.get(base_url+str(ep)).content.decode('utf-8')
    if server == 'mcloud':
        referer = 'https://mcloud.to/'
        securl = re.findall('data-embed=\"(.*?)\"', main_page)[1]
        print(securl)
    else:
        referer = 'https://vidstream.pro/'
        securl = re.findall('embedUrl\": \"(.*)?\"', main_page)[0]
    player = requests.get(securl, headers = {'referer': 'https://'+urlparse(base_url).netloc+'/'}).content.decode('utf-8')
    key = re.findall('window.skey = \'(.*?)\'', player)[0]
    thridurl = securl.replace('/e/', '/info/') + '&skey=' + key
    last_page = requests.get(thridurl, headers = {'referer': securl}).content.decode('utf-8')
    data = json.loads(last_page)
    url = data['media']['sources'][0]['file']
    print(url)
    url = url.replace('list.m3u8', 'hls/' + res + '/' + res + '.m3u8')
    tmp_dir = './'+str(ep)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    go_code = os.system('go run . -i ' + url + ' -thread 16 -h "referer: ' + referer +'" -t ' + str(ep) + ' -nomerge -t '+ tmp_dir)
    print(go_code)
    if go_code != 0:
        print("cant download", ep)
        return
    ffmpeg_code = os.system('ffmpeg -i {} -acodec copy -bsf:a aac_adtstoasc -vcodec copy {}'.format(os.path.join(tmp_dir, "playlist.m3u8"), str(ep)+".mp4"))
    print(ffmpeg_code)
    shutil.rmtree(tmp_dir)

def main():
    base_url = sys.argv[1]
    start_ep = sys.argv[2]
    max_episodes = sys.argv[3]
    if len(sys.argv) >= 5:
        res = sys.argv[4]
    else:
        res = '1080'
    if len(sys.argv) >= 6:
        server = sys.argv[5]
    else:
        server = 'vidstream'
    for i in range(int(start_ep), int(max_episodes)+1):
        download_ep(base_url, i, server, res)

    print("finished")

if __name__ == '__main__':
    main()