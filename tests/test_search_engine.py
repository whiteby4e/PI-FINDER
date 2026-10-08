from search_engine import builtin_find, kmp_search, naive_search


def test_empty_pattern_matches_at_zero():
    data = b"12345"
    for search in (builtin_find, naive_search, kmp_search):
        assert search(data, b"") == 0


def test_all_algorithms_return_same_position():
    data = b"314159265358979323846"
    pattern = b"9265"
    expected = data.find(pattern)
    assert naive_search(data, pattern) == expected
    assert kmp_search(data, pattern) == expected
    assert builtin_find(data, pattern) == expected


def test_missing_pattern():
    data = b"123456"
    pattern = b"999"
    assert naive_search(data, pattern) == -1
    assert kmp_search(data, pattern) == -1
    assert builtin_find(data, pattern) == -1
