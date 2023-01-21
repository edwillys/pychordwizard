from src.chord import Chord


def test_one_note() -> None:
    assert (str(Chord("A")) == 'A')
    assert (str(Chord(" a ")) == 'A')
    assert (str(Chord("")) == '')
    assert (str(Chord("  ")) == '')
    assert (str(Chord(" I ")) == '')


def test_intervals():
    test_array = [
        ["C C#", "m2", "M7"],
        ["C Db", "m2", "M7"],
        ["C D", "M2", "m7"],
        ["C D#", "m3", "M6"],
        ["C Eb", "m3", "M6"],
        ["C E", "M3", "m6"],
        ["C F", "4", "5"],
        ["C F#", "aug4", "dim5"],
        ["C Gb", "dim5", "aug4"],
        ["C G", "5", "4"],
        ["C G#", "aug5", "M3"],
        ["C Ab", "m6", "M3"],
        ["C A", "M6", "m3"],
        ["C A#", "m7", "M2"],
        ["C Bb", "m7", "M2"],
        ["C B", "M7", "m2"],
    ]

    for el in test_array:
        notes, expected, expected_inv = el
        chord = Chord(notes)
        assert(str(chord) == expected)
        # test different octaves 
        notes_oct = notes.split()
        notes_oct[0] += '3'
        notes_oct[1] += '6'
        notes_oct = ' '.join(notes_oct)
        chord_oct = Chord(notes_oct)
        assert(str(chord_oct) == expected)
        # test inversion
        notes_inv = notes.split()
        notes_inv[0] += '5'
        notes_inv[1] += '4'
        notes_inv = ' '.join(notes_inv)
        chord_inv = Chord(notes_inv)
        assert(str(chord_inv) == expected_inv)
    
    assert(str(Chord("C4 C5")) == "8")
    assert(str(Chord("C0 C5")) == "8")

def test_triads():
    test_array = [
        ["C E G", "C"],
        ["C Eb G", "Cm"],
        ["C Eb Gb", "Cdim"],
        ["C E G#", "Caug"],
        ["C D# G", "Cm"],
        ["C D# F#", "Cdim"],
        ["C E Ab", "Caug"],
        ["C3 E3 G3 C4 E4 G4", "C"],
        ["C D G", "Csus2"],
        ["C F G", "Csus4"],
    ]
    for t in test_array:
        assert(str(Chord(t[0])) == t[1])

def test_triad_inversion():
    pass

def test_sevenths():
    pass

def test_extensions():
    pass

def test_alternate_names():
    pass

if __name__ == "__main__":
    import pytest
    pytest.main()
