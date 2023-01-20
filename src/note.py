
class Note():
    PITCHES_SHARP = ["C", "C#", "D", "D#", "E",
                     "F", "F#", "G", "G#", "A", "A#", "B"]
    PITCHES_FLAT = ["C", "Db", "D", "Eb", "E",
                    "F", "Gb", "G", "Ab", "A", "Bb", "B"]

    def __init__(self, note: str) -> None:
        self.pitch = ""
        self.octave = -1

        if len(note) == 0:
            return

        note = note.split()[0]

        if len(note) >= 3:
            letter = note[0].upper()
            accident = note[1].lower()
            if len(self.check_pitch(letter + accident)) > 0:
                octave = self.check_octave(note[2:])
                if octave > 0:
                    self.assign_pitch(letter, accident)
                    self.octave = octave
            elif len(self.check_pitch(letter)) > 0:
                octave = self.check_octave(note[1:])
                if octave > 0:
                    self.pitch = letter
                    self.octave = octave
        elif len(note) == 2:
            letter = note[0].upper()
            accident_octave = note[1].lower()
            if len(self.check_pitch(letter + accident_octave)) > 0:
                self.assign_pitch(letter, accident_octave)
            elif len(self.check_pitch(letter)) > 0:
                octave = self.check_octave(accident_octave)
                if octave > 0:
                    self.assign_pitch(letter)
                    self.octave = octave
        elif len(note) == 1:
            letter = note[0].upper()
            self.assign_pitch(self.check_pitch(letter))

    def __eq__(self, __o: "Note") -> bool:
        return self.pitch == __o.pitch and self.octave == __o.octave

    def __le__(self, __o: "Note") -> bool:
        return self == __o or self < __o
    
    def __ge__(self, __o: "Note") -> bool:
        return self == __o or self > __o

    def __lt__(self, __o: "Note") -> bool:
        if self.octave < __o.octave:
            return True
        elif self.octave > __o.octave:
            return False
        else:
            this_pitch_ind = self.check_pitch_ind(self.pitch)
            other_pitch_ind = self.check_pitch_ind(__o.pitch)
            return this_pitch_ind < other_pitch_ind

    def __gt__(self, __o: "Note") -> bool:
        return not self.__lt__(__o)

    def __str__(self) -> str:
        if self.octave >= 0:
            return self.pitch + str(self.octave)
        else:
            return self.pitch

    def __sub__(self, __o: "Note") -> int:
        diff = 0
        this_pitch_ind = self.check_pitch_ind(self.pitch)
        other_pitch_ind = self.check_pitch_ind(__o.pitch)
        if this_pitch_ind >= 0 and other_pitch_ind >= 0:
            diff = this_pitch_ind - other_pitch_ind
            diff += (self.octave - __o.octave) * 12
        return diff

    def __hash__(self) -> int:
        return hash(self.pitch)

    def assign_pitch(self, letter: str, accident: str = ""):
        self.letter = letter
        self.accident = accident
        self.pitch = letter + accident

    def check_pitch(self, pitch: str):
        if pitch in self.PITCHES_FLAT or pitch in self.PITCHES_SHARP:
            return pitch
        else:
            return ""
    
    def check_pitch_ind(self, pitch: str):
        if pitch in self.PITCHES_FLAT:
            return self.PITCHES_FLAT.index(pitch)
        elif pitch in self.PITCHES_SHARP:
            return self.PITCHES_SHARP.index(pitch)
        else:
            return -1

    def check_octave(self, octave_str: str):
        retval = -1
        try:
            octave = int(octave_str)
            if octave >= 0 and octave <= 8:
                retval = octave
        except:
            pass
        return retval