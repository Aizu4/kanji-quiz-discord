from typing import Callable

_PRIORITY = {
    '+': 1,
    '-': 1,
    '|': 1,
    '*': 2,
    '^': 2,
    '&': 2
}


def _is_operator(char: str) -> bool:
    return char in {'+', '-', '*', '^', '&', '|', '(', ')'}


def _perform(op: str, stack: list[set]) -> None:
    b, a = stack.pop(), stack.pop()
    match op:
        case '+' | '|':
            stack.append(a | b)

        case '-':
            stack.append(a - b)

        case '*' | '&':
            stack.append(a & b)

        case '^':
            stack.append(a ^ b)


def _infix_to_postfix(expr: list[str]) -> list[str]:
    stack = []
    output = []

    for ch in expr:
        if not _is_operator(ch):
            output.append(ch)
        elif ch == '(':
            stack.append('(')
        elif ch == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != '(' and _PRIORITY[ch] <= _PRIORITY[stack[-1]]:
                output.append(stack.pop())
            stack.append(ch)

    while stack:
        output.append(stack.pop())

    return output


def str_to_set(expr: str, get_set: Callable[[str], set]) -> set:
    expr = expr.replace('|', '+').replace('&', '*') \
        .replace('+', ' + ') \
        .replace('-', ' - ') \
        .replace('*', ' * ') \
        .replace('^', ' ^ ') \
        .replace('(', ' ( ').replace(')', ' ) ')

    stack = []
    postfix = _infix_to_postfix(expr.split())

    for ch in postfix:
        if _is_operator(ch):
            _perform(ch, stack)
        else:
            stack.append(get_set(ch))

    return stack[0]


if __name__ == '__main__':
    print(_infix_to_postfix(['2', '-', '(', '3', '+', '4', ')']))
