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


def gender_time(cue_points):
    '''This should be used prior to the use of split_voice_sections()
    to make sure silence, music, and nosie are not counted as either
    male or female. This function just determines the percentage of 
    male and female audio. This could be useful to determine how often
    a person is gendered as male vs female, or it could be used to 
    study how much speaking time women are given by men, say, in a
    debate, meeting, or other situation.'''

    data = {}
    for gender, start_point, end_point in cue_points:
        duration = float(end_point) - float(start_point)
        data[gender] += duration
        data['total'] += duration
    return data


def load_voice_sections(filename):
    '''inaSpeechSegmenter reads an audio file and tries to determine the
    different sections of the audio file. While it can detect music and
    noise, we are most interested in places where the identified audio
    is the voice of a man or a woman.'''

    # Only run inaSpeechSegmenter if necessary...

    csv_file = f"{Path(filename).stem}.csv"
    if not os.path.exists(csv_file):
        os.system(f"ina_speech_segmenter.py -i {filename} -o . -d sm -g true")

    with open(csv_file) as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [line for line in reader if line[0] == "male" or line[0] == "female"]


def split_voice_sections(split_points):
    '''Perhaps a better name for this is consolidate_voice_sections(). The purpose of 
    this function is to reduce the chance of having a bunch of adjacent audio clips of
    the same gender--we only want to cut the audio file when the gender changes.'''

    new_split_points = []
    retain_start_point = False
    start_point = 0

    for i, point in enumerate(split_points):
        # If this is the last record ...
        if i == len(split_points) - 1:
            new_split_points.append(
                [point[0], start_point, point[2]]
            )
        else:
            if not retain_start_point:
                start_point = point[1]
            end_point = point[2]
            # If the gender of the next set of cue points is the same as the cgender of the current cue points...
            if point[0] == split_points[i + 1][0]:
                retain_start_point = True
            else:
                new_split_points.append([point[0], start_point, end_point])
                retain_start_point = False

    # TODO: debug zombies
    # pprint(split_points)
    # pprint(new_split_points)

    return new_split_points


def split_audio(split_points):
    for i, [gender, start_point, end_point] in enumerate(split_points):
        # Split original file at specified points with a name representing male and female sections
        cmd = f"ffmpeg -y -hide_banner -nostats -loglevel 0 -i {filename} -ss {start_point} -to {end_point} -c copy {str(i+1)+'-' + gender}.wav"
        print(cmd)
        os.system(cmd)


if __name__ == "__main__":
    split_points = load_voice_sections(sys.argv[-1])
    duration_data = gender_time(split_points)
    print(f"% Male: {duration_data['male'] / duration_data['total']}")
    print(f"% Female: {duration_data['female'] / duration_data['total']}")
    split_audio(split_voice_sections(split_points))
