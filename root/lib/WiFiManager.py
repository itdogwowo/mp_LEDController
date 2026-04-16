import network
import time
import json
import os
from lib.globalMethod import debugPrint

class WiFiManager:
    """
    WiFi 管理類 - 自動連接或創建熱點,支持 mDNS 服務發現
    
    使用方法:
        network_config = {
            "enable": 1,
            "pcName": "myesp32",
            "ssid": "YourWiFi",
            "password": "YourPassword"
        }
        wifi = WiFiManager(config_dict=network_config)
        wifi.connect()
    """
    
    def __init__(self, config_dict=None, config_file=None, hostname=None, max_retries=3):
        """
        初始化 WiFi 管理器
        
        Args:
            config_dict: 配置字典 (優先使用)
            config_file: WiFi 配置文件路徑 (當 config_dict 為 None 時使用)
            hostname: mDNS 主機名 (可選,優先從配置中讀取)
            max_retries: 最大重試次數 (默認10次)
        """
        self.sta = None
        self.ap = None
        self.is_ap_mode = False
        self.mdns = None
        self.max_retries = max_retries
        
        # 加載配置
        if config_dict is not None:
            # 使用傳入的字典配置
            self.config = self._parse_config_dict(config_dict)
            self.config_file = None
            debugPrint("[WiFi] 使用外部配置字典")
        else:
            # 使用配置文件
            self.config_file = config_file or 'wifi_config.json'
            self.config = self._load_config()
            debugPrint(f"[WiFi] 使用配置文件: {self.config_file}")
        
        # 設置主機名 (優先級: 參數 > 配置 > 默認值)
        self.hostname = (
            hostname or 
            self.config.get('network', {}).get('pcName') or 
            self.config.get('hostname', 'esp32')
        )
        
        debugPrint(f"[WiFi] 主機名: {self.hostname}")
        debugPrint(f"[WiFi] 最大重試次數: {self.max_retries}")

        if self.is_enabled():
            self._get_sta()

    def _get_sta(self):
        if self.sta is not None:
            return self.sta

        try:
            self.sta = network.WLAN(network.STA_IF)
            return self.sta
        except OSError as e:
            debugPrint(f"[WiFi] STA 初始化失敗: {e}")
            self.sta = None
            return None

    def _get_ap(self):
        if self.ap is not None:
            return self.ap

        try:
            self.ap = network.WLAN(network.AP_IF)
            return self.ap
        except OSError as e:
            debugPrint(f"[WiFi] AP 初始化失敗: {e}")
            self.ap = None
            return None
    
    def _parse_config_dict(self, network_config):
        """
        解析你的配置格式,轉換為內部標準格式
        
        Args:
            network_config: 你的 Network 配置字典
            
        Returns:
            dict: 標準化的配置字典
        """
        # 檢查是否啟用網絡
        enabled = network_config.get('enable', 0)
        
        # 轉換為標準格式
        standard_config = {
            'network': {
                'enabled': bool(enabled),
                'pcName': network_config.get('pcName', 'esp32'),
                'ssid': network_config.get('ssid', '00'),
                'password': network_config.get('password', '00')
            },
            'sta': {
                'ssid': network_config.get('ssid', '00'),
                'password': network_config.get('password', '00'),
                'timeout': network_config.get('timeout', 15)
            },
            'ap': {
                'ssid': f"{network_config.get('pcName', 'ESP32')}-AP",
                'password': '12345678',
                'authmode': 3,
                'channel': 11,
                'hidden': False
            },
            'mdns': {
                'enabled': True,
                'services': [
                    {
                        'type': '_http',
                        'protocol': '_tcp',
                        'port': 80,
                        'txt': 'path=/'
                    }
                ]
            }
        }
        
        return standard_config
    
    def _load_config(self):
        """
        從配置文件加載 WiFi 設置
        如果文件不存在,使用默認配置
        """
        default_config = {
            'network': {
                'enabled': True,
                'pcName': 'esp32',
                'ssid': 'YourWiFiSSID',
                'password': 'YourPassword'
            },
            'sta': {
                'ssid': 'YourWiFiSSID',
                'password': 'YourPassword',
                'timeout': 15
            },
            'ap': {
                'ssid': 'ESP32-AP',
                'password': '12345678',
                'authmode': 3,
                'channel': 11,
                'hidden': False
            },
            'mdns': {
                'enabled': True,
                'services': [
                    {
                        'type': '_http',
                        'protocol': '_tcp',
                        'port': 80,
                        'txt': 'path=/'
                    }
                ]
            }
        }
        
        try:
            if self.config_file in os.listdir():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    debugPrint(f"[WiFi] 已加載配置文件: {self.config_file}")
                    return config
            else:
                debugPrint(f"[WiFi] 配置文件不存在,使用默認配置")
                self._save_config(default_config)
                return default_config
        except Exception as e:
            debugPrint(f"[WiFi] 加載配置出錯: {e}, 使用默認配置")
            return default_config
    
    def _save_config(self, config):
        """保存配置到文件"""
        if self.config_file is None:
            debugPrint("[WiFi] 使用外部配置,不保存到文件")
            return
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            debugPrint(f"[WiFi] 配置已保存到: {self.config_file}")
        except Exception as e:
            debugPrint(f"[WiFi] 保存配置失敗: {e}")
    
    def is_enabled(self):
        """
        檢查網絡功能是否啟用
        
        Returns:
            bool: 啟用返回 True
        """
        return self.config.get('network', {}).get('enabled', True)
    
    def _setup_mdns(self):
        """
        設置 mDNS 服務
        使設備可以通過 hostname.local 訪問
        """
        if not self.config.get('mdns', {}).get('enabled', True):
            debugPrint("[mDNS] mDNS 功能已禁用")
            return False
        
        try:
            import mdns
            
            # 創建 mDNS 實例
            if self.mdns is None:
                self.mdns = mdns.MDNSResponder()
            
            # 設置主機名
            self.mdns.start(self.hostname, "MicroPython Device")
            debugPrint(f"[mDNS] 已啟動,主機名: {self.hostname}.local")
            
            # 註冊服務
            services = self.config.get('mdns', {}).get('services', [])
            for service in services:
                try:
                    service_type = service.get('type', '_http')
                    protocol = service.get('protocol', '_tcp')
                    port = service.get('port', 80)
                    txt = service.get('txt', '')
                    
                    # 註冊服務
                    self.mdns.advertise_service(
                        service_type,
                        protocol,
                        port,
                        txt
                    )
                    debugPrint(f"[mDNS] 已註冊服務: {service_type}.{protocol} (端口 {port})")
                except Exception as e:
                    debugPrint(f"[mDNS] 註冊服務失敗: {e}")
            
            return True
            
        except ImportError:
            debugPrint("[mDNS] 警告: mdns 模塊不可用")
            debugPrint("[mDNS] 嘗試使用備用方案...")
            return self._setup_mdns_fallback()
        except Exception as e:
            debugPrint(f"[mDNS] 啟動失敗: {e}")
            return False
    
    def _setup_mdns_fallback(self):
        """
        mDNS 備用方案 (適用於某些固件版本)
        使用 network 模塊的 hostname 功能
        """
        try:
            # 設置網絡接口的主機名
            if self.is_ap_mode:
                ap = self._get_ap()
                if ap is None:
                    return False
                ap.config(dhcp_hostname=self.hostname)
                debugPrint(f"[mDNS] AP 模式主機名設置為: {self.hostname}")
            else:
                sta = self._get_sta()
                if sta is None:
                    return False
                sta.config(dhcp_hostname=self.hostname)
                debugPrint(f"[mDNS] STA 模式主機名設置為: {self.hostname}.local")
            
            return True
        except Exception as e:
            debugPrint(f"[mDNS] 備用方案也失敗: {e}")
            debugPrint(f"[mDNS] 只能通過 IP 訪問設備")
            return False
    
    def _stop_mdns(self):
        """停止 mDNS 服務"""
        if self.mdns:
            try:
                self.mdns.stop()
                debugPrint("[mDNS] 服務已停止")
            except Exception as e:
                debugPrint(f"[mDNS] 停止服務時出錯: {e}")
    
    def scan_and_display_networks(self, target_ssid=None):
        """
        掃描並顯示周圍的 WiFi 網絡
        
        Args:
            target_ssid: 目標 SSID (可選,會特別標註)
            
        Returns:
            tuple: (所有網絡列表, 是否找到目標網絡)
        """
        if not self.is_enabled():
            debugPrint("[WiFi] 網絡功能已禁用 (enable=0),跳過掃描")
            return [], False

        sta = self._get_sta()
        if sta is None:
            return [], False

        if not sta.active():
            sta.active(True)
            time.sleep(0.5)
        
        debugPrint("\n" + "="*60)
        debugPrint("📡 正在掃描周圍的 WiFi 網絡...")
        debugPrint("="*60)
        
        try:
            networks = sta.scan()
            
            if not networks:
                debugPrint("⚠️  未找到任何 WiFi 網絡")
                return [], False
            
            debugPrint(f"✓ 找到 {len(networks)} 個 WiFi 網絡:\n")
            
            # 按信號強度排序
            networks_sorted = sorted(networks, key=lambda x: x[3], reverse=True)
            
            target_found = False
            
            # 表頭
            debugPrint(f"{'序號':<4} {'SSID':<25} {'信號強度':<12} {'頻道':<6} {'加密':<8} {'標記'}")
            debugPrint("-" * 60)
            
            for i, net in enumerate(networks_sorted, 1):
                ssid = net[0].decode('utf-8') if net[0] else '<隱藏網絡>'
                bssid = net[1]
                channel = net[2]
                rssi = net[3]
                authmode = net[4]
                hidden = net[5]
                
                # 信號強度評估
                if rssi >= -50:
                    signal_bars = "▂▄▆█"
                    signal_text = "優秀"
                elif rssi >= -60:
                    signal_bars = "▂▄▆"
                    signal_text = "良好"
                elif rssi >= -70:
                    signal_bars = "▂▄"
                    signal_text = "一般"
                else:
                    signal_bars = "▂"
                    signal_text = "較弱"
                
                # 加密類型
                auth_types = {
                    0: "開放",
                    1: "WEP",
                    2: "WPA-PSK",
                    3: "WPA2-PSK",
                    4: "WPA/WPA2",
                    5: "WPA2-ENT"
                }
                auth_text = auth_types.get(authmode, "未知")
                
                # 特殊標記
                marker = ""
                if target_ssid and ssid == target_ssid:
                    marker = "👈 目標網絡"
                    target_found = True
                elif hidden:
                    marker = "🔒 隱藏"
                
                # 打印網絡信息
                signal_display = f"{signal_bars} {rssi}dBm"
                debugPrint(f"{i:<4} {ssid:<25} {signal_display:<12} {channel:<6} {auth_text:<8} {marker}")
            
            debugPrint("="*60 + "\n")
            
            # 如果指定了目標 SSID,顯示結果
            if target_ssid:
                if target_found:
                    debugPrint(f"✓ 找到目標網絡: {target_ssid}")
                else:
                    debugPrint(f"✗ 未找到目標網絡: {target_ssid}")
                    debugPrint(f"  請檢查 SSID 是否正確或網絡是否在範圍內")
            
            return networks_sorted, target_found
            
        except Exception as e:
            debugPrint(f"⚠️  掃描網絡時出錯: {e}")
            return [], False
    
    def connect_sta(self, ssid=None, password=None, timeout=None, show_scan=True):
        """
        連接到 WiFi (STA 模式) - 支持多次重試
        
        Args:
            ssid: WiFi 名稱 (可選,默認使用配置)
            password: WiFi 密碼 (可選)
            timeout: 單次連接超時時間(秒) (可選)
            show_scan: 是否在連接前掃描並顯示網絡 (默認True)
            
        Returns:
            bool: 連接成功返回 True, 失敗返回 False
        """
        if not self.is_enabled():
            debugPrint("[WiFi] 網絡功能已禁用 (enable=0),跳過 STA 連接")
            self.disconnect()
            return False

        debugPrint("[WiFi] 連接用戶wi-fi")
        sta = self._get_sta()
        if sta is None:
            return False

        # 使用傳入參數或配置中的值
        ssid = ssid or self.config['sta']['ssid']
        password = password or self.config['sta']['password']
        timeout = timeout or self.config['sta']['timeout']

        debugPrint(f"\n[WiFi] 準備連接到: {ssid}")

        # 停止 mDNS (如果正在運行)
        self._stop_mdns()

        # 關閉 AP 模式
        ap = self.ap
        if ap is not None and ap.active():
            ap.active(False)
            debugPrint("[WiFi] 已關閉 AP 模式")

        # 啟動 STA 模式
        if not sta.active():
            sta.active(True)
            time.sleep(0.5)

        # 掃描網絡 (可選)
        target_found = False
        if show_scan:
            _, target_found = self.scan_and_display_networks(target_ssid=ssid)

        # 設置主機名 (在連接前)
        try:
            sta.config(dhcp_hostname=self.hostname)
        except:
            pass

        # 如果已經連接,先斷開
        if sta.isconnected():
            sta.disconnect()
            time.sleep(1)

        # 開始重試連接
        debugPrint(f"\n[WiFi] 開始連接嘗試 (最多 {self.max_retries} 次)...")
        debugPrint("="*60)

        for attempt in range(1, self.max_retries + 1):
            debugPrint(f"\n🔄 第 {attempt}/{self.max_retries} 次嘗試連接到: {ssid}")

            # 開始連接
            try:
                sta.connect(ssid, password)
            except Exception as e:
                debugPrint(f"  ✗ 連接命令執行失敗: {e}")
                time.sleep(2)
                continue

            # 等待連接
            start_time = time.time()
            dots = 0
            while not sta.isconnected():
                elapsed = time.time() - start_time

                if elapsed > timeout:
                    debugPrint(f"\n  ✗ 連接超時 ({timeout}秒)")
                    break

                # 每秒打印一個點
                if int(elapsed) > dots:
                    debugPrint(".", end="", flush=True)
                    dots = int(elapsed)

                time.sleep(0.1)

            # 檢查連接結果
            if sta.isconnected():
                debugPrint(f"\n  ✓ 連接成功! (用時 {time.time() - start_time:.1f} 秒)")
                debugPrint("="*60)
                self.is_ap_mode = False

                # 啟動 mDNS
                time.sleep(1)
                self._setup_mdns()

                return True
            else:
                # 連接失敗,斷開並準備重試
                try:
                    sta.disconnect()
                except:
                    pass

                # 最後一次嘗試不需要等待
                if attempt < self.max_retries:
                    wait_time = min(2 * attempt, 10)  # 遞增等待時間,最多10秒
                    debugPrint(f"  ⏳ 等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)

        # 所有嘗試都失敗
        debugPrint(f"\n✗ 連接失敗: 已嘗試 {self.max_retries} 次")
        debugPrint("="*60)

        # 提供建議
        debugPrint("\n💡 建議檢查:")
        debugPrint("  1. SSID 是否正確 (區分大小寫)")
        debugPrint("  2. 密碼是否正確")
        debugPrint("  3. WiFi 路由器是否正常工作")
        debugPrint("  4. 設備是否在 WiFi 覆蓋範圍內")
        if show_scan and not target_found:
            debugPrint(f"  5. 目標網絡 '{ssid}' 未在掃描列表中,可能不在範圍內\n")

        return False
            
    
    def create_ap(self, ssid=None, password=None):
        """
        創建 WiFi 熱點 (AP 模式)
        
        Args:
            ssid: 熱點名稱 (可選)
            password: 熱點密碼 (可選)
            
        Returns:
            bool: 創建成功返回 True
        """
        if not self.is_enabled():
            debugPrint("[WiFi] 網絡功能已禁用 (enable=0),跳過 AP 建立")
            self.disconnect()
            return False

        ap = self._get_ap()
        if ap is None:
            return False

        # 使用傳入參數或配置中的值
        ap_config = self.config['ap']
        ssid = ssid or ap_config['ssid']
        password = password or ap_config['password']
        
        debugPrint(f"\n[WiFi] 創建 AP 熱點: {ssid}")
        
        # 停止 mDNS (如果正在運行)
        self._stop_mdns()
        
        # 關閉 STA 模式
        sta = self.sta
        if sta is not None and sta.active():
            sta.active(False)
            debugPrint("[WiFi] 已關閉 STA 模式")
        
        # 啟動 AP 模式
        if not ap.active():
            ap.active(True)
        
        # 配置 AP
        ap.config(
            essid=ssid,
            password=password,
            authmode=ap_config['authmode'],
            channel=ap_config['channel'],
            hidden=ap_config['hidden']
        )
        
        # 設置主機名
        try:
            ap.config(dhcp_hostname=self.hostname)
        except:
            pass
        
        # 等待 AP 啟動
        time.sleep(1)
        
        debugPrint("[WiFi] ✓ AP 模式已啟動!")
        self.is_ap_mode = True
        
        # 啟動 mDNS (AP 模式下可能不支持,但嘗試一下)
        self._setup_mdns()
        
        return True
    
    def connect(self, force_ap=False, show_scan=True):
        """
        智能連接: 優先連接 WiFi, 失敗則創建 AP
        
        Args:
            force_ap: 強制使用 AP 模式
            show_scan: 是否在連接前掃描網絡
            
        Returns:
            bool: 是否成功建立連接
        """
        if not self.is_enabled():
            debugPrint("[WiFi] 網絡功能已禁用 (enable=0),跳過連接")
            self.disconnect()
            return False
        
        if force_ap:
            debugPrint("[WiFi] 強制啟用 AP 模式")
            return self.create_ap()
        
        # 嘗試連接 WiFi
        if self.connect_sta(show_scan=show_scan):
            return True
        
        # WiFi 連接失敗,切換到 AP 模式
        debugPrint("\n[WiFi] STA 模式連接失敗,切換到 AP 模式")
        return self.create_ap()
    
    def disconnect(self):
        """斷開所有連接"""
        # 停止 mDNS
        self._stop_mdns()
        
        if self.sta is not None and self.sta.active():
            self.sta.disconnect()
            self.sta.active(False)
            debugPrint("[WiFi] STA 模式已關閉")
        
        if self.ap is not None and self.ap.active():
            self.ap.active(False)
            debugPrint("[WiFi] AP 模式已關閉")

        self.is_ap_mode = False
    
    def get_connection_info(self):
        """
        獲取當前連接信息
        
        Returns:
            dict: 包含連接狀態的字典
        """
        info = {
            'mode': 'AP' if self.is_ap_mode else 'STA',
            'enabled': self.is_enabled(),
            'connected': False,
            'ip': None,
            'netmask': None,
            'gateway': None,
            'dns': None,
            'mac': None,
            'ssid': None,
            'hostname': self.hostname,
            'mdns_name': f"{self.hostname}.local"
        }
        
        if self.is_ap_mode and self.ap is not None and self.ap.active():
            # AP 模式信息
            info['connected'] = True
            ifconfig = self.ap.ifconfig()
            info['ip'] = ifconfig[0]
            info['netmask'] = ifconfig[1]
            info['gateway'] = ifconfig[2]
            info['dns'] = ifconfig[3]
            info['mac'] = self._mac_to_str(self.ap.config('mac'))
            info['ssid'] = self.config['ap']['ssid']
            
        elif not self.is_ap_mode and self.sta is not None and self.sta.active() and self.sta.isconnected():
            # STA 模式信息
            info['connected'] = True
            ifconfig = self.sta.ifconfig()
            info['ip'] = ifconfig[0]
            info['netmask'] = ifconfig[1]
            info['gateway'] = ifconfig[2]
            info['dns'] = ifconfig[3]
            info['mac'] = self._mac_to_str(self.sta.config('mac'))
            info['ssid'] = self.config['sta']['ssid']
        
        return info
    
    def _mac_to_str(self, mac_bytes):
        """將 MAC 地址字節轉換為字符串"""
        return ':'.join(['%02X' % b for b in mac_bytes])
    
    def debugPrint_info(self):
        """打印連接信息 (便於調試)"""
        info = self.get_connection_info()
        debugPrint("\n" + "="*60)
        debugPrint(f"🌐 WiFi 連接信息")
        debugPrint("="*60)
        debugPrint(f"網絡功能: {'✓ 啟用' if info['enabled'] else '✗ 禁用'}")
        debugPrint(f"WiFi 模式: {info['mode']}")
        debugPrint(f"連接狀態: {'✓ 已連接' if info['connected'] else '✗ 未連接'}")
        if info['connected']:
            debugPrint(f"\nSSID: {info['ssid']}")
            debugPrint(f"IP 地址: {info['ip']}")
            debugPrint(f"mDNS 名稱: {info['mdns_name']}")
            debugPrint(f"主機名: {info['hostname']}")
            debugPrint(f"子網掩碼: {info['netmask']}")
            debugPrint(f"網關: {info['gateway']}")
            debugPrint(f"DNS: {info['dns']}")
            debugPrint(f"MAC 地址: {info['mac']}")
            debugPrint(f"\n📱 訪問方式:")
            debugPrint(f"  • http://{info['ip']}")
            debugPrint(f"  • http://{info['mdns_name']}")
            debugPrint(f"  • ping {info['mdns_name']}")
        debugPrint("="*60 + "\n")
    
    def scan_networks(self, show_details=True):
        """
        掃描周圍的 WiFi 網絡 (簡化版)
        
        Args:
            show_details: 是否顯示詳細信息
            
        Returns:
            list: WiFi 網絡列表
        """
        if not self.is_enabled():
            debugPrint("[WiFi] 網絡功能已禁用 (enable=0),跳過掃描")
            return []

        networks, _ = self.scan_and_display_networks()
        return networks
    
    def add_service(self, service_type, protocol, port, txt=''):
        """
        動態添加 mDNS 服務
        
        Args:
            service_type: 服務類型 (如 '_http', '_ftp')
            protocol: 協議 (如 '_tcp', '_udp')
            port: 端口號
            txt: TXT 記錄 (可選)
        """
        if self.mdns:
            try:
                self.mdns.advertise_service(service_type, protocol, port, txt)
                debugPrint(f"[mDNS] 已添加服務: {service_type}.{protocol}:{port}")
            except Exception as e:
                debugPrint(f"[mDNS] 添加服務失敗: {e}")
        else:
            debugPrint("[mDNS] mDNS 未啟動,無法添加服務")
