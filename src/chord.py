from note import Note
from collections import OrderedDict


class Chord():

    def __init__(self, notes: str | set[Note]) -> None:
        self.variants = []

        if isinstance(notes, str):
            notes = set([Note(n) for n in notes.split()])
        self.notes = sorted(list(filter(None, notes)))
        if len(self.notes) > 0:
            bass = self.notes[0]
            if len(self.notes) == 1:
                self.variants = [NoteVariant(self.notes, bass)]
            elif len(self.notes) == 2:
                self.variants = [
                    IntervalVariant(self.notes, bass),
                ]
            else:
                for i in range(len(self.notes)):
                    next = [self.notes[(j+i) % len(self.notes)]
                            for j in range(len(self.notes))]
                    self.variants += [ChordVariant(next, bass)]
            self.variants.sort()

    def __str__(self) -> str:
        if len(self.variants) > 0:
            return str(self.variants[0])
        else:
            return ""


class Variant():
    def __init__(self, notes: list[Note], bass: Note) -> None:
        self.root = notes[0]
        self.notes = notes
        self.sorted_notes = sorted(notes)
        self.bass = bass
        self.name_short = ""
        self.name_complete = ""

    def __str__(self) -> str:
        return self.name_short


class NoteVariant(Variant):
    def __init__(self, notes: list[Note], bass: Note) -> None:
        super().__init__(notes, bass)
        self.name_short = self.root.pitch

    def __lt__(self, __o: "NoteVariant"):
        return self.root < __o.root


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

    def __init__(self, notes: list[Note], bass: Note) -> None:
        super().__init__(notes, bass)
        self.form(self.sorted_notes[0], self.sorted_notes[1])

    def __lt__(self, __o: "IntervalVariant"):
        return self.sorted_notes[0] < __o.sorted_notes[0]

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
        self.name_short = n0.pitch + self.name_short
        self.name_complete = n0.pitch + self.name_complete


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

    SEVENTH_MAP = OrderedDict({
        10: "7",
        11: "maj7",
    })

    TRIAD_MAP = OrderedDict({
        ("3", "#5"): ("#5", "augmented"),
        ("3", "5"): ("5", "major"),
        ("3", "b5"): ("", "major"),
        ("3", ""): ("", "major"),
        ("m3", "b5"): ("b5", "diminished"),
        ("m3", "5"): ("5", "minor"),
        ("m3", "#5"): ("", "minor"),
        ("m3", ""): ("", "minor"),
        ("4", "b5"): ("", "sus4"),
        ("4", "5"): ("5", "sus4"),
        ("4", "#5"): ("", "sus4"),
        ("4", ""): ("", "sus4"),
        ("2", "b5"): ("", "sus2"),
        ("2", "5"): ("5", "sus2"),
        ("2", "#5"): ("", "sus2"),
        ("2", ""): ("", "sus2"),
    })

    TRIAD_NAME_MAP = {
        "major": "",
        "minor": "m",
        "diminished": "dim",
        "augmented": "aug",
        "sus4": "sus4",
        "sus2": "sus2",
    }

    TRIAD_EXTENSION_MAP = {
        1: "addb9",
        2: "add9",
        3: "add#9",
        5: "add11",
        6: "add#11",
        8: "b6",
        9: "6",
    }

    SEVENTH_EXTENSION_MAP = {
        1: "b9",
        2: "9",
        3: "#9",
        5: "11",
        6: "#11",
        8: "b13",
        9: "13",
    }

    def __init__(self, notes: list[Note], bass: Note) -> None:
        super().__init__(notes, bass)
        self.triad = {}
        self.extensions = {}
        self.alterations = None
        self.third = {}
        self.fifth = {}
        self.seventh = {}

        if len(notes) > 2:
            # TODO: remove notes in different octaves
            self.distances = [notes[i] - notes[0]
                              for i in range(1, len(notes))]
            self.form(self.distances)

    def __lt__(self, __o: "ChordVariant") -> bool:
        if self.triad and not __o.triad:
            return True
        elif __o.triad and not self.triad:
            return False
        elif self.triad and __o.triad:
            if len(self.extensions) == 0 and len(__o.extensions) > 0:
                return True
            elif len(self.extensions) > 0 and len(__o.extensions) == 0:
                return False
            elif self.bass == self.root and __o.bass != __o.root:
                return True
            elif self.bass != self.root and __o.bass == __o.root:
                return False
            else:
                return len(self.extensions) < len(__o.extensions)
        else:
            return True

    def update_name(self) -> None:
        name_short = self.root.pitch
        for key in self.triad:
            name_short += self.TRIAD_NAME_MAP[key]
        if self.seventh:
            name_short += f"{','.join([key for key in self.seventh])}"
        if self.extensions:
            name_short += f"({','.join([key for key in self.extensions])})"
        if self.bass and self.root.letter != self.bass.letter:
            name_short += f'/{self.bass.letter}'
        self.name_short = name_short

    def form(self, dists: list[int]) -> None:
        # restrain everything to one octave and remove repeated intervals and unissons to the root
        # this also takes care of negative intervals
        filt_dists = set([dist % 12 for dist in dists if dist % 12])

        # find third
        third_name = ""
        third_dist = -1
        for dist, name in self.THIRD_MAP.items():
            if dist in filt_dists:
                third_name = name
                third_dist = dist
                break

        # find fifth
        fifth_name = ""
        fifth_dist = -1
        for dist, name in self.FIFTH_MAP.items():
            if dist in filt_dists:
                fifth_name = name
                fifth_dist = dist
                break

        # try to make the triad, given the third and fith from above
        if (third_name, fifth_name) in self.TRIAD_MAP:
            mapped_fith, triad_name = self.TRIAD_MAP[(third_name, fifth_name)]
            self.third[third_name] = None
            filt_dists.remove(third_dist)
            if mapped_fith:
                self.fifth[mapped_fith] = None
                filt_dists.remove(fifth_dist)
            self.triad[triad_name] = None

        # deal with seventh(s)
        dists_to_remove = []
        for dist, name in self.SEVENTH_MAP.items():
            if dist in filt_dists:
                self.seventh[name] = None
                dists_to_remove += [dist]
                # notice we don't break here, as we can have multiple 7ths
        for dist in dists_to_remove:
            filt_dists.remove(dist)

        # deal with remaining extensions
        if self.triad:
            if not self.seventh:
                ext_map = self.TRIAD_EXTENSION_MAP
            else:
                ext_map = self.SEVENTH_EXTENSION_MAP
            keys_to_remove = []
            for dist in filt_dists:
                if dist in self.TRIAD_EXTENSION_MAP:
                    ext = ext_map[dist]
                    self.extensions[ext] = None
                    keys_to_remove += [dist]
            for key in keys_to_remove:
                filt_dists.remove(key)

        self.update_name()
