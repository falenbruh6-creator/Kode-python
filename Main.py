from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.utils import platform

# Konfigurasi Server VPN (Sesuaikan IP & Port server VPN nyata Anda)
VPN_SERVERS = {
    'United States': {'ip': '192.0.2.10', 'port': '51820', 'code': 'US'},
    'United Kingdom': {'ip': '198.51.100.20', 'port': '51820', 'code': 'GB'}
}

class AndroidVPNApp(App):
    def build(self):
        self.is_connected = False
        self.is_connecting = False
        self.progress_value = 0

        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        # Header
        title_label = Label(
            text="VPN Client Android", 
            font_size='24sp', 
            bold=True, 
            size_hint=(1, 0.15)
        )
        
        # Status Label
        self.status_label = Label(
            text="Status: Disconnected", 
            font_size='18sp', 
            size_hint=(1, 0.15)
        )

        # Dropdown
        self.country_spinner = Spinner(
            text='United States',
            values=tuple(VPN_SERVERS.keys()),
            size_hint=(1, 0.15),
            font_size='16sp'
        )

        # Progress UI
        self.progress_label = Label(
            text="0%", 
            font_size='18sp', 
            bold=True,
            size_hint=(1, 0.1),
            opacity=0
        )
        
        self.progress_bar = ProgressBar(
            max=100, 
            value=0, 
            size_hint=(1, 0.1),
            opacity=0
        )

        # Tombol
        self.btn_action = Button(
            text="Connect VPN", 
            font_size='20sp', 
            size_hint=(1, 0.25),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.btn_action.bind(on_press=self.on_btn_click)

        layout.add_widget(title_label)
        layout.add_widget(self.status_label)
        layout.add_widget(self.country_spinner)
        layout.add_widget(self.progress_bar)
        layout.add_widget(self.progress_label)
        layout.add_widget(self.btn_action)

        return layout

    def on_btn_click(self, instance):
        if self.is_connecting:
            return

        if not self.is_connected:
            self.start_loading_process()
        else:
            self.stop_vpn_service()

    def start_loading_process(self):
        self.is_connecting = True
        self.country_spinner.disabled = True
        self.btn_action.disabled = True
        
        self.progress_bar.opacity = 1
        self.progress_label.opacity = 1
        self.progress_value = 0
        self.progress_bar.value = 0
        
        country = self.country_spinner.text
        self.status_label.text = f"Connecting to {country}..."

        Clock.schedule_interval(self.update_progress, 0.04)

    def update_progress(self, dt):
        self.progress_value += 2
        
        if self.progress_value >= 100:
            self.progress_value = 100
            self.progress_bar.value = 100
            self.progress_label.text = "100% - Handshake Done"
            
            Clock.unschedule(self.update_progress)
            self.establish_vpn()
            return False
            
        self.progress_bar.value = self.progress_value
        self.progress_label.text = f"Connecting... {self.progress_value}%"

    def establish_vpn(self):
        country = self.country_spinner.text
        server = VPN_SERVERS[country]

        if platform == 'android':
            try:
                from jnius import autoclass
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                VpnService = autoclass('android.net.VpnService')
                Intent = autoclass('android.content.Intent')
                
                activity = PythonActivity.mActivity

                # 1. Cek & Minta Izin VPN Sistem Android
                intent_prepare = VpnService.prepare(activity)
                if intent_prepare is not None:
                    activity.startActivityForResult(intent_prepare, 100)
                    self.status_label.text = "Menunggu Izin VPN dari Sistem..."
                    self.finish_connecting_ui(success=False)
                    return

                # 2. Jalankan Native Service Android
                service_intent = Intent(activity, autoclass('org.test.vpn.MyVpnService'))
                service_intent.putExtra("SERVER_IP", server['ip'])
                service_intent.putExtra("SERVER_PORT", server['port'])
                service_intent.putExtra("COUNTRY", country)
                
                activity.startService(service_intent)

                self.status_label.text = f"Status: Connected to {country}\nIP: {server['ip']}"
                self.is_connected = True
                self.finish_connecting_ui(success=True)

            except Exception as e:
                self.status_label.text = f"Error Android VPN: {str(e)}"
                self.is_connected = False
                self.finish_connecting_ui(success=False)
        else:
            # Simulasi di PC / Desktop
            self.status_label.text = f"Status: Connected to {country}\nIP: {server['ip']}"
            self.is_connected = True
            self.finish_connecting_ui(success=True)

    def stop_vpn_service(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                
                activity = PythonActivity.mActivity
                service_intent = Intent(activity, autoclass('org.test.vpn.MyVpnService'))
                service_intent.setAction("STOP")
                activity.startService(service_intent)
            except Exception as e:
                print(f"Error stopping service: {e}")

        self.disconnect_vpn()

    def disconnect_vpn(self):
        self.is_connected = False
        self.status_label.text = "Status: Disconnected"
        self.btn_action.text = "Connect VPN"
        self.btn_action.background_color = (0.2, 0.6, 1, 1)
        self.country_spinner.disabled = False
        
        self.progress_bar.opacity = 0
        self.progress_label.opacity = 0

    def finish_connecting_ui(self, success):
        self.is_connecting = False
        self.btn_action.disabled = False
        
        if success:
            self.btn_action.text = "Disconnect VPN"
            self.btn_action.background_color = (0.9, 0.2, 0.2, 1)
        else:
            self.btn_action.text = "Connect VPN"
            self.btn_action.background_color = (0.2, 0.6, 1, 1)


if __name__ == '__main__':
    AndroidVPNApp().run()
