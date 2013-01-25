#!/usr/bin/python3

import sys
import string
import re

# Meta-compiler supporting machine, based on a tutorial/website by
# James M. Neighbors: "Tutorial: Metacompilers Part 1" (2008). This was
# in turn based on a paper by D. V. Schorre: "META II: A Syntax-Oriented
# Compiler Writing Language" (1964).

#--------------------------------------------------------
# Global variables

INPUT = None
INPUT_position = 0

OUTPUT_line = "\t" # start set to col 8 (bizzare 1960s I/O)

PC = 0
SWITCH = False
TOKEN = ""
STACK = []
LABEL_counter = 1

#--------------------------------------------------------
# Supporting functions

def error(*args):
    print(*args)
    sys.exit(1)

LABELS = {}
def label(s, value):
    LABELS[s] = value

def lookup(s):
    if s in LABELS:
        return LABELS[s]
    else:
        error("+++ No such label:", s)

# This list is filled in right at the end, with a sequence
# of [function, argument] lists
PROGRAM = []
def execute(NAME):
    global PC
    global INPUT
        
    fin = sys.stdin
    INPUT = fin.read()

    # label1, label2, return addr, rule-name
    STACK.append([None, None, None, NAME])

    while True:
        instruction = PROGRAM[PC]
        PC += 1
        fun, args = instruction[0], instruction[1:]
        fun(*args)

#--------------------------------------------------------
# Parsing machine instructions

# Note that I am trying hard here to avoid using regexps.
# The tokenisation stuff gets taken care of using a few more
# instructions in a later version of the metacompiler.

def TST(s):
    global INPUT_position
    global SWITCH
    
    # skip initial whitespace
    while INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match string s
    if s == INPUT[INPUT_position:INPUT_position+len(s)]:
        # skip if matched & set switch
        INPUT_position += len(s)
        SWITCH = True
    else:
        SWITCH = False

def ID():
    global INPUT_position
    global TOKEN
    global SWITCH
    
    # skip initial whitespace
    while INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match identifier
    if INPUT[INPUT_position] in string.ascii_lowercase or \
       INPUT[INPUT_position] in string.ascii_uppercase:
        TOKEN = INPUT[INPUT_position]
        INPUT_position += 1
        SWITCH = True
        
        while INPUT[INPUT_position] in string.ascii_lowercase or \
              INPUT[INPUT_position] in string.ascii_uppercase or \
              INPUT[INPUT_position] in string.digits:
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1
    else:
        SWITCH = False

def NUM():
    global INPUT_position
    global TOKEN
    global SWITCH
    
    # skip initial whitespace
    while INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match number
    if INPUT[INPUT_position] in string.digits:
        TOKEN = INPUT[INPUT_position]
        INPUT_position += 1
        SWITCH = True
        
        while INPUT[INPUT_position] in string.digits:
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1
    else:
        SWITCH = False       

def SR():
    global INPUT_position
    global TOKEN
    global SWITCH
    
    # skip initial whitespace
    while INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match single-quoted string
    if INPUT[INPUT_position] == "'":
        TOKEN = INPUT[INPUT_position]
        INPUT_position += 1
        SWITCH = True
        
        while INPUT[INPUT_position] != "'":
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1

        # this is the closing quote
        TOKEN += INPUT[INPUT_position]
        INPUT_position += 1
    else:
        SWITCH = False

def CLL(rule):
    global PC
    # label1, label2, return addr, rule
    STACK.append([None, None, PC, rule])
    PC = lookup(rule)

def R():
    global PC
    _, _, PC, _ = STACK.pop()
    if PC == None:
        END()
    
def SET():
    global SWITCH
    SWITCH = True

def ADR(label):
    B(label)

def B(label):
    global PC
    PC = lookup(label)

def BT(label):
    global PC
    if SWITCH:
        PC = lookup(label)
   
def BF(label):
    global PC
    if not SWITCH:
        PC = lookup(label)
        
def BE():
    if not SWITCH:
        # I've seen more informative error messages ...
        text = "... " + INPUT[max(0, INPUT_position - 40):INPUT_position] + "\n" + \
               "***ERROR HERE:\n" + \
               INPUT[INPUT_position:INPUT_position + 40] + " ...\n"
        while len(STACK) > 0:
            _, _, _, rule = STACK.pop()
            text += "in <" + rule + "> "
        error(text)
        
def CL(literal):
    global OUTPUT_line
    OUTPUT_line += literal

def CI():
    global OUTPUT_line
    OUTPUT_line += TOKEN

def GN1():
    global OUTPUT_line
    global LABEL_counter
    label, _, _, _ = STACK[-1]
    if label == None:
        label = "L" + str(LABEL_counter)
        LABEL_counter += 1
        STACK[-1][0] = label
        
    OUTPUT_line += label

def GN2():
    global OUTPUT_line
    global LABEL_counter
    _, label,_, _ = STACK[-1]
    if label == None:
        label = "L" + str(LABEL_counter)
        LABEL_counter += 1
        STACK[-1][1] = label
        
    OUTPUT_line += label

def LB():
    global OUTPUT_line
    # set ouput buffer to col 1 (bizzare 1960s I/O)
    OUTPUT_line = ""

def OUT():
    global OUTPUT_line
    print(OUTPUT_line)
    # set ouput buffer to col 8 (bizzare 1960s I/O)
    OUTPUT_line = "\t" 

def END():
    sys.stdout.flush()
    sys.exit(0)

#-------------------------------------------------------
# The "assembler" instuctions go here
PROG_TEXT = \
"""
	ADR PROGRAM
OUT1
	TST '*1'
	BF L1
	CL 'GN1'
	OUT
L1
	BT L2
	TST '*2'
	BF L3
	CL 'GN2'
	OUT
L3
	BT L2
	TST '*'
	BF L4
	CL 'CI'
	OUT
L4
	BT L2
	SR
	BF L5
	CL 'CL '
	CI
	OUT
L5
L2
	R
OUTPUT
	TST '.OUT'
	BF L6
	TST '('
	BE
L7
	CLL OUT1
	BT L7
	SET
	BE
	TST ')'
	BE
L6
	BT L8
	TST '.LABEL'
	BF L9
	CL 'LB'
	OUT
	CLL OUT1
	BE
L9
L8
	BF L10
	CL 'OUT'
	OUT
L10
L11
	R
EX3
	ID
	BF L12
	CL 'CLL '
	CI
	OUT
L12
	BT L13
	SR
	BF L14
	CL 'TST '
	CI
	OUT
L14
	BT L13
	TST '.ID'
	BF L15
	CL 'ID'
	OUT
L15
	BT L13
	TST '.NUMBER'
	BF L16
	CL 'NUM'
	OUT
L16
	BT L13
	TST '.STRING'
	BF L17
	CL 'SR'
	OUT
L17
	BT L13
	TST '('
	BF L18
	CLL EX1
	BE
	TST ')'
	BE
L18
	BT L13
	TST '.EMPTY'
	BF L19
	CL 'SET'
	OUT
L19
	BT L13
	TST '$'
	BF L20
	LB
	GN1
	OUT
	CLL EX3
	BE
	CL 'BT '
	GN1
	OUT
	CL 'SET'
	OUT
L20
L13
	R
EX2
	CLL EX3
	BF L21
	CL 'BF '
	GN1
	OUT
L21
	BT L22
	CLL OUTPUT
	BF L23
L23
L22
	BF L24
L25
	CLL EX3
	BF L26
	CL 'BE'
	OUT
L26
	BT L27
	CLL OUTPUT
	BF L28
L28
L27
	BT L25
	SET
	BE
	LB
	GN1
	OUT
L24
L29
	R
EX1
	CLL EX2
	BF L30
L31
	TST '/'
	BF L32
	CL 'BT '
	GN1
	OUT
	CLL EX2
	BE
L32
L33
	BT L31
	SET
	BE
	LB
	GN1
	OUT
L30
L34
	R
ST
	ID
	BF L35
	LB
	CI
	OUT
	TST '='
	BE
	CLL EX1
	BE
	TST '.,'
	BE
	CL 'R'
	OUT
L35
L36
	R
PROGRAM
	TST '.SYNTAX'
	BF L37
	ID
	BE
	CL 'ADR '
	CI
	OUT
L38
	CLL ST
	BT L38
	SET
	BE
	TST '.END'
	BE
	CL 'END'
	OUT
L37
L39
	R
	END
"""
#-------------------------------------------------------
# After the "assembler" instructions, decode all that and run

# It may seem a little inconsistent to use a regexp here after spending
# so much time avoiding them earlier, but really this is part of the
# grammar "object code" loader, not really part of the runtime.
RE_instruction = re.compile(r"\s+([A-Z]+\d?)\s*(.*)")
funs = globals()

for line in PROG_TEXT.split("\n"):
    mob = RE_instruction.match(line)
    if mob:
        # Instruction
        instr = mob.group(1)
        data  = mob.group(2).strip("'")
        if data:
            PROGRAM.append([funs[instr], data])
            if instr == "ADR":
                NAME = data
        else:
            PROGRAM.append([funs[instr]]) 
    elif len(line) > 0:
        # Label
        #PROG.append(line.strip())
        label(line.strip(), len(PROGRAM))
        
execute(NAME)
