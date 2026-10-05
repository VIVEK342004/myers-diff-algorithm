from pathlib import Path
import argparse
import sys


def myers_diff(old, new):
    """
    Compare two sequences using Myers' diff algorithm.

    Returns:
        A list of tuples:
        (" ", value) -> unchanged item
        ("-", value) -> deleted item
        ("+", value) -> added item
    """

    # Number of items in the old and new sequences.
    n = len(old)
    m = len(new)

    # V[k] stores the furthest x-position reached
    # on diagonal k.
    v = {1: 0}

    # Save V after every edit distance.
    trace = []

    # Try every possible edit distance.
    for d in range(n + m + 1):

        # Save a copy of V before processing this distance.
        trace.append(v.copy())

        # Check every diagonal possible at this distance.
        for k in range(-d, d + 1, 2):

            # Move down when k is the lower boundary.
            if k == -d:
                x = v.get(k + 1, 0)

            # Move right when k is the upper boundary.
            elif k == d:
                x = v.get(k - 1, 0) + 1

            # Choose the path that reaches farther.
            elif v.get(k - 1, 0) < v.get(k + 1, 0):
                x = v.get(k + 1, 0)

            else:
                x = v.get(k - 1, 0) + 1

            # Calculate the y-position from x and k.
            y = x - k

            # Follow equal items along the diagonal.
            while x < n and y < m and old[x] == new[y]:
                x += 1
                y += 1

            # Store the furthest x-position for this diagonal.
            v[k] = x

            # The end of both sequences has been reached.
            if x >= n and y >= m:
                return build_edit_script(trace, old, new, d)

    return []


def build_edit_script(trace, old, new, d):
    """
    Reconstruct the edit operations from the Myers trace.
    """

    # Start at the end of both sequences.
    x = len(old)
    y = len(new)

    # Store operations in reverse order.
    result = []

    # Walk backwards through the edit distances.
    for depth in range(d, 0, -1):

        # IMPORTANT:
        # We need the V array from the PREVIOUS edit distance.
        #
        # Using trace[depth] here causes incorrect reconstruction.
        previous_v = trace[depth - 1]

        # Current diagonal.
        k = x - y

        # Decide which diagonal the previous step came from.
        if k == -depth:
            previous_k = k + 1

        elif k == depth:
            previous_k = k - 1

        elif previous_v.get(k - 1, 0) < previous_v.get(k + 1, 0):
            previous_k = k + 1

        else:
            previous_k = k - 1

        # Position before the edit operation.
        previous_x = previous_v.get(previous_k, 0)
        previous_y = previous_x - previous_k

        # Walk backwards through unchanged items.
        while x > previous_x and y > previous_y:
            result.append((" ", old[x - 1]))
            x -= 1
            y -= 1

        # If x did not change, an item was added to new.
        if x == previous_x:
            result.append(("+", new[y - 1]))
            y -= 1

        # Otherwise, an item was deleted from old.
        else:
            result.append(("-", old[x - 1]))
            x -= 1

    # Any remaining items are unchanged.
    while x > 0 and y > 0:
        result.append((" ", old[x - 1]))
        x -= 1
        y -= 1

    # Remaining old items were deleted.
    while x > 0:
        result.append(("-", old[x - 1]))
        x -= 1

    # Remaining new items were added.
    while y > 0:
        result.append(("+", new[y - 1]))
        y -= 1

    # We reconstructed backwards, so reverse the result.
    result.reverse()

    return result


def read_file(path):
    """
    Read a UTF-8 text file and return its lines.
    """

    return Path(path).read_text(encoding="utf-8").splitlines()


def diff_files(old_path, new_path):
    """
    Read two files and calculate their line-level diff.
    """

    old_lines = read_file(old_path)
    new_lines = read_file(new_path)

    return myers_diff(old_lines, new_lines)


def print_diff(result):
    """
    Print diff operations.
    """

    for operation, value in result:
        print(f"{operation} {value}")


def main():
    """
    Command-line entry point.
    """

    # Accept the old and new file from the command line.
    parser = argparse.ArgumentParser(
        description="Compare two text files using Myers' diff algorithm."
    )

    parser.add_argument(
        "old_file",
        help="Path to the original/old file."
    )

    parser.add_argument(
        "new_file",
        help="Path to the updated/new file."
    )

    args = parser.parse_args()

    try:
        # Calculate the diff.
        result = diff_files(args.old_file, args.new_file)

    except (FileNotFoundError, IsADirectoryError, PermissionError):
        # Missing/unreadable input must produce exit code 2
        # and no normal stdout output.
        sys.exit(2)

    # Print only the diff.
    print_diff(result)


if __name__ == "__main__":
    main()