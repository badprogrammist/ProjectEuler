from collections import deque
from heapq import heappush, heappop

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

RBORDERS = {
    2: {2, 4},
    3: {3, 6, 9},
    4: {4, 8, 12, 16}
}

LBORDERS = {
    2: {-1, 1},
    3: {-1, 2, 5},
    4: {-1, 3, 7, 11}
}

OPS = {
    "left": "L",
    "right": "R",
    "up":"U",
    "down": "D"
}

CODE_TO_OPS = {
    "L": "left",
    "R": "right",
    "U": "up",
    "D": "down"
}

REVERSE_OPS = {
    "L": "R",
    "R": "L",
    "U": "D",
    "D": "U"
}


class Slider(object):
    def __init__(self, N, code, w, target_code):
        self.code = code
        self.N = N
        self.w = w
        self.hash = hash(tuple(self.code))
        self.diff = 0
        self.target_code = target_code
        

    @classmethod
    def from_str_code(cls, N, str_code, target_code=None):
        code = [STR_TO_CODE[c] for c in str_code]
        w = code.index(W)
        return cls(N, code, w, target_code)

    @classmethod
    def from_int_code(cls, N, int_code, target_code):
        code = [int(c) for c in str(int_code)]
        w = code.index(W)
        return cls(N, code, w, target_code)

    @property
    def target_code(self):
        return self._target_code

    @target_code.setter
    def target_code(self, target_code):
        self._target_code = target_code
        self._calc_diff()

    def _calc_diff(self):
        if not self.target_code:
            return
        for c1 in self.code:
            for c2 in self.target_code:
                if c1 != c2:
                    self.diff += 1

    def _shift(self, pos, op):
        code = list(self.code)
        c = code[pos]
        code[pos] = W
        code[self.w] = c

        return Slider(self.N, code, pos, self.target_code)

    def can_right(self):
        pos = self.w + 1
        if pos in RBORDERS[self.N]:
            return False
        return True

    def right(self):
        pos = self.w + 1
        return self._shift(pos, "right")

    def can_left(self):
        pos = self.w - 1
        if pos in LBORDERS[self.N]:
            return False
        return True

    def left(self):
        pos = self.w - 1
        return self._shift(pos, "left")
        
    def can_up(self):
        pos = self.w - self.N
        if pos < 0:
            return False
        return True

    def up(self):
        pos = self.w - self.N
        return self._shift(pos, "up")

    def can_down(self):
        pos = self.w + self.N
        if pos >= len(self.code):
            return False
        return True

    def down(self):
        pos = self.w + self.N
        return self._shift(pos, "down")

    def possible_op_keys(self):
        if self.can_left():
            yield "left"
        if self.can_right():
            yield "right"
        if self.can_up():
            yield "up"
        if self.can_down():
            yield "down"

    def do_op(self, op_key):
        op = getattr(self, op_key)
        return op()

    def __int__(self):
        return int(''.join(map(str, self.code)))
        
    def __str__(self):
        return "".join([CODE_TO_STR[c] for c in self.code])

    def __repr__(self):
        return f"N:{self.N}, w:{self.w}, code: {str(self)}"

    def __eq__(self, other): 
        # if not isinstance(other, Slider):
        #     return False
        return self.hash == other.hash

    def __hash__(self):
        return self.hash

    def __lt__(self, other):
        return self.diff < other.diff

    def __le__(self, other):
        return self.diff <= other.diff

    def __gt__(self, other):
        self.diff > other.diff

    def __ge__(self, other):
        self.diff >= other.diff

    
def search_solution(N, start_code, end_code):
    end = Slider.from_str_code(N, end_code)
    start = Slider.from_str_code(N, start_code, target_code=end.code)
    end.target_code = start.code
    
    shortage_solution = None
    solutions = set()

    start_states = {start: ""}
    # start_stack = [start]
    start_stack = deque()
    start_stack.append(start)

    end_states = {end: ""}
    # end_stack = [end]
    end_stack = deque()
    end_stack.append(end)

    stack = start_stack
    forward_states = start_states
    forward_state = start
    backward_states = end_states
    backward_state = end
    direction = "forward"

    # stack = deque()
    # stack.append(start)

    # states = {start: 0}
    # stack = [start]

    while len(stack) > 0:
        state = stack.pop()
        # state = heappop(stack)
        state_ops = forward_states[state]


        if state in backward_states:
            if direction == "forward":
                fops = [REVERSE_OPS[c] for c in state_ops]
                bops = [c for c in backward_states[state]][::-1]
                # print(f"fmerge:{fops} and {bops}")
            elif direction == "backward":
                fops = [REVERSE_OPS[c] for c in backward_states[state]]
                bops = [c for c in state_ops[::-1]]
                # print(f"bmerge:{fops} and {bops}")
            ops = fops + bops
            solution = ''.join(ops)

            # print(f"{direction[0]}{len(solution)} {solution}")
            solutions.add(solution)

            if not shortage_solution or len(solution) < len(shortage_solution):
                shortage_solution = solution

            # continue


        if shortage_solution and len(shortage_solution) < len(state_ops):
            continue


        # if state in forward_states and forward_states[state] < len(state.ops_history):
        #     continue
        # else:
        #     forward_states[state] = len(state.ops_history)


        

        for op_key in state.possible_op_keys():
            new_state = state.do_op(op_key)
            new_ops = state_ops+OPS[op_key]

            if new_state in forward_states and len(forward_states[new_state]) < len(new_ops):
                continue
            else:
                forward_states[new_state] = new_ops
                stack.append(new_state)
                # heappush(stack, new_state)


        if direction == "backward" and len(start_stack) > 0:
            stack = start_stack
            forward_states = start_states
            forward_state = start
            backward_states = end_states
            backward_state = end
            direction = "forward"
        elif direction == "forward" and len(end_stack) > 0:
            stack = end_stack
            forward_states = end_states
            forward_state = end
            backward_states = start_states
            backward_state = start
            direction = "backward"


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

    solutions = search_solution(3, "BBBBWRRRR", "RBRBWBRBR")
    print(solutions)
    assert solutions_checksum(solutions) == 86665639

    # solutions = search_solution(4, "WRBBRRBBRRBBRRBB", "WBRBBRBRRBRBBRBR")
    # print(solutions)
    # print(solutions_checksum(solutions))


    # N = int(input())
    
    # S = ""
    # while len(S) != (N * N):
    #     S += input().rstrip()

    # E = ""
    # while len(E) != (N * N):
    #     E += input().rstrip()

    # print(N, S, E)