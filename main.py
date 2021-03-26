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


def dispatchKeyEvent(name, options):
    global driver

    # Описываем событие
    options["type"] = name
    body = json.dumps({'cmd': 'Input.dispatchKeyEvent', 'params': options})

    # Вычисляем executor_url текущего браузера, на который му будем посылать созданное событие
    resource = "/session/%s/chromium/send_command" % driver.session_id
    url = driver.command_executor._url + resource

    # Посылаем событие
    driver.command_executor._request('POST', url, body)

# Функция, симулируяющая удержание кнопки на определённый промежуток.
def holdKey(key, duration):
    # Вычисляем время окончания работы функции
    endtime = time.time() + duration

    # Опции для посылки в событиях
    options = {
        "code": "Key"+key,
        "key": key,
        "text": key,
        "unmodifiedText": key,
        "nativeVirtualKeyCode": ord(key),
        "windowsVirtualKeyCode": ord(key)
    }

    while True:
        # Отправляет все необходимые события
        dispatchKeyEvent( "rawKeyDown", options)
        dispatchKeyEvent( "char", options)

        # Если пора заканчивать, заканчиваем, при этом не забывая о событии поднятия клавиши
        if time.time() > endtime:
            dispatchKeyEvent( "keyUp", options)
            break

        # После первого раза все нажатия являеются повторами, что надо отметить в опциях
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
            # После цифр, оканчивающихся девяткой, будут рассматриваться английские заглавные буквы в алфавитном порядке
            curSymbol = 'A'
        else:
            # Код следующего символа (если мы не на девятке) всегда можно получить, добавив единицу к коду текущего
            curSymbol = chr(ord(curSymbol) + 1)

        # Если текущий символ отутствует на карте, мы считаем, что алгоритм выполнен
        if curSymbol not in dictionariedMap:
            return

        # В зависимости от расположения следующего символа относительно текущего, мы делаем соответствующее действие
        # (Предполагается, что от каждого символа можно попасть к следующему одним движением змеи)
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

    # Отыскиваем индикатор
    indicator = driver.find_element_by_tag_name('div')

    # Выбираем клавишу в зависимости от требуемого направления
    if sideToGo == 'right':
        key = 'D'
    else:
        key = 'A'

    # Пока индикатор не сообщает о бессмысленности наших действий, продолжаем вращение
    while indicator.get_attribute("class") != 'done':
        holdKey(key=key,duration=0.1)


def R(mapPath = "Rmap.txt", moveTime = 0.1):
    global driver

    body = driver.find_element_by_tag_name('body')
    # Отыскиваем индикатор
    indicator = driver.find_element_by_class_name('notDone')

    # Считываем и анализируем посланную нам карту, в которой в каждой строке слева написана x координата.
    # Разделённые запятыми числа, справа от координат, - номера фигур, которые мы попытаемся расположить на
    # Соответствующих x координатах.
    # (К примеру, '1:2,3' значит, что мы попытаемся расположить фигуру#2 и фигуру#3 на столбце#1) (Отсчёт с нуля).
    rMap = open(currentDirectory + mapPath, 'r').read().split('\n')
    dictionariedMap = {}
    for i in range(len(rMap)):
        row = rMap[i].split(':')

        # Если в строке присутствовало разделение двоеточием, читаем вторую часть деления.
        if len(row) == 2:
            row = row[1]
            nums = row.split(',')
            for num in nums:
                # Заполняем словарь, используя как ключи номера фигур, а как значения - x координаты
                dictionariedMap[int(num)] = i

    curColumn = None
    curNum = -1
    # Отдельно находим верхнюю строку
    cellsToCheck = driver.find_elements_by_tag_name('div')[1:11]
    while True:
        time.sleep(moveTime)

        # Если индикатор сообщает нам о завершении игры, заканчиваем
        if indicator.get_attribute('class') == 'done':
            return

        # Проверяем первую строку: если там присутствует фигура, то, очевидно, эта фигура появилась только что, а
        # Старая приземлилась (или, может, старой ещё не было).
        anyCellIsFigure = False
        for cell in cellsToCheck:
            if cell.get_attribute('class') == 'figure':
                anyCellIsFigure=True
                break
        if anyCellIsFigure:
            # При появляении новой фигуры, увеличиваем номер текущей фигуры и обнуляем координаты
            curNum+=1
            curColumn=2

        # В зависимости от расположения интересущего нас столбца относительно текущего, мы делаем соответствующее действие
        if curColumn > dictionariedMap[curNum]:
            body.send_keys('A')
            curColumn -= 1
        elif curColumn < dictionariedMap[curNum]:
            body.send_keys('D')
            curColumn += 1
        else:
            body.send_keys('S')

def D(song = "D|0.5|hD|2.0"):
    global driver

    # Находим все клавишиш
    keys = driver.find_elements_by_tag_name('div')

    # Удобно располагаем их в словаре, за ключ принимая их уникальный id.
    dictionariedKeys = {}
    for key in keys:
        dictionariedKeys[key.get_attribute("id")]=key

    # Следуем указаниям из отправленной нам песни, в которой вертикальными чертами отделены действия, которые могут
    # содержать либо паузы (в секундах), либо id клавиши, на которую нужно нажать.
    for action in song.split('|'):
        if action not in dictionariedKeys:
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