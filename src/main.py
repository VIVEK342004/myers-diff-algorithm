from pathlib import Path
import argparse
import sys


def myers_diff(old, new):
    """
    Myers' O(ND) diff algorithm.

    Works with any indexable sequence:
        (" ", value) -> unchanged
        ("-", value) -> deleted
        ("+", value) -> inserted
    """

    n = len(old)
    m = len(new)

    # V[k] = furthest x reached on diagonal k.
    v = {1: 0}

    # Save V before each edit-distance layer.
    trace = []

    for d in range(n + m + 1):
        trace.append(v.copy())

        for k in range(-d, d + 1, 2):

            # Move down: insertion into old / take from new.
            if k == -d:
                x = v.get(k + 1, 0)

            # Move right: deletion from old.
            elif k == d:
                x = v.get(k - 1, 0) + 1

            # Choose the path that reaches farther.
            elif v.get(k - 1, 0) < v.get(k + 1, 0):
                x = v.get(k + 1, 0)

            else:
                x = v.get(k - 1, 0) + 1

            y = x - k

            # Follow the snake of equal values.
            while x < n and y < m and old[x] == new[y]:
                x += 1
                y += 1

            v[k] = x

            # Reached the end.
            if x >= n and y >= m:
                return build_edit_script(trace, old, new, d)

    return []


def build_edit_script(trace, old, new, d):
    """
    Reconstruct the Myers edit script from the trace.
    """

    x = len(old)
    y = len(new)

    result = []

    for depth in range(d, 0, -1):

        previous_v = trace[depth - 1]

        k = x - y

        # Determine which diagonal the previous edit came from.
        if k == -depth:
            previous_k = k + 1

        elif k == depth:
            previous_k = k - 1

        elif previous_v.get(k - 1, 0) < previous_v.get(k + 1, 0):
            previous_k = k + 1

        else:
            previous_k = k - 1

        previous_x = previous_v.get(previous_k, 0)
        previous_y = previous_x - previous_k

        # Walk backwards over unchanged values.
        while x > previous_x and y > previous_y:
            result.append((" ", old[x - 1]))
            x -= 1
            y -= 1

        # Insertion.
        if x == previous_x:
            result.append(("+", new[y - 1]))
            y -= 1

        # Deletion.
        else:
            result.append(("-", old[x - 1]))
            x -= 1

    # Remaining unchanged values.
    while x > 0 and y > 0:
        result.append((" ", old[x - 1]))
        x -= 1
        y -= 1

    # Remaining deletions.
    while x > 0:
        result.append(("-", old[x - 1]))
        x -= 1

    # Remaining insertions.
    while y > 0:
        result.append(("+", new[y - 1]))
        y -= 1

    result.reverse()

    return result


def read_file(path):
    """
    Read a file exactly as raw bytes.

    The assignment requires:
    - split on byte \\n
    - drop final empty piece
    - preserve \\r
    - do not decode as UTF-8 for Part A
    """

    data = Path(path).read_bytes()

    lines = data.split(b"\n")

    # A final newline does not create an additional empty line.
    if lines and lines[-1] == b"":
        lines.pop()

    return lines


def diff_files(old_path, new_path):
    """
    Read two files and calculate their line-level diff.
    """

    old_lines = read_file(old_path)
    new_lines = read_file(new_path)

    return myers_diff(old_lines, new_lines)


def write_part_a(result):
    """
    Write the Part A diff.

    Output is written as bytes because input lines may contain
    arbitrary bytes and may not be valid UTF-8.
    """

    stdout = sys.stdout.buffer

    for operation, value in result:
        stdout.write(operation.encode("ascii"))
        stdout.write(value)
        stdout.write(b"\n")


def changed_ranges(old_line, new_line):
    """
    Find the minimum changed character ranges between two lines.

    Both arguments are Python strings, so indexing is by Unicode
    code point as required by the assignment.

    Returns:
        (old_ranges, new_ranges)

    Each range is represented as:
        (start, end)
    """

    diff = myers_diff(old_line, new_line)

    old_ranges = []
    new_ranges = []

    old_position = 0
    new_position = 0

    old_change_start = None
    new_change_start = None

    for operation, value in diff:

        if operation == " ":
            # Finish an old-side change.
            if old_change_start is not None:
                old_ranges.append(
                    (old_change_start, old_position)
                )
                old_change_start = None

            # Finish a new-side change.
            if new_change_start is not None:
                new_ranges.append(
                    (new_change_start, new_position)
                )
                new_change_start = None

            old_position += 1
            new_position += 1

        elif operation == "-":
            if old_change_start is None:
                old_change_start = old_position

            old_position += 1

        elif operation == "+":
            if new_change_start is None:
                new_change_start = new_position

            new_position += 1

    # Finish changes at the end of the line.
    if old_change_start is not None:
        old_ranges.append(
            (old_change_start, old_position)
        )

    if new_change_start is not None:
        new_ranges.append(
            (new_change_start, new_position)
        )

    return old_ranges, new_ranges


def format_ranges(ranges):
    """
    Convert [(start, end), ...] to:
        start-end,start-end

    An empty list becomes ".".
    """

    if not ranges:
        return "."

    return ",".join(
        f"{start}-{end}"
        for start, end in ranges
    )


def make_highlight_line(old_line, new_line):
    """
    Create the Part B '?' line for a pair of changed lines.
    """

    old_text = old_line.decode("utf-8")
    new_text = new_line.decode("utf-8")

    old_ranges, new_ranges = changed_ranges(
        old_text,
        new_text
    )

    return (
        "? "
        + format_ranges(old_ranges)
        + " | "
        + format_ranges(new_ranges)
    )


def write_highlight(result):
    """
    Print Part A output plus character highlighting.

    Changed lines are paired inside each change block:
        first - with first +
        second - with second +
        ...

    Unpaired lines receive no '?' line.
    """

    stdout = sys.stdout.buffer

    i = 0
    total = len(result)

    while i < total:

        operation, value = result[i]

        # Keep line.
        if operation == " ":
            stdout.write(b" ")
            stdout.write(value)
            stdout.write(b"\n")
            i += 1
            continue

        # We are at the beginning of a change block.
        deleted = []
        inserted = []

        while i < total and result[i][0] != " ":

            op, line = result[i]

            if op == "-":
                deleted.append(line)
            else:
                inserted.append(line)

            i += 1

        # Part A output:
        # all deletions first, then all insertions.
        for line in deleted:
            stdout.write(b"-")
            stdout.write(line)
            stdout.write(b"\n")

        for line in inserted:
            stdout.write(b"+")
            stdout.write(line)
            stdout.write(b"\n")

        # Part B pairing.
        pair_count = min(
            len(deleted),
            len(inserted)
        )

        for index in range(pair_count):

            highlight = make_highlight_line(
                deleted[index],
                inserted[index]
            )

            stdout.write(
                highlight.encode("utf-8")
            )
            stdout.write(b"\n")


def parse_arguments():
    """
    Parse:
        main.py lines A B
        main.py highlight A B
    """

    parser = argparse.ArgumentParser(
        description="Myers line diff"
    )

    parser.add_argument(
        "command",
        choices=("lines", "highlight"),
        help="Run Part A or Part B"
    )

    parser.add_argument(
        "old_file",
        help="Original file A"
    )

    parser.add_argument(
        "new_file",
        help="Updated file B"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        result = diff_files(
            args.old_file,
            args.new_file
        )

    except (
        FileNotFoundError,
        IsADirectoryError,
        PermissionError,
        OSError
    ) as error:

        # Assignment requires:
        # - nothing on stdout
        # - error on stderr
        # - exit code 2
        print(
            f"error: {error}",
            file=sys.stderr
        )

        sys.exit(2)

    if args.command == "lines":
        write_part_a(result)

    else:
        # Part B requires the same Part A output plus
        # character-level highlights.
        write_highlight(result)


if __name__ == "__main__":
    main()