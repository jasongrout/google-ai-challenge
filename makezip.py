#!/usr/bin/env python

from zipfile import ZipFile

if __name__ == '__main__':
    f=ZipFile('bot.zip','w')
    f.write('MyBot.py', 'bot/MyBot.py')
    f.write('PlanetWars.py', 'bot/PlanetWars.py')
    f.close()
