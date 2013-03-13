package mobile.SFS;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

import android.annotation.TargetApi;
import android.app.Activity;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class HybridLoc extends Activity {
	
	@Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.hybridloc);
    }

    @Override
    protected void onStart() {
        super.onStart();
    }

    @Override
    protected void onRestart() {
        super.onRestart();
    }

    @Override
    protected void onResume() {
        super.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
    }

    @Override
    protected void onStop() {
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
    }
    
    public void localize(View view) {
    	TextView locationTextView = (TextView)findViewById(R.id.location);
    	locationTextView.setText("Localizing...");
    	
    	new LocalizeTask().execute();
    }
    
    @TargetApi(Build.VERSION_CODES.CUPCAKE)
	private class LocalizeTask extends AsyncTask<Void, Void, String> {
    	@Override
        protected String doInBackground(Void...values) {
    		String locationStr = "";
    		 
        	//get signature
        	String requestStr = "{\"data\": {\"wifi\": {\"timestamp\": \"1354058706884971435\", \"sigstr\": \"00:22:90:39:07:12,UNKNOWN,-77 00:17:df:a7:4c:f2,UNKNOWN,-81 dc:7b:94:35:25:02,UNKNOWN,-90 00:17:df:a7:33:12,UNKNOWN,-92 00:22:90:39:07:15,UNKNOWN,-79 00:17:df:a7:4c:f5,UNKNOWN,-79 dc:7b:94:35:25:05,UNKNOWN,-90 00:17:df:a7:33:15,UNKNOWN,-92 00:22:90:39:07:11,UNKNOWN,-77 00:22:90:39:07:16,UNKNOWN,-79 00:17:df:a7:4c:f6,UNKNOWN,-79 00:17:df:a7:4c:f0,UNKNOWN,-79 00:22:90:39:07:10,UNKNOWN,-80 00:17:df:a7:4c:f1,UNKNOWN,-81 dc:7b:94:35:25:01,UNKNOWN,-89 dc:7b:94:35:25:00,UNKNOWN,-91 00:17:df:a7:33:16,UNKNOWN,-91 00:17:df:a7:33:11,UNKNOWN,-92 dc:7b:94:35:25:06,UNKNOWN,-93 00:22:90:39:70:a1,UNKNOWN,-93\"}, \"ABS\": \"\"}, \"type\": \"localization\"}";
    		
    		// Connect to hybridLoc server with signature and wait for results
        	String HOST = "128.32.46.187";
        	int PORT = 10000;
        	
        	Socket clientSock = null;
        	PrintWriter out = null;
         	BufferedReader in = null;
        	try{
        		clientSock = new Socket(HOST, PORT);
        		
        		out = new PrintWriter(clientSock.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(
                		clientSock.getInputStream()));
    		}
    		catch(UnknownHostException e){
    			// TODO Auto-generated catch block
    			e.printStackTrace();
    			System.exit(1);
    		}
    		catch(IOException e){
    			// TODO Auto-generated catch block
    			e.printStackTrace();
    			System.exit(1);
    		}
        	
        	if (clientSock != null && out != null && in != null) {
    	    	out.println(requestStr);
    			out.flush();
    			
    			try {
    				locationStr = (String)in.readLine();
    			} catch (IOException e) {
    				// TODO Auto-generated catch block
    				e.printStackTrace();
    				System.exit(1);
    			}
    			
    			
    			try {
    				in.close();
    				out.close();
    				clientSock.close();
    			} catch (IOException e) {
    				// TODO Auto-generated catch block
    				e.printStackTrace();
    				System.exit(1);
    			}
    			
        	}
        	
        	return locationStr;
        }

    	@Override
        protected void onPostExecute(String locationStr) {
        	TextView locationTextView = (TextView)findViewById(R.id.location);
			locationTextView.setText(locationStr);
        }
    }
}
