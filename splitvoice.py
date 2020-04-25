#!/usr/local/bin/python3
# Split voice file
# This script does a few different things
# First, it takes a voice .wav file and runs ina_speech_segmenter to get the timestamps where
# it thinks a male or female voice is speaking.
# Then it splits the .wav file based on the csv file ina_speech_segmenter provides and splits the file
# into male and female wav files so we can then listen to speech and hear where it thinks a male vs. female
# is speaking. In theory, this should help me to "hone in" on what a Zoë female voice might actually sound like

from pprint import pprint
import sys
import os
from pathlib import Path
import csv

filename = sys.argv[-1]

os.system(f"ina_speech_segmenter.py -i {filename} -o . -d sm -g true")

csv_file = f"{Path(filename).stem}.csv"

with open(csv_file) as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    split_points = [line for line in reader if line[0]=='male' or line[0]=='female']

# pprint(split_points)

# If we have a bunch of sections that are of the same gender, there is no need to create a new file
# This section tries to condense the number of files by merging timecodes of adjacent same-gender clips
# Should turn this:
# [['male', '0.8', '9.76'],
#  ['female', '9.76', '13.84'],
#  ['male', '13.84', '16.94'],
#  ['female', '16.94', '19.240000000000002'],
#  ['male', '20.28', '25.8'],
#  ['male', '26.72', '29.86'],
#  ['female', '29.86', '31.1'],
#  ['male', '31.1', '32.24'],
#  ['female', '32.24', '37.86'],
#  ['male', '37.86', '39.4'],
#  ['female', '39.9', '43.18'],
#  ['female', '43.660000000000004', '53.0'],
#  ['female', '53.46', '58.18'],
#  ['male', '58.18', '61.34'],
#  ['female', '61.82', '65.22'],
#  ['male', '65.66', '70.74'],
#  ['female', '71.28', '73.10000000000001'],
#  ['male', '73.10000000000001', '75.3'],
#  ['female', '76.48', '79.28'],
#  ['male', '79.28', '80.28'],
#  ['female', '80.28', '82.86'],
#  ['male', '82.86', '99.12'],
#  ['male', '99.74000000000001', '101.02'],
#  ['female', '101.02', '102.74000000000001'],
#  ['female', '103.72', '106.8'],
#  ['male', '108.02', '113.88'],
#  ['male', '114.60000000000001', '121.42'],
#  ['male', '121.88', '123.38000000000001']]
#
#
#
# into this:
# [['male', '0.8', '9.76'],
#  ['female', '9.76', '13.84'],
#  ['male', '13.84', '16.94'],
#  ['female', '16.94', '19.240000000000002'],
#  ['male', '20.28', '29.86'],
#  ['female', '29.86', '31.1'],
#  ['male', '31.1', '32.24'],
#  ['female', '32.24', '37.86'],
#  ['male', '37.86', '39.4'],
#  ['female', '39.9', '58.18'],
#  ['male', '58.18', '61.34'],
#  ['female', '61.82', '65.22'],
#  ['male', '65.66', '70.74'],
#  ['female', '71.28', '73.10000000000001'],
#  ['male', '73.10000000000001', '75.3'],
#  ['female', '76.48', '79.28'],
#  ['male', '79.28', '80.28'],
#  ['female', '80.28', '82.86'],
#  ['male', '82.86', '101.02'],
#  ['female', '101.02', '106.8'],
#  ['male', '108.02', '123.38000000000001']]

new_split_points = []
retain_start_point = False

for i in range(len(split_points)):
    # If this is the last record ...
    if i == len(split_points) - 1:
        new_split_points.append([split_points[i][0], start_point, split_points[i][2]])
    else:
        if retain_start_point==False:
            start_point = split_points[i][1]
        end_point = split_points[i][2]
        # If the gender of the next set of cue points is the same as the cgender of the current cue points...
        if split_points[i][0] == split_points[i+1][0]:
            retain_start_point = True
        else:
            new_split_points.append([split_points[i][0], start_point, end_point])
            retain_start_point=False

# pprint(split_points)
# pprint(new_split_points)

split_points = new_split_points

for i, [gender, start_point, end_point] in enumerate(split_points):
    # Split original file at specified points with a name representing male and female sections
    cmd = (f"ffmpeg -y -hide_banner -nostats -loglevel 0 -i {filename} -ss {start_point} -to {end_point} -c copy {str(i+1)+'-' + gender}.wav")
    print(cmd)
    os.system(cmd)
