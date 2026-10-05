def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def myers_diff(a, b):
    n = len(a)
    m = len(b)

    v = {1: 0}
    trace = []
    distance = None

    # Forward search
    for d in range(n + m + 1):
        trace.append(v.copy())

        for k in range(-d, d + 1, 2):

            if k == -d or (
                k != d
                and v.get(k - 1, -1) < v.get(k + 1, -1)
            ):
                x = v.get(k + 1, 0)

            else:
                x = v.get(k - 1, 0) + 1

            y = x - k

            # Follow matching lines
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[k] = x

            if x >= n and y >= m:
                distance = d
                break

        if distance is not None:
            break

    # Backtracking
    x = n
    y = m
    result = []

    for d in range(distance, 0, -1):

        v = trace[d]
        k = x - y

        if k == -d or (
            k != d
            and v.get(k - 1, -1) < v.get(k + 1, -1)
        ):
            previous_k = k + 1

        else:
            previous_k = k - 1

        previous_x = v.get(previous_k, 0)
        previous_y = previous_x - previous_k

        # Matching lines
        while x > previous_x and y > previous_y:
            result.append(("equal", a[x - 1]))
            x -= 1
            y -= 1

        # Insert or delete
        if x == previous_x:
            result.append(("insert", b[y - 1]))
            y -= 1

        else:
            result.append(("delete", a[x - 1]))
            x -= 1

    # Remaining matching lines
    while x > 0 and y > 0:
        result.append(("equal", a[x - 1]))
        x -= 1
        y -= 1

    while x > 0:
        result.append(("delete", a[x - 1]))
        x -= 1

    while y > 0:
        result.append(("insert", b[y - 1]))
        y -= 1

    result.reverse()
    return result


def print_diff(diff):
    for operation, line in diff:

        if operation == "equal":
            print(" " + line)

        elif operation == "delete":
            print("-" + line)

        elif operation == "insert":
            print("+" + line)


def main():
    file_a = read_file("test_a.txt")
    file_b = read_file("test_b.txt")

    diff = myers_diff(file_a, file_b)

    print_diff(diff)


if __name__ == "__main__":
    main()