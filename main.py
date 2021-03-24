import requests
import selenium
from bs4 import BeautifulSoup
from lxml import html
from urllib.request import Request, urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import tkinter as tk
import os

def H(clickTime = 0.1):
    buttons = driver.find_elements_by_tag_name('button')
    specialRange = range(15, 30)  # Полоска, соединяющая правую и левую часть 'H'
    # Нас интересует кнопка, если она находится в левой или правой части и в полоске.
    ids = [i for i in range(len(buttons)) if i % 5 == 0 or (i - 4) % 5 == 0 or i in specialRange]

    for i in ids:
        buttons[i].click()
        time.sleep(clickTime)


def E(mapPath = "Emap.txt", moveTime = 0.1):
    global driver
    body = driver.find_element_by_tag_name('body')
    eMap = open(mapPath,'r').read().split('\n')
    dictionariedMap = {}
    for row in range(len(eMap)):
        for symbol in range(len(eMap[row])):
            dictionariedMap[eMap[row][symbol]] = [row,symbol]
    curCoords = dictionariedMap['1']
    curSymbol = '1'
    while True:
        if curSymbol == '9':
            curSymbol = 'A'
        else:
            curSymbol = chr(ord(curSymbol) + 1)
        if curSymbol not in dictionariedMap:
            return
        nextCoords = dictionariedMap[curSymbol]
        if nextCoords[0] > curCoords[0]:
            # Вниз
            body.send_keys('S')
        elif  nextCoords[0] < curCoords[0]:
            body.send_keys('W')
            # Вверх
        elif  nextCoords[1] > curCoords[1]:
            body.send_keys('D')
            # Вправо
        elif  nextCoords[1] < curCoords[1]:
            body.send_keys('A')
            # Влево
        curCoords=nextCoords
        time.sleep(moveTime)


class LetterScript:
    def __init__(self,letter,path, args):
        self.letter=letter
        self.path=path
        if 'waitBefore' in args:
            self.waitBefore=float(args['waitBefore'])
            args.pop('waitBefore')
        if 'waitAfter' in args:
            self.waitAfter=float(args['waitAfter'])
            args.pop('waitAfter')
        firstDone = False
        string = "("
        for i in args:
            if firstDone:
                string +=','
            firstDone=True
            string +=i + '=' + args[i]
        string += ')'
        self.args = string

    def executeScript(self):
        global driver

        if hasattr(self,'waitBefore'):
            time.sleep(self.waitBefore)

        driver.get(self.path)
        eval(self.letter+self.args)

        if hasattr(self,'waitAfter'):
            time.sleep(self.waitAfter)

def setup():
    global driver
    global task_list
    task_list = []
    settings = open('settings.txt','r').read().split('\n')
    for i in settings:
        args = i.split(',')
        letterInfo = args[0].split('=')
        args = args[1:]
        letter = letterInfo[0].split("'")[1]
        curPath = ''  #os.getcwd() +'\\'      #Раскомментировать, когда все файлы в сабдиректориях этой папки
        path = 'file:///' + curPath + letterInfo[1].split("'")[1]
        argsDict = {}
        for arg in args:
            arg = arg.split('=')
            argsDict[arg[0].split("'")[1]] = arg[1].split("'")[1]
        task_list.append(LetterScript(letter,path,argsDict))

    driver = webdriver.Chrome(ChromeDriverManager().install())


setup()
for task in task_list:
    task.executeScript()



driver.close()
time.sleep(100)