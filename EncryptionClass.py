import math
import matplotlib.pyplot as plt
import sys

import codecs

import json
import click

import time

class Random:
    def __init__ (self, seed = 321785):
        self.init_frequency (16)
        self.seed = seed

    def init_frequency (self, bitPlace):
        self.frequency = 0
        
        for i in range (0, bitPlace):
            self.frequency |= (1 << i)

    def rnd (self):
        self.seed += 0.5

        seededPoint = self.seed * self.frequency
        sinValue = (math.sin (seededPoint) + 1) * 0.5

        return sinValue

    def Event (self, probability):
        return self.rnd() < (probability / 100)

    def Range (self, x, y):
        return x + (y - x) * self.rnd()

    def RangeInt (self, x, y):
        return math.floor (self.Range (x, y))

class MakeKeys:
    def __init__ (self):
        self.zobrist = []
        self.characters = []

        self.BIT32MAX = 0

        for i in range(15):
            self.BIT32MAX |= (1 << (i + 1))

        self.build_zobrist (0)

    def build_zobrist (self, seed):
        random = Random (seed)
        self.zobrist = []

        self.characters = list("QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890")

        for character in self.characters:
            bit64 = 0

            for i in range (1, 64):
                if random.Event (25):
                    bit64 |= (1 << i)
            
            self.zobrist.append (bit64)

    def GetSeedFromKey (self, key):
        self.build_zobrist (len(key))

        seed = 0

        for char in key:
            index = self.characters.index (char)

            seed ^= self.zobrist[index]

        return seed

class Encryption:
    def __init__ (self):
        self.Key = MakeKeys ()
        self.ValidCharacters = list("1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm .,/?!;'\"-=+_@#%$^&*()<>\n:[]\\{}~|`")
        self.Num = len(self.ValidCharacters)

    def GetChar (self, index):
        return self.ValidCharacters [index % self.Num]
        
    def Encrypt (self, sequence, key):
        seed = self.Key.GetSeedFromKey (key) / self.Key.BIT32MAX
        crypto = Random (seed)

        timeBasedRandom = Random (time.time() / 1000)

        encrypted = ""

        extraEnum = 0

        for character in sequence:
            index = self.ValidCharacters.index (character)

            newCharacter = self.GetChar (index + crypto.RangeInt(0, self.Num) + extraEnum)

            extraEnum += crypto.RangeInt (0, self.Num)

            encrypted += newCharacter

            excess = crypto.RangeInt (0, 3)
            for i in range(excess):
                encrypted += self.GetChar (timeBasedRandom.RangeInt (0, self.Num))

        return encrypted

    def GetRealKey (self, key):
        return str(self.Key.GetSeedFromKey (key))

    def Decrypt (self, sequence, key):
        seed = self.Key.GetSeedFromKey (key) / self.Key.BIT32MAX
        crypto = Random (seed)

        decrypted = ""

        extraEnum = 0
        excess = 0

        for character in sequence:
            if excess > 0:
                excess -= 1
                continue

            index = self.ValidCharacters.index (character)

            realCharacter = self.GetChar (index - crypto.RangeInt(0, self.Num) - extraEnum)

            extraEnum += crypto.RangeInt (0, self.Num)

            excess = crypto.RangeInt (0, 3)

            decrypted += realCharacter

        return decrypted

@click.command ()
@click.option ("--path")
@click.option ("--key")
@click.option ("--option")
def main (path, key, option):
    cryptography = Encryption ()

    encryptionScheme = cryptography.Encrypt if option == "E" else cryptography.Decrypt

    if option == "E":
        with open (path, "rb") as f:
            internalText = str(f.read())

            internalText = json.dumps({
                "type": path.split(".")[1],
                "text": internalText
            })

            encryptedText = cryptography.Encrypt (internalText, key)
            newPath = path.split(".")[0] + "-encrypted.txt"
            print (newPath)

            with open (newPath, "w") as of:
                of.write (encryptedText)

                of.close ()

            f.close()

    if option == "D":
        with open (path, "r") as f:
            internalText = f.read()

            decryptedText = cryptography.Decrypt (internalText, key)

            decryptedData = json.loads (decryptedText)

            newPath = path.split(".")[0] + "-decrypted." + decryptedData["type"]
            print (newPath)

            with open (newPath, "wb") as of:
                hex_string = decryptedData["text"].strip()
                byteArr = hex_string.encode('utf-8').decode('unicode_escape').encode('latin-1')

                of.write (byteArr)
                of.close ()

            f.close()

if __name__ == "__main__":
    main()