/**
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
    */

package HBrain;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.concurrent.TimeUnit;


/**
 * Main Klasse des Hbrains. Verbindet den UDP server mit dem Textparser.
 * 
 * Main main = new Main(args);
 * main.start();
 * main.addInput("#BRAIN##TEXT#ich bin ein Test.{35,27}[:-)]schaue. hier{Person}[idle3:true]");
 * main.addInput("#TTS#received");
 * main.addInput("#TTS#finished");
 * main.addInput("#HBRAIN##PERSON#{67,36}");
 * main.addInput("#NAV##ROTBODY#90#");
 * main.addInput("#NAV##ROTHEAD#80#");
 * main.stop();
 */

public class HBrain implements Runnable {
	private static HBrain instance = null;
	
	protected UDPio udpio;
	protected CommandParser parser;
	
	private HBrainCallback log;
	private HBrainCallback responseBrain;
	
	protected int 		SelfPort;
	protected InetAddress SelfIPAddress;	
	protected int 		MasterPort;
	protected InetAddress MasterIPAddress;
	protected InetAddress TTSIPAddress;
	protected int 		TTSPort;
	protected InetAddress EMOIPAddress;
	protected int 		EMOPort;
	protected InetAddress MiraIPAddress;
	protected int 		MiraPort;
	
	
	public HBrain(String[] args) throws UnknownHostException{		
		
		for (String string : args) {
			System.out.println(string);
		}
		
		//set Callbacks
		this.registerCallbackLog(new Log());
		this.registerCallbackResponseBrain(new ResponseBrain());
		
		//default IPs and Ports
		this.SelfIPAddress = InetAddress.getByName("localhost");
		this.SelfPort = 11000;		
		this.MasterIPAddress = InetAddress.getByName("localhost");
		this.MasterPort = 11000;
		this.TTSIPAddress = InetAddress.getByName("localhost");
		this.TTSPort = 11003;
		this.EMOIPAddress = InetAddress.getByName("localhost");
		this.EMOPort = 11002;
		this.MiraIPAddress = InetAddress.getByName("localhost");
		this.MiraPort = 11001;
		
		//args to variablen
		if(args.length == 11 ){
			this.SelfIPAddress = InetAddress.getByName(args[1]);
			this.SelfPort = Integer.parseInt(args[2]);
			this.MasterIPAddress = InetAddress.getByName(args[3]);
			this.MasterPort = Integer.parseInt(args[4]);
			this.TTSIPAddress = InetAddress.getByName(args[5]);
			this.TTSPort = Integer.parseInt(args[6]);			
			this.EMOIPAddress = InetAddress.getByName(args[7]);
			this.EMOPort = Integer.parseInt(args[8]);			
			this.MiraIPAddress = InetAddress.getByName(args[9]);
			this.MiraPort = Integer.parseInt(args[10]);	
		}

		//generate objects
		this.udpio = new UDPio(this.SelfPort);
		this.parser = new CommandParser(this);
		
		log("SelfIPAddress: " + this.SelfIPAddress);
		log("SelfPort: " + this.SelfPort);
		log("MasterIPAddress: " + this.MasterIPAddress);
		log("MasterPort: " + this.MasterPort);
		log("TTSIPAddress: " + this.TTSIPAddress);
		log("TTSPort: " + this.TTSPort);
		log("EMOIPAddress: " + this.EMOIPAddress);
		log("EMOPort: " + this.EMOPort);
		log("MiraIPAddress: " + this.MiraIPAddress);
		log("MiraPort: " + this.MiraPort);
		
	}
	
	public static HBrain instanceOf(String[] args) throws UnknownHostException{
		if(instance==null)
			instance = new HBrain(args);
		
		return instance;
	}
	
	public static HBrain getInstance(){
		return instance;
	}
	
	/**
	 * verbindet in dauerschleife, den UDP server mit dem Textparser
	 */
	public void run(){
		String input = "";
		while(!input.contentEquals("exit")){
			
			input = this.udpio.listen();
			this.parser.addInput(input);
			
			if (input.contentEquals("exit"))
					this.udpio.stopp();	
			}
		this.log("main beendet");
	}
	
	/**
	 * startet das komplette H_Brain als eigener Thread wenn nicht gewünscht, dann direkt du Run methode
	 */
	public void start(){
		Thread t0 = new Thread(this);
		t0.start();
	}
	
	/**
	 * beendet alle das gesamte programm in dem das Keyword exit per 
	 * UDP an sich selbst geschickt wird
	 */
	public void stop(){
		this.udpio.send(SelfIPAddress, SelfPort, "exit");
	}
	
	/**
	 * der direkte Weg kommandos zu geben
	 */
	public void addInput(String input){
		this.parser.addInput(input);
	}

	/**
	 * Testmethode
	 */
	public static void main(String[] args) throws UnknownHostException {
		HBrain hbrain = HBrain.instanceOf(args);
		hbrain.start();
		
		
		//Im Gespraechstring darf Text vorkommen, der an TTS weitergeleitet wird {} sind Positoen die angeschaut werden 
		//sollen und[] sind Emotionen. Nichts wird automatisch rueckgestellt! Gespraechstrings werden der Reihe nach 
		//bearbeitet (kein Abbruch, bei neuem Gespraechstring)
		hbrain.addInput("#BRAIN##TEXT#ich bin ein Test.{35,27}[:-)]schaue. hier{Person}[idle3:true]");
		
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//muss gesendet werden, wenn TTS die Nachricht empfangen hat!
		hbrain.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//muss gesendet werden, wenn TTS fertig mit dem sprechen ist!
		hbrain.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		hbrain.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		hbrain.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		hbrain.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		hbrain.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}		
		
		hbrain.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		hbrain.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//Einen Punkt an dem sich die der Aktuelle Gespraechspartner befindet. Kann staendig zwischdrin gesedet werden. 
		//Durch {Person} im Gespraechstring schaut Leonie immer den Gespraechspartner an. nach dem ein seperater Punkt 
		//angeschaut wurde, muss erst wieder {Person} gesendet werden, damit Leonie wieder den Gespraechspartner anschaut.
		hbrain.addInput("#HBRAIN##PERSON#{67,36}");
		
		//#NAV##ROTBODY#[angle:int]# clockwise
		hbrain.addInput("#NAV##ROTBODY#90#");
		//#NAV##ROTHEAD#[angle:int]#
		hbrain.addInput("#NAV##ROTHEAD#80#");
		
		
		try {
			TimeUnit.SECONDS.sleep(10);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		hbrain.stop();
			
	}
	
	public void registerCallbackLog(HBrainCallback log) {
		this.log = log;
	}

	public void registerCallbackResponseBrain(HBrainCallback responseBrain) {
		this.responseBrain = responseBrain;
	}
	
	public boolean log(String msg){
		return this.log.call(msg);
	}
	
	public boolean responseBrain(String msg){
		return this.responseBrain.call(msg);
	}

	public UDPio getUdpio() {
		return udpio;
	}


}
