"""
    Autor:  Joern Hoffarth
    Mailto: joern.hoffart(at)me.com
    
    Beschreibung des Programms:
        Das H(Head)_Brain dient der Koordination zwischen MasterBrain (Robert) und den 3 Modulen TTS (text to spech), EmoFani(Emotion-Face-Animation) und Mira welches fuer die Kopfdrehung / Koerperdrehung zustaendig ist.
    _______________________________________________________________________________________________
    
    H_Brain empfaengt:
    MasterBrain:
        "#BRAIN##TEXT#ich bin ein Test{35,27}[:-)]schaue hier{Person}[:-|]" (Im Gespraechstring darf Text vorkommen, der an TTS weitergeleitet wird {} sind Positoen die angeschaut werden sollen und [] sind Emotionen. Nichts wird automatisch rueckgestellt! Gespraechstrings werden der Reihe nach bearbeitet (kein Abbruch, bei neuem Gespraechstring)
    
        "#BRAIN##PERSON#{67;36}" (Einen Punkt an dem sich die der Aktuelle Gespraechspartner befindet. Kann staendig zwischdrin gesedet werden. Durch {Person} im Gespraechstring schaut Leonie immer den Gespraechspartner an. nach dem ein seperater Punkt angeschaut wurde, muss erst wieder {Person} gesendet werden, damit Leonie wieder den Gespraechspartner anschaut.
    
    TTS:
        "#TTS#finished" muss gesendet werden, wenn TTS fertig mit dem sprechen ist!
        "#TTS#received" muss gesendet werden, wenn TTS die Nachricht empfangen hat!
    _______________________________________________________________________________________________
    
    H_Brain sendet:
    MasterBrain
        "#HBRAIN#1#" (beschaeftigt)
        "#HBRAIN#0#" (Fertig)
    
    TTS:
        "blabla" (reine Textstrings)
    
    EmoFani:
        ""t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(personX)" /   (Augenpositionen)
        ""t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=True"" / (Lippenbewegung)
        ""t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=neutral%100"" (Emotionen)
    
    Mira: (noch nicht fertig)
    Rotate Body:	 #NAV##ROTBODY#[angle:int]#	//#NAV##ROTBODY#80# clockwise
    Rotate Head:	 #NAV##ROTHEAD#[angle:int]#	//#NAV##ROTHEAD#90#

    _______________________________________________________________________________________________
"""


import socket
import sys
import time
from collections import namedtuple
import multiprocessing

adress = namedtuple("adress", "UDP_IN_IP UDP_IN_PORT")



"""
############################## UDP IP/Port Einstellungen ##############################
#Nur ein Block der folgenden UDP Einstellungen sollte aktiv sein. Rest mit Fueschen von drei Gaensen auskomentieren!

####################### Mac an der Hochschule ####################################
HBrainAD      = adress(UDP_IN_IP = "134.103.204.164", UDP_IN_PORT = 11005)
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "134.103.204.164", UDP_IN_PORT = 11010)
EmoFaniAD     = adress(UDP_IN_IP = "134.103.204.164", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "134.103.204.164", UDP_IN_PORT = 11001)
MIRAAD        = adress(UDP_IN_IP = "134.103.204.164", UDP_IN_PORT = 11002)
##################################################################################
"""

#######################  Mac bei mir zuhause ###################################
HBrainAD      = adress(UDP_IN_IP = "10.0.1.4", UDP_IN_PORT = 11005)
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "192.168.188.22", UDP_IN_PORT = 8888)
EmoFaniAD     = adress(UDP_IN_IP = "192.168.188.22", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "192.168.188.21", UDP_IN_PORT = 5555)
MIRAAD        = adress(UDP_IN_IP = "192.168.188.21", UDP_IN_PORT = 8888)
#################################################################################

"""
#######################  NUC an FritzBox ########################################
HBrainAD      = adress(UDP_IN_IP = "192.168.188.108", UDP_IN_PORT = 11005)
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "192.168.188.23", UDP_IN_PORT = 8888)
EmoFaniAD     = adress(UDP_IN_IP = "192.168.188.11", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "192.168.188.10", UDP_IN_PORT = 5555)
MIRAAD        = adress(UDP_IN_IP = "192.168.188.10", UDP_IN_PORT = 8888)
#################################################################################
"""


print "HBrainAD     ", HBrainAD
print "MasterBrain  ", MasterBrainAD
print "EmoFani      ", EmoFaniAD
print "TTS          ", TTSAD
print "MIRA         ", MIRAAD

TTS =""
textString = ""
personFlag = True
personX ="0"
personY ="0"
messageReceived = 1
position=""
emotion=""
now = (int(time.time() * 1000))
try:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((HBrainAD.UDP_IN_IP, HBrainAD.UDP_IN_PORT))
except:
    print "Irgendeine IPadresse ist nicht ansprechbar / falsch"
    exit()



#Input string von allen moeglich Modulen
def empfangen():
    global TTS
    sprechen = 0
    textString = ""
    personFlag = True
    global personX
    global personY
    global messageReceived
    data = ""
    global position
    global emotion
    global now
    
    global HBrainAD
    global MasterBrainAD
    global EmoFaniAD
    global TTSAD
    global MIRAAD
    
    
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data
    messageReceived=0
    if data[:13] == "#TTS#received": #Rueckgabe wann TTS Nachricht empfangen hat
        messageReceived = 1
        
    elif data[:15] == "#BRAIN##PERSON#":  #Augenposition UDP (FaceAni)
        data = data [15:]
        b = data.find('}')
        Augenposition = data[1:b]
        b = Augenposition.find(';')
        personX=Augenposition[:b]
        personY=Augenposition[b+1:]
        if personFlag:
            print "Augenposition wird veraendert: ", Augenposition
            Augenposition = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(personX))
            sock.sendto(Augenposition, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
            Augenposition = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazey=" + str(personY))
            sock.sendto(Augenposition, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
        else:
            print "Augenposition wird gespeichert: ", Augenposition

    elif data[:13] == "#BRAIN##TEXT#":
        textString += (" " + data[13:])

    if data[:13] == "#TTS#finished" or not sprechen: #Rueckgabe wann TTS fertig ist
        sprechen = 0
        
        while sprechen == 0 and textString != "":
            try:
                if textString[0] == ' ':
                    klappt = 0 #leere Anweisung
            except:
                textString = ""
                break
            
            
            if textString[0] == '[':
                a = textString.find(']')
                emotion = textString[1:a]
                textString = textString[(a+1):]
                emotionenKlasifizierung()
            elif textString[0] == '{':  #Blickposition Weiterleitung
                b = textString.find('}')
                position = textString[1:b]
                textString = textString[b+1:]
                if not KOPFUNDAUGEN.is_alive():
                    KOPFUNDAUGEN.run()
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
            
                if TTS != " ":  #Sprach Weiterleitung
                    
                    #Sprache UDP (TTS)
                    time.sleep(0.05)
                    print TTS
                    sock.sendto(TTS, (TTSAD.UDP_IN_IP, TTSAD.UDP_IN_PORT))
                    #Mundbewegug
                    EmoFaniString = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=True")
                    sock.sendto(EmoFaniString, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
                    messageReceived = 0
                    sprechen = 1
                    sock.sendto("#HBRAIN#1#", (MasterBrainAD.UDP_IN_IP, MasterBrainAD.UDP_IN_PORT))

    if textString == "" and sprechen == 0:
        EmoFaniString = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=False")
        sock.sendto(EmoFaniString, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
        sock.sendto("#HBRAIN#0#", (MasterBrainAD.UDP_IN_IP, MasterBrainAD.UDP_IN_PORT))


#Thread zum staendige nachstellen der Augen
def kopfUndAugen():
    global HBrainAD
    global EmoFaniAD
    global MIRAAD
    
    
    global position
    global personX
    global personY
    global now
    
    if position == "Person":
        print "Position :", position," (", personX, ";", personY, ")"
        personFlag = True
        x = personX
        y = personY
    else:
        print "Position :", position
        personFlag = False
        b = position.find(';')
        x=position[:b]
        y=position[b+1:]

    sendeString = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazex=" + str(x))
    sock.sendto(sendeString, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
    sendeString = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:gazey=" + str(y))
    sock.sendto(sendeString, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))


#Funktion zur Emotionsausgabe
def emotionenKlasifizierung():
    global emotion
    global now
    global HBrainAD
    global EmoFaniAD
    global MIRAAD

    print "Emotion: ", emotion
    if emotion == 'neutral' or emotion == ':-|':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=neutral%100")

    elif emotion == 'happy' or emotion == ':-)':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=happy%100")

    elif emotion == 'sad' or emotion == ':-(':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=sad%100")

    elif emotion == 'attentive':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=attentive%100")

    elif emotion == 'excited' or emotion == ':-O':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=excited%100")

    elif emotion == 'relaxed':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=relaxed%100")

    elif emotion == 'sleepy':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=sleepy%100")

    elif emotion == 'frustrated' or emotion == '-.-':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:expression=frustrated%100")

    elif emotion == 'idle:true':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:idle=true")

    elif emotion == 'idle:false':
        emotion = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:idle=false")

    sock.sendto(emotion, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))


#Funktion zum berechnen der Deltatime
STime=0
def deltaTime(dTime):
    global STime
    if not STime:
        STime=time.time()
        return False
    if STime+dTime<= time.time():
        STime=0
        return True
    else:
        return False



#Hauptprogramm mit Hoheit ueber Multithreading
KOPFUNDAUGEN = multiprocessing.Process(target=kopfUndAugen)
KOPFUNDAUGEN.start()
EMPFANGEN = multiprocessing.Process(target=empfangen)
EMPFANGEN.start()
while True:
    time.sleep(1)
    now = (int(time.time() * 1000))
    print messageReceived
 
    if EMPFANGEN.is_alive():
        if messageReceived == 0:# and deltaTime(0.5):
            print "erneueter Versuch TTS zu erreichen!"
            sock.sendto(TTS, (TTSAD.UDP_IN_IP, TTSAD.UDP_IN_PORT))

    else:
        
        EMPFANGEN.join()

                

