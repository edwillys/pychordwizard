from src.chord import Chord


def test_one_note() -> None:
    assert (str(Chord("A")) == 'A')
    assert (str(Chord(" a ")) == 'A')
    assert (str(Chord("")) == '')
    assert (str(Chord("  ")) == '')
    assert (str(Chord(" I ")) == '')


def test_intervals():
    test_array = [
        ["C C#", "Cm2", "C#M7"],
        ["C Db", "Cm2", "DbM7"],
        ["C D", "CM2", "Dm7"],
        ["C D#", "Cm3", "D#M6"],
        ["C Eb", "Cm3", "EbM6"],
        ["C E", "CM3", "Em6"],
        ["C F", "C4", "F5"],
        ["C F#", "Caug4", "F#dim5"],
        ["C Gb", "Cdim5", "Gbaug4"],
        ["C G", "C5", "G4"],
        ["C G#", "Caug5", "G#M3"],
        ["C Ab", "Cm6", "AbM3"],
        ["C A", "CM6", "Am3"],
        ["C A#", "Cm7", "A#M2"],
        ["C Bb", "Cm7", "BbM2"],
        ["C B", "CM7", "Bm2"],
    ]

    for el in test_array:
        notes, expected, expected_inv = el
        chord = Chord(notes)
        assert (str(chord) == expected)
        # test different octaves
        notes_oct = notes.split()
        notes_oct[0] += '3'
        notes_oct[1] += '6'
        notes_oct = ' '.join(notes_oct)
        chord_oct = Chord(notes_oct)
        assert (str(chord_oct) == expected)
        # test inversion
        notes_inv = notes.split()
        notes_inv[0] += '5'
        notes_inv[1] += '4'
        notes_inv = ' '.join(notes_inv)
        chord_inv = Chord(notes_inv)
        assert (str(chord_inv) == expected_inv)

    assert (str(Chord("C4 C5")) == "C8")
    assert (str(Chord("C0 C5")) == "C8")


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
        ["C3 E4 G5", "C"],
    ]
    for t in test_array:
        assert (str(Chord(t[0])) == t[1])


def test_triad_inversion():
    test_array = [
        ["C4 E4 G3", "C/G"],
    ]
    for t in test_array:
        chord = Chord(t[0])
        chord_names = [str(var) for var in chord.variants]
        assert (t[1] in chord_names)


def test_sevenths():
    test_array = [
        ["C E G B", "Cmaj7"],
        ["C E B", "Cmaj7"],  # no 5th
        ["C E G Bb", "C7"],
        ["C Eb G Bb", "Cm7"],
        ["C Eb G B", "Cmmaj7"],
        ["C3 E4 G5 B6", "Cmaj7"],  # different octaves
    ]
    for t in test_array:
        assert (str(Chord(t[0])) == t[1])


def test_extensions():
    pass


if __name__ == "__main__":
    import pytest
    pytest.main()
