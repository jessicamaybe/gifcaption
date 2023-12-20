#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageSequence, ImageFont
import textwrap
import io
import sys
import argparse
import re
from pathlib import Path

parser = argparse.ArgumentParser(prog='Gif Captioner', description='Captions your gifs like the funny iFunny gifs')

parser.add_argument('-i', '--input')
parser.add_argument('string')
args = vars(parser.parse_args())

message = args["string"]
inputFile = args["input"]

#inputFile = sys.argv[1]

if inputFile.endswith('.gif'):
    originalGif = Image.open(inputFile)
else:
    print("Input file is not a gif!")
    exit(1)

fontName = "futura_black.otf"

#font size of 32
font = ImageFont.truetype(fontName, 32)

def resize_gif(gif, Width):
    frames = []
    for frame in ImageSequence.Iterator(gif):
        new_gif = frame.copy()
        widthPercent = (Width / float(new_gif.size[0]))
        hsize = int((float(new_gif.size[1]) * float(widthPercent)))
        new_gif = new_gif.resize((Width, hsize), Image.Resampling.LANCZOS)
        frames.append(new_gif)

    frames[0].info = originalGif.info
    fobj = io.BytesIO()
    frames[0].save(fobj, 'GIF', save_all=True, append_images=frames[1:])
    return Image.open(fobj)

lineWrapMax = 24

# if the gif is too small we scale it up and change the font size and linewrap max
if originalGif.height < 360:
    #baseWidth = 360
    #print("baby size")
    font = ImageFont.truetype(fontName, 28)
    originalGif = resize_gif(originalGif, 360)

# weird ratio edge case, change font size and change linewrap
ratio = originalGif.height / originalGif.width
if ratio >= 1.0 :
    #print("weird ratio")
    font = ImageFont.truetype(fontName, 28)
    lineWrapMax = 20

#more weird ratio edge cases
if ratio <= 1.8 and ratio >= 1.4:
    #print("tall ratio")
    font = ImageFont.truetype(fontName, 28)
    lineWrapMax = 14

messageSplit = message.split(' ')
messageWrap = textwrap.wrap(message, width=lineWrapMax)
messageFill = textwrap.fill(message, width=lineWrapMax)


# big text if short message
if len(messageWrap) == 1 and (len(message) < 14):
    #print("weird ratio")
    font = ImageFont.truetype(fontName, 48)


#frames = ImageSequence.Iterator(originalGif)
newGif = originalGif.copy()
newGif.thumbnail((480, 360)) #just to get new size properly


captionText = Image.new(mode="RGB", size=(newGif.width, newGif.height + 1000), color="white")
draw = ImageDraw.Draw(captionText)


W = newGif.width
H = newGif.height + 1000

_, _, _, line_height = font.getbbox(message)
current_h = line_height
lineCount = 0

for line in messageWrap:
    _, _, w, h = draw.textbbox((0, 0), line, font=font)
    draw.text(((W - w) / 2, current_h), line, font=font, fill="black")
    current_h += line_height
    lineCount += 1


#crop to make make message fit nice
_, cropTop, _, cropBottom = font.getbbox(messageFill)
captionText = captionText.crop((0, 0, W, lineCount * line_height + line_height + line_height))

#captionText = captionText.resize((originalGif.width, originalGif.height))

frames = []

for frame in ImageSequence.Iterator(originalGif):
    frame = frame.copy()
    frame.thumbnail((480, 360))

    new_frame = Image.new('RGB', (newGif.width, newGif.height + captionText.height), color="white")
    new_frame.paste(captionText, (0, 0))
    new_frame.paste(frame, (0, captionText.height))
    frames.append(new_frame)


frames[0].info = originalGif.info

#making the cool filename
outputFilename = "_".join(messageSplit[:6]) + "_[" + Path(inputFile).stem + "gif]_" + ".gif"

#saving final gif
frames[0].save(outputFilename, save_all=True, append_images=frames[1:])