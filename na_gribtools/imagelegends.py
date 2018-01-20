#!/usr/bin/env python3

"""Modifys an image, put legends on it."""


from PIL import Image, ImageDraw, ImageFont

interpol = lambda x1, x, x2, y1, y2: y1 + (x-x1)/(x2-x1)*(y2-y1)


class ColorReliefParser:

    def __init__(self, filename, useNearestColor=False):
        src = open(filename, "r").read().strip()
        lines = [[float(i) for i in l.split()] for l in src.split("\n") if l]
        self.data = sorted(lines, key=lambda e: e[0])
        self.range = self.data[0][0], self.data[-1][0]
        self.useNearestColor = useNearestColor

    def get(self, value):
        if not self.useNearestColor:
            if value <= self.data[0][0]:
                ret = tuple(self.data[0][1:])
            elif value > self.data[-1][0]:
                ret = tuple(self.data[-1][1:])
            else:
                for i in range(0, len(self.data)-1):
                    p1, p2 = self.data[i], self.data[i+1]
                    x1, x2 = p1[0], p2[0]
                    if x1 < value and value <= x2:
                        r = interpol(x1, value, x2, p1[1], p2[1])
                        g = interpol(x1, value, x2, p1[2], p2[2])
                        b = interpol(x1, value, x2, p1[3], p2[3])
                        ret = (r, g, b)
                        break
        else:
            distances = [abs(value-each[0]) for each in self.data]
            index = distances.index(min(distances))
            ret = tuple(self.data[index])[1:]
        return tuple([int(i) for i in ret])


def getLegendedImage(
    imgFilename, colorreliefFile, datarange=None, time=None, title=None,
    useNearestColor=True, config=None
):
    assert config != None
    colorRelief = ColorReliefParser(colorreliefFile, useNearestColor)
    img = Image.open(imgFilename)

    width, height = img.size
    if not datarange:
        colorReliefRange = colorRelief.range
    else:
        colorReliefRange = datarange

    barHeight = 20

    # generate bar of color reliefs
    
    barColor = Image.new(img.mode, (width, barHeight))
    barDraw = ImageDraw.Draw(barColor)
    for x in range(0, width):
        v = interpol(0, x, width, *colorReliefRange)
        color = colorRelief.get(v)
        barDraw.line([(x, 0), (x, barHeight)], fill=color)
    del barDraw

    # generate bar of numbers

    barText = Image.new(img.mode, (width, barHeight), (255, 255, 255))
    barDraw = ImageDraw.Draw(barText)

    v1 = round(colorReliefRange[0], 1)
    v2 = round(colorReliefRange[1], 1)
    v = v1
    while v <= v2:
        if int(v * 10) % 10 == 0 and int(v) % 5 == 0:
            text = str(int(v))
            x = interpol(colorReliefRange[0], v, colorReliefRange[1], 0, width)
            barDraw.text((x, 0), text, fill=(0, 0, 0))
        v += 0.1
    del barDraw
    barText.show()



    exit()
