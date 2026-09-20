android.permissions = INTERNET, ACCESS_NETWORK_STATE, BIND_VPN_SERVICE, FOREGROUND_SERVICE

android.add_src = src/org/test/vpn/MyVpnService.java

android.manifest.application_child = <service android:name="org.test.vpn.MyVpnService" android:permission="android.permission.BIND_VPN_SERVICE" android:exported="false"><intent-filter><action android:name="android.net.VpnService"/></intent-filter></service>
