#!/bin/bash

for filename in ./gifs/*.gif; do
	clear
	echo $filename
	img2sixel "$filename"
	read -p "Enter your funny prompt: "
	python captiongif.py -i $filename "$REPLY"
done