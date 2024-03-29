package mobile.SFS;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.StringTokenizer;
import java.util.Vector;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class Bind extends Activity {
	private static final String host_ = GlobalConstants.HOST;
	//private static final String host_ = "http://is4server.com:8083";
	//private static final String host_ = "http://is4server.com:8084";
	
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.bind);
		Bundle extras = getIntent().getExtras();
		
		TextView currLoc = (TextView) findViewById(R.id.currLoc);
		final String currLocString = extras.getString("curr_loc");
        currLoc.setText(currLocString);
		
		Button changeCurrLoc = (Button) findViewById(R.id.changeCurrLoc);
        changeCurrLoc.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				Intent next = new Intent(Bind.this, ChangeLocation.class);
				next.putExtra("return_intent", new Intent(Bind.this, Bind.class));
				startActivity(next);
			}
		});
        
        TextView item = (TextView) findViewById(R.id.item);
        TextView meter = (TextView) findViewById(R.id.meter);
        final String itemUri = extras.getString("root");
        final String meterUri = extras.getString("node");
        item.setText(itemUri);
        meter.setText(meterUri);
        
        Button bind = (Button) findViewById(R.id.bind);
        bind.setOnClickListener(new OnClickListener() {
        	public void onClick(View v) {
        		try {
        			if(!Util.getProperties(host_ + itemUri).getString("Type").equals("Item") ||
        					Util.getProperties(host_ + meterUri).has("Type")) {
        				Toast.makeText(Bind.this, "Invalid binding. Scan first an item then a meter.", Toast.LENGTH_LONG).show();
        				Intent next = new Intent(Bind.this, MobileSFS.class);
        				next.putExtra("curr_loc", currLocString);
        				startActivity(next);
        				return;
        			}
        			
        			JSONArray jarr = Util.getChildren(host_ + itemUri);
        			String[] s;
        			
        			if(jarr != null) {
        				for(int i = 0; i < jarr.length(); i++) { //check for already bound
        					s = jarr.getString(i).split("->");
        					        					
        					if(!Util.getProperties(host_ + itemUri + "/" + s[0].trim()).has("Type")) {
        						Toast.makeText(Bind.this, "Already bound to: " +
               						 s[0].trim() + "\nPlease unbind first.", Toast.LENGTH_SHORT).show();
        						Intent next = new Intent(Bind.this, Unbind.class);
        						next.putExtra("curr_loc", currLocString);
        						next.putExtra("root", itemUri);
        						next.putExtra("node", s[1].trim());
        						startActivity(next);
        						return;
        					}
        				}
        			}
        			
        			String res ="None";
        			String meterName = "None";
					try {
						StringTokenizer tokenizer = new StringTokenizer(meterUri, "/");
						Vector<String> tokens = new Vector<String>();
						while(tokenizer.hasMoreElements())
							tokens.add(tokenizer.nextToken());
						meterName = tokens.elementAt(tokens.size()-1);
						
						String itemLoc = Util.getLocationByUri(itemUri);
						String meterLoc = Util.getLocationByUri(meterUri);
						Log.i(Bind.class.getName(), "itemLoc=" + itemLoc + ", meterLoc=" + meterLoc);
						
						if(itemLoc.equals(meterLoc)){
							res = Util.createSymlink(itemUri, meterUri, host_);
							Log.i("Bind", "creating symlink from qrc; " + itemUri + " to " + meterUri);
							JSONObject properties = new JSONObject();
							properties.put("bindattach_ts", TXM.serverInitTime_ - TXM.localInitTime_ + System.currentTimeMillis());
							JSONObject jsonObj = new JSONObject();
							jsonObj.put("operation", "update_properties");
							jsonObj.put("properties", properties);
							try {
								CurlOps.post(jsonObj.toString(), host_ + itemUri);
								Log.i("Bind", "json: " + jsonObj.toString() + "; itemUri: " + host_ + itemUri);
							} catch(Exception e){
								e.printStackTrace();
							}
							
						} else {
							Toast.makeText(Bind.this, 
        							"Cannot attach items registered in different locations!", 
        							Toast.LENGTH_LONG).show();
						}
					} catch(Exception e){
						e.printStackTrace();
						String itemuri=itemUri;
						if(itemUri.endsWith("/"))
							itemuri =itemUri.substring(0, itemUri.length()-1);
						Log.i("Bind", "Exists? " + itemuri + "/" + meterName);
						if(!Util.isExistingResource(host_ + itemuri + "/" + meterName)){
							Log.i("Bind.onActivityResult", "Exists? NO");
							Toast.makeText(getApplicationContext(), "Could not create:" + host_ + itemuri + "/" + meterName, 
									Toast.LENGTH_LONG).show();
							throw e;
						}
					}
        			Intent next = new Intent(Bind.this, MobileSFS.class);
        			next.putExtra("curr_loc", currLocString);
        			startActivity(next);
        			Toast.makeText(Bind.this, res, Toast.LENGTH_LONG).show();
        		}
        		catch(Exception e) {
        			e.printStackTrace();
        		}
        	}
        });
        
        Button cancel = (Button) findViewById(R.id.cancel);
        cancel.setOnClickListener(new OnClickListener() {
        	public void onClick(View v) {
        		Intent next = new Intent(Bind.this, MobileSFS.class);
        		next.putExtra("curr_loc", currLocString);
        		startActivity(next);
        	}
        });
	}
}
