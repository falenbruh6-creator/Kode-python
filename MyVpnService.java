package org.test.vpn;

import android.content.Intent;
import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import android.util.Log;

public class MyVpnService extends VpnService {
    private ParcelFileDescriptor vpnInterface = null;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && "STOP".equals(intent.getAction())) {
            disconnectVpn();
            return START_NOT_STICKY;
        }

        String serverIp = intent != null ? intent.getStringExtra("SERVER_IP") : "192.0.2.10";
        String country = intent != null ? intent.getStringExtra("COUNTRY") : "US";

        connectVpn(serverIp, country);
        return START_STICKY;
    }

    private void connectVpn(String serverIp, String country) {
        try {
            if (vpnInterface != null) {
                vpnInterface.close();
            }

            // Membangun interface TUN bawaan Android OS
            Builder builder = new Builder();
            builder.setSession("VPN (" + country + ")")
                   .addAddress("10.0.0.2", 24)        // IP Virtual Lokal
                   .addDnsServer("8.8.8.8")           // DNS Google
                   .addRoute("0.0.0.0", 0);           // Alihkan SEMUA traffic melalui VPN

            // Menyalakan Virtual Network Interface (Ikon Kunci Akan Muncul)
            vpnInterface = builder.establish();
            Log.d("VPN_SERVICE", "VPN Connected successfully to " + serverIp);

        } catch (Exception e) {
            Log.e("VPN_SERVICE", "Failed to establish VPN", e);
        }
    }

    private void disconnectVpn() {
        try {
            if (vpnInterface != null) {
                vpnInterface.close();
                vpnInterface = null;
            }
            stopSelf();
            Log.d("VPN_SERVICE", "VPN Disconnected");
        } catch (Exception e) {
            Log.e("VPN_SERVICE", "Error on disconnect", e);
        }
    }

    @Override
    public void onDestroy() {
        disconnectVpn();
        super.onDestroy();
    }
}
