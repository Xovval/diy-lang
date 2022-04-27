# -*- coding: utf-8 -*-

from .types import Environment, DiyLangError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, \
    is_integer, is_string
from .parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports,
making your work a bit easier. (We're supposed to get through this thing
in a day, after all.)
"""


def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if ast == []:
        raise DiyLangError('cannot eval empty')

    if is_boolean(ast): return ast
    if is_integer(ast): return ast
    if is_string(ast): return ast
    if is_symbol(ast):  return env.lookup(ast)

    # basics
    op = ast[0]
    if op == 'quote': return ast[1]

    if op == 'define':
        if len(ast) != 3:
            raise DiyLangError('Wrong number of arguments: expected 2, got ' + str(len(ast)))
        if not is_symbol(ast[1]):
            raise DiyLangError(str(ast[1]) + ' is not a symbol')
        env.set(ast[1], evaluate(ast[2], env))
        return ast[2]

    if op == 'lambda':
        if len(ast) != 3:
            raise DiyLangError('Wrong number of arguments: expected 2, got ' + str(len(ast)))
        if not is_list(ast[1]):
            raise DiyLangError('not a list')
        return Closure(env, ast[1], ast[2])

    if is_closure(op):
        args = zip(op.params, [evaluate(a, env) for a in ast[1:]])
        return evaluate(op.body, op.env.extend(dict(args)))

    if is_list(op):
        return call(evaluate(op, env), ast[1:], env)

    # conditions
    if op == 'if':
        cond = evaluate(ast[1], env)
        return evaluate(ast[2], env) if cond else evaluate(ast[3], env)

    # math and simple operators
    if op == 'atom':
        return is_atom(evaluate(ast[1], env))

    if op in ['+','-','*','/','>','eq', 'mod']:
        lhs = evaluate(ast[1], env)
        rhs = evaluate(ast[2], env)
        if op == 'eq':
            if is_list(lhs) or is_list(rhs): return False
            return lhs == rhs
        if not is_integer(lhs) or not is_integer(rhs):
            raise DiyLangError('only integers supported for math expressions')
        if op == '+':
            return lhs + rhs
        if op == '-':
            return lhs - rhs
        if op == '*':
            return lhs * rhs
        if op == '/':
            return lhs // rhs
        if op == 'mod':
            return lhs % rhs
        if op == '>':
            return lhs > rhs

    if op == 'cons':
        lhs = evaluate(ast[1], env)
        rhs = evaluate(ast[2], env)
        if is_list(rhs):
            return [lhs] + rhs
        return String(lhs.val + rhs.val)

    if op == 'head':
        l = evaluate(ast[1], env)
        verify_list(l)
        verify_len(l)
        if is_list(l):
            return l[0]
        return String(l.val[0])

    if op == 'tail':
        l = evaluate(ast[1], env)
        verify_list(l)
        verify_len(l)
        if is_list(l):
            return l[1:]
        return String(l.val[1:])

    if op == 'empty':
        l = evaluate(ast[1], env)
        verify_list(l)
        return empty_list(l)

    if op == 'cond':
        cases = ast[1]
        for c in cases:
            if evaluate(c[0], env):
                return evaluate(c[1], env)
        return '#f'
        # return False?

    if op == 'let':
        ctx = ast[1]
        body = ast[2]
        letenv = Environment()
        for exp in ctx:
            letenv.set(exp[0], evaluate(exp[1], env.extend(letenv.bindings)))
        return evaluate(body, env.extend(letenv.bindings))

    if op == 'defn':
        name = ast[1]
        params = ast[2]
        body = ast[3]

        if not is_symbol(name):
            raise DiyLangError(str(ast[1]) + ' is not a symbol')
        f = evaluate(['lambda', params, body], env)
        env.set(name, f)
        return f

    if op == 'print':
        result = evaluate(ast[1], env)
        print(result)
        return result

    # TODO this is semantically wrong
    if not is_symbol(op):
        raise DiyLangError(str(op) + ' is not a function')

    return call(env.lookup(op), ast[1:], env)

def call(fun, args, env):
    if not is_closure(fun):
        raise DiyLangError(str(fun) + ' is not a function')
    if len(fun.params) != len(args):
        raise DiyLangError(f'wrong number of arguments, expected {len(fun.params)} got {len(args)}')
    return evaluate([fun, *args], env)

def empty_list(list):
    if is_list(list):
        return len(list) < 1
    return len(list.val) < 1

def verify_list(list):
    if not is_list(list) and not is_string(list):
        raise DiyLangError('not a list')

def verify_len(list):
    if empty_list(list):
        raise DiyLangError('empty list')
