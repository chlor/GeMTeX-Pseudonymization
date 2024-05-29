def get_pattern_ID(name_string):

    def handle_last_pattern(c, last_pattern, cnt_last_pattern, pattern):

        if last_pattern is None:  # init
            cnt_last_pattern = 1

        elif last_pattern == c:  # same
            cnt_last_pattern = cnt_last_pattern + 1

        elif last_pattern not in ['L', 'U']:
            cnt_last_pattern = 1

        else:  # change
            pattern = pattern + last_pattern + str(cnt_last_pattern)
            cnt_last_pattern = 1

        last_pattern = c

        return pattern, cnt_last_pattern, last_pattern


    p = name_string

    last_pattern = None
    cnt_last_pattern = 0
    pattern = ''

    for c in p:

        if c.isupper():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                c='U',
                last_pattern=last_pattern,
                cnt_last_pattern=cnt_last_pattern,
                pattern=pattern
            )

        elif c.islower():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                c='L',
                last_pattern=last_pattern,
                cnt_last_pattern=cnt_last_pattern,
                pattern=pattern
            )
        elif c.isnumeric():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                c='D',
                last_pattern=last_pattern,
                cnt_last_pattern=cnt_last_pattern,
                pattern=pattern
            )
        else:

            if last_pattern == None:  # init
                cnt_last_pattern = 1

            if last_pattern in ['L', 'U', 'D']:
                pattern = pattern + last_pattern + str(cnt_last_pattern) + c
                cnt_last_pattern = 1
            else:
                pattern = pattern + c
                cnt_last_pattern = 1

            last_pattern = c

    if last_pattern in ['L', 'U', 'D']:
        pattern = pattern + last_pattern + str(cnt_last_pattern)

    return pattern
