from pathlib import Path


def myers_diff(a, b):
    """
    Compute the shortest edit script between two sequences
    using Myers' diff algorithm.

    Returns a list of tuples:
        (" ", value)  -> unchanged
        ("-", value)  -> deleted
        ("+", value)  -> added
    """

    n = len(a)
    m = len(b)

    # V stores the furthest-reaching x coordinate
    # for each diagonal k.
    v = {1: 0}

    trace = []

    for d in range(n + m + 1):
        trace.append(v.copy())

        for k in range(-d, d + 1, 2):

            if k == -d:
                x = v.get(k + 1, 0)
            elif k == d:
                x = v.get(k - 1, 0) + 1
            elif v.get(k - 1, 0) < v.get(k + 1, 0):
                x = v.get(k + 1, 0)
            else:
                x = v.get(k - 1, 0) + 1

            y = x - k

            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[k] = x

            if x >= n and y >= m:
                return _build_edit_script(trace, a, b, d)

    return []


def _build_edit_script(trace, a, b, d):
    """
    Reconstruct the edit script from Myers' trace.
    """

    x = len(a)
    y = len(b)

    result = []

    for depth in range(d, 0, -1):
        v = trace[depth]

        k = x - y

        if k == -depth:
            previous_k = k + 1
        elif k == depth:
            previous_k = k - 1
        elif v.get(k - 1, 0) < v.get(k + 1, 0):
            previous_k = k + 1
        else:
            previous_k = k - 1

        previous_x = v.get(previous_k, 0)
        previous_y = previous_x - previous_k

        while x > previous_x and y > previous_y:
            result.append((" ", a[x - 1]))
            x -= 1
            y -= 1

        if x == previous_x:
            result.append(("+", b[y - 1]))
            y -= 1
        else:
            result.append(("-", a[x - 1]))
            x -= 1

    while x > 0 and y > 0:
        result.append((" ", a[x - 1]))
        x -= 1
        y -= 1

    while x > 0:
        result.append(("-", a[x - 1]))
        x -= 1

    while y > 0:
        result.append(("+", b[y - 1]))
        y -= 1

    result.reverse()

    return result


def diff_files(old_file, new_file):
    """
    Compare two text files using Myers diff.
    """

    old_path = Path(old_file)
    new_path = Path(new_file)

    old_lines = old_path.read_text(encoding="utf-8").splitlines()
    new_lines = new_path.read_text(encoding="utf-8").splitlines()

    return myers_diff(old_lines, new_lines)


def print_diff(diff):
    """
    Print the diff in a simple readable format.
    """

    for operation, value in diff:
        print(f"{operation} {value}")


if __name__ == "__main__":
    old_file = "samples/paper_old.txt"
    new_file = "samples/paper_new.txt"

    result = diff_files(old_file, new_file)

    print_diff(result)