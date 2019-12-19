W = 1
R = 2
B = 3

STR_TO_CODE = {
    "W": W,
    "R": R,
    "B": B
}

CODE_TO_STR = {
    W: "W",
    R: "R",
    B: "B"
}

REVERSE_OPS = {
    "L": "R",
    "R": "L",
    "U": "D",
    "D": "U"
}


class Shifts(object):
    def __init__(self, N):
        self.N = N
        self.shifts = [[] for _ in range((self.N * self.N))]
        self.generate()

    def generate(self):
        rborders = {r + self.N for r in range(0, (self.N * self.N), self.N)}
        lborders = {r - 1 for r in range(0, (self.N * self.N), self.N)}
        ops = [
            (1, "R", lambda w: w not in rborders),
            (-1, "L", lambda w: w not in lborders),
            (self.N, "D", lambda w: w < (self.N * self.N)),
            (-self.N, "U", lambda w: w >= 0)
        ]

        for w in range((self.N * self.N)):
            pos_ops = [
                (w + offset, code)
                for offset, code, iscorrect in ops
                if iscorrect(w + offset)
            ]
            self.shifts[w] = pos_ops

    def make(self, slider, prev_ops):
        for pos, op_code in self.shifts[slider.w]:
            if REVERSE_OPS[op_code] == slider.prev_op:
                continue

            code = list(slider.code)
            code[pos], code[slider.w] = code[slider.w], code[pos]
            ops = "".join((prev_ops, op_code))

            yield (Slider(code, pos, op_code), ops)


class Slider(object):
    def __init__(self, code, w, prev_op):
        self.code = tuple(code)
        self.w = w
        self.prev_op = prev_op

    @classmethod
    def from_str_code(cls, str_code):
        code = [STR_TO_CODE[c] for c in str_code]
        w = code.index(W)
        return cls(code, w, "")

    def __str__(self):
        return "".join([CODE_TO_STR[c] for c in self.code])

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


def next_states(states, shifts):
    new_states = dict()
    for state, ops in states.items():
        for new_state, new_ops in shifts.make(state, ops):
            if new_state in states:
                continue
            new_states[new_state] = new_ops
    return new_states


def have_solutions(head_states, tail_states):
    solutions = set()
    min_len = None

    for state, ops in head_states.items():
        if state in tail_states:
            fops = [REVERSE_OPS[c] for c in ops]
            bops = [c for c in tail_states[state]][::-1]
            ops = fops + bops
            solution = ''.join(ops)
            solutions.add(solution)

            if not min_len or len(solution) < min_len:
                min_len = len(solution)

    return [solution for solution in solutions
            if len(solution) == min_len]


def search_solution(N, start_code, end_code):
    end = Slider.from_str_code(end_code)
    start = Slider.from_str_code(start_code)
    shifts = Shifts(N)

    solutions = None

    head_states = {start: ""}
    tail_states = {end: ""}

    while True:
        head_states = next_states(head_states, shifts)
        solutions = have_solutions(head_states, tail_states)
        if solutions:
            break

        tail_states = next_states(tail_states, shifts)
        solutions = have_solutions(head_states, tail_states)
        if solutions:
            break

    return solutions


def solution_checksum(solution):
    cs = 0
    for c in solution:
        cs = (cs * 243 + ord(c)) % 100000007

    return cs


def solutions_checksum(solutions):
    checksums = [solution_checksum(s) for s in solutions]
    cs_sum = sum(checksums, 0) % 100000007

    return cs_sum


if __name__ == "__main__":
    solutions = search_solution(2, "WRBB", "RBBW")
    print(solutions)
    assert solutions_checksum(solutions) == 18553

    solutions = search_solution(3, "BBBBWRRRR", "RBRBWBRBR")
    print(solutions)
    assert solutions_checksum(solutions) == 86665639

    solutions = search_solution(4, "WRBBRRBBRRBBRRBB", "WBRBBRBRRBRBBRBR")
    print(solutions)
    assert solutions_checksum(solutions) == 96356848

    # fptr = open(os.environ['OUTPUT_PATH'], 'w')
    # N = int(input())
    #
    # S = ""
    # while len(S) != (N * N):
    #     S += input().rstrip()
    #
    # E = ""
    # while len(E) != (N * N):
    #     E += input().rstrip()
    #
    # solutions = search_solution(N, S, E)
    # fptr.write(str(solutions_checksum(solutions)))
    # fptr.write('\n')
    #
    # fptr.close()
