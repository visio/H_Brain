"""
    Autor:  Joern Hoffarth
    Mailto: joern.hoffart(at)me.com
    
    Beschreibung des Programms:
        Das H(Head)_Brain dient der Koordination zwischen MasterBrain (Robert) und den 3 Modulen TTS (text to spech), EmoFani(Emotion-Face-Animation) und Mira welches fuer die Kopfdrehung / Koerperdrehung zustaendig ist.
    _______________________________________________________________________________________________
    
    H_Brain empfaengt:
    MasterBrain:
        "#HBRAIN##TEXT#ich bin ein Test{35,27}[:-)]schaue hier{Person}[:-|]" (Im Gespraechstring darf Text vorkommen, der an TTS weitergeleitet wird {} sind Positoen die angeschaut werden sollen und [] sind Emotionen. Nichts wird automatisch rueckgestellt! Gespraechstrings werden der Reihe nach bearbeitet (kein Abbruch, bei neuem Gespraechstring)
    
        "#HBRAIN##PERSON#{67;36}" (Einen Punkt an dem sich die der Aktuelle Gespraechspartner befindet. Kann staendig zwischdrin gesedet werden. Durch {Person} im Gespraechstring schaut Leonie immer den Gespraechspartner an. nach dem ein seperater Punkt angeschaut wurde, muss erst wieder {Person} gesendet werden, damit Leonie wieder den Gespraechspartner anschaut.
    
    TTS:
        "#TTS#finished" muss gesendet werden, wenn TTS fertig mit dem sprechen ist!
    _______________________________________________________________________________________________
    
    H_Brain sendet:
    MasterBrain
        "#HBRAIN#busy" (beschaeftigt)
        "#HBRAIN#free" (Fertig)
    
    TTS:
        "blabla" (reine Textstrings)
    
    EmoFani:
        ""t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(personX)" /   (Augenpositionen)
        ""t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=True"" / (Lippenbewegung)
        ""t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=neutral%100"" (Emotionen)
    
    Mira: (noch nicht fertig)
        "Hx"(Kopfdrehung)
        "Bx"(Bodydrehung)
    _______________________________________________________________________________________________
"""


import socket
import sys
import time
from collections import namedtuple

adress = namedtuple("adress", "UDP_IN_IP UDP_IN_PORT")




############################## UDP IP/Port Einstellungen ##############################
#Nur ein Block der folgenden UDP Einstellungen sollte aktiv sein. Rest mit Fueschen von drei Gaensen auskomentieren!
"""

####################### Mac an der Hochschule ####################################
HBrainAD      = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11005)
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11010)
EmoFaniAD     = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11001)
MIRAAD        = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11002)
##################################################################################
"""
"""
#######################  Mac bei mir zuhause ###################################
HBrainAD      = adress(UDP_IN_IP = "10.0.1.4", UDP_IN_PORT = 11005)
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "10.0.1.4", UDP_IN_PORT = 11010)
EmoFaniAD     = adress(UDP_IN_IP = "10.0.1.4", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "10.0.1.4", UDP_IN_PORT = 11001)
MIRAAD        = adress(UDP_IN_IP = "10.0.1.4", UDP_IN_PORT = 11002)
#################################################################################
"""

#######################  NUC an FritzBox ########################################
HBrainAD      = adress(UDP_IN_IP = "192.168.188.22", UDP_IN_PORT = 11005)
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "192.168.188.24", UDP_IN_PORT = 8888)
EmoFaniAD     = adress(UDP_IN_IP = "192.168.188.22", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "192.168.188.21", UDP_IN_PORT = 5555)
MIRAAD        = adress(UDP_IN_IP = "192.168.188.21", UDP_IN_PORT = 8888)
#################################################################################



print "HBrainAD     ", HBrainAD
print "MasterBrain  ", MasterBrainAD
print "EmoFani      ", EmoFaniAD
print "TTS          ", TTSAD
print "MIRA         ", MIRAAD


sprechen = 0
textString = ""
personFlag = True
personX ="0"
personY ="0"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((HBrainAD.UDP_IN_IP, HBrainAD.UDP_IN_PORT))


while True:
    
    
#Input string von allen moeglich Modulen
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    now = (int(time.time() * 1000))
    #print "received message:", data
    #print data[:16]
    #print data[:13]
    #print personFlag
    
    
    if data[:16] == "#HBRAIN##PERSON#":
        print "Augenposition wird veraendert"
        #Augenposition UDP (FaceAni)
        data = data [16:]
        b = data.find('}')
        Augenposition = data[1:b]
        print "Position: ", Augenposition
        b = Augenposition.find(';')
        personX=Augenposition[:b]
        personY=Augenposition[b+1:]
        if personFlag == True:
            Augenposition = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(personX))
            sock.sendto(Augenposition, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
            Augenposition = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazey=" + str(personY))
            sock.sendto(Augenposition, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))


    elif data[:14] == "#HBRAIN##TEXT#":
        textString += (data[14:] + " ")

    if data[:13] == "#TTS#finished" or sprechen == 0: #Rueckgabe wann TTS fertig ist
        sprechen = 0
        
        if textString == "":
            TTS = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=False")
            sock.sendto(TTS, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
            sock.sendto("#HBRAIN#free", (MasterBrainAD.UDP_IN_IP, MasterBrainAD.UDP_IN_PORT))
            continue
        
        while sprechen == 0:
            emotion = 0
            position = 0

            try:
                if textString[0] == ' ':
                    klappt = 0 #leere Anweisung
            except:
                textString = ""
                break
        
            if textString[0] == '[':
                emotion = 1

            elif textString[0] == '{':
                position = 1
        
            else:
                a = textString.find('[')
                b = textString.find('{')
                if a == -1:
                    a = 100000
                if b == -1:
                    b = 100000
                if a < b:
                    TTS = textString[0:a]
                    textString = textString[(a):]
                elif b < a:
                    TTS = textString[0:b]
                    textString = textString[(b):]
                else:
                    TTS = textString
                    textString = ""


#Sprach Weiterleitung
            if not position and not emotion:
                
                #Sprache UDP (TTS)
                print TTS
                sock.sendto(TTS, (TTSAD.UDP_IN_IP, TTSAD.UDP_IN_PORT))
                
                #Mundbewegug
                TTS = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=True")
                sock.sendto(TTS, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
                sprechen = 1
                sock.sendto("#HBRAIN#busy", (MasterBrainAD.UDP_IN_IP, MasterBrainAD.UDP_IN_PORT))


#Emotion Weiterleitung
            if emotion:
                #Emotions UDP (FaceAni)
                a = textString.find(']')
                emotion = textString[1:a]
                textString = textString[(a+1):]
                print "Emotion: ", emotion
                if emotion == ':-|':
                    emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=neutral%100")
                elif emotion == ':-)':
                    emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=happy%100")
                sock.sendto(emotion, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))



#Blickposition Weiterleitung
            if position:
                #Augenposition UDP (FaceAni)
                b = textString.find('}')
                position = textString[1:b]
                textString = textString[b+1:]
                print "Position: ", position
                if position == "Person":
                    personFlag = True
                    x = personX
                    y = personY
                else:
                    personFlag = False
                    b = position.find(';')
                    x=position[:b]
                    y=position[b+1:]


                position = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(x))
                sock.sendto(position, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
                position = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazey=" + str(y))
                sock.sendto(position, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))

            if textString == "":
                break
