import os

#Leitura de um arquivo com endereços
def getAddressFile(fileName):
    #consts = os.getenv.const
    lines = []
    if fileName:
        #Abre o arquivo
        with open(os.getenv("ROOT_DIR") + '\\' + fileName + '.dat', encoding="utf8") as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines] #Realiza leitura

    return lines #Retorna linhas lidas

