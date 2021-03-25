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
import threading
from http.server import HTTPServer, CGIHTTPRequestHandler
import http.server
import socketserver
import json, time


def dispatchKeyEvent( name, options):
    global driver
    options["type"] = name
    body = json.dumps({'cmd': 'Input.dispatchKeyEvent', 'params': options})
    resource = "/session/%s/chromium/send_command" % driver.session_id
    url = driver.command_executor._url + resource
    driver.command_executor._request('POST', url, body)

# Функция, симулируяющая удержание кнопки на определённый промежуток.
def holdKey(key, duration):
    endtime = time.time() + duration
    options = {
        "code": "Key"+key,
        "key": key,
        "text": key,
        "unmodifiedText": key,
        "nativeVirtualKeyCode": ord(key),
        "windowsVirtualKeyCode": ord(key)
    }

    while True:
        dispatchKeyEvent( "rawKeyDown", options)
        dispatchKeyEvent( "char", options)

        if time.time() > endtime:
            dispatchKeyEvent( "keyUp", options)
            break

        options["autoRepeat"] = True
        time.sleep(0.01)


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
    eMap = open(currentDirectory + mapPath,'r').read().split('\n')
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

def W(sideToGo = "right"):
    global driver
    indicator = driver.find_element_by_tag_name('div')
    if sideToGo == 'right':
        key = 'D'
    else:
        key = 'A'

    while indicator.get_attribute("class") != 'done':
        holdKey(key=key,duration=0.1)


def R(mapPath = "Rmap.txt", moveTime = 0.1):
    global driver
    body = driver.find_element_by_tag_name('body')
    indicator = driver.find_element_by_class_name('notDone')
    rMap = open(currentDirectory + mapPath,'r').read().split('\n')
    dictionariedMap = {}
    for i in range(len(rMap)):
        row = rMap[i].split(':')
        if len(row)==2:
            row = row[1]
            nums = row.split(',')
            for num in nums:
                dictionariedMap[int(num)] = i
    curColumn = None
    curNum = -1
    cellsToCheck = driver.find_elements_by_tag_name('div')[1:11]
    while True:
        time.sleep(moveTime)
        if indicator.get_attribute('class') == 'done':
            return
        anyCellIsFigure = False
        for cell in cellsToCheck:
            if cell.get_attribute('class') == 'figure':
                anyCellIsFigure=True
                break
        if anyCellIsFigure:
            curNum+=1
            curColumn=2
            print(curNum)
        if curColumn > dictionariedMap[curNum]:
            body.send_keys('A')
            curColumn-=1
        elif curColumn < dictionariedMap[curNum]:
            body.send_keys('D')
            curColumn+=1
        else:
            body.send_keys('S')

def D(song = "D|0.5|hD|2.0"):
    global driver
    keys = driver.find_elements_by_tag_name('div')
    dictionariedKeys = {}
    for key in keys:
        dictionariedKeys[key.get_attribute("id")]=key
    for action in song.split('|'):
        if '.' in action:
            time.sleep(float(action))
        else:
            dictionariedKeys[action].click()


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
        print(self.path)
        driver.get(self.path)
        eval(self.letter+self.args)

        if hasattr(self,'waitAfter'):
            time.sleep(self.waitAfter)

def setup():
    global driver
    global task_list
    global currentDirectory
    # Make sure the server is created at current directory
    currentDirectory = os.getcwd() + '\\'



    os.chdir('D:\\Projects\\WebstormProjects\\HW21\\HnoReact')

    PORT = 1337

    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map.update({
        ".js": "application/javascript",
    })

    httpd = socketserver.TCPServer(("", PORT), Handler)

    # Start the web server
    x = threading.Thread(target=httpd.serve_forever)
    x.start()

    task_list = []
    settings = open(currentDirectory + 'settings.txt','r').read().split('\n')
    for i in settings:
        args = i.split(',')
        letterInfo = args[0].split('=')
        args = args[1:]
        letter = letterInfo[0].split("'")[1]
        writtenPath = letterInfo[1].split("'")[1]
        if writtenPath.startswith('http'):
            path = writtenPath
        else:
            curPath = ''
            path = 'http://localhost:'+str(PORT)+'/' + curPath + writtenPath
        argsDict = {}
        for arg in args:
            arg = arg.split('=')
            argsDict[arg[0].split("'")[1]] = arg[1].split("'")[1]
        task_list.append(LetterScript(letter,path,argsDict))

    options = webdriver.ChromeOptions()
    options.add_argument("--allow-file-access-from-files")
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)


setup()
for task in task_list:
    task.executeScript()



driver.close()
time.sleep(100)