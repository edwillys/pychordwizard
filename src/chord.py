from .note import Note
from enum import Enum
import itertools as it
from collections import OrderedDict


class Chord():
    class Type(Enum):
        EMPTY = 0,
        NOTE = 1,
        INTERVAL = 2,
        CHORD = 3

    def __init__(self, chord: str) -> None:
        self.type = self.Type.EMPTY
        self.variants = []
        self.bass = None

        notes = set([Note(n) for n in chord.split()])
        self.notes = sorted(list(filter(None, notes)))
        if len(self.notes) > 0:
            self.bass = self.notes[0]
            if len(self.notes) == 1:
                self.type = self.Type.NOTE
                self.variants = [NoteVariant(self.notes[0])]
            elif len(self.notes) == 2:
                self.type = self.Type.INTERVAL
                self.variants = [
                    IntervalVariant(self.notes[0], self.notes[1]),
                    IntervalVariant(self.notes[1], self.notes[0]),
                ]
            else:
                self.type = self.Type.CHORD
                for i in range(len(self.notes)):
                    next = list(
                        it.islice(it.cycle(self.notes), i, len(self.notes)))
                    self.variants += [ChordVariant(next)]
            
    def __str__(self) -> str:
        if len(self.variants) > 0:
            var = self.variants[0]
            name_short = str(var)
            if self.bass and  var.root != self.bass:
                name_short += f'/{self.bass.letter}'

            return str(self.variants[0])
        else:
            return ""

    def all(self):
        return self.variants

class Variant():
    def __init__(self) -> None:
        self.root = None
        self.name_short = ""
        self.name_complete = ""
    
    def __str__(self) -> str:
        return self.name_short

class NoteVariant(Variant):
    def __init__(self, n0: Note) -> None:
        super().__init__()
        self.root = n0
        self.name_short = n0.pitch

class IntervalVariant(Variant):
    INTERVAL_MAP = {
        0: [("8", "Octave")],
        1: [("m2", "Minor second")],
        2: [("M2", "Major second")],
        3: [("m3", "Minor third")],
        4: [("M3", "Major third")],
        5: [("4", "Perfect fourth")],
        6: [("aug4", "Augmented fourth"), ("dim5", "Diminished fifth")],
        7: [("5", "Perfect fifth")],
        8: [("aug5", "Augmented fifth"), ("m6", "Minor sixth")],
        9:  [("M6", "Major sixth")],
        10: [("m7", "Minor seventh")],
        11: [("M7", "Major seventh")],
    }
    def __init__(self, n0: Note, n1: Note) -> None:
        super().__init__()
        self.root = n0
        self.form(n0, n1)
    
    def form(self, n0: Note, n1: Note) -> None:
        interval = (n1 - n0) % 12
        possible_names = self.INTERVAL_MAP[interval]
        if len(possible_names) == 1:
            self.name_short, self.name_complete = possible_names[0]
        else:
            if n1.accident == '#' or n0.accident == 'b':
                self.name_short, self.name_complete = possible_names[0]
            else:
                self.name_short, self.name_complete = possible_names[1]

class ChordVariant(Variant):
    THIRD_MAP = OrderedDict({
        4: "3",  # major
        3: "m3",  # minor
        5: "4",  # 4
        2: "2",  # 2
    })

    FIFTH_MAP = OrderedDict({
        7: "5",  # perfect 5th
        6: "b5",  # flat 5
        8: "#5",  # sharp 5
    })

    TRIAD_MAP = OrderedDict({
        ("3", "#5"): ("3", "#5", "", "augmented"),
        ("3", "5"): ("3", "5", "", "major"),
        ("3", "b5"): ("3", "", "#11", "major"),
        ("m3", "b5"): ("m3", "b5", "", "diminished"),
        ("m3", "5"): ("m3", "5", "", "minor"),
        ("m3", "#5"): ("m3", "", "b6", "minor"),
        ("4", "b5"): ("4", "", "b5", "sus4"),
        ("4", "5"): ("4", "5", "", "sus4"),
        ("4", "#5"): ("4", "", "b6", "sus4"),
        ("2", "b5"): ("2", "", "#11", "sus2"),
        ("2", "5"): ("2", "5", "", "sus2"),
        ("2", "#5"): ("2", "", "b6", "sus2"),
    })

    TRIAD_NAME_MAP = {
        "major": "",
        "minor": "m",
        "diminished": "dim",
        "augmented": "aug",
        "sus4": "sus4",
        "sus2": "sus2",
    }

    def __init__(self, notes: list[Note]) -> None:
        super().__init__()
        self.triad = {}
        self.extensions = {}
        self.alterations = None
        self.third = {}
        self.fifth = {}
        self.seventh = {}

        if len(notes) > 2:
            # TODO: remove notes in different octaves
            self.root = notes[0]
            self.distances = [notes[i] - notes[0]
                              for i in range(1, len(notes))]
            self.form(self.distances)

    def update_name(self):
        name_short = self.root.letter
        for key in self.triad:
            name_short += self.TRIAD_NAME_MAP[key]
        self.name_short = name_short

    def form(self, dists: list[int]) -> None:
        # restrain everything to one octave and remove repeated intervals and unissons to the root
        # this also takes care of negative intervals
        filt_dists = set([dist % 12 for dist in dists if dist % 12])

        # find third
        third_name = ""
        for dist, name in self.THIRD_MAP.items():
            if dist in filt_dists:
                third_name = name
                filt_dists.remove(dist)
                break

        # find fifth
        fifth_name = ""
        for dist, name in self.FIFTH_MAP.items():
            if dist in filt_dists:
                fifth_name = name
                filt_dists.remove(dist)
                break

        # try to make the triad, given the third and fith from above
        if (third_name, fifth_name) in self.TRIAD_MAP:
            mapped_third, mapped_fith, ext, triad_name = self.TRIAD_MAP[(third_name, fifth_name)]
            self.third[mapped_third] = None
            if mapped_fith:
                self.fifth[mapped_fith] = None
            if ext:
                self.extensions[ext] = None
            self.triad[triad_name] = None
        
        self.update_name()
