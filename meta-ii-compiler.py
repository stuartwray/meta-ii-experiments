#!/usr/bin/python3

import sys
import string
import re
import os

# Meta-compiler supporting machine, based on a tutorial/website by
# James M. Neighbors: "Tutorial: Metacompilers Part 1" (2008). This was
# in turn based on a paper by D. V. Schorre: "META II: A Syntax-Oriented
# Compiler Writing Language" (1964).

#--------------------------------------------------------

def error(*args):
    print(*args)
    sys.exit(1)

#--------------------------------------------------------
# Parse command-line arguments, get filenames straight

myname = os.path.basename(sys.argv[0])
if myname == "meta-ii-compiler.py":
    if len(sys.argv) == 1:
        error("Usage: <name>-grammar.txt")
    
    # special case: meta-ii can use *this* program as the runtime
    RUNTIME_name = myname        
    
    INPUT_name = sys.argv[1]
    RE_grammar_file = re.compile(r"(.*)-grammar.txt")
    mob = RE_grammar_file.match(INPUT_name)
    if not mob:
        error("+++ input file must be called <name>-grammar.txt")
    out_base = mob.group(1)

    if out_base == "meta-ii":
        # special case: don't overwrite the original compiler
        OUTPUT_name = "new-" + out_base + "-compiler.py"
    else:
        OUTPUT_name = out_base + "-compiler.py"
else:
    # We are a compiler for some other language
    if len(sys.argv) == 1:
        error("Usage: <source>.txt")

    RE_compiler_file = re.compile(r"(.*)-compiler.py")
    mob = RE_compiler_file.match(myname)
    if not mob:
        error("+++ Compiler executable must be called <name>-compiler.py")
    runtime_base = mob.group(1)
    RUNTIME_name = runtime_base + "-runtime.py"

    INPUT_name = sys.argv[1]
    RE_source_file = re.compile(r"(.*).txt")
    mob = RE_source_file.match(INPUT_name)
    if not mob:
        error("+++ Source file must be called <source>.txt")
    out_base = mob.group(1)
    OUTPUT_name = out_base + "-object.py"

#--------------------------------------------------------
# Global variables holding input file contents

with open(INPUT_name) as fin:
    INPUT = fin.read()

# split_list :: Regexp -> List[String] -> List[List[String]]
def split_list(pat, xs):
    result = []
    part = []
    for x in xs:
        if pat.match(x):
            result.append(part)
            part = []
        else:
            part.append(x)
    if part != []:
        result.append(part)
    return result
      
with open(RUNTIME_name) as fin:
    RE_triple_quote = re.compile(r'^"""')
    runtime = split_list(RE_triple_quote, fin.readlines())
    if len(runtime) != 3:
        print(runtime)
        error("+++ Check the format of your runtime. (Too many triple-quotes.)")
    RUNTIME_HEADER_list, _, RUNTIME_TRAILER_list = runtime
    
# Other global variables

INPUT_position = 0

OUTPUT_line = "\t" # start set to col 8 (bizzare 1960s I/O)
OUTPUT_list = []

PC = 0
STACK = []
SWITCH = False
TOKEN = ""
LABEL_counter = 1

#--------------------------------------------------------
# Supporting functions

LABELS = {}
def label(s, value):
    LABELS[s] = value

def lookup(s):
    if s in LABELS:
        return LABELS[s]
    else:
        error("+++ No such label:", s)

# execute :: String -> List[(function, argument)] -> None
def execute(name, program):
    global PC, STACK, SWITCH, TOKEN, LABEL_counter
    PC = 0
    # label1, label2, return addr, rule-name
    STACK = [[None, None, None, name]]
    SWITCH = False
    TOKEN = ""
    LABEL_counter = 1

    while PC != None:
        instruction = program[PC]
        PC += 1
        fun, args = instruction[0], instruction[1:]
        fun(*args)

#--------------------------------------------------------
# Parsing machine instructions

# Note that I am trying hard here to avoid using regexps.
# (So as to demonstrate that this part can be implemented on a
# runtime with no regexps.)
# The tokenisation stuff gets taken care of using a few more
# instructions in a later version of Neighbors' metacompiler.

def TST(s):
    global INPUT_position
    global SWITCH
    
    # skip initial whitespace
    while INPUT_position < len(INPUT) and \
              INPUT[INPUT_position] in string.whitespace:
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
    while INPUT_position < len(INPUT) and \
              INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match identifier
    if INPUT_position < len(INPUT) and \
           (INPUT[INPUT_position] in string.ascii_lowercase or \
            INPUT[INPUT_position] in string.ascii_uppercase):
        TOKEN = INPUT[INPUT_position]
        INPUT_position += 1
        SWITCH = True
        
        while INPUT_position < len(INPUT) and \
                (INPUT[INPUT_position] in string.ascii_lowercase or \
                 INPUT[INPUT_position] in string.ascii_uppercase or \
                 INPUT[INPUT_position] in string.digits):
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1
    else:
        SWITCH = False

def NUM():
    global INPUT_position
    global TOKEN
    global SWITCH
    
    # skip initial whitespace
    while INPUT_position < len(INPUT) and \
            INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match number
    if INPUT_position < len(INPUT) and \
            INPUT[INPUT_position] in string.digits:
        TOKEN = INPUT[INPUT_position]
        INPUT_position += 1
        SWITCH = True
        
        while INPUT_position < len(INPUT) and \
                INPUT[INPUT_position] in string.digits:
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1
    else:
        SWITCH = False       

def SR():
    global INPUT_position
    global TOKEN
    global SWITCH
    
    # skip initial whitespace
    while INPUT_position < len(INPUT) and \
            INPUT[INPUT_position] in string.whitespace:
        INPUT_position += 1

    # try match single-quoted string
    if INPUT_position < len(INPUT) and \
            INPUT[INPUT_position] == "'":
        TOKEN = INPUT[INPUT_position]
        INPUT_position += 1
        
        while INPUT_position < len(INPUT) and \
                INPUT[INPUT_position] != "'":
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1

        if INPUT_position < len(INPUT):
            # this is the closing quote
            TOKEN += INPUT[INPUT_position]
            INPUT_position += 1
            SWITCH = True
        else:
            # ran out of characters in input before closing quote
            SWITCH = FALSE            
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
    OUTPUT_list.append(OUTPUT_line + "\n")
    # set ouput buffer to col 8 (bizzare 1960s I/O)
    OUTPUT_line = "\t" 

def END():
    PC = None # halt interpreter

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

PROGRAM = []

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
        label(line.strip(), len(PROGRAM))

# We already have output date in in RUNTIME_HEADER_list
# and RUNTIME_TRAILER_list, and now ...
        
execute(NAME, PROGRAM)

# ... we also have the "assembler code" in OUTPUT_list. So put it all together:

with open(OUTPUT_name, "w") as fout:
    fout.writelines(RUNTIME_HEADER_list)
    fout.write('"""\n')
    fout.writelines(OUTPUT_list)
    fout.write('"""\n')
    fout.writelines(RUNTIME_TRAILER_list)

# And finally make that executatble

import stat
mode = os.stat(OUTPUT_name).st_mode 
os.chmod(OUTPUT_name, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


    
