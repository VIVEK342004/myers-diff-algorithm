from pathlib import Path


def myers_diff(old, new):
    """
    Compare two sequences using Myers' diff algorithm.

    Returns:
        A list of tuples:
        (" ", value) -> unchanged item
        ("-", value) -> deleted item
        ("+", value) -> added item
    """

    # Store the lengths of the old and new sequences.
    n = len(old)
    m = len(new)

    # V stores the furthest x-position reached on each diagonal.
    # The algorithm starts from diagonal 1 at position 0.
    v = {1: 0}

    # Store V for every edit distance so that the final
    # edit operations can be reconstructed later.
    trace = []

    # Try increasing edit distances until the end of both
    # sequences is reached.
    for d in range(n + m + 1):

        # Save the current state of V before processing this distance.
        trace.append(v.copy())

        # A diagonal is represented by k = x - y.
        # For edit distance d, k ranges from -d to d in steps of 2.
        for k in range(-d, d + 1, 2):

            # If we are at the lower boundary, move down
            # to the next diagonal.
            if k == -d:
                x = v.get(k + 1, 0)

            # If we are at the upper boundary, move right
            # from the previous diagonal.
            elif k == d:
                x = v.get(k - 1, 0) + 1

            # Choose the diagonal that reaches farther.
            elif v.get(k - 1, 0) < v.get(k + 1, 0):
                x = v.get(k + 1, 0)

            else:
                x = v.get(k - 1, 0) + 1

            # Calculate the corresponding y-coordinate.
            y = x - k

            # Follow matching items along the diagonal.
            # These matching items require no edit operation.
            while x < n and y < m and old[x] == new[y]:
                x += 1
                y += 1

            # Store the furthest x-position reached on this diagonal.
            v[k] = x

            # If both sequences have been completely processed,
            # the shortest edit path has been found.
            if x >= n and y >= m:
                return build_edit_script(trace, old, new, d)

    # Return an empty result if no comparison result was produced.
    return []


def build_edit_script(trace, old, new, d):
    """
    Reconstruct the actual edit operations from the Myers trace.

    The trace tells us which path the algorithm followed.
    We walk backwards from the end to reconstruct the changes.
    """

    # Start from the end of both sequences.
    x = len(old)
    y = len(new)

    # Store reconstructed operations here.
    result = []

    # Walk backwards through each edit distance.
    for depth in range(d, 0, -1):

        # Get the saved diagonal information for this depth.
        v = trace[depth]

        # Calculate the current diagonal.
        k = x - y

        # At the lower boundary, the previous move
        # must have come from the next diagonal.
        if k == -depth:
            previous_k = k + 1

        # At the upper boundary, the previous move
        # must have come from the previous diagonal.
        elif k == depth:
            previous_k = k - 1

        # Otherwise choose the diagonal that could have
        # reached the current position.
        elif v.get(k - 1, 0) < v.get(k + 1, 0):
            previous_k = k + 1

        else:
            previous_k = k - 1

        # Find the previous x-position.
        previous_x = v.get(previous_k, 0)

        # Calculate the corresponding previous y-position.
        previous_y = previous_x - previous_k

        # Matching values between the previous position and
        # current position are unchanged.
        while x > previous_x and y > previous_y:
            result.append((" ", old[x - 1]))
            x -= 1
            y -= 1

        # If x did not change, the current item was added.
        if x == previous_x:
            result.append(("+", new[y - 1]))
            y -= 1

        # Otherwise, the current item was deleted.
        else:
            result.append(("-", old[x - 1]))
            x -= 1

    # Handle any remaining matching items.
    while x > 0 and y > 0:
        result.append((" ", old[x - 1]))
        x -= 1
        y -= 1

    # Handle remaining deleted items from the old sequence.
    while x > 0:
        result.append(("-", old[x - 1]))
        x -= 1

    # Handle remaining added items from the new sequence.
    while y > 0:
        result.append(("+", new[y - 1]))
        y -= 1

    # Operations were reconstructed backwards,
    # so reverse them to get the correct order.
    result.reverse()

    return result


def read_file(path):
    """Read a UTF-8 text file and return its lines."""

    # Convert the provided path into a Path object,
    # read the file using UTF-8 encoding,
    # and split the content into individual lines.
    return Path(path).read_text(encoding="utf-8").splitlines()


def diff_files(old_path, new_path):
    """Read two files and compare their contents."""

    # Read the old version of the file.
    old_lines = read_file(old_path)

    # Read the new version of the file.
    new_lines = read_file(new_path)

    # Run Myers' algorithm on both sets of lines.
    return myers_diff(old_lines, new_lines)


def print_diff(result):
    """Display the diff result in a readable format."""

    # Process every operation generated by Myers' algorithm.
    for operation, value in result:

        # Print the operation symbol followed by the line.
        # " " means unchanged, "-" means deleted,
        # and "+" means added.
        print(f"{operation} {value}")


def main():
    """Run the default file comparison."""

    # Define the original/older file.
    old_file = "samples/paper_old.txt"

    # Define the updated/newer file.
    new_file = "samples/paper_new.txt"

    # Compare the two files using Myers' algorithm.
    result = diff_files(old_file, new_file)

    # Display which files are being compared.
    print(f"Comparing: {old_file}")
    print(f"      with: {new_file}")

    # Print a separator for better terminal readability.
    print("-" * 50)

    # Display the generated diff.
    print_diff(result)


# Run main() only when this file is executed directly.
# It will not run automatically if the file is imported elsewhere.
if __name__ == "__main__":
    main()