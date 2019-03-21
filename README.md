# superperm2midi
This is a simple python script to create midi-files from text-files containing superpermutations (or any other number sequence with a limited number of elements) in the form of digits. 

The script already contains a couple of common 7, 6 and 5 note scales

You can choose between even lengths on the notes, note lengths based on the edge-weight of the graph of the superpermutation and note lengths based on the distance to neighbouring elements of the same type.

## dependencies

This script depends on the mido library (https://github.com/mido/mido/) for writing midi files. 
```
pip install mido
```

If you want to playback the files from the script you also need one of the mido backends, the recommended one is python-rtmidi.
```
pip install python-rtmidi
```
