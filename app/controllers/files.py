from numpy import loadtxt
import env

def getAddressFile(fileName):
    consts = env.const
    lines = []
    if fileName:
        with open(consts["ROOT_DIR"] + '\\' + fileName + '.dat', encoding="utf8") as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]

    return lines

