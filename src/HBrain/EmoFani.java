package HBrain;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.ThreadLocalRandom;

/**
 * @author jorn
 * Klasse zum uebersetzten der unterschiedlichen Emotions Kuerzeln, Thread fuer Idele
 */
public class EmoFani implements Runnable{
	private final BlockingQueue queue;
	private HBrain main;
	private String state = "";
	private boolean run;
	private boolean bla = false;
	
	public EmoFani(HBrain main){
		this.main = main;
		this.queue = new LinkedBlockingQueue();
	}
	
	/**
	 * uebersetzung der emotions Kuerzel
	 */
	public void showEmotion(String emotion){
		if(emotion.contains("neutral") || emotion.contains(":-|") ||emotion.contentEquals("0")){
			this.sendExpression("expression=neutral%100");
		}
		else if(emotion.contains("happy") || emotion.contains(":-)") ||emotion.contentEquals("1")){
			this.sendExpression("expression=happy%100");
		}
		else if(emotion.contains("sad") || emotion.contains(":-(") ||emotion.contentEquals("5")){
			this.sendExpression("expression=sad%100");
		}
		else if(emotion.contains("attentive")){
			this.sendExpression("expression=attentive%100");
		}
		else if(emotion.contains("excited") || emotion.contains(":-O") ||emotion.contentEquals("2")){
			this.sendExpression("expression=excited%60");
		}
		else if(emotion.contains("laughing") || emotion.contains(":-D") ||emotion.contentEquals("3")){
			this.sendExpression("expression=excited%100");
		}
		else if(emotion.contains("relaxed")){
			this.sendExpression("expression=relaxed%100");
		}
		else if(emotion.contains("sleepy")){
			this.sendExpression("expression=sleepy%100");
		}
		else if(emotion.contains("frustrated") || emotion.contains("-.-") ||emotion.contentEquals("4")){
			this.sendExpression("expression=frustrated%100");
		}
		else if(emotion.contains(":-/")){
			this.sendExpression("pleasure=-37");
			this.sendExpression("arousal=-36");
		}
		else if(emotion.contains("idle")){
			this.ideleState(emotion);
		}
		else if(emotion.contains("blush:true")){
			this.sendExpression("blush=100");
		}
		else if(emotion.contains("blush:false")){
			this.sendExpression("blush=0");
		}


	}
	
	/**
	 * Methode zum senden von Daten an Emofani
	 */
    public void sendExpression(String expression){
    	String message = ("t:" + System.currentTimeMillis() + ";s:127.0.0.1" + ";p:" + this.main.EMOPort + ";d:" + expression);
    	System.out.println("sendEmo: " + message);
    	this.main.udpio.send(this.main.EMOIPAddress, this.main.EMOPort, message);
		try {
			TimeUnit.MILLISECONDS.sleep(5);;
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
    
    /**
	 * Methode für den Textparser, fuer die Mundbewegung
	 */
    public void blabla(boolean state){
    	if (state != this.bla){
    		this.bla = state;
    		if(this.bla){
    			this.sendExpression("talking=True");
    		}
    		else{
    			this.sendExpression("talking=False");
    		}
    	}
    }
	
    /**
	 * zur Kommunikation mit dem Idle Thread
	 */
	public void ideleState(String state) {
		try {
			this.queue.put(state);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * Idle Thread fuer zufallsbewegungen
	 */
	public void run() {
		boolean idle1Flag = false;
		this.run = true;
		while(this.run){
			if(!this.queue.isEmpty()){
				try {
					this.state = (String) this.queue.take();
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				
				if(this.state.equals("exit")){
					this.run = false;
					continue;
				}
				System.out.println("IDLE: " + this.state);
				
			}
			
			
			
			if(this.state.contains("idle1:true")){
				if(idle1Flag == false){
					idle1Flag = true;
					this.sendExpression("idle=true");
				}
				try {
					TimeUnit.MILLISECONDS.sleep(200);;
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
			else{
				if(idle1Flag == true){
					idle1Flag = false;
					this.sendExpression("idle=false");
				}
			
				if(this.state.contains("idle2:true")){
					int a = ThreadLocalRandom.current().nextInt(-80, 81);
					int b = ThreadLocalRandom.current().nextInt(-60, 61);
					int sleep = ThreadLocalRandom.current().nextInt(3000, 9001);
					try {
						TimeUnit.MILLISECONDS.sleep(sleep);;
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
					this.main.parser.look_obj.lookAt("{" + a + "," + b + "}");
					
					sleep = ThreadLocalRandom.current().nextInt(500, 2001);
					try {
						TimeUnit.MILLISECONDS.sleep(sleep);;
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
					this.main.parser.look_obj.lookAt("{0,0}");

				}
				else if(this.state.contains("idle3:true")){
					int a = ThreadLocalRandom.current().nextInt(-50, 51);
					int b = ThreadLocalRandom.current().nextInt(-50, 11);
					int sleep = ThreadLocalRandom.current().nextInt(7000, 15001);
					try {
						TimeUnit.MILLISECONDS.sleep(sleep);;
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
					this.main.parser.look_obj.lookAt("{" + a + "," + b + "}");
					
					sleep = ThreadLocalRandom.current().nextInt(800, 2001);
					try {
						TimeUnit.MILLISECONDS.sleep(sleep);;
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
					this.main.parser.look_obj.lookAt("{0,0}");
					
				}
				else{
					try {
						TimeUnit.MILLISECONDS.sleep(200);;
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}

			}
		}
		System.out.println("emo beendet");
	}
}
