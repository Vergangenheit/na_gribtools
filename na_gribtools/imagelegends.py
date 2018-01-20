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
    signature="NeoAtlantis", unit=None, useNearestColor=True, config=None,
    baseHeight=20
):
    assert config != None and time != None
    
    colorRelief = ColorReliefParser(colorreliefFile, useNearestColor)
    font = ImageFont.truetype(
        font=config.resourceDir("font.ttf"),
        size=int(baseHeight * 0.8)
    )
    img = Image.open(imgFilename)

    width, height = img.size
    if not datarange:
        colorReliefRange = colorRelief.range
    else:
        colorReliefRange = datarange

    # Generate bar of legend 
    
    bar = Image.new(img.mode, (width, baseHeight*4), (255, 255, 255))
    barDraw = ImageDraw.Draw(bar)

    # ---- color relief

    for x in range(0, width):
        v = interpol(0, x, width, *colorReliefRange)
        color = colorRelief.get(v)
        barDraw.line([(x, baseHeight), (x, baseHeight*2)], fill=color)

    # ---- text over color relief

    v1 = round(colorReliefRange[0], 1)
    v2 = round(colorReliefRange[1], 1)
    v = v1
    while v <= v2:
        if int(v * 10) % 10 == 0 and int(v) % 5 == 0:
            text = str(int(v))
            x = interpol(colorReliefRange[0], v, colorReliefRange[1], 0, width)
            barDraw.text((x, 0), text, fill="black", font=font)
        v += 0.1

    # ---- Unit mark, Timestamp

    write = lambda text, x, l: barDraw.text((x, l * baseHeight), text, font=font, fill="black")

    titleText = "%s [%s]" % (str(title), unit)
    titleTextSize = font.getsize(titleText)
    write(titleText, (width-titleTextSize[0])/2, 2)

    write("Forecast for: %04d-%02d-%02d %02d:%02d (UTC)" % (
        time.year,
        time.month,
        time.day, 
        time.hour,
        time.minute
    ), 0, 3)

    if signature:
        signatureSize = font.getsize(signature)
        write(signature, (width - signatureSize[0]), 3)

    # paste bar into image

    newImg = Image.new(img.mode, (width, img.size[1] + bar.size[1]))
    newImg.paste(img, (0, 0))
    newImg.paste(bar, (0, img.size[1]))

    img.close()
    bar.close()
    del img
    del bar

    newImg.save(imgFilename)
