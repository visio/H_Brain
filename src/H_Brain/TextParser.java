/**
 * 
 */
package H_Brain;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

/**
 * @author jorn
 *Klasse zum zerlegen der Strings
 */
public class TextParser implements Runnable{
	private final BlockingQueue queue;
	private final BlockingQueue command;
	private Main main;
	protected EmoFani emo;
	private String text;
	private boolean run;
	
	/**
	 * Konstruktor, der den Emofani thread startet
	 */
	public TextParser(Main main){
		this.main = main;
		this.emo = new EmoFani(main);
		this.queue = new LinkedBlockingQueue();
		this.command = new LinkedBlockingQueue();
		
		Thread t3 = new Thread(this.emo);
		t3.start();
		}
	
	/**
	 * funktion um asynchron neue Text hinzuzufuegen. Wird von dem Komandoparser aufgerufen
	 */
	public void newText(String text) {
		try {
			this.queue.put(text);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * Fuer Kommandos wie TTS finnished
	 */
	public void newCommand(String text) {
		try {
			this.command.put(text);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * run methode mit endlosschleife, in dem die Textstrings zerlegt werden
	 */
	public void run() {
		this.run = true;
		while(this.run){
			
			//wenn queue emty aufhoeren zu sprechen
			if(this.queue.isEmpty()){
				this.emo.blabla(false);
				this.main.udpio.send(this.main.SelfIPAddress, this.main.SelfPort, "#HBRAIN#0#");
			}
			
			//get new command
			try {
				this.text = (String) this.queue.take();
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
			//beenden des Threads with exit
			if(this.text.equals("exit")){
				this.run = false;
				continue;
			}
			
			this.main.udpio.send(this.main.SelfIPAddress, this.main.SelfPort, "#HBRAIN#1#");
			
			//zerlegen des Textstrings
			String[] textA1 = this.text.split("\\{");
			for(String text2 : textA1){
				String[] textA3 = text2.split("\\[");
				for(String text4 : textA3){
					if(text4.contains("}")){
						String[] textA5 = text4.split("}");
						if(textA5.length>1){
							text4 = textA5[1];
						}
						else{
							text4 = null;
						}
						
						String text6 = textA5[0];
						if(text6.contains("Person")){
							this.main.parser.PersonHandler(true, "");
						}
						else{
							this.main.parser.PersonHandler(false, text6);
						}	
					}
					else if(text4.contains("]")){
							String[] textA5 = text4.split("]");
							if(textA5.length>1){
								text4 = textA5[1];
							}
							else{
								text4 = null;
							}
							String emotion = textA5[0];
							this.emo.showEmotion(emotion);
					}
					if(text4 != null){
						if (text4.trim().length() != 0){
							this.speak(text4);		
							}				
					}
				}
			}
		}
		System.out.println("text beendet");
	}
	
	/**
	 * vorverarbeitung für TTS z.B bei einem Punkt hoert der mund auf zu sprechen
	 */
	private void speak(String text){
		//fange an zu sprechen
		this.emo.blabla(true);
		
		//String in einzelen Sätze zerlegen
		boolean point = false;
		String next = null;
		if(text.contains(".")){
			point = true;
			if (text.length() - text.indexOf(".")+1 > 0)
				next = text.substring(text.indexOf(".")+1, text.length());
				text = text.substring(0, text.indexOf(".")+1);
		}
		
		//Senden an TTS
		String c = null;
		System.out.println("sendTTS: " + text);
		this.main.udpio.send(this.main.TTSIPAddress, this.main.TTSPort, text);
		
		//warten auf reaktion von TTS
		do{
			try {
				c = (String) this.command.poll(500L, TimeUnit.MILLISECONDS);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				c = "received";
				e.printStackTrace();
			}
			if(c == null) System.out.println("TTS not available, send again");
		}while(c == null);

		//warten aufs fertig labern
		System.out.println("waiting for finishing jabbering...");
		try {
			c = (String) this.command.poll(60L, TimeUnit.SECONDS);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			c = "received";
			e.printStackTrace();
			}
		
		//wenn punkt exestiert kurz lippenbewegung einstellen
		if(point){
			this.emo.blabla(false);
			try {
				TimeUnit.MILLISECONDS.sleep(500);;
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		//selbst aufruf fuer den Fall das es mehere Saetze gab
		if (next != null){
			if(!(next.trim().length() == 0)){
				this.speak(next);
				}
		}
	}
	
}
