from pathlib import Path


def myers_diff(old, new):
    """
    Compare two sequences using Myers' diff algorithm.

    Returns:
        A list of tuples:
        (" ", value) for unchanged items
        ("-", value) for deleted items
        ("+", value) for added items
    """

    n = len(old)
    m = len(new)

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

            while x < n and y < m and old[x] == new[y]:
                x += 1
                y += 1

            v[k] = x

            if x >= n and y >= m:
                return build_edit_script(trace, old, new, d)

    return []


def build_edit_script(trace, old, new, d):
    """Reconstruct the edit script from the Myers trace."""

    x = len(old)
    y = len(new)

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
            result.append((" ", old[x - 1]))
            x -= 1
            y -= 1

        if x == previous_x:
            result.append(("+", new[y - 1]))
            y -= 1

        else:
            result.append(("-", old[x - 1]))
            x -= 1

    while x > 0 and y > 0:
        result.append((" ", old[x - 1]))
        x -= 1
        y -= 1

    while x > 0:
        result.append(("-", old[x - 1]))
        x -= 1

    while y > 0:
        result.append(("+", new[y - 1]))
        y -= 1

    result.reverse()

    return result


def read_file(path):
    """Read a UTF-8 text file."""

    return Path(path).read_text(encoding="utf-8").splitlines()


def diff_files(old_path, new_path):
    """Read and compare two text files."""

    old_lines = read_file(old_path)
    new_lines = read_file(new_path)

    return myers_diff(old_lines, new_lines)


def print_diff(result):
    """Display the diff in a readable format."""

    for operation, value in result:
        print(f"{operation} {value}")


def main():
    old_file = "samples/paper_old.txt"
    new_file = "samples/paper_new.txt"

    result = diff_files(old_file, new_file)

    print(f"Comparing: {old_file}")
    print(f"      with: {new_file}")
    print("-" * 50)

    print_diff(result)


if __name__ == "__main__":
    main()