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
>>>>>>> origin/master
#  =>Alle Module senden bitte an die HBrain IN Adresse
MasterBrainAD = adress(UDP_IN_IP = "192.168.188.22", UDP_IN_PORT = 8888)
EmoFaniAD     = adress(UDP_IN_IP = "192.168.188.22", UDP_IN_PORT = 11000)
TTSAD         = adress(UDP_IN_IP = "192.168.188.21", UDP_IN_PORT = 5555)
MIRAAD        = adress(UDP_IN_IP = "192.168.188.21", UDP_IN_PORT = 8888)
#################################################################################
"""
"""
#######################  NUC an FritzBox ########################################
HBrainAD      = adress(UDP_IN_IP = "192.168.188.11", UDP_IN_PORT = 11005)
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





sprechen = 0
textString = ""
personFlag = True
personX ="0"
personY ="0"
messageReceived = 1
data = ""
try:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((HBrainAD.UDP_IN_IP, HBrainAD.UDP_IN_PORT))
except:
    print "Irgendeine IPadresse ist nicht ansprechbar / falsch"
    exit()


def empfangen():
    try:
        #Input string von allen moeglich Modulen
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        uerbergabe.put(data)
    
    except:
        print "fehler beim empfangen!"


while True:
    
    if __name__ == '__main__':
        # Start bar as a process
        now = (int(time.time() * 1000))
        uerbergabe = multiprocessing.Queue()
        p = multiprocessing.Process(target=empfangen)
        p.start()
        while p.is_alive():
            # Wait for 0.5 seconds or until process finishes
            p.join(0.5)
        
            # If thread is still active
            if messageReceived == 0:
                print "erneueter Versuch TTS zu erreichen!"
                sock.sendto(TTS, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
                
                
    data = uerbergabe.get()
    if data[:13] == "#TTS#received": #Rueckgabe wann TTS Nachricht empfangen hat
        messageReceived = 1
    print "received message:", data
    
    
    if data[:15] == "#BRAIN##PERSON#":
        print "Augenposition wird veraendert"
        #Augenposition UDP (FaceAni)
        data = data [15:]
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


    elif data[:13] == "#BRAIN##TEXT#":
        textString += (" " + data[13:])



    if data[:13] == "#TTS#finished" or sprechen == 0: #Rueckgabe wann TTS fertig ist
	#print "Ausgesprochen"
        sprechen = 0
        
        
        while sprechen == 0 and textString != "":
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
            if not position and not emotion and TTS != " ":
                
                #Sprache UDP (TTS)
                time.sleep(0.05)
                print TTS
                sock.sendto(TTS, (TTSAD.UDP_IN_IP, TTSAD.UDP_IN_PORT))
                messageReceived = 0
                
                #Mundbewegug
                EmoFaniString = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=True")
                sock.sendto(EmoFaniString, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
                sprechen = 1
                sock.sendto("#HBRAIN#1#", (MasterBrainAD.UDP_IN_IP, MasterBrainAD.UDP_IN_PORT))


#Emotion Weiterleitung
            if emotion:
                #Emotions UDP (FaceAni)
                a = textString.find(']')
                emotion = textString[1:a]
                textString = textString[(a+1):]
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

            
        if textString == "" and sprechen == 0:
            EmoFaniString = str("t:" + str(now) + ";s:"+ HBrainAD.UDP_IN_IP + ";p:" + str(HBrainAD.UDP_IN_PORT) + ";d:talking=False")
            sock.sendto(EmoFaniString, (EmoFaniAD.UDP_IN_IP, EmoFaniAD.UDP_IN_PORT))
            sock.sendto("#HBRAIN#0#", (MasterBrainAD.UDP_IN_IP, MasterBrainAD.UDP_IN_PORT))
            continue
