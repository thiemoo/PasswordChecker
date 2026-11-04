from checker.strength import calc_entropy, find_patterns


def test_nur_zahlen():
    assert "Besteht nur aus Zahlen" in find_patterns("123456")


def test_entropie_steigt_mit_laenge():
    assert calc_entropy("abcdefgh") > calc_entropy("abcd")
