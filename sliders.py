from collections import deque

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
        rborders = {r+self.N for r in range(0, (self.N * self.N), self.N)}
        lborders = {r-1 for r in range(0, (self.N * self.N), self.N)}
        ops = [
            (1, "R", lambda w: w not in rborders),
            (-1, "L", lambda w: w not in lborders),
            (self.N, "D", lambda w: w < (self.N * self.N)),
            (-self.N, "U", lambda w: w >= 0) 
        ]

        for w in range((self.N * self.N)):
            pos_ops = [
                (w+offset, code)
                for offset, code, iscorrect in ops
                if iscorrect(w+offset)
            ]
            self.shifts[w] = pos_ops

    def make(self, slider, prev_ops):
        for pos, op_code in self.shifts[slider.w]:
            code = list(slider.code)
            code[pos], code[slider.w] = code[slider.w], code[pos]
            yield (Slider(code, pos), "".join((prev_ops,op_code)))


class Slider(object):
    def __init__(self, code, w):
        self.code = tuple(code)
        self.w = w

    @classmethod
    def from_str_code(cls, N, str_code):
        code = [STR_TO_CODE[c] for c in str_code]
        w = code.index(W)
        return cls(code, w)

    def __str__(self):
        return "".join([CODE_TO_STR[c] for c in self.code])

    def __eq__(self, other): 
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

def next_states(states, shifts, shortage_solution):
    new_states = dict()
    for state, ops in states.items():
        for new_state, new_ops in shifts.make(state, ops):
            if shortage_solution and len(shortage_solution) < len(new_ops):
                continue
            if new_state in states:
                continue
            new_states[new_state] = new_ops
    return new_states

def search_solution(N, start_code, end_code):
    end = Slider.from_str_code(N, end_code)
    start = Slider.from_str_code(N, start_code)
    shifts = Shifts(N)
    
    shortage_solution = None
    solutions = set()

    head_states = {start: ""}
    tail_states = {end: ""}

    direction = "forward"
    states = head_states
    other_states = tail_states
    
    new_states = next_states(states, shifts, shortage_solution)
    while len(new_states) > 0:

        for state, ops in new_states.items():
            if state in other_states:
                if direction == "forward":
                    fops = [REVERSE_OPS[c] for c in ops]
                    bops = [c for c in other_states[state]][::-1]
                    ops = fops + bops
                    solution = ''.join(ops)
                    solutions.add(solution)

                    if not shortage_solution or len(solution) < len(shortage_solution):
                        shortage_solution = solution

                elif direction == "backward":
                    fops = [REVERSE_OPS[c] for c in other_states[state]]
                    bops = [c for c in ops[::-1]]
                    ops = fops + bops
                    solution = ''.join(ops)
                    solutions.add(solution)

                    if not shortage_solution or len(solution) < len(shortage_solution):
                        shortage_solution = solution

        states.update(new_states)

        if direction == "forward":
            states = tail_states
            other_states = head_states
            direction = "backward"
        elif direction == "backward":
            states = head_states
            other_states = tail_states
            direction = "forward"

        new_states = next_states(states, shifts, shortage_solution)

    return [solution for solution in solutions 
            if len(solution) == len(shortage_solution)]


def solution_checksum(solution):
    cs = 0
    for c in solution:
        cs = (cs * 243 + ord(c)) % 100000007
    
    return cs


def solutions_checksum(solutions):
    if len(solutions) > 0:
        checksums = [solution_checksum(s) for s in solutions]
        cs_sum = checksums[0]
        for cs in checksums[1:]:
            cs_sum += cs
            cs_sum = cs_sum % 100000007
        return cs_sum
    else:
        return solution_checksum(solutions[0])



if __name__ == "__main__":
    # solutions = search_solution(2, "WRBB", "RBBW")
    # print(solutions)
    # assert solutions_checksum(solutions) == 18553

    # solutions = search_solution(3, "BBBBWRRRR", "RBRBWBRBR")
    # print(solutions)
    # assert solutions_checksum(solutions) == 86665639

    solutions = search_solution(4, "WRBBRRBBRRBBRRBB", "WBRBBRBRRBRBBRBR")
    print(solutions)
    print(solutions_checksum(solutions))
