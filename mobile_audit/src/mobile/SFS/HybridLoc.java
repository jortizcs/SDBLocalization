package mobile.SFS;


import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.List;

import org.apache.http.HttpResponse;
import org.apache.http.ParseException;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

import android.app.Activity;
import android.net.wifi.ScanResult;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class HybridLoc extends Activity implements WifiScanner.Listener {

	private static final String UNKNOWN_SSID = "UNKNOWN";
	private String latestSigStr = "";
	
	@Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.hybridloc);
        
        // start up the wifi scanner
        WifiScanner.addListener(getApplicationContext(), this);
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
        WifiScanner.removeListener(this);
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
    
    @Override
    public void onScanResult(List<ScanResult> results) {
    	String newSigStr = "";
        for (ScanResult sr : results) {
        	newSigStr += sr.BSSID + "," + UNKNOWN_SSID + "," + sr.level + " ";
        }

        latestSigStr = newSigStr.trim();
        
        //Toast.makeText(getApplicationContext(), latestSigStr, Toast.LENGTH_LONG).show();
    }
    
	private class LocalizeTask extends AsyncTask<Void, Void, String> {
    	@Override
        protected String doInBackground(Void...values) {
    		String locationStr = "";
    		 
        	//get signature
        	String requestStr = "{\"data\": " +
        							"{\"wifi\": " +
        								"{\"timestamp\": \"1354058706884971435\", " +
        								"\"sigstr\": \""+latestSigStr+"\"}, " +
        							"\"ABS\": \"\"}, " +
        						"\"type\": \"localization\"}";
    		
    		// Connect to hybridLoc server with signature and wait for results
        	String HOST = "128.32.46.187";
        	Integer PORT = 10000;
        	String service = "localize";
        	String Url = "http://" + HOST + ":" + PORT.toString() + "/" + service;
        	
        	//instantiates httpclient to make request
            DefaultHttpClient httpclient = new DefaultHttpClient();

            //url with the post data
            HttpPost httppost = new HttpPost(Url);

            //passes the results to a string builder/entity
            StringEntity se = null;
			try {
				se = new StringEntity(requestStr);
			} catch (UnsupportedEncodingException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

            //sets the post request as the resulting string
            httppost.setEntity(se);
            //sets a request header so the page receving the request
            //will know what to do with it
            httppost.setHeader("Accept", "application/json");
            httppost.setHeader("Content-type", "application/json");

            //Handles what is returned from the page 
            HttpResponse response = null;
            try {
			    response = httpclient.execute(httppost);
			} catch (ClientProtocolException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
        	
            try {
				locationStr = EntityUtils.toString(response.getEntity(), "UTF-8");
			} catch (ParseException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
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
