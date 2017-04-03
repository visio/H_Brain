"""
    Autor:  Joern Hoffarth
    Mailto: joern.hoffart(at)me.com
    
    Beschreibung des Programms:
        Das H(Head)_Brain dient der Koordination zwischen MasterBrain (Robert) und den 3 Modulen TTS (text to spech), EmoFani(Emotion-Face-Animation) und Mira welches fuer die Kopfdrehung / Koerperdrehung zustaendig ist.
    _______________________________________________________________________________________________
    
    H_Brain empfaengt:
    MasterBrain:
        "#BRAIN##TEXT#ich bin ein Test{35,27}[:-)]schaue hier{Person}[:-|]" (Im Gespraechstring darf Text vorkommen, der an TTS weitergeleitet wird {} sind Positoen die angeschaut werden sollen und [] sind Emotionen. Nichts wird automatisch rueckgestellt! Gespraechstrings werden der Reihe nach bearbeitet (kein Abbruch, bei neuem Gespraechstring)
    
        "#HBRAIN##PERSON#{67;36}" (Einen Punkt an dem sich die der Aktuelle Gespraechspartner befindet. Kann staendig zwischdrin gesedet werden. Durch {Person} im Gespraechstring schaut Leonie immer den Gespraechspartner an. nach dem ein seperater Punkt angeschaut wurde, muss erst wieder {Person} gesendet werden, damit Leonie wieder den Gespraechspartner anschaut.
    
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
    
    Mira:
    Rotate Body:	 #NAV##ROTBODY#[angle:int]#	//#NAV##ROTBODY#80# clockwise
    Rotate Head:	 #NAV##ROTHEAD#[angle:int]#	//#NAV##ROTHEAD#90#

    _______________________________________________________________________________________________
"""


import socket
import sys
import time
import random
import multiprocessing



############################## UDP IP/Port Einstellungen ##############################
#IP Adressen und Ports:                 IP-Adresse    UDP   TCP  both/UDP/TCP

adressen = {"MasterBrainAD->HBrain" : ("192.168.188.11", 11005),
            "HBrain->MasterBrainAD" : ("192.168.188.23",  8888),
            
            "TTSAD->HBrain"         : ("192.168.188.11", 11005),
            "HBrain->TTSAD"         : ("192.168.188.23", 11003),
            
            "MIRAAD->HBrain"        : ("192.168.188.11", 11005),
            "HBrain->MIRAAD"        : ("192.168.188.10",  5000),
            
            "EmoFani->HBrain"       : ("192.168.188.11", 11005),
            "HBrain->EmoFani"       : ("192.168.188.12", 11000)            
            }

"""

adressen = {"MasterBrainAD->HBrain" : ("134.103.204.95", 11005),
            "HBrain->MasterBrainAD" : ("192.168.188.23",  8888),
            
            "TTSAD->HBrain"         : ("192.168.188.11", 11005),
            "HBrain->TTSAD"         : ("192.168.188.23", 11003),
            
            "MIRAAD->HBrain"        : ("192.168.188.11", 11005),
            "HBrain->MIRAAD"        : ("192.168.188.10",  5000),
            
            "EmoFani->HBrain"       : ("192.168.188.11", 11005),
            "HBrain->EmoFani"       : ("192.168.188.12", 11000)            
            }
"""

print "HBrainAD     ", adressen["MasterBrainAD->HBrain"]
print "MasterBrain  ", adressen["HBrain->MasterBrainAD"]
print "EmoFani      ", adressen["HBrain->EmoFani"]
print "TTS          ", adressen["HBrain->TTSAD"]
print "MIRA         ", adressen["HBrain->MIRAAD"]


    
try:
    a=0
    for i, item in enumerate(sys.argv, 2):   
        if item in adressen:
            del adressen[item]
            adressen.update({item : (sys.argv[a+1], sys.argv[a+2])})
        a+=1
except:
    print '''fehler bei der Argumentuebergabe. Richtig: 
            '0' 
            'MasterBrainAD->HBrain' '134.103.204.95' '11005' 
            'HBrain->MasterBrainAD' '134.103.204.95' '11005' 
            'TTSAD->HBrain' '134.103.204.95' '11005'
            'HBrain->TTSAD' '134.103.204.95' '11005'
            'MIRAAD->HBrain' '134.103.204.95' '11005'
            'HBrain->MIRAAD' '134.103.204.95' '11005'
            'EmoFani->HBrain' '134.103.204.95' '11005'
            'HBrain->EmoFani' '134.103.204.95' '11005'    
          '''

  


mirrorFlag=0

try:
    mirrorFlag=int(sys.argv[1])
    if mirrorFlag==1:
        print "H_Bran: Mirrorflag"
    else:
        print "H_Bran: kein Mirrorflag"
except:
    print "H_Bran: kein Argument -> kein Mirrorflag"


sprechen = 0
textString = ""
idleFlag=0
idleFlag2=0
idleFlag3=0
personX ="0"
personY ="0"
messageReceived = 1
data = ""
personFlag = True
satzzeichenFlag=0
try:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind(adressen["MasterBrainAD->HBrain"])
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



def idle2():
    while True:
        a = random.randint(-80,80)
        b = random.randint(-60,60)
        time.sleep(random.randint(3,9))
        sendeString = str("#HBRAIN##RANDOM#{" + str(a) + ";" + str(b) + "}")
        sock.sendto(sendeString, adressen["MasterBrainAD->HBrain"])
        time.sleep(random.randint(5,20)/10)
        sendeString = str("#HBRAIN##RANDOM#{0;0}")
        sock.sendto(sendeString, adressen["MasterBrainAD->HBrain"])


def idle3():
    while True:
        a = random.randint(-50,50)
        b = random.randint(-50,10)
        time.sleep(random.randint(7,15))
        sendeString = str("#HBRAIN##RANDOM#{" + str(a) + ";" + str(b) + "}")
        sock.sendto(sendeString, adressen["MasterBrainAD->HBrain"])
        time.sleep(random.randint(8,20)/10)
        sendeString = str("#HBRAIN##RANDOM#{0;0}")
        sock.sendto(sendeString, adressen["MasterBrainAD->HBrain"])


def kopfDrehung():
    personX = 0
    personY = 0
    global HBrainAD
    global EmoFaniAD
    global MIRAAD
    Xaktuell = 0
    global personFlag
    
    while True:
        position = kopfUbergabe.get()
        person = False
        now = (int(time.time() * 1000))
        
        print "position: ", position
        
        if position == "Person":
            personFlag = True
            x = personX
            y = personY
        elif position[0]=='#' and personFlag:
            b = position.find(';')
            x=position[1:b]
            y=position[b+1:]
        elif position[0]=='#' and not personFlag:
            b = position.find(';')
            personX=position[1:b]
            personY=position[b+1:]
            continue
        else:
            personFlag = False
            b = position.find(';')
            x=position[:b]
            y=position[b+1:]
        try:
            x=int(x)
        except:
            continue

        sendeString = str("#NAV##ROTHEAD#" + str(-180 - x) + "#")
        sock.sendto(sendeString, adressen["HBrain->MIRAAD"])
        x=int(x*2)
        sendeString = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazey=" + str(y))
        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
        a=int(x)-Xaktuell
        sendeString = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazex=" + str(a))
        sock.sendto(sendeString, adressen["HBrain->EmoFani"])
        
        
        time.sleep(0.3)
        while Xaktuell != x:
            time.sleep(0.1)
            if (x+10) < Xaktuell:
                Xaktuell -= 15
            elif (x-10) > Xaktuell:
                Xaktuell += 15
            else:
                break
            a=int(x)-Xaktuell
            sendeString = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:gazex=" + str(a))
            sock.sendto(sendeString, adressen["HBrain->EmoFani"])



        Xaktuell = x
        print "Augen Nachfuehren beedet"


kopfUbergabe = multiprocessing.Queue()
o = multiprocessing.Process(target=kopfDrehung)
o.start()



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
                sock.sendto(TTS, adressen["HBrain->TTSAD"])
                
                
    data = uerbergabe.get()
    if data[:13] == "#TTS#received": #Rueckgabe wann TTS Nachricht empfangen hat
        messageReceived = 1
    print "received message:", data
    
    
    if data[:16] == "#HBRAIN##PERSON#" or data[:16] == "#HBRAIN##RANDOM#":
        print "Augenposition wird veraendert"
        #Augenposition UDP (FaceAni)
        data = data [16:]
        b = data.find('}')
        Augenposition = data[1:b]
        kopfUbergabe.put("#" + Augenposition)



    elif data[:13] == "#BRAIN##TEXT#":
        textString += (" " + data[13:])

    elif data[:17] == "#VBRAIN##EMOTION#" and mirrorFlag:
        textString += (" [" + data[17:-1] + "]")
        print "Mirror: ", data[17:-1]




    if data[:13] == "#TTS#finished" or sprechen == 0: #Rueckgabe wann TTS fertig ist
	#print "Ausgesprochen"
        sprechen = 0
        messageReceived = 1
        
        
        while sprechen == 0 and textString != "":
            emotion = 0
            position = 0
            
            
            if satzzeichenFlag:
                EmoFaniString = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:talking=False")
                sock.sendto(EmoFaniString, adressen["HBrain->EmoFani"])
            

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
                satzzeichenFlag=0
                if a == -1:
                    a = 100000
                b = textString.find('{')
                if (a > b and b != -1):
                    a = b

                b = textString.find('.')
                if (a > b and b != -1):
                    satzzeichenFlag = 1
                    a = b

                b = textString.find('?')
                if (a > b and b != -1):
                    satzzeichenFlag = 1
                    a = b

                b = textString.find('!')
                if (a > b and b != -1):
                    satzzeichenFlag = 1
                    a = b

                if a == 100000:
                    TTS = textString
                    textString = ""
                else:
                    if satzzeichenFlag:
                        a+=1
                    TTS = textString[0:a]
                    textString = textString[(a):]


                """
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
                """


#Sprach Weiterleitung
            if not position and not emotion and TTS != "" and TTS != " " and TTS != "  " and TTS != "   " and TTS != "    ":
                
                #Sprache UDP (TTS)
                time.sleep(0.1)
                print TTS
                sock.sendto(TTS, adressen["HBrain->TTSAD"])
                messageReceived = 0
                
                #Mundbewegug
                time.sleep(0.5)
                EmoFaniString = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:talking=True")
                sock.sendto(EmoFaniString, adressen["HBrain->EmoFani"])
                sprechen = 1
                sock.sendto("#HBRAIN#1#", adressen["HBrain->MasterBrainAD"])


#Emotion Weiterleitung
            if emotion:
                
                
                #Emotions UDP (FaceAni)
                a = textString.find(']')
                emotion = textString[1:a]
                textString = textString[(a+1):]
                print "Emotion: ", emotion
                if emotion == 'neutral' or emotion == ':-|' or emotion == '0':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=neutral%100")
                
                elif emotion == 'happy' or emotion == ':-)' or emotion == '1':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=happy%100")

                elif emotion == 'sad' or emotion == ':-(' or emotion == '5':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=sad%100")
                
                elif emotion == 'attentive':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=attentive%100")
                
                elif emotion == 'excited' or emotion == ':-O' or emotion == '2':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=excited%60")

                elif emotion == 'laughing' or emotion == ':-D' or emotion == '3':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=excited%100")

                elif emotion == ':-/':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:pleasure=-37")
                    sock.sendto(emotion, adressen["HBrain->EmoFani"])
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:arousal=-36")
        
                elif emotion == 'relaxed':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=relaxed%100")
                
                elif emotion == 'sleepy':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=sleepy%100")
                
                elif emotion == 'frustrated' or emotion == '-.-' or emotion == '4':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:expression=frustrated%100")
                
                elif emotion == 'idle:true':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:idle=true")
                    idleFlag=1
                    try:
                        y.terminate()
                    except:
                        print "laeuft noch garnicht"
                    try:
                        z.terminate()
                    except:
                        print "laeuft noch garnicht"
    
                        
                elif emotion == 'idle:false':
                    idleFlag=0
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:idle=false")
                    
                elif emotion == 'idle2:true':
                    if idleFlag2==0:
                        y = multiprocessing.Process(target=idle2)
                        try:
                            y.start()
                        except:
                            print "idle laeuft schon"
                    idleFlag2=1
                    try:
                        z.terminate()
                    except:
                        print "laeuft noch garnicht"

                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:idle=false")

                elif emotion == 'idle2:false':
                    try:
                        y.terminate()
                    except:
                        print "laeuft noch garnicht"

                    idleFlag2=0

                elif emotion == 'idle3:true':
                    if idleFlag3==0:
                        z = multiprocessing.Process(target=idle3)
                        try:
                            z.start()
                        except:
                            print "idle laeuft schon"
                    idleFlag3=1
                    try:
                        y.terminate()
                    except:
                        print "laeuft noch garnicht"
                
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:idle=false")

                elif emotion == 'idle3:false':
                    try:
                        z.terminate()
                    except:
                        print "laeuft noch garnicht"
                    idleFlag3=0

                elif emotion == 'blush:true':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:blush=100")
                elif emotion == 'blush:false':
                    emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:blush=0")


                sock.sendto(emotion, adressen["HBrain->EmoFani"])



#Blickposition Weiterleitung
            if position:
                #Augenposition UDP (FaceAni)
                b = textString.find('}')
                position = textString[1:b]
                kopfUbergabe.put(position)
                textString = textString[b+1:]
    
        if textString == "" and sprechen == 0:
            EmoFaniString = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:talking=False")
            sock.sendto(EmoFaniString, adressen["HBrain->EmoFani"])
            sock.sendto("#HBRAIN#0#", adressen["HBrain->MasterBrainAD"])
            
            if idleFlag:
                emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:idle=true")
            else:
                emotion = str("t:" + str(now) + ";s:"+ adressen["EmoFani->HBrain"][0] + ";p:" + str(adressen["EmoFani->HBrain"][1]) + ";d:idle=false")

            sock.sendto(emotion, adressen["HBrain->EmoFani"])
            continue
	    
	    
