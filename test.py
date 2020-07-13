numLines = 0
file = open("static/cardInfo.txt", "r")
for line in file:
    line = line.strip("\n")
    numLines += 1
print(numLines)