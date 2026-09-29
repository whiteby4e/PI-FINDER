from search_engine import builtin_find, kmp_search, naive_search


def test_empty_pattern():
    data = b"123456789"
    assert builtin_find(data, b"") == 0
    assert naive_search(data, b"") == 0
    assert kmp_search(data, b"") == 0


def test_found():
    data = b"314159265358979323846"
    pattern = b"265358"
    expected = data.find(pattern)

    assert builtin_find(data, pattern) == expected
    assert naive_search(data, pattern) == expected
    assert kmp_search(data, pattern) == expected


def test_not_found():
    data = b"314159265358979323846"
    pattern = b"000000000"
    assert builtin_find(data, pattern) == -1
    assert naive_search(data, pattern) == -1
    assert kmp_search(data, pattern) == -1
