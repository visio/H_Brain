/**
 * 
 */
package HBrain;

import java.net.UnknownHostException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

/**
 * @author jorn
 * Klasse zur Kooerdination von Blickposition von Emofani zur Kopfdrehumng Mira
 */
public class LookAtPosition implements Runnable{
	private final BlockingQueue queue;
	private HBrain main;
	private String position = null;
	private boolean run;
	
	public LookAtPosition(HBrain main){
		this.main = main;
		this.queue = new LinkedBlockingQueue();
	}
	
	public void lookAt(String position) {
		try {
			this.queue.put(position);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * endlosschleife, wartet auf neue Blickposition
	 */
	public void run() {
		int oldPan = 0;
		int oldTilt = 0;
		String[] positionA;
		
		this.run = true;
		while(this.run){
			try {
				this.position = (String) this.queue.take();
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
			if(this.position.equals("exit")){
				this.run = false;
				continue;
			}
			
			position = position.replace("{", "");
			position = position.replace("}", "");
	
			if(position.contains(","))
				positionA = position.split(",");
			else
				positionA = position.split(",");
			@SuppressWarnings("unused")
			int pan = Integer.parseInt(positionA[0]);
			int tilt = Integer.parseInt(positionA[1]);
			
			System.out.println("lookAt: " + position);
			
			this.main.udpio.send(this.main.MiraIPAddress, this.main.MiraPort, "#NAV##ROTHEAD#" + (-180 - pan) + "#");
			
			pan = pan * 2;
			this.main.parser.text_obj.emo.sendExpression("gazey=" + tilt);
	        
	        int pan_corrected = pan - oldPan;
	        this.main.parser.text_obj.emo.sendExpression("gazex=" + pan_corrected);
	        
	        try {
				TimeUnit.MILLISECONDS.sleep(300);;
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
	        
	        while(oldPan != pan){
		        try {
					TimeUnit.MILLISECONDS.sleep(100);;
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
		        
	            if((pan+10) < oldPan) 
	            	oldPan -= 15;
	            else if ((pan-10) > oldPan) 
	            	oldPan += 15;
	            else 
	            	break;
	            
	            pan_corrected = pan - oldPan;
		        this.main.parser.text_obj.emo.sendExpression("gazex=" + pan_corrected);
	        }

	        oldPan = pan;
	        System.out.println("Augen Nachfuehren beedet");
			
		}
		System.out.println("Look at beendet");
	}

	
	/**
	 * TestMethode
	 */
	public static void main(String[] args) throws UnknownHostException {
		HBrain Settings = new HBrain(args);
		LookAtPosition a = new LookAtPosition(Settings);
		Thread t1 = new Thread( a );
		t1.start();
		
		a.lookAt("{67,36}");
		
		a.lookAt("exit");
	}
}
