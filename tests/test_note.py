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
    assert((Note("C") - base_note) == -2)
    assert((Note("D") - base_note) == 0)
    assert((Note("E") - base_note) == 2)
    base_note = Note("D4")
    assert((Note("D5") - base_note) == 12)

def test_lt() -> None:
    assert(Note("D") > Note("C"))
    assert(Note("D") >= Note("C"))
    assert(Note("C") < Note("D"))
    assert(Note("C") <= Note("D"))
    assert(Note("C4") < Note("C5"))
    assert(Note("C5") > Note("C4"))

if __name__ == "__main__":
    import pytest
    pytest.main()
