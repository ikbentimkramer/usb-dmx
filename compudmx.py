import time
import dmx
import threading
import random

sender = dmx.DMX_Serial('COM3')
data = [0] * 512
freq = 0.25 # is in seconds
gens = 0
channels = [0, 8]

def setbpm(bpm) :
    global freq
    freq = 60 / bpm

def clock() :
    while True :
        doclock()
        time.sleep(freq)

def doclock() :
    execute()
    sender.start()
    sender.set_data(bytes(data))
    time.sleep(0.0001)
    sender.stop()

def execute() :
    next(gens)

def chase(scenes) :
    global data
    i = 0
    while True :
        if i < len(scenes) :
            scene = scenes[i]
            for j in list(zip(channels, scene)) :
                color = colors[j[1]]
                data[j[0]] = color[0]
                data[j[0] + 1] = color[1]
                data[j[0] + 2] = color[2]
            i += 1
            yield
        else :
            i = 0

def randlights(nlamps, nscenes, colors) :
    # nlamps: number of lamps
    # nscenes: number of scenes
    res = []
    for i in range(nscenes) :
        res.append([])
        for j in range(nlamps) :
            res[i].append(random.choice(list(colors.keys())))
    return res

def repl() :
    global gens
    while True :
        print(data[0:15])
        ins = input("> ")
        try :
            i = int(ins)
            setbpm(i)
        except ValueError :
            pass
        try :
            gens = chases[ins]()
        except TypeError :
            try :
                gens = chases[ins]
            except KeyError :
                pass
        except KeyError :
            pass
        if ins == "exit" :
            break

colors = {
    "red" : [255, 0, 0],
    "green" : [0, 255, 0],
    "blue" : [0, 0, 255],
    "yellow" : [255, 255, 0],
    "magenta" : [255, 0, 255],
    "cyan" : [0, 255, 255],
    "orange" : [255, 127, 0],
    "pink" : [255, 0, 127],
    "lime" : [127, 255, 0],
    "turquoise" : [0, 255, 127],
    "purple" : [127, 0, 255],
    "sky" : [0, 127, 255],
    "white" : [255, 255, 255],
    "black" : [0, 0, 0]
}

chases = {
    "mayday" : chase([["yellow", "blue"], ["blue", "yellow"]]),
    "colorwheel" : chase([["red", "orange"], 
                          ["orange", "yellow"], 
                          ["yellow", "lime"],
                          ["lime", "green"],
                          ["green", "turquoise"],
                          ["turquoise", "cyan"],
                          ["cyan", "sky"],
                          ["sky", "blue"],
                          ["blue", "purple"],
                          ["purple", "magenta"],
                          ["magenta", "pink"],
                          ["pink", "red"]]),
    "blackout" : chase([["black", "black"]]),
    "random" : lambda : chase(randlights(2, 8, colors))
}

gens = chases["blackout"]
clk = threading.Thread(target = clock)
clk.daemon = True
clk.start()
repl()
