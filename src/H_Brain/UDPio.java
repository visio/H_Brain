package H_Brain;

import java.io.IOException;
import java.net.*;


/**
 * @author jorn
 *Klasse die sich rund um die Kommunikation per UDP befasst
 */
public class UDPio
{
	DatagramSocket clientSocket = null;
	
		public UDPio(int port){
			try {
				this.clientSocket = new DatagramSocket(port);
			} catch (SocketException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		/**
		 *schließt den Socket 
		 */
		public void stopp(){
			this.clientSocket.close();
			System.out.println("udpio beendet");
		}
		/**
		 *wartet auf UDP-Strings und gibt diese an die main zurück 
		 */
		public String listen(){
			byte[] receiveData = new byte[1024];
			DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
		    try {
				this.clientSocket.receive(receivePacket);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		    String modifiedSentence = new String(receivePacket.getData());
		    modifiedSentence = modifiedSentence.trim();
		    System.out.println("FROM SERVER:" + modifiedSentence);
		    return modifiedSentence;
			
		}
		/**
		 *allgemeine UDP-Sendemethode 
		 */
		public void send(InetAddress IPAddress, int port, String message){
			byte[] sendData = new byte[1024];
			sendData = message.getBytes();
			
			DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, IPAddress, port);
			try {
				this.clientSocket.send(sendPacket);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
		}
	
		/**
		 *Testmethode
		 */
	    public static void main(String args[]) throws Exception
	    {
	    	UDPio test = new UDPio(11000);
	    	InetAddress IPAddress = InetAddress.getByName("localhost");
	    	test.send(IPAddress, 11000, "test");
	    	test.listen();
	    	test.stopp();
	       
	    }
	}
