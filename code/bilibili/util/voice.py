__all__ = ('playsound', 'voice_via_baidu', 'music')



import hashlib
import os
import requests
import subprocess
import tempfile
import warnings

from fuzzywuzzy import process

from music_dl import config
from music_dl.source import MusicSource



config.init()
ms = MusicSource()



def playsound(path):
    '''
    TODO:
        Maybe we can consider `playsound.playsound`.
    '''
    warnings.warn('It remains to be improved...', DeprecationWarning, stacklevel=2)
    with tempfile.TemporaryFile('w') as null:
        subprocess.check_call(['mplayer', path], stdout=null, stderr=null)


def voice_via_baidu(text, lan='zh', spd=3, dirname='voice'):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = hashlib.md5(f'{text}-{lan}-{spd}'.encode()).hexdigest()
    path = os.path.join(dirname, f'{filename}.mp3')
    if not os.path.exists(path):
        url = 'https://fanyi.baidu.com/gettts'
        params = dict(text=text, lan=lan, spd=spd)
        response = requests.get(url, params=params)
        with open(path, 'wb') as f:
            f.write(response.content)
    return path


def music(text):
    '''Download music via `music_dl`.
    '''
    songs = ms.search(text, config.get('source').split(' '))
    name, _ = process.extractOne(text, map(lambda x: x.name, songs))
    for song in songs:
        if song.name == name:
            if not os.path.exists(name):
                song.download()
            return name
