from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
import time
import os
import threading
import http.server
import socketserver
import json
import pyautogui
import shutil
import math
from random import randrange
screenshotsTaken = 0
screenshotFolder = "screenshots\\"

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
    eMap = open(currentDirectory + mapPath, 'r').read().split('\n')
    dictionariedMap = {}
    for row in range(len(eMap)):
        for symbol in range(len(eMap[row])):
            dictionariedMap[eMap[row][symbol]] = [row, symbol]
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
        elif nextCoords[0] < curCoords[0]:
            body.send_keys('W')
            # Вверх
        elif nextCoords[1] > curCoords[1]:
            body.send_keys('D')
            # Вправо
        elif nextCoords[1] < curCoords[1]:
            body.send_keys('A')
            # Влево
        curCoords = nextCoords
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
        holdKey(key=key, duration=0.1)


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
                anyCellIsFigure = True
                break
        if anyCellIsFigure:
            # При появляении новой фигуры, увеличиваем номер текущей фигуры и обнуляем координаты
            curNum += 1
            curColumn = 2

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
        dictionariedKeys[key.get_attribute("id")] = key

    # Следуем указаниям из отправленной нам песни, в которой вертикальными чертами отделены действия, которые могут
    # содержать либо паузы (в секундах), либо id клавиши, на которую нужно нажать.
    for action in song.split('|'):
        if action not in dictionariedKeys:
            time.sleep(float(action))
        else:
            dictionariedKeys[action].click()


def exc(moveTime = 0.5):
    global driver
    global currentDirectory
    global screenshotsTaken
    # Находим все клетки
    cells = driver.find_elements_by_tag_name('div')

    neededCells = []

    for cellId in range(len(cells)):
        if ((cellId - 2) % 6 == 0 and (cellId-2)/6 < 3) \
                or ((cellId - 3) % 6 == 0 and (cellId-3)/6 != 4) \
                or ((cellId - 4) % 6 == 0 and (cellId-4) / 6 < 3):
            neededCells.append(cells[cellId])
    currentScreenshotId = 0

    serverPath =  os.getcwd()
    curUrl = driver.current_url.replace('http://', '').replace('https://', '')

    screenUrl = serverPath + curUrl[curUrl.find('/'):curUrl.rfind('/')+1] + screenshotFolder

    shutil.rmtree(screenUrl, ignore_errors=True)
    shutil.copytree(currentDirectory + screenshotFolder, screenUrl)

    for cell in neededCells:
        time.sleep(moveTime)
        driver.execute_script("""arguments[0].innerHTML = '""" + "<img style = \"width: 100%; height: 100%;\" src = \\'" + screenshotFolder.replace('\\','/') + "screenshot" + str(currentScreenshotId+1) + ".png" +"\\'>" + "'", cell)
        currentScreenshotId = (currentScreenshotId+1) % screenshotsTaken


def O(moveTime = 0.1, minMove = 20,maxMove = 40,radius = 100, radiusRandomness = 41, fullCircles = 3):
    global driver
    body = driver.find_element_by_tag_name('body')
    grad = 0
    center = driver.get_window_size()
    center['width']/=2
    center['height']/=2
    click = ActionChains(driver).click()
    ActionChains(driver).move_to_element_with_offset(body, center['width']+math.cos(math.radians(grad))*radius,  center['height']+math.sin(math.radians(grad))*radius).click().perform()
    maxGrad = 360*fullCircles
    while grad < maxGrad:
        grad += randrange(maxMove+1-minMove)+minMove
        radiusMove = randrange(radiusRandomness)-radiusRandomness//2
        if grad >= maxGrad:
            grad=maxGrad
            radiusMove=0
        coords = [center['width']+math.cos(math.radians(grad))*(radius+radiusMove),  center['height']+math.sin(math.radians(grad))*(radius+radiusMove)]
        action = ActionChains(driver).move_to_element_with_offset(body, coords[0],coords[1])
        action.perform()
        click.perform()
        click.perform()
        time.sleep(moveTime)


def SPACE():
    return

def L(moveTime = 0.01, wordAmount = 1000, wordsAtOnce = 10):
    global driver
    body = driver.find_element_by_tag_name('body')

    window_before = driver.current_window_handle

    link = 'https://www.wordfinders.com/words-starting-with-l/'
    driver.execute_script('window.open("' + link + '","_blank");')
    window_now = driver.window_handles[-1]
    driver.switch_to_window(window_now)

    words = []
    for el in driver.find_elements_by_tag_name('a')[:wordAmount]:
        word = el.get_attribute('innerHTML')
        if word.startswith('l'):
            words.append(word)

    driver.close()
    driver.switch_to_window(window_before)




    curWordId = 0
    texts = [driver.find_element_by_class_name('vert'),driver.find_element_by_class_name('hor')]
    for text in texts:
        while text.get_attribute('contenteditable') == 'true':
            sentence = ""
            for _ in range(wordsAtOnce):
                sentence+=words[curWordId] + ' '
                curWordId = (curWordId+1)%len(words)
            text.send_keys(sentence)
            time.sleep(moveTime)


class LetterScript:
    def __init__(self, letter, path, args):
        self.letter = letter
        self.path = path
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
                string += ','
            firstDone = True
            string += i + '=' + args[i]
        string += ')'
        self.args = string


    def executeScript(self):
        global driver

        if hasattr(self,'waitBefore'):
            time.sleep(self.waitBefore)

        driver.get(self.path)
        eval(self.letter+self.args)

        takeScreenshot()

        if hasattr(self,'waitAfter'):
            time.sleep(self.waitAfter)


def takeScreenshot():
    global currentDirectory
    global screenshotsTaken
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(currentDirectory + screenshotFolder + 'screenshot' + str(screenshotsTaken + 1) + ".png")
    screenshotsTaken += 1


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
    settings = open(currentDirectory + 'settings.txt', 'r').read().split('\n')
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
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


setup()
for task in task_list:
    task.executeScript()



driver.close()
time.sleep(100)