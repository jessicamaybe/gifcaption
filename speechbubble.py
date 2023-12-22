#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageSequence, ImageFont, ImageFilter, GifImagePlugin
import textwrap
import io
import sys
import argparse
import re
from pathlib import Path

GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY

parser = argparse.ArgumentParser(prog='Gif Bubbler', description='Puts a funny speech bubble on the gif')

parser.add_argument('-i', '--input')
parser.add_argument('-r', '--reverse', action='store_true', required=False)
args = parser.parse_args()

inputFile = args.input
reverse = args.reverse

if inputFile.endswith('.gif'):
    originalGif = Image.open(inputFile)
else:
    print("Input file is not a gif!")
    exit(1)


def flip_bbox_coordinates(bbox, image_width):
    x_min, y_min, x_max, y_max = bbox
    flipped_x_min = image_width - x_max
    flipped_x_max = image_width - x_min
    return (flipped_x_min, y_min, flipped_x_max, y_max)


def resize_gif(gif, Width):
    frames = []
    for frame in ImageSequence.Iterator(gif):
        new_gif = frame.copy()
        widthPercent = (Width / float(new_gif.size[0]))
        hsize = int((float(new_gif.size[1]) * float(widthPercent)))
        new_gif = new_gif.resize((Width, hsize), Image.Resampling.LANCZOS)
        new_gif.info = frame.info
        frames.insert(0, new_gif)

    frames[0].info = originalGif.info
    fobj = io.BytesIO()
    frames[0].save(fobj, 'GIF', save_all=True, append_images=frames[1:], optimize=False, disposal=2)
    return Image.open(fobj)


# if the gif is too small we scale it up and change the font size and linewrap max
if originalGif.height < 360:
    originalGif = resize_gif(originalGif, 360)

# weird ratio edge case, change font size and change linewrap
ratio = originalGif.height / originalGif.width
if ratio >= 1.0 :
    lineWrapMax = 20


# more weird ratio edge cases
if ratio <= 1.8 and ratio >= 1.4:
    lineWrapMax = 14


newGif = originalGif.copy()
newGif.thumbnail((480, 360)) # just to get new gif dimensions properly

frames = []

for frame in ImageSequence.Iterator(originalGif):
    frame = frame.copy()
    frame.thumbnail((480, 360))
    new_frame = Image.new('RGBA', (frame.width, frame.height), (0, 0, 0, 0))
    new_frame.paste(frame, (0, 0))
    mask = Image.new('L', new_frame.size, 255)
    draw = ImageDraw.Draw(mask)

    # the tail of the bubble, reverse determines side
    tailMaskBox1 = (frame.width / 12, 0 - frame.height / 2, frame.width, frame.height / 4)
    tailMaskBox2 = (frame.width / 3.75, 0 - frame.height / 2, frame.width, frame.height / 2.75)

    if reverse:
        draw.ellipse(flip_bbox_coordinates(tailMaskBox1, new_frame.width), fill=0)
        draw.ellipse(flip_bbox_coordinates(tailMaskBox2, new_frame.width), fill=255)
    else:
        draw.ellipse(tailMaskBox1, fill=0)
        draw.ellipse(tailMaskBox2, fill=255)


    # the bubble of the bubble
    draw.ellipse((-30, 0 - frame.height/3, frame.width + 30, frame.height/8), fill=0)
    #draw.polygon()
    #mask = mask.filter(ImageFilter.GaussianBlur(5))

    new_frame.putalpha(mask)

    frames.insert(0, new_frame)


frames[0].info = originalGif.info

# making the cool filename
outputFilename = Path(inputFile).stem + "_bubble" + ".gif"

# saving final gif
frames[0].save("whatever.gif", save_all=True, append_images=frames[1:], disposal=2)