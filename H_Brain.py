#geschrieben von Joern Hoffarth
#Mailto: joern.hoffart(at)me.com

import socket
import sys
import time
from collections import namedtuple

adress = namedtuple("adress", "UDP_IN_IP UDP_IN_PORT")


#######################  UDP IP/Port Einstellungen ######################
HBrainAD      = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11005)
#  => Fuer alle Module gilt die HBrainAdresse als Output!
MasterBrainAD = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11010)
EmoFaniAD     = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11001)
MIRAAD        = adress(UDP_IN_IP = "134.103.205.72", UDP_IN_PORT = 11002)
#########################################################################
print "HBrainAD     ", HBrainAD
print "MasterBrain  ", MasterBrainAD
print "EmoFani      ", EmoFaniAD
print "TTS          ", TTSAD
print "MIRA         ", MIRAAD


sprechen = 0
textString = " "
personFlag = False

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((HBrainAD.UDP_IN_IP, HBrainAD.UDP_IN_PORT))


while True:
    now = (int(time.time() * 1000))
    emotion = 0
    position = 0
    
#Input string von allen moeglich Modulen
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data
    print data[:16]
    print personFlag
    if data[:16] == "#HBRAIN##PERSON#" and personFlag == True:
        print 1
        #Augenposition UDP (FaceAni)
        data = data [16:]
        b = data.find('}')
        Augenposition = data[1:b]
        print "Position: ", Augenposition
        b = Augenposition.find(';')
        x=Augenposition[:b]
        y=Augenposition[b+1:]
        Augenposition = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(x))
        sock.sendto(Augenposition, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
        Augenposition = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazey=" + str(y))
        sock.sendto(Augenposition, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))


    elif data[:14] == "#HBRAIN##TEXT#":
        print 2
        textString += " " + data[14:]
        continue

    elif data == "#TTS#finished" or sprechen == 0: #Rueckgabe wann TTS fertig ist
        TTS = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=False")
        sock.sendto(TTS, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
        sprechen == 0
        if textString == " ":
            continue
                

        print textString
        try:
            if textString[0] == ' ':
                klappt = 0 #leere Anweisung
        except:
            textString = " "
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
                textString = " "


#Sprach Weiterleitung
        if not position and not emotion:
            #Sprache UDP (TTS)
            print TTS
            sock.sendto(TTS, (TTSAD.UDP_IN_IP, TTSAD.UDP_IN_PORT))
            #Mundbewegug
            TTS = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=True")
            sock.sendto(TTS, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
            sprechen = 1

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
                continue
            personFlag = False
            b = position.find(';')
            x=position[:b]
            y=position[b+1:]
            position = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(x))
            sock.sendto(position, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
            position = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazey=" + str(y))
            sock.sendto(position, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
