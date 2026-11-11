"""Hack assembler. K = 08 -> K mod 3 = 2 -> warn on duplicate labels.
Usage: python assembler.py Prog.asm   (writes Prog.hack)"""
import sys

COMP = {"0":"0101010","1":"0111111","-1":"0111010","D":"0001100","A":"0110000",
        "!D":"0001101","!A":"0110001","-D":"0001111","-A":"0110011","D+1":"0011111",
        "A+1":"0110111","D-1":"0001110","A-1":"0110010","D+A":"0000010","D-A":"0010011",
        "A-D":"0000111","D&A":"0000000","D|A":"0010101",
        "M":"1110000","!M":"1110001","-M":"1110011","M+1":"1110111","M-1":"1110010",
        "D+M":"1000010","D-M":"1010011","M-D":"1000111","D&M":"1000000","D|M":"1010101"}
DEST = {"":"000","M":"001","D":"010","MD":"011","A":"100","AM":"101","AD":"110","AMD":"111"}
JUMP = {"":"000","JGT":"001","JEQ":"010","JGE":"011","JLT":"100","JNE":"101","JLE":"110","JMP":"111"}

def predefined():
    t = {"SP":0,"LCL":1,"ARG":2,"THIS":3,"THAT":4,"SCREEN":16384,"KBD":24576}
    for i in range(16):
        t["R%d" % i] = i
    return t

def clean(line):
    return line.split("//")[0].strip().replace(" ", "")

def assemble(path):
    with open(path) as f:
        raw = f.read().splitlines()
    symbols = predefined()

    # First pass: record labels
    rom = 0
    for n, line in enumerate(raw, 1):
        c = clean(line)
        if not c:
            continue
        if c.startswith("("):
            label = c.strip("()")
            if label in symbols:
                print("Warning: Line %d: label '(%s)' is defined more than once" % (n, label))
            else:
                symbols[label] = rom
        else:
            rom += 1

    # Second pass: translate
    out, next_var = [], 16
    for n, line in enumerate(raw, 1):
        c = clean(line)
        if not c or c.startswith("("):
            continue
        if c[0] == "@":
            s = c[1:]
            if s.isdigit():
                val = int(s)
            else:
                if s not in symbols:
                    symbols[s] = next_var
                    next_var += 1
                val = symbols[s]
            out.append(format(val, "016b"))
        else:
            dest, jump = "", ""
            if "=" in c:
                dest, c = c.split("=", 1)
            if ";" in c:
                c, jump = c.split(";", 1)
            out.append("111" + COMP[c] + DEST[dest] + JUMP[jump])
    return out

if __name__ == "__main__":
    src = sys.argv[1]
    code = assemble(src)
    dst = src.rsplit(".", 1)[0] + ".hack"
    with open(dst, "w") as f:
        f.write("\n".join(code) + "\n")
    print("Wrote %s (%d instructions)" % (dst, len(code)))