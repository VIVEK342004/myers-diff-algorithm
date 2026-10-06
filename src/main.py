import sys


def shortest_edit(a, b):
    """Myers O(ND): returns list of (op, item) for the middle part."""

    # Get the length of the old and new sequences.
    n, m = len(a), len(b)

    # If both sequences are empty, there is nothing to compare.
    if n + m == 0:
        return []

    # Offset used to allow negative diagonal (k) indexes in the V array.
    off = n + m + 1

    # V array stores the furthest x-position reached on each diagonal.
    v = [0] * (2 * off + 1)

    # Store the V array state for every edit-distance layer.
    # This information is required later during backtracking.
    trace = []

    # Try every possible edit distance from 0 up to n + m.
    for d in range(n + m + 1):

        # Save the current diagonal range of V before processing this layer.
        trace.append(v[off - d:off + d + 1])

        # k represents a diagonal in the edit graph.
        # Only every second diagonal is reachable at a given depth.
        for k in range(-d, d + 1, 2):

            # Decide whether the next move should be an insertion
            # or a deletion based on which path reaches farther.
            if k == -d or (k != d and v[off + k - 1] < v[off + k + 1]):
                x = v[off + k + 1]
            else:
                x = v[off + k - 1] + 1

            # Calculate the corresponding position in sequence b.
            y = x - k

            # Move diagonally while the current elements are equal.
            # These matching elements do not require an edit.
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            # Store the furthest x-position reached on this diagonal.
            v[off + k] = x

            # If both sequences have been completely consumed,
            # the shortest edit path has been found.
            if x >= n and y >= m:
                return backtrack(trace, a, b, d)


def backtrack(trace, a, b, d):
    # Start from the end of both sequences.
    x, y = len(a), len(b)

    # This list will contain the final sequence of operations.
    result = []

    # Walk backwards through each edit-distance layer.
    for depth in range(d, 0, -1):

        # Get the V state saved for this depth.
        prev = trace[depth]

        # Calculate the current diagonal.
        k = x - y

        # Determine the previous diagonal from which this path came.
        if k == -depth or (k != depth and prev[k - 1 + depth] < prev[k + 1 + depth]):
            pk = k + 1
        else:
            pk = k - 1

        # Get the previous x-coordinate from the selected diagonal.
        px = prev[pk + depth]

        # Calculate the previous y-coordinate.
        py = px - pk

        # Walk backwards through matching characters/items.
        while x > px and y > py:
            result.append((" ", a[x - 1]))
            x -= 1
            y -= 1

        # If x did not change, the operation was an insertion.
        if x == px:
            result.append(("+", b[y - 1]))
            y -= 1

        # Otherwise, the operation was a deletion.
        else:
            result.append(("-", a[x - 1]))
            x -= 1

    # Add any remaining matching items at the beginning.
    while x > 0 and y > 0:
        result.append((" ", a[x - 1]))
        x -= 1
        y -= 1

    # Backtracking creates the result in reverse order,
    # so reverse it to get the correct sequence.
    result.reverse()

    # Return the complete list of diff operations.
    return result


def myers_diff(old, new):
    # Find the length of the common prefix.
    # These items are unchanged and can be skipped.
    s = 0
    while s < len(old) and s < len(new) and old[s] == new[s]:
        s += 1

    # Find the length of the common suffix.
    # These items are also unchanged.
    e = 0
    while e < len(old) - s and e < len(new) - s and old[-1 - e] == new[-1 - e]:
        e += 1

    # Run the Myers diff algorithm only on the changed middle section.
    middle = shortest_edit(
        old[s:len(old) - e],
        new[s:len(new) - e]
    )

    # Add the unchanged common prefix to the result.
    result = [(" ", x) for x in old[:s]]

    # Temporary block used to collect consecutive additions/deletions.
    block = []

    # Process the changed middle section followed by the unchanged suffix.
    for item in middle + [(" ", x) for x in old[len(old) - e:]]:

        # A space means the item is unchanged.
        if item[0] == " ":

            # Output deletions before insertions inside the change block.
            result += sorted(block, key=lambda t: t[0] == "+")

            # Start a new change block.
            block = []

            # Add the unchanged item.
            result.append(item)

        # Otherwise, collect the deletion/insertion in the current block.
        else:
            block.append(item)

    # Add the final change block.
    return result + sorted(block, key=lambda t: t[0] == "+")


def read_file(path):
    # Open the file in binary mode so the original bytes are preserved.
    # Split the file into separate lines using the newline character.
    lines = open(path, "rb").read().split(b"\n")

    # Remove the extra empty item created when the file ends with a newline.
    if lines[-1] == b"":
        lines.pop()

    # Return the list of file lines.
    return lines


def mark(diff, sign):
    """Changed character ranges for one side ('-' = old, '+' = new)."""

    # Store the character ranges that were changed.
    ranges = []

    # Current character position in the selected side.
    pos = 0

    # Go through every diff operation.
    for op, _ in diff:

        # Process unchanged characters and characters belonging
        # to the requested side of the diff.
        if op == " " or op == sign:

            # If this operation represents a change on the requested side,
            # record its character position.
            if op == sign:

                # If the current change is directly next to the previous
                # change, extend the existing range.
                if ranges and ranges[-1][1] == pos:
                    ranges[-1][1] = pos + 1

                # Otherwise, start a new changed-character range.
                else:
                    ranges.append([pos, pos + 1])

            # Move to the next character position.
            pos += 1

    # Convert the ranges into a string such as "2-4,7-8".
    # Return "." when there are no changed characters.
    return ",".join(f"{s}-{e}" for s, e in ranges) or "."


def highlight_line(old, new):
    # Decode both byte strings into UTF-8 text.
    # This allows the Myers diff to compare individual characters.
    diff = myers_diff(old.decode("utf-8"), new.decode("utf-8"))

    # Create a highlight line showing changed character ranges
    # for the old line and the new line.
    return f"? {mark(diff, '-')} | {mark(diff, '+')}\n".encode()


def main():
    # Check that the program receives exactly three command-line arguments:
    # the mode (lines/highlight) and two file paths.
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):

        # Print the correct command usage to standard error.
        print("usage: main.py lines|highlight A B", file=sys.stderr)

        # Exit with code 2 to indicate invalid command-line usage.
        sys.exit(2)

    try:
        # Read both files and calculate their Myers diff.
        result = myers_diff(
            read_file(sys.argv[2]),
            read_file(sys.argv[3])
        )

    # Handle file-related errors such as missing files or permission issues.
    except OSError as error:

        # Print the error message to standard error.
        print(f"error: {error}", file=sys.stderr)

        # Exit with code 2 to indicate an error.
        sys.exit(2)

    # Enable character-level highlighting only when
    # the "highlight" mode is selected.
    show = sys.argv[1] == "highlight"

    # Store the final output lines.
    out = []

    # Store consecutive deleted lines.
    dels = []

    # Store consecutive inserted lines.
    ins = []

    def flush():
        # Output all deleted lines first.
        for line in dels:
            out.append(b"-" + line + b"\n")

        # Output all inserted lines after the deletions.
        for i, line in enumerate(ins):
            out.append(b"+" + line + b"\n")

            # When highlight mode is enabled, compare each inserted line
            # with the corresponding deleted line.
            if show and i < len(dels):
                out.append(highlight_line(dels[i], line))

        # Clear the current change block for the next set of changes.
        dels.clear()
        ins.clear()

    # Process every operation returned by the diff algorithm.
    for op, line in result:

        # A "-" operation means the line exists only in the old file.
        if op == "-":
            dels.append(line)

        # A "+" operation means the line exists only in the new file.
        elif op == "+":
            ins.append(line)

        # A space means the line is unchanged.
        else:

            # Finish the current deletion/insertion block.
            flush()

            # Add the unchanged line with a leading space.
            out.append(b" " + line + b"\n")

    # Flush any remaining changes at the end of the file.
    flush()

    # Write the complete diff output to standard output.
    sys.stdout.buffer.write(b"".join(out))


# Run main() only when this file is executed directly,
# not when it is imported as a Python module.
if __name__ == "__main__":
    main()