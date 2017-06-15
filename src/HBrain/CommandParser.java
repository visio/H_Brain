package HBrain;

import java.net.UnknownHostException;
import java.util.concurrent.TimeUnit;

/**
 * @author jorn
 *Klasse die UDP-Strings von der main entgegen nimmt und diese nach den 
 *Grundkategorien auftteilt
 */
public class CommandParser {
	private HBrain main;
	protected LookAtPosition look_obj;
	protected TextParser text_obj;
	
	volatile boolean see_to_person = false;
	String person = "{67,36}";
	
	
	/**
	 *Konstruktor, in dem der LookatPosition und der Textparser Thread gestartet wird.
	 */
	public CommandParser(HBrain main){
		this.main = main;
		this.look_obj = new LookAtPosition(this.main);
		this.text_obj = new TextParser(this.main);
		
		Thread t1 = new Thread( this.look_obj );
		t1.start();
		
		Thread t2 = new Thread( this.text_obj );
		t2.start();
		
	}
	
	/**
	 *von der main aufgerufene Methode, die Strings entweder direkt bearbeitet oder wenn nicht Zeintnahe
	 *in Warteschlangen(Queues) schiebt, auch wird hier das exit keyword verteilt, wenn alle THreads 
	 *runtergefahren werden sollen
	 */
	public void addInput(String input){
		int index;
		
		if(-1 != (index = input.lastIndexOf("#TTS#"))){
			this.TTShandler(input.substring(index+5));
		}
		else if(-1 != (index = input.lastIndexOf("#PERSON#"))){
			this.PersonHandler(input.substring(index+8));
		}
		else if(-1 != (index = input.lastIndexOf("#TEXT#"))){
			this.calculateTextString(input.substring(index+6));
		}
		else if(-1 != (index = input.lastIndexOf("#NAV#"))){
			this.MiraHandler(input.substring(index+5));
		}
		else if(input.equals("exit")){
			this.text_obj.newText(input);
			this.look_obj.lookAt(input);
			this.text_obj.emo.ideleState(input);
			}
		else{
			main.log("wrong command");
		}

	}
	
	/**
	 *weitergabe zum Textparser
	 */
	private void calculateTextString(String input){
		main.log("Text: " + input);
		this.text_obj.newText(input);
	}
	
	/**
	 *Interrupts für TTS resceiv und TTS finished
	 */
	private void TTShandler(String input){
		main.log("TTS: " + input);
			this.text_obj.newCommand(input);		
		}
	
	/**
	 * Innterrupts für Position von Person die gegenueber steht
	 */
	private void PersonHandler(String input){
		main.log("Person: " + input);
		this.person = input;
		if(this.see_to_person)
			this.look_obj.lookAt(this.person);	
	}
	public void PersonHandler(Boolean input, String position){
		main.log("Person: " + input);
		this.see_to_person = input;
		if(input)
			this.look_obj.lookAt(this.person);
		else{
			this.look_obj.lookAt(position);
		}
	}
	
	/**
	 * Innterrupts für indirektes ansteuern von mira ueber H_Brain
	 */
	private void MiraHandler(String input){
		if(input.contains("#ROTBODY#")){
			input = input.replace("#ROTBODY#", "");
			input = input.replace("#", "");
			int bodyrotation = Integer.parseInt(input);
			main.log("sendNAV: body" + bodyrotation);
			this.main.udpio.send(this.main.MiraIPAddress, this.main.MiraPort, "#NAV##ROTBODY#" + bodyrotation + "#");
			
		}
		else if(input.contains("ROTHEAD")){
			input = input.replace("#ROTHEAD#", "");
			input = input.replace("#", "");
			int headrotation = Integer.parseInt(input);
			main.log("sendNAV: head" + headrotation);
			this.main.udpio.send(this.main.MiraIPAddress, this.main.MiraPort, "#NAV##ROTHEAD#" + headrotation + "#");
		}
		else{
			main.log("Nav do not understand: " + input);
		}
		
	}

	
	/**
	 * @param args
	 * Tetsmethode ausführbar ohne Main
	 */
	public static void main(String[] args) throws UnknownHostException {
		// TODO Auto-generated method stub
		HBrain Settings = HBrain.instanceOf(args);
		CommandParser parser = new CommandParser(Settings);
		
		//nicht erlaubt muesste ignoriert werden
		parser.addInput("test");
		
		//Im Gespraechstring darf Text vorkommen, der an TTS weitergeleitet wird {} sind Positoen die angeschaut werden 
		//sollen und[] sind Emotionen. Nichts wird automatisch rueckgestellt! Gespraechstrings werden der Reihe nach 
		//bearbeitet (kein Abbruch, bei neuem Gespraechstring)
		parser.addInput("#BRAIN##TEXT#ich bin ein Test.{35,27}[:-)]schaue. hier{Person}[idle3:true]");
		
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//muss gesendet werden, wenn TTS die Nachricht empfangen hat!
		parser.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//muss gesendet werden, wenn TTS fertig mit dem sprechen ist!
		parser.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		parser.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		parser.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		parser.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		parser.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}		parser.addInput("#TTS#received");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		parser.addInput("#TTS#finished");
		try {
			TimeUnit.SECONDS.sleep(1);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//Einen Punkt an dem sich die der Aktuelle Gespraechspartner befindet. Kann staendig zwischdrin gesedet werden. 
		//Durch {Person} im Gespraechstring schaut Leonie immer den Gespraechspartner an. nach dem ein seperater Punkt 
		//angeschaut wurde, muss erst wieder {Person} gesendet werden, damit Leonie wieder den Gespraechspartner anschaut.
		parser.addInput("#HBRAIN##PERSON#{67;36}");
		
		//#NAV##ROTBODY#[angle:int]# clockwise
		parser.addInput("#NAV##ROTBODY#90#");
		//#NAV##ROTHEAD#[angle:int]#
		parser.addInput("#NAV##ROTHEAD#80#");
		
	}

}
