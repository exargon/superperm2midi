import numpy as np
import mido
from mido import Message, MidiFile, MidiTrack
import argparse
from functools import partial

def main():

    #Get options from input
    parser = argparse.ArgumentParser(description='Superpermutation to midi converter')
    parser.add_argument('inputfile',
                    help='The file containing the superpermutation to convert.')
    parser.add_argument('outputfile', nargs='?', default='inputfile',
                    help='The file to store the midi output in.')
    parser.add_argument('-s', '--scale', nargs='?', default="default",
                    help='Scale to translate the numbers into. Possible scales:\
                          major, natural-minor, harmonic-minor, whole-note')
    parser.add_argument('-p', '--play', action='store_true',
                    help='Play back the midifile when running the script(requires python-rtmidi)')
    parser.add_argument('-I', '--instrument', default=46,
                    help='General MIDI instrument number from 0 to 127. Default: 46 (harp)')
    parser.add_argument('-l', '--note_length', default='edge-weight',
                    help='The method to decide note lengths.\
                          Possible values are: edge-weight, free-space, even')

    args = parser.parse_args()

    input_string = open(args.inputfile, 'r').read().strip()
    superpermutation = np.array(list(input_string), dtype=int)
    #Make sure it is zero indexed
    superpermutation -= superpermutation.min()

    N = superpermutation.max() + 1

    note_lengths = np.zeros_like(superpermutation)

    scale = args.scale
    if args.scale == "default":
        if   N == 7:
            scale = "major"
        elif N == 6:
            scale = "whole-note"
        elif N == 5:
            scale = "major-pentatonic"

    scaleFunction = {
        "major"           : partial(numberToScale, scale=Scales.major),
        "natural-minor"   : partial(numberToScale, scale=Scales.natural_minor),
        "harmonic-minor"  : partial(numberToScale, scale=Scales.harmonic_minor),
        "whole-note"      : partial(numberToScale, scale=Scales.whole_note),
        "major-pentatonic": partial(numberToScale, scale=Scales.major_pentatonic),
        "miyako-bushi"    : partial(numberToScale, scale=Scales.miyako_bushi)
    }.get(scale, "major")

    if args.note_length == 'free-space':
        for i, number in enumerate(superpermutation):
            num_perms = 0

            # Length based on how far it is to the same value on both sides
            for j in range(1, N):
                if i-j < 0 or superpermutation[i-j] == number:
                    break
                num_perms += 1
            for j in range(1, N):
                if i+j >= superpermutation.size or superpermutation[i+j] == number:
                    break
                num_perms += 1
            note_lengths[i] = num_perms - N + 1

    elif args.note_length == 'edge-weight':
        for i, number in enumerate(superpermutation):
            weight = 0
            for j in range(i+1, i+N+1):
                if j >= N and j < superpermutation.size:
                    if isLegalPermutation(superpermutation[j-N:j]):
                        break;
                weight += 1

            note_lengths[i] = N - weight - 1
    else:
        note_lengths[:] = N - 1

    # Fix the end values
    note_lengths[0:N-1] = N - 1

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('program_change', program=args.instrument, time=0))

    for i in range(superpermutation.size):
        note = scaleFunction(superpermutation[i])

        track.append(Message('note_on', note=note, time=0))
        track.append(Message('note_off', note=note, time=2**(note_lengths[i] + 10 - N)))

    if args.outputfile == "inputfile":
        mid.save(args.inputfile.split('.')[0] + ".mid")
    else:
        mid.save(args.outputfile)

    if args.play:
        port = mido.open_output()
        for msg in mid.play():
            port.send(msg)

def isLegalPermutation(array):
    if np.unique(array).size == array.size:
        return True
    else:
        return False

def numberToScale(number, scale, base_note=64):
    octave = number // scale.__len__()
    note = number % scale.__len__()
    return base_note + octave*12 + scale.get(note, 0)


class Scales:
    whole_note = {number: 2*number for number in range(7)}

    major = {
        0: 0,
        1: 2,
        2: 4,
        3: 5,
        4: 7,
        5: 9,
        6: 11
    }

    natural_minor = {
        0: 0,
        1: 2,
        2: 3,
        3: 5,
        4: 7,
        5: 8,
        6: 10
    }

    harmonic_minor = {
        0: 0,
        1: 2,
        2: 3,
        3: 5,
        4: 7,
        5: 8,
        6: 11
    }

    major_pentatonic = {
        0: 0,
        1: 2,
        2: 4,
        3: 7,
        4: 9
    }

    miyako_bushi = {
        0: 0,
        1: 1,
        2: 5,
        3: 7,
        4: 8
    }


if __name__ == "__main__":
    main()
