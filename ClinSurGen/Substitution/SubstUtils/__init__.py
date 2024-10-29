def get_pattern(name_string):

    pattern_chars = ['L', 'U', 'D']

    def handle_last_pattern(_c, _last_pattern, _cnt_last_pattern, _pattern):

        if _last_pattern is None:  # init
            _cnt_last_pattern = 1

        elif _last_pattern == _c:  # same
            _cnt_last_pattern = _cnt_last_pattern + 1

        elif _last_pattern not in pattern_chars:
            _cnt_last_pattern = 1

        else:  # change
            _pattern = _pattern + _last_pattern + str(_cnt_last_pattern)
            _cnt_last_pattern = 1

        _last_pattern = _c

        return _pattern, _cnt_last_pattern, _last_pattern

    p = name_string

    last_pattern = None
    cnt_last_pattern = 0
    pattern = ''

    for c in p:

        if c.isupper():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                _c='U',
                _last_pattern=last_pattern,
                _cnt_last_pattern=cnt_last_pattern,
                _pattern=pattern
            )

        elif c.islower():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                _c='L',
                _last_pattern=last_pattern,
                _cnt_last_pattern=cnt_last_pattern,
                _pattern=pattern
            )
        elif c.isnumeric():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                _c='D',
                _last_pattern=last_pattern,
                _cnt_last_pattern=cnt_last_pattern,
                _pattern=pattern
            )
        else:

            if last_pattern is None:  # init
                cnt_last_pattern = 1

            if last_pattern in pattern_chars:
                pattern = pattern + last_pattern + str(cnt_last_pattern) + c
                cnt_last_pattern = 1
            else:
                pattern = pattern + c
                cnt_last_pattern = 1

            last_pattern = c

    if last_pattern in pattern_chars:
        pattern = pattern + last_pattern + str(cnt_last_pattern)

    return pattern
