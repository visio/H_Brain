package HBrain;

public interface HBrainCallback {
	public boolean call(String msg);
}

class ResponseBrain implements HBrainCallback{
	@Override
	public boolean call(String msg) {
		if(msg != null){
			HBrain hbrain = HBrain.getInstance();
			if (hbrain != null) {
				hbrain.getUdpio().send(hbrain.MasterIPAddress, hbrain.MasterPort, msg);
				System.out.println(msg);
				return true;
			}
		}
		System.err.println("responseBrain callback: There is a problem with param");
		return false;
	}
}

class Log implements HBrainCallback{
	@Override
	public boolean call(String msg) {
		if(msg != null){
				System.out.println(msg);
				return true;
		}
		System.err.println("log callback: There is a problem with param");
		return false;
	}
}
