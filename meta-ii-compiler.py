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
def prepare(program):
    for i in range(len(program)):
        it = program[i]
        if isinstance(it, str):                
            LABELS[it] = i + 1

def lookup(s):
    if s in LABELS:
        return LABELS[s]
    else:
        error("+++ No such label:", s)
            
def execute(program, NAME):
    global PC
    global INPUT

    prepare(program)
        
    fin = sys.stdin
    INPUT = fin.read()

    # label1, label2, return addr, rule-name
    STACK.append([None, None, None, NAME])

    while True:
        instruction = program[PC]
        PC += 1
        if isinstance(instruction, str):
            # actually a label, so do nothing
            pass
        else:
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
PROGRAM
	TST '.SYNTAX'
	BF L1
	ID
	BE
	CL 'ADR '
	CI
	OUT
L2
	CLL ST
	BT L2
	SET
	BE
	TST '.END'
	BE
	CL 'END'
	OUT
L1
L3
	R
ST
	ID
	BF L4
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
L4
L5
	R
EX1
	CLL EX2
	BF L6
L7
	TST '/'
	BF L8
	CL 'BT '
	GN1
	OUT
	CLL EX2
	BE
L8
L9
	BT L7
	SET
	BE
	LB
	GN1
	OUT
L6
L10
	R
EX2
	CLL EX3
	BF L11
	CL 'BF '
	GN1
	OUT
L11
	BT L12
	CLL OUTPUT
	BF L13
L13
L12
	BF L14
L15
	CLL EX3
	BF L16
	CL 'BE'
	OUT
L16
	BT L17
	CLL OUTPUT
	BF L18
L18
L17
	BT L15
	SET
	BE
	LB
	GN1
	OUT
L14
L19
	R
EX3
	ID
	BF L20
	CL 'CLL '
	CI
	OUT
L20
	BT L21
	SR
	BF L22
	CL 'TST '
	CI
	OUT
L22
	BT L21
	TST '.ID'
	BF L23
	CL 'ID'
	OUT
L23
	BT L21
	TST '.NUMBER'
	BF L24
	CL 'NUM'
	OUT
L24
	BT L21
	TST '.STRING'
	BF L25
	CL 'SR'
	OUT
L25
	BT L21
	TST '('
	BF L26
	CLL EX1
	BE
	TST ')'
	BE
L26
	BT L21
	TST '.EMPTY'
	BF L27
	CL 'SET'
	OUT
L27
	BT L21
	TST '$'
	BF L28
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
L28
L21
	R
OUTPUT
	TST '.OUT'
	BF L29
	TST '('
	BE
L30
	CLL OUT1
	BT L30
	SET
	BE
	TST ')'
	BE
L29
	BT L31
	TST '.LABEL'
	BF L32
	CL 'LB'
	OUT
	CLL OUT1
	BE
L32
L31
	BF L33
	CL 'OUT'
	OUT
L33
L34
	R
OUT1
	TST '*1'
	BF L35
	CL 'GN1'
	OUT
L35
	BT L36
	TST '*2'
	BF L37
	CL 'GN2'
	OUT
L37
	BT L36
	TST '*'
	BF L38
	CL 'CI'
	OUT
L38
	BT L36
	SR
	BF L39
	CL 'CL '
	CI
	OUT
L39
L36
	R
	END
"""
#-------------------------------------------------------
# After the "assembler" instructions, decode that and run

RE_instruction = re.compile(r"\s+([A-Z]+\d?)\s*(.*)")
PROG = []
funs = globals()

for line in PROG_TEXT.split("\n"):
    mob = RE_instruction.match(line)
    if mob:
        # Instruction
        if mob.group(2):
            PROG.append([funs[mob.group(1)], mob.group(2).strip("'")])
            if mob.group(1) == "ADR":
                NAME = mob.group(2).strip("'")
        else:
            PROG.append([funs[mob.group(1)]]) 
    elif len(line) > 0:
        # label
        PROG.append(line.strip())
        
execute(PROG, NAME)
