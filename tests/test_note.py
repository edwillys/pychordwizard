from src.note import Note


def test_letter() -> None:
    assert (str(Note("a")) == 'A')


def test_letter_accident() -> None:
    assert (str(Note("a#")) == 'A#')
    assert (str(Note("ab")) == 'Ab')


def test_letter_accident_octave() -> None:
    note = Note("a#5")
    assert (str(note) == 'A#5')


def test_dummy() -> None:
    assert (str(Note(" E# ")) == '')
    assert (str(Note(" Fb ")) == '')
    assert (str(Note(" a#5 ")) == 'A#5')
    assert (str(Note("")) == "")
    assert (str(Note("I")) == "")
    assert (str(Note("I#5")) == "")
    assert (str(Note("a#20")) == "")
    assert (str(Note("ak20")) == "")


def test_equal() -> None:
    assert (Note("E") == Note("E"))
    assert (Note("e") == Note("E"))
    assert (Note("e") == Note(" E "))
    assert (Note("e") != Note("f"))


def test_interval() -> None:
    base_note = Note("D")
    assert ((Note("C") - base_note) == -2)
    assert ((Note("D") - base_note) == 0)
    assert ((Note("E") - base_note) == 2)
    base_note = Note("D4")
    assert ((Note("D5") - base_note) == 12)


def test_lt() -> None:
    assert (Note("D") > Note("C"))
    assert (Note("D") >= Note("C"))
    assert (Note("C") < Note("D"))
    assert (Note("C") <= Note("D"))
    assert (Note("C4") < Note("C5"))
    assert (Note("C5") > Note("C4"))


def test_find_below() -> None:
    assert (Note("C4").find_below(Note("D")) == Note("D3"))
    assert (Note("C4").find_below(Note("D5")) == Note("D3"))
    assert (Note("C4").find_below(Note("D3")) == Note("D3"))
    assert (Note("C4").find_below(Note("A")) == Note("A3"))
    assert (Note("C4").find_below(Note("C")) == Note("C3"))
    assert (Note("D4").find_below(Note("C")) == Note("C4"))
    assert (Note("G4").find_below(Note("F")) == Note("F4"))
    assert (Note("A4").find_below(Note("F")) == Note("F4"))
    assert (Note("B3").find_below(Note("G")) == Note("G3"))
    assert (Note("E4").find_below(Note("B")) == Note("B3"))
    assert (Note("Bb3").find_below(Note("G#")) == Note("G#3"))


def test_add() -> None:
    assert ((Note("C") + 0) == Note("C"))
    assert ((Note("C") + 1) == Note("C#"))
    assert ((Note("C") + 12) == Note("C"))
    assert ((Note("C") + 13) == Note("C#"))
    assert ((Note("C4") + 0) == Note("C4"))
    assert ((Note("C4") + 1) == Note("C#4"))
    assert ((Note("C4") + 12) == Note("C5"))
    assert ((Note("C4") + 13) == Note("C#5"))
    assert ((Note("B3") + 1) == Note("C4"))


if __name__ == "__main__":
    import pytest
    pytest.main()
