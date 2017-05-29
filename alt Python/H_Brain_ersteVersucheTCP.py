#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 17:44:57 2017

@author: root
"""
import threading
import Queue
import time
import sys
import random
import socket

#IP Adressen und Ports:                 IP-Adresse    UDP   TCP  both/UDP/TCP
adressen = {"MasterBrainAD->HBrain" : ("10.0.1.5", 11000, 5000, 'both'),
            "HBrain->MasterBrainAD" : ("10.0.1.5", 11001, 5001, 'both'),
            
            "TTSAD->HBrain"         : ("10.0.1.5", 11002, 5002, 'both'),
            "HBrain->TTSAD"         : ("10.0.1.5", 11003, 5003, 'both'),
            
            "MIRAAD->HBrain"        : ("10.0.1.5", 11004, 5004, 'both'),
            "HBrain->MIRAAD"        : ("10.0.1.5", 11005, 5005, 'both'),
            
            "EmoFani->HBrain"       : ("10.0.1.5", 11006, 5006, 'both'),
            "HBrain->EmoFani"       : ("10.0.1.5", 11007, 5007, 'both')            
            }

for i, item in enumerate(sys.argv, 1):
    if item in adressen:
        del adressen[item]
        adressen.update({item : (sys.argv[i+1], sys.argv[i+2], sys.argv[i+3])})
    

class UDPSendReciver(threading.Thread):
    def __init__(self, inputQ, ip, port):
        super(UDPSendReciver, self).__init__()
        self._stop = threading.Event()        
        self.inputQ = inputQ
        self.ip = ip
        self.port = port
        try:
            self.sock = socket.socket(socket.AF_INET, # Internet
                                     socket.SOCK_DGRAM) # UDP
            self.sock.bind((self.ip, self.port))
        except:
            print self.ip, self.port, "nicht ansprechbar"
           
                
        
    def stop(self):
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()
    
    def run(self):
        while not self.isStopped():      
            try:
                #Input string von allen moeglich Modulen
                data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
                self.inputQ.put(data)
                if data == "exit":
                    self._stop.set()
            except:
                print "fehler beim empfangen!"
                
    def send(self, text):
        self.sock.sendto(text, (self.ip, self.port))
            

class TCPSendReciver(threading.Thread):
    def __init__(self, inputQ, inputIP, inputPort, outputIP, outputPort):
        super(TCPSendReciver, self).__init__()
        self._stop = threading.Event()        
        self.inputQ = inputQ
        self.inputIP = inputIP
        self.inputPort = inputPort
        self.outputIP = outputIP
        self.outputPort = outputPort
        
        self.inputC = None
        self.outputC = None
        try:
            self.inputC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.inputC.bind((self.inputIP, self.inputPort))
            self.inputC.listen(1)
        except:
            print self.inputIP, self.inputPort, "nicht ansprechbar"
            
        try:
            self.outputC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.outputC.connect((self.outputIP, self.outputPort))
        except:
            print self.outputIP, self.outputPort, "nicht ansprechbar"
        
    def stop(self):
        self.outputC.close()
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()
    
    def run(self):
        while not self.isStopped():      
            try:
                conn, addr = self.s.accept()
                print 'Connection address:', addr
                while not self.isStopped():
                    data = conn.recv(1024)
                    if not data or data == "exit": 
                        self._stop.set()
                        
                    print "received data:", data
                    conn.send("HBrainSuccesfullyr.:" + data)  # echo
                conn.close()
            except:
                print "fehler beim empfangen!"
                
    def send(self, text):
        self.outputC.send(text)
        


class InputWorker(threading.Thread):
    def __init__(self, inputQ, settingInQ, adressen):
        super(InputWorker, self).__init__()
        self._stop = threading.Event()
        
        self.inputQ = inputQ
        self.settingInQ = settingInQ
        self.adressen = adressen
        

    def stop(self):
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()
    
    def run(self):
        while not self.isStopped():
            time.sleep(0.5)
            inputQ.put("hi1")
            
            if not self.settingInQ.empty():
                data = self.settingInQ.get()
                self.settingInQ.task_done()
                print "settingInQ: ", data 
                self.adressen = data
                
            self.UDPresive()
            
            
    def UDPresive(self):
        pass
        
                


class OutputWorker(threading.Thread):
    def __init__(self, inputQ, settingOutQ, adressen):
        super(OutputWorker, self).__init__()
        self._stop = threading.Event()
        
        self.inputQ = inputQ
        self.settingOutQ = settingOutQ
        self.adressen = adressen

    def stop(self):
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()
    
    def run(self):
        while not self.isStopped():
            time.sleep(0.5)
            if not self.inputQ.empty():
                data = self.inputQ.get()
                self.inputQ.task_done()
                print "inputQ: ", data 
                
            if not self.settingOutQ.empty():
                data = self.settingOutQ.get()
                self.settingOutQ.task_done()
                print "settingOutQ: ", data 
                self.adressen = data
            



if __name__ == '__main__':
    inputQ = Queue.Queue()
    settingInQ = Queue.Queue()
    settingOutQ = Queue.Queue()
    
    meine_threads = []
    
    thread = InputWorker(inputQ, settingInQ, adressen) 
    meine_threads.append(thread)
    thread = OutputWorker(inputQ, settingOutQ, adressen) 
    meine_threads.append(thread)
    
    settingInQ.put(adressen)
    settingOutQ.put(adressen)
    
    for t in meine_threads: 
        time.sleep(0.5)
        t.start()
  
    time.sleep(5)    
    for t in meine_threads: 
        t.stop()
        
    for t in meine_threads: 
        t.join()
    
    print "bye"
    