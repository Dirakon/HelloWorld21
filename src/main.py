from selenium import webdriver # pip install selenium
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager # pip install webdriver_manager
from selenium.webdriver import ActionChains
import time
import os
import threading
import http.server
import socketserver
import json
import pyautogui # pip install pyautogui
import shutil
import math
import vlc # pip install python-vlc
from random import randrange

# Сохраняем количество взятых скриншотов
screenshotsTaken = 0

# Все необходимые папки
screenshotFolder = "screenshots\\"
settingsFolder = "config\\"
resourcesFolder = "resources\\"


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


def H(moveTime = 0.1):
    # Находим все кнопки
    buttons = driver.find_elements_by_tag_name('button')
    specialRange = range(15, 30)  # Полоска, соединяющая правую и левую часть 'H'
    # Нас интересует кнопка, если она находится в левой или правой части и в полоске.
    ids = [i for i in range(len(buttons)) if i % 5 == 0 or (i - 4) % 5 == 0 or i in specialRange]

    for i in ids:
        # Нажимаем на них
        buttons[i].click()
        time.sleep(moveTime)


def E(mapPath = "mapOfE.txt", moveTime = 0.1):
    global driver

    # Находим тело сайта, на которое будем посылать нажатие клавиш
    body = driver.find_element_by_tag_name('body')

    # Считываем карту, название которой нам указали в параметрах
    eMap = open(currentDirectory + settingsFolder + mapPath, 'r').read().split('\n')

    # Приводим данные из карты в более читабельный формат, как ключ используем символ из карты, а как значение -
    # Его координаты. Как интерпретируется карта можно узнать из кода далее или из раздела по этой букве в
    # Algorithm.pdf
    dictionariedMap = {}
    for row in range(len(eMap)):
        for symbol in range(len(eMap[row])):
            dictionariedMap[eMap[row][symbol]] = [row, symbol]

    # Находим наш первый символ и начинаем путь
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
            # Вверх
            body.send_keys('W')
        elif nextCoords[1] > curCoords[1]:
            # Вправо
            body.send_keys('D')
        elif nextCoords[1] < curCoords[1]:
            # Влево
            body.send_keys('A')
        curCoords = nextCoords
        time.sleep(moveTime)


def L3(moveTime = 0.01,amountOfClicks = 50):
    global driver

    # Находим тело сайта, относительно которого мы будем перемещаться
    body = driver.find_element_by_tag_name('body')

    # Находим тело сайта и превращаем его ширину в ширину левой части 'L'
    size = body.size
    size['width']*=0.2

    # Сохраняем клик
    click = ActionChains(driver).click()

    # Начинаем совершать указанное число кликов, при этом каждый "rateOfClicksInRightPart" клик совершается в правую часть 'L',
    # А остальные - в левую.
    rateOfClicksInRightPart = 3
    for clickId in range(amountOfClicks):
        if clickId % rateOfClicksInRightPart == 0:
            # Правая часть 'L'
            x = randrange(int(size['width']),int(size['width']*2)-1)
            y = randrange(int(size['height']*0.8),int(size['height'])-1)
        else:
            # Левая часть 'L'
            x = randrange(0,int(size['width'])-1)
            y = randrange(0,int(size['height'])-1)

        # Перемещаемся туда и кликаем
        ActionChains(driver).move_to_element_with_offset(body, x, y).perform()
        click.perform()
        time.sleep(moveTime)


def L(moveTime = 0.01, wordAmount = 1000, wordsAtOnce = 10):
    global driver
    global currentDirectory

    # Сохраняем текущую вкладку
    window_before = driver.current_window_handle

    # Переходим на сайт со списком слов на 'l'
    link = 'https://www.wordfinders.com/words-starting-with-l/'
    driver.execute_script('window.open("' + link + '","_blank");')

    # Фокусируемся на этом сайте
    window_now = driver.window_handles[-1]
    driver.switch_to_window(window_now)

    # Получаем какое-то количество слов
    words = []
    for el in driver.find_elements_by_tag_name('a')[:wordAmount]:
        word = el.get_attribute('innerHTML')
        if word.startswith('l'):
            words.append(word)

    # Закрываем вкладку
    driver.close()
    # Возвращаемся на первую
    driver.switch_to_window(window_before)

    # Получаем поля для ввода и вводим пока дают
    texts = [driver.find_element_by_class_name('vert'), driver.find_element_by_class_name('hor')]
    curWordId = 0
    for text in texts:
        while text.get_attribute('contenteditable') == 'true':
            # Добавляем сразу несколько слов, чтобы не сильно замедлять процесс
            sentence = ""
            for _ in range(wordsAtOnce):
                sentence += words[curWordId] + ' '
                # После полного обхода списка слов возвращаемся в начало
                curWordId = (curWordId+1) % len(words)

            text.send_keys(sentence)
            time.sleep(moveTime)


def O2(config = "0.19/0/0|-0.19/0/100"):
    global driver

    # Получаем поля для ввода и кнопку для подтверждения
    inputers = driver.find_elements_by_class_name('inputer')
    button = driver.find_element_by_tag_name('button')

    # Вводим указанные в параметрах данные
    for singularConfig in config.split('|'):
        nums = singularConfig.split('/')
        for i in range(len(nums)):
            # 10 бэкспэйсов должны стереть всё, что там было раньше
            inputers[i].send_keys(Keys.BACKSPACE*10 + nums[i])
        button.click()


def SPACE():
    return


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


def O(moveTime = 0.1, minMove = 20, maxMove = 40, radius = 100, radiusRandomness = 41, fullCircles = 3):
    global driver

    # Находим тело сайта, относительно которого мы будем перемещаться
    body = driver.find_element_by_tag_name('body')

    # Находим центр сайта
    center = driver.get_window_size()
    center['width'] /= 2
    center['height'] /= 2

    # Перемещаемся на стартовую позицию (точка (cos0, sin0)) и совершаем один клик
    ActionChains(driver).move_to_element_with_offset(body,
                                                     center['width'] + math.cos(math.radians(0))*radius,
                                                     center['height'] + math.sin(math.radians(0))*radius
                                                     ).click().perform()

    # Отдельно сохраняем клик, который мы будем часто использовать
    click = ActionChains(driver).click()

    # Начинаем вращение по окружности
    grad = 0
    maxGrad = 360*fullCircles
    while grad < maxGrad:
        # Перемещаемся на случайное количество градусов (конфигурируемо)
        grad += randrange(maxMove+1-minMove)+minMove

        # Добавляем случайности в радуиус, чтобы фигура выглядела уникально, но всё-таки походила на 'О'
        # (тоже конфигурируемо)
        radiusMove = randrange(radiusRandomness)-radiusRandomness//2

        # Однако если мы прошли все круги, то хотим закончить там, где начали
        if grad >= maxGrad:
            grad = maxGrad
            radiusMove=0

        # Находим новую позицию, используя как координаты косинус и синус нашего угла
        coords = [center['width'] + math.cos(math.radians(grad))*(radius+radiusMove),
                  center['height'] + math.sin(math.radians(grad))*(radius+radiusMove)]

        # Переходим на координаты и дважды кликаем (первый клик - закончить линию, второй - начать новую)
        action = ActionChains(driver).move_to_element_with_offset(body, coords[0], coords[1])
        action.perform()
        click.perform()
        click.perform()

        time.sleep(moveTime)


def R(mapPath = "mapOfR.txt", moveTime = 0.1):
    global driver

    body = driver.find_element_by_tag_name('body')
    # Отыскиваем индикатор
    indicator = driver.find_element_by_class_name('notDone')

    # Считываем и анализируем посланную нам карту, в которой в каждой строке слева написана x координата.
    # Разделённые запятыми числа, справа от координат, - номера фигур, которые мы попытаемся расположить на
    # Соответствующих x координатах.
    # (К примеру, '1:2,3' значит, что мы попытаемся расположить фигуру#2 и фигуру#3 на столбце#1) (Отсчёт с нуля).
    rMap = open(currentDirectory + settingsFolder + mapPath, 'r').read().split('\n')
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
            # Влево
            body.send_keys('A')
            curColumn -= 1
        elif curColumn < dictionariedMap[curNum]:
            # Вправо
            body.send_keys('D')
            curColumn += 1
        else:
            # Продолжаем падение
            body.send_keys('S')


def L2(config = "1/1:-45|1/99:45|1/50:45|1/50:-45", radius = 10):
    global driver

    # Находим тело сайта, относительно которого мы будем перемещаться
    body = driver.find_element_by_tag_name('body')

    # Находим размер сайта
    size = body.size

    # Отдельно сохраняем клик, который будем часто применять
    click = ActionChains(driver).click()

    # Итерируемся по данным в аргументах инструкциям
    for singularConfig in config.split('|'):
        # Извлекаем угол и координаты
        coords, angle = singularConfig.split(':')
        angle = int(angle)

        # Координаты переводим из формата (0...100) в формат (0...[ширина/высота] сайта)
        coords = [(int(i)/100) for i in coords.split('/')]
        coords[0] *= size['width']
        coords[1] *= size['height']

        # Получаем первую позицию (указанные координата) и вторую (координаты с отклонением в сторону указанного угла
        # на данный в аргументах угол), кликаем в эти позиции
        firstPosition = ActionChains(driver).move_to_element_with_offset(body, coords[0], coords[1])
        secondPosition = ActionChains(driver).move_to_element_with_offset(body, coords[0] + math.cos(math.radians(angle))*radius, coords[1] + math.sin(math.radians(angle))*radius)
        firstPosition.perform()
        click.perform()
        secondPosition.perform()
        click.perform()


def D(song = "D|0.5|hD|2.0", newVolume = 25):
    global driver
    global standartBGMVolume

    # Временно убавляем музыку
    bgmObject.audio_set_volume(newVolume)

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

    # Возвращаем стандартное значение громкости
    bgmObject.audio_set_volume(standartBGMVolume)


# '!'
def exc(moveTime = 0.5):
    global driver
    global currentDirectory
    global screenshotsTaken

    # Находим все клетки
    cells = driver.find_elements_by_tag_name('div')

    neededCells = []

    # Запоминаем все клетки, которые соответствуют восклицательному знаку. Id должно равняться:
    # Либо "2 + 6x, где x принадлежит Z, x  < 3" (левая часть '!'),
    # Либо "3 + 6x, где x принадлежит Z, x != 4" (средняя часть '!'),
    # Либо "4 + 6x, где x принадлежит Z, x < 3" (правая часть '!')
    for cellId in range(len(cells)):
        if ((cellId - 2) % 6 == 0 and (cellId-2)/6 < 3) \
                or ((cellId - 3) % 6 == 0 and (cellId-3)/6 != 4) \
                or ((cellId - 4) % 6 == 0 and (cellId-4) / 6 < 3):
            neededCells.append(cells[cellId])

    # Получаем путь к папке локального сервера
    serverPath =  os.getcwd()

    # Получаем url сервера, удаляя приставки 'http' или 'https' если такие присутствуют
    curUrl = driver.current_url.replace('http://', '').replace('https://', '')

    # При помощи пути к папке сервера и текущего url, из которого мы убираем начало (localhost) и конец (index.html),
    # Мы получаем полный путь к папке конкретно отображающегося сейчас сайта.
    # В эту папку мы хотим поместить папку скриншотов
    screenUrl = serverPath + curUrl[curUrl.find('/'):curUrl.rfind('/')+1] + screenshotFolder

    # Удаляем папку со скриншотами, если такая там уже сущестовавала и
    # Перебрасываем туда сохранённые нами в течение этой сессии скриншоты
    shutil.rmtree(screenUrl, ignore_errors=True)
    shutil.copytree(currentDirectory + screenshotFolder, screenUrl)

    # Начинаем расстановку скриншотов в необходимые клетки
    currentScreenshotId = 0
    for cell in neededCells:
        time.sleep(moveTime)
        # Вставляем в клетку новый элемент, который будет отображать скриншот и при этом не выходить за рамки клетки
        driver.execute_script("""arguments[0].innerHTML = '""" + "<img style = \"width: 100%; height: 100%;\" src = \\'"
                              + screenshotFolder.replace('\\', '/') + "screenshot" + str(currentScreenshotId+1) + ".png"
                              + "\\'>" + "'", cell)
        # Переходим на следующий скриншот (или на первый, если мы уже прошли все)
        currentScreenshotId = (currentScreenshotId+1) % screenshotsTaken


# Фоновая фунция, готовая в любое время возобновить воспроизведение музыки, если оно завершилось
def bgmController(pathToReopen):
    global bgmObject
    global standartBGMVolume

    while True:
        if bgmObject.get_state() == vlc.State.Ended:
            bgmObject = vlc.MediaPlayer(pathToReopen)
            bgmObject.play()
            bgmObject.audio_set_volume(standartBGMVolume)
        time.sleep(0.1)


def bgmStart(path):
    global bgmObject
    global standartBGMVolume

    # Запускаем проигрыватель и фоновую функцию
    bgmObject = vlc.MediaPlayer(path)
    bgmObject.play()
    bgmObject.audio_set_volume(standartBGMVolume)
    # daemon=True -> функция не должна помешать завершению программы
    threading.Thread(target=bgmController,args=(path,),daemon=True).start()


# Класс, отвечающий за логику, присущую всем буквенным функциям (ожидание перед выполнением, ожиданием после выполнения,
# переход на сайт буквы, интерпретация аргументов)
class LetterScript:
    def __init__(self, letter, path, args):
        self.letter = letter
        self.path = path

        # Отдельно забираем из аргументов ожидание перед и после выполнения
        if 'waitBefore' in args:
            self.waitBefore=float(args['waitBefore'])
            args.pop('waitBefore')
        if 'waitAfter' in args:
            self.waitAfter=float(args['waitAfter'])
            args.pop('waitAfter')

        # Переводим аргументы из простого словаря в формат аргументов, используемый в реальных функциях Python
        # К примеру: L3(moveTime = 0.01,amountOfClicks = 50)
        firstDone = False
        # Открываем скобки
        string = "("
        for i in args:
            # Не ставим запятую перед первым аргументом
            if firstDone:
                string += ','
            firstDone = True

            string += i + '=' + args[i]
        # Закрываем скобки
        string += ')'

        self.args = string

    def executeScript(self):
        global driver

        # Переходим на сайт буквы
        driver.get(self.path)

        # Выполняем соответствующее ожидание при необходимости
        if hasattr(self,'waitBefore'):
            time.sleep(self.waitBefore)

        # Выполняем функцию
        eval(self.letter+self.args)

        # Выполняем соответствующее ожидание при необходимости
        if hasattr(self,'waitAfter'):
            time.sleep(self.waitAfter)

        # Сохраняем скриншот (для '!')
        takeScreenshot()


def takeScreenshot():
    global currentDirectory
    global screenshotsTaken

    # Берём скриншот
    myScreenshot = pyautogui.screenshot()

    # Создаём папку со скриншотами, если её ещё нет
    try:
        os.mkdir(currentDirectory + screenshotFolder)
    except:
        """directory already exists"""

    # Сохраняем скриншот в специальную папку
    myScreenshot.save(currentDirectory + screenshotFolder + 'screenshot' + str(screenshotsTaken + 1) + ".png")
    screenshotsTaken += 1


def setup():
    global driver
    global task_list
    global currentDirectory
    global standartBGMVolume

    # Переходим на директорию вверх и запоминаем её, т.к. она является основной папкой проекта
    os.chdir('..')
    currentDirectory = os.getcwd() + '\\'

    # Переходим в папку сервера, чтобы начать его
    os.chdir(currentDirectory + 'src\\')

    # Настраиваем сервер
    PORT = 1337
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map.update({
        ".js": "application/javascript",
    })
    httpd = socketserver.TCPServer(("", PORT), Handler)

    # Стартуем его, при этом не давая ему мешать закрыть нашу программу
    x = threading.Thread(target=httpd.serve_forever, daemon=True)
    x.start()

    task_list = []

    # Считываем настройки
    settings = open(currentDirectory + settingsFolder + 'settings.txt', 'r').read().split('\n')
    for i in settings:
        # Отдельно настройки фоновой музыки
        if i.startswith('BGM'):
            info = i.split('=')[1].split(',')
            standartBGMVolume = int(info[1].split("'")[1])
            pathToBgm = info[0].split("'")[1]
            bgmStart(pathToBgm)
            continue

        args = i.split(',')
        letterInfo = args[0].split('=')
        args = args[1:]

        # Символ - название функции
        letter = letterInfo[0].split("'")[1]
        # Путь к сайту символа
        writtenPath = letterInfo[1].split("'")[1]
        path = 'http://localhost:'+str(PORT)+'/' + writtenPath

        # Переводим аргументы в словарь
        argsDict = {}
        for arg in args:
            arg = arg.split('=')
            argsDict[arg[0].split("'")[1]] = arg[1].split("'")[1]

        # Заносим все полученные данные в наш список
        task_list.append(LetterScript(letter, path, argsDict))

    # Открываем наш браузер
    options = webdriver.ChromeOptions()
    # Разрешаем сайтам пользоваться файлами нашего компьютера
    options.add_argument("--allow-file-access-from-files")
    # Стартуем в полноэкранном режиме
    options.add_argument("--start-maximized")

    # Открываем (возможно, устанавливаем с нуля)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


setup()
for task in task_list:
    task.executeScript()



driver.close()