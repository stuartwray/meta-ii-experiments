#!/usr/bin/python3

import sys
import string

# Meta-compiler supporting machine, baed on a tutorial/website by
# James M. Neighbors: "Tutorial: Metacompilers Part 1" (2008). This was
# in turn baed on a paper by D. V. Schorre: "META II: A Syntax-Oriented
# Compiler Writing Language" (1964).

#--------------------------------------------------------
# Global variables

INPUT = None
INPUT_position = 0

OUTPUT_line = ""

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
##    #DEBUG XXX
##    for label in LABELS:
##        print(label, "=", LABELS[label])

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

##    # DEBUG XXX
##    print(INPUT)

    while True:
        instruction = program[PC]
##        #DEBUG XXX
##        print(SWITCH, PC, instruction)
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
##    #DEBUG XXX
##    print(">>> Call", rule)

def R():
    global PC
    _, _, PC, _ = STACK.pop()
##    #DEBUG XXX
##    print("<<< Return")
    if PC == None:
        END()
    
def SET():
    global SWITCH
    SWITCH = True

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
    OUTPUT_line = ""

def OUT():
    global OUTPUT_line
    print(OUTPUT_line)
    # in original this spaces to col 8
    OUTPUT_line = "" 

def END():
    sys.stdout.flush()
    sys.exit(0)

    
