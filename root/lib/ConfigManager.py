import btree
import json
import os
import time
from lib.globalMethod import debugPrint

class _MemoryKV:
    def __init__(self):
        self._d = {}

    def __contains__(self, key):
        return key in self._d

    def __getitem__(self, key):
        return self._d[key]

    def __setitem__(self, key, value):
        self._d[key] = value

    def __delitem__(self, key):
        del self._d[key]

    def keys(self):
        return list(self._d.keys())

    def flush(self):
        return

    def close(self):
        return

class ConfigManager:
    """
    配置和狀態管理器 - 使用 btree 實現斷電恢復
    
    設計理念:
    1. startup_config.json: 啟動配置模板 (每次開機加載)
    2. btree 數據庫: 
       - config.* : 從 startup_config 同步的配置 (每次開機更新)
       - state.*  : 運行狀態數據 (持久化,不受 startup_config 影響)
       - user.*   : 用戶自定義數據 (持久化,不受 startup_config 影響)
    
    使用方法:
        cfg = ConfigManager()
        
        # 讀取配置 (每次開機從 startup_config 同步)
        lum = cfg.get('c_lum')
        
        # 修改配置 (不存在會自動創建)
        cfg.set('c_lum', 0.5)
        
        # 讀取狀態 (持久化,斷電保留)
        count = cfg.get_state('run_count', default=0)
        cfg.set_state('run_count', count + 1)
        
        # 直接操作 btree (不存在會自動創建)
        cfg.update('user.custom_key', 'custom_value')
        value = cfg.read('user.custom_key')
        cfg.delete('user.custom_key')
    """
    
    def __init__(self, startup_file='startup_config.json', db_file='config.db'):
        """
        初始化配置管理器
        
        Args:
            startup_file: 啟動配置文件路徑
            db_file: btree 數據庫文件路徑
        """
        self.startup_file = startup_file
        self.db_file = db_file
        self.db = None
        self.f = None
        
        # 打開 btree 數據庫
        self._open_db()
        
        # 加載啟動配置並同步到 btree
        self.startup_config = self._load_startup_config()
        self._sync_config_from_startup()
        
        # 更新啟動計數
        self._update_boot_info()
        
        debugPrint(f"[Config] 配置管理器已就緒")
    
    def _load_startup_config(self):
        """
        加載啟動配置文件
        
        Returns:
            dict: 啟動配置字典
        """
        try:
            with open(self.startup_file, 'r') as f:
                config = json.load(f)
                debugPrint(f"[Config] ✓ 已加載啟動配置: {self.startup_file}")
                return config
        except OSError:
            debugPrint(f"[Config] ⚠ 未找到啟動配置文件 {self.startup_file}, 使用默認配置")
            return self._get_default_config()
        except Exception as e:
            debugPrint(f"[Config] ✗ 加載配置出錯: {e}, 使用默認配置")
            return self._get_default_config()
    
    def _get_default_config(self):
        """
        獲取默認配置
        
        Returns:
            dict: 默認配置字典
        """
        return {
            "c_lum": 1.0,
            "LED_IO": {
                "enable": 1,
                "GPIO": [9]
            },
            "UART_IO": {
                "enable": 1,
                "baudrate": 115200,
                "GPIO": {"tx": 1, "rx": 2}
            },
            "i2c_IO": {
                "enable": 0,
                "i2c_List": []
            },
            "i2s_IO": {
                "enable": 0,
                "sampling_rate": 16000,
                "sample_bits": 16,
                "buffer_frames": 1024,
                "channel_to_use": 1,
                "i2s_List": []
            },
            "RGB_IO": {
                "enable": 0,
                "GPIO": []
            }
        }
    
    def _open_db(self):
        """打開 btree 數據庫"""
        def _open_file_rw():
            try:
                return open(self.db_file, 'r+b')
            except OSError:
                return open(self.db_file, 'w+b')

        try:
            self.f = _open_file_rw()
            try:
                self.db = btree.open(self.f)
                debugPrint(f"[Config] ✓ 數據庫已打開: {self.db_file}")
                return
            except OSError as e:
                debugPrint(f"[Config] ⚠ 數據庫打開失敗: {e}, 嘗試重建 {self.db_file}")
                try:
                    self.f.close()
                except:
                    pass

                try:
                    os.remove(self.db_file)
                except:
                    pass

                self.f = open(self.db_file, 'w+b')
                self.db = btree.open(self.f)
                debugPrint(f"[Config] ✓ 數據庫已重建並打開: {self.db_file}")
                return
        except Exception as e:
            debugPrint(f"[Config] ✗ 數據庫不可用: {e}, 改用記憶體模式")
            try:
                if self.f:
                    self.f.close()
            except:
                pass
            self.f = None
            self.db = _MemoryKV()
    
    def _sync_config_from_startup(self):
        """
        從啟動配置同步到 btree (每次開機執行)
        會覆蓋所有 config.* 的鍵,但保留 state.* 和 user.* 的鍵
        """
        debugPrint("[Config] 🔄 正在同步啟動配置到數據庫...")
        
        # 記錄同步時間
        sync_time = time.time()
        
        # 刪除所有舊的 config.* 鍵
        keys_to_delete = []
        for key_bytes in self.db.keys():
            key = key_bytes.decode()
            if key.startswith('config.'):
                keys_to_delete.append(key_bytes)
        
        for key_bytes in keys_to_delete:
            del self.db[key_bytes]
        
        if keys_to_delete:
            debugPrint(f"[Config]   已清除 {len(keys_to_delete)} 個舊配置項")
        
        # 將啟動配置扁平化並保存
        count = self._flatten_and_save(self.startup_config, prefix='config')
        
        # 保存同步元數據
        self._write_raw('_meta.last_sync_time', sync_time, auto_flush=False)
        self._write_raw('_meta.config_version', 1, auto_flush=False)
        
        # 提交更改
        self.db.flush()
        
        debugPrint(f"[Config] ✓ 已同步 {count} 個配置項")
    
    def _flatten_and_save(self, data, prefix='', count=0):
        """
        將嵌套字典扁平化並保存到 btree
        
        Args:
            data: 要保存的數據 (可以是字典或其他類型)
            prefix: 鍵的前綴
            count: 計數器
            
        Returns:
            int: 保存的項目數量
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                count = self._flatten_and_save(value, new_prefix, count)
        else:
            # 將值轉換為 JSON 字符串並編碼
            key_bytes = prefix.encode()
            value_bytes = json.dumps(data).encode()
            self.db[key_bytes] = value_bytes
            count += 1
        
        return count
    
    def _update_boot_info(self):
        """更新啟動信息"""
        # 更新啟動次數
        boot_count = self.get_state('boot_count', default=0)
        self.set_state('boot_count', boot_count + 1, auto_flush=False)
        
        # 記錄上次啟動時間
        last_boot_time = self.get_state('last_boot_time', default=0)
        current_time = time.time()
        self.set_state('last_boot_time', current_time, auto_flush=False)
        
        # 記錄啟動間隔
        if last_boot_time > 0:
            boot_interval = current_time - last_boot_time
            self.set_state('last_boot_interval', boot_interval, auto_flush=False)
        
        self.db.flush()
        
        debugPrint(f"[Config] 📊 啟動次數: {boot_count + 1}")
    
    # ========================================
    # 底層讀寫方法 (內部使用)
    # ========================================
    
    def _write_raw(self, key, value, auto_flush=True):
        """
        直接寫入 btree (內部方法,不做任何檢查)
        
        Args:
            key: 鍵名 (字符串)
            value: 值
            auto_flush: 是否立即寫入磁盤
        """
        key_bytes = key.encode()
        value_bytes = json.dumps(value).encode()
        self.db[key_bytes] = value_bytes
        
        if auto_flush:
            self.db.flush()
    
    # ========================================
    # CRUD 操作 - 直接操作 btree
    # ========================================
    
    def create(self, key, value, auto_flush=True, overwrite=False):
        """
        創建新的鍵值對
        
        Args:
            key: 鍵名 (字符串)
            value: 值 (任意 JSON 可序列化的類型)
            auto_flush: 是否立即寫入磁盤
            overwrite: 如果鍵已存在是否覆蓋 (默認 False)
            
        Returns:
            bool: 創建成功返回 True
            
        Raises:
            KeyError: 如果鍵已存在且 overwrite=False
        """
        key_bytes = key.encode()
        
        # 檢查鍵是否已存在
        if key_bytes in self.db and not overwrite:
            raise KeyError(f"鍵 '{key}' 已存在,使用 update() 或設置 overwrite=True")
        
        # 創建新鍵
        value_bytes = json.dumps(value).encode()
        self.db[key_bytes] = value_bytes
        
        if auto_flush:
            self.db.flush()
        
        action = "已覆蓋" if (key_bytes in self.db and overwrite) else "已創建"
        debugPrint(f"[Config] ✓ {action}: {key} = {value}")
        return True
    
    def read(self, key, default=None):
        """
        讀取鍵的值
        
        Args:
            key: 鍵名 (字符串)
            default: 默認值 (當鍵不存在時返回)
            
        Returns:
            鍵的值或默認值
        """
        key_bytes = key.encode()
        
        try:
            value_bytes = self.db[key_bytes]
            return json.loads(value_bytes.decode())
        except KeyError:
            return default
        except Exception as e:
            debugPrint(f"[Config] ✗ 讀取 '{key}' 出錯: {e}")
            return default
    
    def update(self, key, value, auto_flush=True):
        """
        更新鍵的值 (如果鍵不存在則自動創建)
        
        Args:
            key: 鍵名 (字符串)
            value: 新值
            auto_flush: 是否立即寫入磁盤
            
        Returns:
            bool: 更新成功返回 True
        """
        key_bytes = key.encode()
        
        # 檢查鍵是否存在
        is_new = key_bytes not in self.db
        
        # 寫入值 (不存在會自動創建)
        value_bytes = json.dumps(value).encode()
        self.db[key_bytes] = value_bytes
        
        if auto_flush:
            self.db.flush()
        
        # 提示信息
        if is_new:
            debugPrint(f"[Config] ✓ 已創建: {key} = {value}")
        else:
            debugPrint(f"[Config] ✓ 已更新: {key} = {value}")
        
        return True
    
    def delete(self, key, auto_flush=True, silent=False):
        """
        刪除鍵值對
        
        Args:
            key: 鍵名 (字符串)
            auto_flush: 是否立即寫入磁盤
            silent: 如果鍵不存在是否靜默 (默認 False 會拋出異常)
            
        Returns:
            bool: 刪除成功返回 True
            
        Raises:
            KeyError: 如果鍵不存在且 silent=False
        """
        key_bytes = key.encode()
        
        if key_bytes not in self.db:
            if silent:
                debugPrint(f"[Config] ⚠ 鍵 '{key}' 不存在,跳過刪除")
                return False
            else:
                raise KeyError(f"鍵 '{key}' 不存在")
        
        # 刪除鍵
        del self.db[key_bytes]
        
        if auto_flush:
            self.db.flush()
        
        debugPrint(f"[Config] ✓ 已刪除: {key}")
        return True
    
    def exists(self, key):
        """
        檢查鍵是否存在
        
        Args:
            key: 鍵名 (字符串)
            
        Returns:
            bool: 存在返回 True
        """
        key_bytes = key.encode()
        return key_bytes in self.db
    
    def keys(self, prefix=None):
        """
        獲取所有鍵的列表
        
        Args:
            prefix: 鍵的前綴 (可選,例如 'state.' 只返回狀態鍵)
            
        Returns:
            list: 鍵名列表
        """
        all_keys = []
        
        for key_bytes in self.db.keys():
            key = key_bytes.decode()
            
            # 過濾前綴
            if prefix is None or key.startswith(prefix):
                all_keys.append(key)
        
        return sorted(all_keys)
    
    def items(self, prefix=None):
        """
        獲取所有鍵值對
        
        Args:
            prefix: 鍵的前綴 (可選)
            
        Returns:
            list: [(key, value), ...] 列表
        """
        all_items = []
        
        for key in self.keys(prefix):
            value = self.read(key)
            all_items.append((key, value))
        
        return all_items
    
    def clear(self, prefix=None, auto_flush=True):
        """
        清除所有鍵值對 (或指定前綴的鍵)
        
        Args:
            prefix: 鍵的前綴 (可選,None 則清除所有)
            auto_flush: 是否立即寫入磁盤
            
        Returns:
            int: 刪除的鍵數量
        """
        keys_to_delete = self.keys(prefix)
        
        for key in keys_to_delete:
            self.delete(key, auto_flush=False, silent=True)
        
        if auto_flush:
            self.db.flush()
        
        debugPrint(f"[Config] ✓ 已清除 {len(keys_to_delete)} 個鍵 (前綴: {prefix or '全部'})")
        return len(keys_to_delete)
    
    # ========================================
    # 便捷方法 - 配置和狀態
    # ========================================
    
    def get(self, key, default=None):
        """
        獲取配置值 (自動添加 config. 前綴)
        
        Args:
            key: 配置鍵 (例如 'c_lum' 或 'LED_IO.enable')
            default: 默認值
            
        Returns:
            配置值或默認值
        """
        full_key = f"config.{key}" if not key.startswith('config.') else key
        return self.read(full_key, default)
    
    def set(self, key, value, auto_flush=True):
        """
        設置配置值 (自動添加 config. 前綴,不存在會自動創建)
        注意: 下次重啟會被 startup_config 覆蓋
        
        Args:
            key: 配置鍵
            value: 配置值
            auto_flush: 是否立即寫入磁盤
        """
        full_key = f"config.{key}" if not key.startswith('config.') else key
        
        # 配置項使用 update (不存在會自動創建)
        is_new = not self.exists(full_key)
        self.update(full_key, value, auto_flush)
        
        if is_new:
            debugPrint(f"[Config] ⚠ 注意: 配置 '{key}' 是新添加的,請考慮更新 startup_config.json")
        else:
            debugPrint(f"[Config] ⚠ 注意: 配置 '{key}' 下次重啟會被 startup_config 覆蓋")
    
    def get_state(self, key, default=None):
        """
        獲取運行狀態值 (自動添加 state. 前綴)
        
        Args:
            key: 狀態鍵 (例如 'boot_count')
            default: 默認值
            
        Returns:
            狀態值或默認值
        """
        full_key = f"state.{key}" if not key.startswith('state.') else key
        return self.read(full_key, default)
    
    def set_state(self, key, value, auto_flush=True):
        """
        設置運行狀態值 (自動添加 state. 前綴,不存在會自動創建)
        狀態值不受 startup_config 影響,斷電保留
        
        Args:
            key: 狀態鍵
            value: 狀態值
            auto_flush: 是否立即寫入磁盤
        """
        full_key = f"state.{key}" if not key.startswith('state.') else key
        
        # 狀態項使用 update (不存在會自動創建)
        self.update(full_key, value, auto_flush)
    
    # ========================================
    # 格式化打印輔助方法
    # ========================================
    
    def _format_dict(self, data, indent=0):
        """
        格式化字典為可讀字符串 (兼容 MicroPython)
        
        Args:
            data: 要格式化的數據
            indent: 縮進級別
            
        Returns:
            str: 格式化後的字符串
        """
        if not isinstance(data, dict):
            return repr(data)
        
        if not data:
            return "{}"
        
        lines = ["{"]
        items = list(data.items())
        
        for i, (key, value) in enumerate(items):
            is_last = (i == len(items) - 1)
            prefix = "  " * (indent + 1)
            
            if isinstance(value, dict):
                # 遞歸格式化嵌套字典
                formatted_value = self._format_dict(value, indent + 1)
                lines.append(f'{prefix}"{key}": {formatted_value}{"" if is_last else ","}')
            elif isinstance(value, list):
                # 格式化列表
                formatted_value = self._format_list(value, indent + 1)
                lines.append(f'{prefix}"{key}": {formatted_value}{"" if is_last else ","}')
            elif isinstance(value, str):
                lines.append(f'{prefix}"{key}": "{value}"{"" if is_last else ","}')
            else:
                lines.append(f'{prefix}"{key}": {value}{"" if is_last else ","}')
        
        lines.append("  " * indent + "}")
        return "\n".join(lines)
    
    def _format_list(self, data, indent=0):
        """
        格式化列表為可讀字符串
        
        Args:
            data: 要格式化的列表
            indent: 縮進級別
            
        Returns:
            str: 格式化後的字符串
        """
        if not data:
            return "[]"
        
        # 簡單列表單行顯示
        if all(not isinstance(item, (dict, list)) for item in data):
            formatted_items = []
            for item in data:
                if isinstance(item, str):
                    formatted_items.append(f'"{item}"')
                else:
                    formatted_items.append(str(item))
            return "[" + ", ".join(formatted_items) + "]"
        
        # 複雜列表多行顯示
        lines = ["["]
        for i, item in enumerate(data):
            is_last = (i == len(data) - 1)
            prefix = "  " * (indent + 1)
            
            if isinstance(item, dict):
                formatted_item = self._format_dict(item, indent + 1)
                lines.append(f'{prefix}{formatted_item}{"" if is_last else ","}')
            elif isinstance(item, list):
                formatted_item = self._format_list(item, indent + 1)
                lines.append(f'{prefix}{formatted_item}{"" if is_last else ","}')
            elif isinstance(item, str):
                lines.append(f'{prefix}"{item}"{"" if is_last else ","}')
            else:
                lines.append(f'{prefix}{item}{"" if is_last else ","}')
        
        lines.append("  " * indent + "]")
        return "\n".join(lines)
    
    # ========================================
    # 高級功能
    # ========================================
    
    def get_all_config(self):
        """
        獲取所有配置 (重建嵌套字典)
        
        Returns:
            dict: 完整配置字典
        """
        config = {}
        
        for key in self.keys('config.'):
            # 去掉 'config.' 前綴
            short_key = key[7:]
            
            # 獲取值
            value = self.read(key)
            
            # 重建嵌套結構
            self._set_nested(config, short_key.split('.'), value)
        
        return config
    
    def get_all_state(self):
        """
        獲取所有運行狀態
        
        Returns:
            dict: 完整狀態字典
        """
        state = {}
        
        for key in self.keys('state.'):
            # 去掉 'state.' 前綴
            short_key = key[6:]
            value = self.read(key)
            state[short_key] = value
        
        return state
    
    def _set_nested(self, dic, keys, value):
        """
        設置嵌套字典的值
        
        Args:
            dic: 字典
            keys: 鍵列表 ['LED_IO', 'enable']
            value: 值
        """
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys[-1]] = value
    
    def save_to_startup(self, backup=True):
        """
        將當前配置保存為啟動配置
        
        Args:
            backup: 是否備份原文件
        """
        config = self.get_all_config()
        
        try:
            # 備份原文件
            if backup:
                try:
                    # 檢查文件是否存在
                    files = os.listdir()
                    if self.startup_file in files:
                        backup_file = f"{self.startup_file}.bak"
                        # 刪除舊備份
                        try:
                            os.remove(backup_file)
                        except:
                            pass
                        os.rename(self.startup_file, backup_file)
                        debugPrint(f"[Config] ✓ 已備份到: {backup_file}")
                except Exception as e:
                    debugPrint(f"[Config] ⚠ 備份失敗: {e}")
            
            # 保存新配置 (使用自定義格式化)
            with open(self.startup_file, 'w') as f:
                f.write(self._format_dict(config))
            
            debugPrint(f"[Config] ✓ 已保存當前配置到: {self.startup_file}")
        except Exception as e:
            debugPrint(f"[Config] ✗ 保存啟動配置失敗: {e}")
    
    def debugPrint_info(self, show_config=True, show_state=True, show_user=True, show_meta=True):
        """
        打印配置和狀態信息
        
        Args:
            show_config: 是否顯示配置
            show_state: 是否顯示狀態
            show_user: 是否顯示用戶數據
            show_meta: 是否顯示元數據
        """
        debugPrint("\n" + "="*70)
        debugPrint("⚙️  配置管理器信息")
        debugPrint("="*70)
        
        # 配置信息
        if show_config:
            config = self.get_all_config()
            debugPrint("\n📋 當前配置 (config.*):")
            # 使用自定義格式化方法
            debugPrint(self._format_dict(config))
        
        # 狀態信息
        if show_state:
            state = self.get_all_state()
            if state:
                debugPrint("\n📊 運行狀態 (state.*):")
                for key, value in state.items():
                    debugPrint(f"  {key}: {value}")
        
        # 用戶數據
        if show_user:
            user_items = self.items('user.')
            if user_items:
                debugPrint("\n👤 用戶數據 (user.*):")
                for key, value in user_items:
                    short_key = key[5:]  # 去掉 'user.' 前綴
                    debugPrint(f"  {short_key}: {value}")
        
        # 元數據
        if show_meta:
            meta_items = self.items('_meta.')
            if meta_items:
                debugPrint("\n🔍 元數據 (_meta.*):")
                for key, value in meta_items:
                    short_key = key[6:]  # 去掉 '_meta.' 前綴
                    debugPrint(f"  {short_key}: {value}")
        
        # 統計信息
        debugPrint("\n📈 統計:")
        debugPrint(f"  總鍵數: {len(self.keys())}")
        debugPrint(f"  配置項: {len(self.keys('config.'))}")
        debugPrint(f"  狀態項: {len(self.keys('state.'))}")
        debugPrint(f"  用戶項: {len(self.keys('user.'))}")
        
        debugPrint("="*70 + "\n")
    
    def close(self):
        """關閉數據庫"""
        if self.db:
            self.db.flush()
            self.db.close()
            debugPrint("[Config] ✓ 數據庫已關閉")
        
        if self.f:
            self.f.close()
    
    def __enter__(self):
        """支持 with 語句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 語句"""
        self.close()
