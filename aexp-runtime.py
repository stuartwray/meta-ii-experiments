#!/usr/bin/python3

import sys
import string
import re
import os

# This runtime for the AEXP example is a modified version of the
# meta-ii runtime (i.e. derived from meta-ii-compiler.py)

#--------------------------------------------------------

def error(*args):
    print(*args)
    sys.exit(1)

#--------------------------------------------------------
# Supporting functions

PC = 0
ENV = {}
STACK = []

# execute :: String -> List[(function, argument)] -> None
def execute(program):
    global PC, ENV, STACK
    PC = 0
    ENV = {}
    STACK = []

    while PC != None and PC < len(program):
        instruction = program[PC]
        PC += 1
        fun, args = instruction[0], instruction[1:]
        fun(*args)

#--------------------------------------------------------
# Machine instructions

def ADDRESS(var):
    if var not in ENV:
        ENV[var] = 0
    STACK.append(var)

def STORE():
    n = STACK.pop()
    var = STACK.pop()
    ENV[var] = n

def ADD():
    a = STACK.pop()
    b = STACK.pop()
    STACK.append(a + b)

def SUB():
    a = STACK.pop()
    b = STACK.pop()
    STACK.append(a - b)
    
def MUL():
    a = STACK.pop()
    b = STACK.pop()
    STACK.append(a * b)
    
def DIV():
    a = STACK.pop()
    b = STACK.pop()
    STACK.append(a / b)
    
def EXP():
    a = STACK.pop()
    b = STACK.pop()
    STACK.append(a ** b)

def NEG():
    a = STACK.pop()
    STACK.append(-a)
    
def LOAD(var):
    STACK.append(ENV[var])

def LITERAL(digits):
    STACK.append(int(digits))

#-------------------------------------------------------
# The "assembler" instuctions go here
PROG_TEXT = \
"""
	address fern
	literal 5
	literal 6
	add
	store
	address ace
	load fern
	literal 5
	mpy
	store
	address waldo
	load fern
	load alpha
	load beta
	minus
	load gamma
	exp
	div
	add
	store
"""
#-------------------------------------------------------
# After the "assembler" instructions, decode all that and run

# It may seem a little inconsistent to use a regexp here after spending
# so much time avoiding them earlier, but really this is part of the
# grammar "object code" loader, not really part of the runtime.
RE_instruction = re.compile(r"\s+([A-Z]+\d?)\s*(.*)")
funs = globals()

PROGRAM = []

for line in PROG_TEXT.split("\n"):
    mob = RE_instruction.match(line)
    if mob:
        # Instruction
        instr = mob.group(1)
        data  = mob.group(2).strip("'")
        if data:
            PROGRAM.append([funs[instr], data])
        else:
            PROGRAM.append([funs[instr]]) 

# run it ...
        
execute(PROGRAM)

# ... and print out the results

for var in ENV:
    print("%s = %g" % (var, ENV[var]))



    
