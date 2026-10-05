import sys


def shortest_edit(a, b):
    """Myers O(ND): returns list of (op, item) for the middle part."""
    n, m = len(a), len(b)
    if n + m == 0:
        return []
    off = n + m + 1
    v = [0] * (2 * off + 1)
    trace = []  # trace[d] = slice of v before layer d (k from -d to d)

    for d in range(n + m + 1):
        trace.append(v[off - d:off + d + 1])
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[off + k - 1] < v[off + k + 1]):
                x = v[off + k + 1]
            else:
                x = v[off + k - 1] + 1
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[off + k] = x
            if x >= n and y >= m:
                return backtrack(trace, a, b, d)


def backtrack(trace, a, b, d):
    x, y = len(a), len(b)
    result = []
    for depth in range(d, 0, -1):
        prev = trace[depth]
        k = x - y
        if k == -depth or (k != depth and prev[k - 1 + depth] < prev[k + 1 + depth]):
            pk = k + 1
        else:
            pk = k - 1
        px = prev[pk + depth]
        py = px - pk
        while x > px and y > py:
            result.append((" ", a[x - 1]))
            x -= 1
            y -= 1
        if x == px:
            result.append(("+", b[y - 1]))
            y -= 1
        else:
            result.append(("-", a[x - 1]))
            x -= 1
    while x > 0 and y > 0:
        result.append((" ", a[x - 1]))
        x -= 1
        y -= 1
    result.reverse()
    return result


def myers_diff(old, new):
    # skip the common start and end, they are always kept
    s = 0
    while s < len(old) and s < len(new) and old[s] == new[s]:
        s += 1
    e = 0
    while e < len(old) - s and e < len(new) - s and old[-1 - e] == new[-1 - e]:
        e += 1
    middle = shortest_edit(old[s:len(old) - e], new[s:len(new) - e])

    # inside every change block, put deletions before insertions
    result = [(" ", x) for x in old[:s]]
    block = []
    for item in middle + [(" ", x) for x in old[len(old) - e:]]:
        if item[0] == " ":
            result += sorted(block, key=lambda t: t[0] == "+")
            block = []
            result.append(item)
        else:
            block.append(item)
    return result + sorted(block, key=lambda t: t[0] == "+")


def read_file(path):
    lines = open(path, "rb").read().split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def mark(diff, sign):
    """Changed character ranges for one side ('-' = old, '+' = new)."""
    ranges = []
    pos = 0
    for op, _ in diff:
        if op == " " or op == sign:
            if op == sign:
                if ranges and ranges[-1][1] == pos:
                    ranges[-1][1] = pos + 1
                else:
                    ranges.append([pos, pos + 1])
            pos += 1
    return ",".join(f"{s}-{e}" for s, e in ranges) or "."


def highlight_line(old, new):
    diff = myers_diff(old.decode("utf-8"), new.decode("utf-8"))
    return f"? {mark(diff, '-')} | {mark(diff, '+')}\n".encode()


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A B", file=sys.stderr)
        sys.exit(2)
    try:
        result = myers_diff(read_file(sys.argv[2]), read_file(sys.argv[3]))
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)

    show = sys.argv[1] == "highlight"
    out = []
    dels, ins = [], []

    def flush():
        for line in dels:
            out.append(b"-" + line + b"\n")
        for i, line in enumerate(ins):
            out.append(b"+" + line + b"\n")
            if show and i < len(dels):
                out.append(highlight_line(dels[i], line))
        dels.clear()
        ins.clear()

    for op, line in result:
        if op == "-":
            dels.append(line)
        elif op == "+":
            ins.append(line)
        else:
            flush()
            out.append(b" " + line + b"\n")
    flush()
    sys.stdout.buffer.write(b"".join(out))


if __name__ == "__main__":
    main()