import requests
import sys
import re
from urllib.parse import urlparse
import json
import os
import shutil
import argparse


def download_ep(base_url, ep, server, res, binary_path):
    main_page = requests.get(base_url+str(ep)).content.decode('utf-8')
    base_domain = urlparse(base_url).netloc
    if server == 'mcloud':
        referer = 'https://mcloud.to/'
        #securl = re.findall('data-embed=\"(.*?)\"', main_page)[1]
        #print(securl)
    else:
        referer = 'https://vidstream.pro/'
    securl = re.findall(referer.replace('/', '\\/') + 'e\/[A-Z0-9]+\?domain='+base_domain, main_page)[0]
    player = requests.get(securl, headers = {'referer': 'https://'+base_domain+'/'}).content.decode('utf-8')
    key = re.findall('window.skey = \'(.*?)\'', player)[0]
    thridurl = securl.replace('/e/', '/info/') + '&skey=' + key
    last_page = requests.get(thridurl, headers = {'referer': securl}).content.decode('utf-8')
    data = json.loads(last_page)
    url = data['media']['sources'][0]['file']
    print(url)
    url = url.replace('list.m3u8', 'hls/' + res + '/' + res + '.m3u8')
    wd = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = os.path.join(wd, str(ep))
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    go_code = os.system((binary_path if binary_path else 'go run .') + ' -i ' + url + ' -thread 16 -h "referer: ' + referer +'" -t ' + str(ep) + ' -nomerge -t '+ tmp_dir)
    print(go_code)
    if go_code != 0:
        print("cant download", ep)
        return
    os.chdir(tmp_dir)
    epname = "_".join(base_url.split('/')[-1:][0].split("-")[:-3])+"_ep_"+str(ep)+".mp4"
    ffmpeg_code = os.system('ffmpeg -i {} -acodec copy -bsf:a aac_adtstoasc -vcodec copy {}'.format(os.path.join(tmp_dir, "playlist.m3u8"), epname))
    shutil.copy2(epname, wd)
    os.chdir(wd)
    print(ffmpeg_code)
    shutil.rmtree(tmp_dir)


def main():
    parser = argparse.ArgumentParser(description='HLS stream downloader')
    parser.add_argument('url', metavar='URL', type=str, help='page url, should be without ep number like https://gogoanime.be/watch/leviathan-the-last-defense-dub-dJnX-episode-')
    parser.add_argument('--start', '-f', type=int, default=1, help='from which ep start downloading')
    parser.add_argument('--end', '-l', type=int, default=1, help='on which ep stop downloading')
    parser.add_argument('--server', '-s', type=str, default='vidstream', help='which streaming service to use, vidstream or mcloud')
    parser.add_argument('--res', '-r', type=str, default='1080', help='which resolution to use')
    parser.add_argument('--downloader_path', '-p', type=str, default='', help='path to go m3u8 downloader binary if empty downloader will be compiled from src in current dir')
    args = parser.parse_args()

    for i in range(int(args.start), int(args.end)+1):
        download_ep(args.url, i, args.server, args.res, args.downloader_path)

    print("finished")


if __name__ == '__main__':
    main()