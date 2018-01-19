import re
from tkinter import *

rx = re.compile(r"^[0-9]*[.,]?[0-9]+$|^p$|^((p|[0-9]*[.,]?[0-9]+)[\+\-\/\*\^]){1,}(p|[0-9]*[.,]?[0-9]+)$")


def matches(line, opendelim='(', closedelim=')'):
    stack = []
    for m in re.finditer(r'[{}{}]'.format(opendelim, closedelim), line):
        pos = m.start()
        if line[pos - 1] == '\\':
            # skip escape sequence
            continue
        c = line[pos]
        if c == opendelim:
            stack.append(pos + 1)
        elif c == closedelim:
            if len(stack) > 0:
                prevpos = stack.pop()
                yield (True, prevpos, pos, len(stack))
            else:
                # error
                yield (False, 0, 0, 0)
                pass
    if len(stack) > 0:
        for pos in stack:
            yield (False, 0, 0, 0)


def isPartCorrect(s):
    result = False
    if rx.match(s):
        result = True
    return result


def isCorrect(s):
    result = True
    if s.find("(") >= 0 or s.find(")") >= 0:
        for correct, openpos, closepos, level in matches(s):
            if correct:
                part = s[openpos:closepos]
                if part.find("(") == -1 and part.find(")") == -1:
                    if not isPartCorrect(part):
                        result = False
                        break
                part = s[openpos - 1:closepos + 1]
                replaced = s.replace(part, "p")
                if replaced.find("(") >= 0 or replaced.find(")") >= 0:
                    if not isCorrect(replaced):
                        result = False
                        break
                else:
                    if not isPartCorrect(replaced):
                        result = False
                        break
            else:
                result = False
                break
    else:
        result = isPartCorrect(s)
    return result


root = Tk()
mainframe = Frame(root, width=260, height=200, bg='lightblue')
mainframe.pack()

line = Text(root, height=1, width=29)
line.pack()
line.place(x=10,y=5)

processline = Label(root, height=1, width=33, bg='white', anchor='w', justify=LEFT)
processline.pack()
processline.place(x=10, y=30)

output = Label(root, height=1, width=33, bg='white', anchor='w', justify=LEFT)
output.pack()
output.place(x=10, y=55)

i = ''
v = 0


def readfromline():
    global i
    global v
    v = line.get('1.0', END)
    x = ''
    for i in range(0, len(v) - 1):
        x += v[i]
    processline['text'] = x
    i = v[:len(v) - 1]
    output['text'] = ''


def check():
    global i
    if isCorrect(i):
        output['text'] = 'Correct'
    else:
        output['text'] = 'Incorrect'

but_read = Button(root, text='Read', command=readfromline)
but_read.pack()
but_read.place(x=10, y=90)

but_check = Button(root, text='Check', command=check)
but_check.pack()
but_check.place(x=60, y=90)
print("hello")

root.mainloop()