from pathlib import Path
import argparse
import sys


# ============================================================
# Myers Diff
# ============================================================

def myers_diff(old, new):
    """
    Myers shortest edit script.

    Works with any sequence:
        (" ", value) = keep
        ("-", value) = delete
        ("+", value) = insert

    The returned edit script is minimal in number of
    insertions + deletions.
    """

    n = len(old)
    m = len(new)

    # V[k] = furthest x reached on diagonal k.
    v = {1: 0}

    # Save V after every completed d layer.
    trace = []

    for d in range(n + m + 1):

        for k in range(-d, d + 1, 2):

            # Move down: insertion.
            if k == -d:
                x = v.get(k + 1, 0)

            # Move right: deletion.
            elif k == d:
                x = v.get(k - 1, 0) + 1

            # Choose the path reaching farther.
            elif v.get(k - 1, 0) < v.get(k + 1, 0):
                x = v.get(k + 1, 0)

            else:
                x = v.get(k - 1, 0) + 1

            y = x - k

            # Follow the snake.
            while (
                x < n
                and y < m
                and old[x] == new[y]
            ):
                x += 1
                y += 1

            v[k] = x

            # End reached.
            if x >= n and y >= m:
                trace.append(v.copy())

                return build_edit_script(
                    trace,
                    old,
                    new,
                    d
                )

        # Save the V array AFTER this d layer.
        trace.append(v.copy())

    return []


def build_edit_script(trace, old, new, d):
    """
    Reconstruct the edit script from the Myers trace.
    """

    x = len(old)
    y = len(new)

    result = []

    # Work backwards through edit distances.
    for depth in range(d, 0, -1):

        previous_v = trace[depth - 1]

        k = x - y

        # Determine previous diagonal.
        if k == -depth:
            previous_k = k + 1

        elif k == depth:
            previous_k = k - 1

        elif (
            previous_v.get(k - 1, 0)
            < previous_v.get(k + 1, 0)
        ):
            previous_k = k + 1

        else:
            previous_k = k - 1

        previous_x = previous_v.get(
            previous_k,
            0
        )

        previous_y = previous_x - previous_k

        # Walk backwards through equal values.
        while (
            x > previous_x
            and y > previous_y
        ):
            result.append(
                (" ", old[x - 1])
            )

            x -= 1
            y -= 1

        # Insertion.
        if x == previous_x:
            result.append(
                ("+", new[y - 1])
            )

            y -= 1

        # Deletion.
        else:
            result.append(
                ("-", old[x - 1])
            )

            x -= 1

    # Remaining equal values.
    while x > 0 and y > 0:
        result.append(
            (" ", old[x - 1])
        )

        x -= 1
        y -= 1

    # Remaining deletions.
    while x > 0:
        result.append(
            ("-", old[x - 1])
        )

        x -= 1

    # Remaining insertions.
    while y > 0:
        result.append(
            ("+", new[y - 1])
        )

        y -= 1

    result.reverse()

    # Normalize every change block so that deletions
    # always come before insertions.
    return normalize_change_blocks(result)


def normalize_change_blocks(result):
    """
    Ensure every change block has:

        - deleted lines
        + inserted lines

    with no keep line between them.
    """

    output = []

    i = 0
    total = len(result)

    while i < total:

        operation, value = result[i]

        if operation == " ":
            output.append((operation, value))
            i += 1
            continue

        deleted = []
        inserted = []

        # Collect one complete change block.
        while (
            i < total
            and result[i][0] != " "
        ):
            op, value = result[i]

            if op == "-":
                deleted.append(value)
            else:
                inserted.append(value)

            i += 1

        # Delete first.
        for value in deleted:
            output.append(("-", value))

        # Insert second.
        for value in inserted:
            output.append(("+", value))

    return output


# ============================================================
# File Reading
# ============================================================

def read_file(path):
    """
    Read a file as RAW BYTES.

    Assignment requirements:
      - split only on byte \\n
      - remove final empty piece
      - preserve \\r
      - invalid UTF-8 must still work
    """

    data = Path(path).read_bytes()

    lines = data.split(b"\n")

    # A final newline does not create an additional empty line.
    if lines and lines[-1] == b"":
        lines.pop()

    return lines


def diff_files(old_path, new_path):
    """
    Read both files and calculate line-level diff.
    """

    old_lines = read_file(old_path)
    new_lines = read_file(new_path)

    return myers_diff(
        old_lines,
        new_lines
    )


# ============================================================
# Part A
# ============================================================

def write_lines(result):
    """
    Write Part A output.

    Output is written as bytes because the input may contain
    arbitrary non-UTF-8 bytes.
    """

    stdout = sys.stdout.buffer

    for operation, value in result:

        stdout.write(
            operation.encode("ascii")
        )

        stdout.write(value)

        stdout.write(b"\n")


# ============================================================
# Part B - Character Diff
# ============================================================

def character_diff(old_text, new_text):
    """
    Myers diff for Unicode strings.

    Python string indexing is by Unicode code point, which is
    what the assignment requires.
    """

    return myers_diff(
        old_text,
        new_text
    )


def make_ranges(old_text, new_text):
    """
    Calculate changed character ranges.

    Returns:

        old_ranges
        new_ranges

    Example:

        [(3, 4)]

    means character position 3 was changed.
    """

    diff = character_diff(
        old_text,
        new_text
    )

    old_ranges = []
    new_ranges = []

    old_pos = 0
    new_pos = 0

    old_start = None
    new_start = None

    for operation, value in diff:

        # Unchanged character.
        if operation == " ":

            if old_start is not None:
                old_ranges.append(
                    (old_start, old_pos)
                )

                old_start = None

            if new_start is not None:
                new_ranges.append(
                    (new_start, new_pos)
                )

                new_start = None

            old_pos += 1
            new_pos += 1

        # Deleted character.
        elif operation == "-":

            if old_start is None:
                old_start = old_pos

            old_pos += 1

        # Inserted character.
        elif operation == "+":

            if new_start is None:
                new_start = new_pos

            new_pos += 1

    # Finish ranges at end of line.
    if old_start is not None:
        old_ranges.append(
            (old_start, old_pos)
        )

    if new_start is not None:
        new_ranges.append(
            (new_start, new_pos)
        )

    return old_ranges, new_ranges


def format_ranges(ranges):
    """
    Convert ranges to assignment format.

    [] -> .
    [(3, 5)] -> 3-5
    [(3, 5), (8, 10)] -> 3-5,8-10
    """

    if not ranges:
        return "."

    return ",".join(
        f"{start}-{end}"
        for start, end in ranges
    )


def make_highlight(old_line, new_line):
    """
    Create:

        ? old_ranges | new_ranges
    """

    old_text = old_line.decode("utf-8")
    new_text = new_line.decode("utf-8")

    old_ranges, new_ranges = make_ranges(
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
    Write Part A output plus Part B highlight lines.

    For each change block:
      - all deletions are printed first
      - insertions are printed next
      - a paired insertion is immediately followed by its '?' line
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

        # ----------------------------------------------------
        # Change block
        # ----------------------------------------------------

        deleted = []
        inserted = []

        while (
            i < total
            and result[i][0] != " "
        ):

            op, line = result[i]

            if op == "-":
                deleted.append(line)
            elif op == "+":
                inserted.append(line)

            i += 1

        # ----------------------------------------------------
        # Part A:
        # All deletions must come before insertions.
        # ----------------------------------------------------

        for line in deleted:

            stdout.write(b"-")
            stdout.write(line)
            stdout.write(b"\n")

        # ----------------------------------------------------
        # Part B:
        # Pair first '-' with first '+', second '-' with
        # second '+', etc. The '?' line MUST appear
        # immediately after its paired '+' line.
        # ----------------------------------------------------

        pairs = min(
            len(deleted),
            len(inserted)
        )

        for index, line in enumerate(inserted):

            # Part A '+' line.
            stdout.write(b"+")
            stdout.write(line)
            stdout.write(b"\n")

            # Part B '?' line for paired insertion.
            if index < pairs:

                highlight = make_highlight(
                    deleted[index],
                    inserted[index]
                )

                stdout.write(
                    highlight.encode("utf-8")
                )

                stdout.write(b"\n")


# ============================================================
# Command Line
# ============================================================

def parse_arguments():
    """
    Expected commands:

        python main.py lines A B

        python main.py highlight A B
    """

    parser = argparse.ArgumentParser(
        description=(
            "Myers minimal line diff "
            "and character highlighting"
        )
    )

    parser.add_argument(
        "command",
        choices=("lines", "highlight"),
        help="lines = Part A, highlight = Part B"
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
    """
    Program entry point.
    """

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

        # Assignment:
        #   stdout = empty
        #   stderr = error
        #   exit code = 2

        print(
            f"error: {error}",
            file=sys.stderr
        )

        sys.exit(2)

    if args.command == "lines":

        write_lines(result)

    else:

        write_highlight(result)


if __name__ == "__main__":
    main()