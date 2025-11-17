好的!我來寫一個詳細的使用手冊和範例。

# ConfigManager 使用手冊

## 📚 目錄

1. [快速開始](#快速開始)
2. [核心概念](#核心概念)
3. [基礎操作](#基礎操作)
4. [進階功能](#進階功能)
5. [完整範例](#完整範例)
6. [常見問題](#常見問題)

---

## 🚀 快速開始

### 安裝

將 `config_manager.py` 複製到你的 MicroPython 設備中。

### 最簡單的使用

```python
from config_manager import ConfigManager

# 創建配置管理器
with ConfigManager() as cfg:
    # 讀取配置
    brightness = cfg.get('c_lum')
    print(f"當前亮度: {brightness}")
    
    # 修改配置
    cfg.set('c_lum', 0.8)
    
    # 查看所有配置
    cfg.print_info()
```

---

## 💡 核心概念

### 數據分類

ConfigManager 將數據分為三類:

| 類型 | 前綴 | 用途 | 持久化 | 受 startup_config 影響 |
|------|------|------|--------|----------------------|
| **配置** | `config.*` | 系統配置項 | ✅ 是 | ✅ 是 (每次開機重置) |
| **狀態** | `state.*` | 運行狀態數據 | ✅ 是 | ❌ 否 (斷電保留) |
| **用戶** | `user.*` | 用戶自定義數據 | ✅ 是 | ❌ 否 (斷電保留) |

### 工作流程

```
開機 → 讀取 startup_config.json → 同步到 btree (覆蓋 config.*)
    → 保留 state.* 和 user.* (斷電恢復)
    → 運行中修改配置 (寫入 btree)
    → 關機 (所有數據自動保存)
下次開機 → config.* 重置, state.* 和 user.* 恢復
```

---

## 📖 基礎操作

### 1. 創建配置管理器

```python
from config_manager import ConfigManager

# 方式 1: 使用 with 語句 (推薦,自動關閉)
with ConfigManager() as cfg:
    # 你的代碼
    pass

# 方式 2: 手動管理
cfg = ConfigManager()
# 你的代碼
cfg.close()  # 記得關閉!

# 方式 3: 自定義文件路徑
with ConfigManager(startup_file='my_config.json', db_file='my_db.db') as cfg:
    pass
```

### 2. 讀取配置

```python
with ConfigManager() as cfg:
    # 讀取配置 (自動添加 config. 前綴)
    brightness = cfg.get('c_lum')
    led_enable = cfg.get('LED_IO.enable')
    
    # 提供默認值
    timeout = cfg.get('timeout', default=30)
    
    # 讀取嵌套配置
    uart_tx = cfg.get('UART_IO.GPIO.tx')
    
    print(f"亮度: {brightness}")
    print(f"LED 啟用: {led_enable}")
    print(f"UART TX: {uart_tx}")
```

### 3. 修改配置

```python
with ConfigManager() as cfg:
    # 修改已有配置
    cfg.set('c_lum', 0.5)
    
    # 添加新配置 (會自動創建)
    cfg.set('night_mode', True)
    
    # 修改嵌套配置
    cfg.set('LED_IO.enable', 0)
    
    # ⚠️ 注意: 這些修改下次重啟會被 startup_config 覆蓋!
```

### 4. 讀寫狀態 (持久化)

```python
with ConfigManager() as cfg:
    # 讀取狀態
    boot_count = cfg.get_state('boot_count', default=0)
    
    # 更新狀態
    cfg.set_state('boot_count', boot_count + 1)
    
    # 記錄運行時間
    cfg.set_state('total_runtime', 12345)
    
    # ✅ 這些數據斷電後依然保留!
```

### 5. 直接操作 btree (CRUD)

```python
with ConfigManager() as cfg:
    # Create - 創建 (鍵存在會報錯)
    try:
        cfg.create('user.name', 'Alice')
    except KeyError:
        print("鍵已存在")
    
    # Read - 讀取
    name = cfg.read('user.name', default='Guest')
    
    # Update - 更新 (不存在會自動創建)
    cfg.update('user.name', 'Bob')
    cfg.update('user.score', 1000)  # 自動創建
    
    # Delete - 刪除
    cfg.delete('user.name')
    
    # 靜默刪除 (不存在不報錯)
    cfg.delete('user.age', silent=True)
    
    # Exists - 檢查存在
    if cfg.exists('user.score'):
        print("分數已記錄")
```

---

## 🔧 進階功能

### 1. 查詢所有鍵

```python
with ConfigManager() as cfg:
    # 獲取所有鍵
    all_keys = cfg.keys()
    print(f"總鍵數: {len(all_keys)}")
    
    # 獲取指定前綴的鍵
    config_keys = cfg.keys('config.')
    state_keys = cfg.keys('state.')
    user_keys = cfg.keys('user.')
    
    print(f"配置鍵: {config_keys}")
```

### 2. 獲取鍵值對

```python
with ConfigManager() as cfg:
    # 獲取所有用戶數據
    user_items = cfg.items('user.')
    
    for key, value in user_items:
        print(f"{key} = {value}")
    
    # 輸出:
    # user.name = Alice
    # user.score = 1000
    # user.level = 5
```

### 3. 批量操作 (性能優化)

```python
with ConfigManager() as cfg:
    # 批量寫入 (延遲 flush 提高性能)
    cfg.update('user.name', 'Alice', auto_flush=False)
    cfg.update('user.age', 25, auto_flush=False)
    cfg.update('user.email', 'alice@example.com', auto_flush=False)
    cfg.update('user.level', 10, auto_flush=False)
    
    # 一次性寫入磁盤
    cfg.db.flush()
    
    print("批量寫入完成!")
```

### 4. 清除數據

```python
with ConfigManager() as cfg:
    # 清除所有用戶數據
    count = cfg.clear('user.')
    print(f"已清除 {count} 個用戶數據")
    
    # 清除所有狀態數據
    cfg.clear('state.')
    
    # 清除所有數據 (危險!)
    # cfg.clear()
```

### 5. 保存配置到啟動文件

```python
with ConfigManager() as cfg:
    # 修改配置
    cfg.set('c_lum', 0.8)
    cfg.set('night_mode', True)
    
    # 保存到 startup_config.json (帶備份)
    cfg.save_to_startup(backup=True)
    
    # 下次重啟會加載這些新配置!
```

### 6. 獲取完整配置字典

```python
with ConfigManager() as cfg:
    # 獲取所有配置 (重建嵌套字典)
    all_config = cfg.get_all_config()
    print(all_config)
    # 輸出: {'c_lum': 1.0, 'LED_IO': {'enable': 1, 'GPIO': [9]}, ...}
    
    # 獲取所有狀態
    all_state = cfg.get_all_state()
    print(all_state)
    # 輸出: {'boot_count': 5, 'total_runtime': 12345, ...}
```

---

## 📝 完整範例

### 範例 1: LED 控制系統

```python
# led_controller.py
from config_manager import ConfigManager
import time
from machine import Pin

def main():
    """LED 控制系統 - 帶斷電恢復功能"""
    
    with ConfigManager() as cfg:
        
        # ========================================
        # 1. 讀取配置
        # ========================================
        print("📋 加載配置...")
        
        led_enable = cfg.get('LED_IO.enable', default=1)
        led_gpio = cfg.get('LED_IO.GPIO', default=[9])
        brightness = cfg.get('c_lum', default=1.0)
        
        if not led_enable:
            print("LED 功能已禁用")
            return
        
        # ========================================
        # 2. 初始化 LED
        # ========================================
        print(f"💡 初始化 LED (GPIO {led_gpio[0]})")
        
        led = Pin(led_gpio[0], Pin.OUT)
        
        # ========================================
        # 3. 恢復上次狀態
        # ========================================
        last_state = cfg.get_state('led.last_state', default=0)
        led.value(last_state)
        
        print(f"🔄 恢復上次狀態: {'開' if last_state else '關'}")
        
        # ========================================
        # 4. 運行計數
        # ========================================
        run_count = cfg.get_state('led.run_count', default=0)
        cfg.set_state('led.run_count', run_count + 1)
        
        print(f"📊 運行次數: {run_count + 1}")
        
        # ========================================
        # 5. 模擬運行
        # ========================================
        print(f"\n⚙️  開始運行 (亮度: {brightness})...")
        
        for i in range(5):
            # 切換 LED
            led.value(not led.value())
            current_state = led.value()
            
            print(f"  LED: {'🟢 開' if current_state else '🔴 關'}")
            
            # 保存當前狀態 (斷電可恢復)
            cfg.set_state('led.last_state', current_state)
            
            time.sleep(1)
        
        # ========================================
        # 6. 記錄運行時間
        # ========================================
        total_runtime = cfg.get_state('led.total_runtime', default=0)
        total_runtime += 5
        cfg.set_state('led.total_runtime', total_runtime)
        
        print(f"\n✓ 運行完成")
        print(f"  累計運行時間: {total_runtime} 秒")
        
        # 關閉 LED
        led.value(0)
        cfg.set_state('led.last_state', 0)

if __name__ == '__main__':
    main()
```

### 範例 2: 用戶系統

```python
# user_system.py
from config_manager import ConfigManager
import time

class UserSystem:
    """用戶系統 - 支持註冊、登入、數據保存"""
    
    def __init__(self):
        self.cfg = ConfigManager()
    
    def register(self, username, password):
        """註冊用戶"""
        user_key = f'user.accounts.{username}'
        
        # 檢查用戶是否已存在
        if self.cfg.exists(f'{user_key}.password'):
            print(f"❌ 用戶 '{username}' 已存在!")
            return False
        
        # 創建用戶
        self.cfg.update(f'{user_key}.password', password, auto_flush=False)
        self.cfg.update(f'{user_key}.created_at', time.time(), auto_flush=False)
        self.cfg.update(f'{user_key}.level', 1, auto_flush=False)
        self.cfg.update(f'{user_key}.score', 0, auto_flush=False)
        self.cfg.update(f'{user_key}.login_count', 0, auto_flush=False)
        self.cfg.db.flush()
        
        print(f"✅ 用戶 '{username}' 註冊成功!")
        return True
    
    def login(self, username, password):
        """登入用戶"""
        user_key = f'user.accounts.{username}'
        
        # 檢查用戶是否存在
        saved_password = self.cfg.read(f'{user_key}.password')
        if saved_password is None:
            print(f"❌ 用戶 '{username}' 不存在!")
            return False
        
        # 驗證密碼
        if saved_password != password:
            print(f"❌ 密碼錯誤!")
            return False
        
        # 更新登入計數
        login_count = self.cfg.read(f'{user_key}.login_count', default=0)
        self.cfg.update(f'{user_key}.login_count', login_count + 1)
        self.cfg.update(f'{user_key}.last_login', time.time())
        
        print(f"✅ 歡迎回來, {username}! (第 {login_count + 1} 次登入)")
        return True
    
    def add_score(self, username, points):
        """增加分數"""
        user_key = f'user.accounts.{username}'
        
        current_score = self.cfg.read(f'{user_key}.score', default=0)
        new_score = current_score + points
        self.cfg.update(f'{user_key}.score', new_score)
        
        # 檢查是否升級
        current_level = self.cfg.read(f'{user_key}.level', default=1)
        new_level = new_score // 1000 + 1
        
        if new_level > current_level:
            self.cfg.update(f'{user_key}.level', new_level)
            print(f"🎉 恭喜升級! Lv.{current_level} → Lv.{new_level}")
        
        print(f"💰 分數: {current_score} + {points} = {new_score}")
    
    def get_user_info(self, username):
        """獲取用戶信息"""
        user_key = f'user.accounts.{username}'
        
        if not self.cfg.exists(f'{user_key}.password'):
            print(f"❌ 用戶 '{username}' 不存在!")
            return None
        
        info = {
            'username': username,
            'level': self.cfg.read(f'{user_key}.level', default=1),
            'score': self.cfg.read(f'{user_key}.score', default=0),
            'login_count': self.cfg.read(f'{user_key}.login_count', default=0),
            'created_at': self.cfg.read(f'{user_key}.created_at', default=0),
            'last_login': self.cfg.read(f'{user_key}.last_login', default=0)
        }
        
        return info
    
    def print_user_info(self, username):
        """打印用戶信息"""
        info = self.get_user_info(username)
        
        if info:
            print(f"\n👤 用戶信息:")
            print(f"  用戶名: {info['username']}")
            print(f"  等級: Lv.{info['level']}")
            print(f"  分數: {info['score']}")
            print(f"  登入次數: {info['login_count']}")
            print(f"  註冊時間: {info['created_at']}")
            print(f"  最後登入: {info['last_login']}\n")
    
    def list_all_users(self):
        """列出所有用戶"""
        user_keys = self.cfg.keys('user.accounts.')
        
        # 提取用戶名
        usernames = set()
        for key in user_keys:
            parts = key.split('.')
            if len(parts) >= 3:
                usernames.add(parts[2])
        
        print(f"\n📋 所有用戶 ({len(usernames)} 人):")
        for username in sorted(usernames):
            info = self.get_user_info(username)
            if info:
                print(f"  • {username} (Lv.{info['level']}, 分數: {info['score']})")
        print()
    
    def close(self):
        """關閉系統"""
        self.cfg.close()


# ============================================
# 使用示例
# ============================================
def demo_user_system():
    """演示用戶系統"""
    
    print("\n" + "🎮 用戶系統演示".center(70, "=") + "\n")
    
    system = UserSystem()
    
    # 註冊用戶
    print("📝 註冊用戶:")
    system.register('alice', 'pass123')
    system.register('bob', 'pass456')
    system.register('alice', 'pass789')  # 重複註冊
    
    # 登入
    print("\n🔐 登入:")
    system.login('alice', 'wrongpass')  # 密碼錯誤
    system.login('alice', 'pass123')    # 登入成功
    system.login('alice', 'pass123')    # 再次登入
    
    # 增加分數
    print("\n💰 增加分數:")
    system.add_score('alice', 500)
    system.add_score('alice', 600)  # 升級!
    system.add_score('bob', 1500)
    
    # 查看用戶信息
    print("\n👤 用戶信息:")
    system.print_user_info('alice')
    system.print_user_info('bob')
    
    # 列出所有用戶
    system.list_all_users()
    
    # 關閉系統
    system.close()
    
    print("="*70 + "\n")
    
    # 模擬斷電重啟
    print("⚡ 模擬斷電...\n")
    time.sleep(1)
    
    print("🔋 重新啟動系統...\n")
    system2 = UserSystem()
    
    # 數據已恢復!
    system2.login('alice', 'pass123')
    system2.print_user_info('alice')
    system2.list_all_users()
    
    system2.close()

if __name__ == '__main__':
    demo_user_system()
```

### 範例 3: 傳感器數據記錄

```python
# sensor_logger.py
from config_manager import ConfigManager
import time
import random

class SensorLogger:
    """傳感器數據記錄器 - 自動保存歷史數據"""
    
    def __init__(self, sensor_name, max_records=100):
        self.cfg = ConfigManager()
        self.sensor_name = sensor_name
        self.max_records = max_records
        self.prefix = f'sensor.{sensor_name}'
    
    def log(self, value, unit=''):
        """記錄數據點"""
        # 獲取當前記錄數
        count = self.cfg.get_state(f'{self.prefix}.count', default=0)
        
        # 保存數據點
        timestamp = time.time()
        self.cfg.update(f'{self.prefix}.data.{count}.value', value, auto_flush=False)
        self.cfg.update(f'{self.prefix}.data.{count}.time', timestamp, auto_flush=False)
        self.cfg.update(f'{self.prefix}.data.{count}.unit', unit, auto_flush=False)
        
        # 更新統計
        self.cfg.update(f'{self.prefix}.latest', value, auto_flush=False)
        self.cfg.update(f'{self.prefix}.latest_time', timestamp, auto_flush=False)
        
        # 更新計數
        count += 1
        self.cfg.set_state(f'{self.prefix}.count', count, auto_flush=False)
        
        # 批量寫入
        self.cfg.db.flush()
        
        # 清理舊數據
        if count > self.max_records:
            self._cleanup_old_records()
    
    def _cleanup_old_records(self):
        """清理最舊的數據"""
        count = self.cfg.get_state(f'{self.prefix}.count', default=0)
        records_to_delete = count - self.max_records
        
        for i in range(records_to_delete):
            self.cfg.delete(f'{self.prefix}.data.{i}.value', silent=True)
            self.cfg.delete(f'{self.prefix}.data.{i}.time', silent=True)
            self.cfg.delete(f'{self.prefix}.data.{i}.unit', silent=True)
    
    def get_latest(self):
        """獲取最新讀數"""
        value = self.cfg.read(f'{self.prefix}.latest')
        timestamp = self.cfg.read(f'{self.prefix}.latest_time')
        return value, timestamp
    
    def get_history(self, limit=10):
        """獲取歷史數據"""
        count = self.cfg.get_state(f'{self.prefix}.count', default=0)
        start = max(0, count - limit)
        
        history = []
        for i in range(start, count):
            value = self.cfg.read(f'{self.prefix}.data.{i}.value')
            timestamp = self.cfg.read(f'{self.prefix}.data.{i}.time')
            unit = self.cfg.read(f'{self.prefix}.data.{i}.unit', default='')
            
            if value is not None:
                history.append({
                    'index': i,
                    'value': value,
                    'time': timestamp,
                    'unit': unit
                })
        
        return history
    
    def print_latest(self):
        """打印最新讀數"""
        value, timestamp = self.get_latest()
        if value is not None:
            print(f"📊 {self.sensor_name} 最新讀數: {value} (時間: {timestamp})")
        else:
            print(f"⚠️  {self.sensor_name} 暫無數據")
    
    def print_history(self, limit=10):
        """打印歷史數據"""
        history = self.get_history(limit)
        
        if not history:
            print(f"⚠️  {self.sensor_name} 暫無歷史數據")
            return
        
        print(f"\n📈 {self.sensor_name} 歷史數據 (最近 {len(history)} 條):")
        print("-" * 60)
        
        for record in history:
            value = record['value']
            unit = record['unit']
            print(f"  [{record['index']}] {value}{unit} @ {record['time']}")
        
        print("-" * 60 + "\n")
    
    def get_statistics(self):
        """獲取統計信息"""
        history = self.get_history(limit=1000)
        
        if not history:
            return None
        
        values = [r['value'] for r in history if isinstance(r['value'], (int, float))]
        
        if not values:
            return None
        
        stats = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
        
        return stats
    
    def print_statistics(self):
        """打印統計信息"""
        stats = self.get_statistics()
        
        if stats:
            print(f"\n📊 {self.sensor_name} 統計:")
            print(f"  數據點數: {stats['count']}")
            print(f"  最小值: {stats['min']}")
            print(f"  最大值: {stats['max']}")
            print(f"  平均值: {stats['avg']:.2f}\n")
        else:
            print(f"⚠️  {self.sensor_name} 暫無統計數據")
    
    def close(self):
        """關閉記錄器"""
        self.cfg.close()


# ============================================
# 使用示例
# ============================================
def demo_sensor_logger():
    """演示傳感器記錄器"""
    
    print("\n" + "🌡️  傳感器數據記錄演示".center(70, "=") + "\n")
    
    # 創建溫度記錄器
    temp_logger = SensorLogger('temperature', max_records=50)
    
    # 模擬記錄數據
    print("📝 記錄溫度數據...")
    for i in range(10):
        temp = random.uniform(20, 30)
        temp_logger.log(temp, unit='°C')
        print(f"  記錄 {i+1}: {temp:.1f}°C")
        time.sleep(0.2)
    
    # 查看最新讀數
    print("\n" + "="*70)
    temp_logger.print_latest()
    
    # 查看歷史數據
    temp_logger.print_history(limit=5)
    
    # 查看統計
    temp_logger.print_statistics()
    
    # 關閉記錄器
    temp_logger.close()
    
    print("="*70 + "\n")
    
    # 模擬斷電重啟
    print("⚡ 模擬斷電...\n")
    time.sleep(1)
    
    print("🔋 重新啟動...\n")
    
    # 重新創建記錄器
    temp_logger2 = SensorLogger('temperature')
    
    # 數據已恢復!
    print("✅ 數據已從斷電前恢復:\n")
    temp_logger2.print_latest()
    temp_logger2.print_history(limit=5)
    temp_logger2.print_statistics()
    
    temp_logger2.close()

if __name__ == '__main__':
    demo_sensor_logger()
```

### 範例 4: 綜合應用

```python
# main.py - 完整的應用程序範例
from config_manager import ConfigManager
import time

def main():
    """主程序 - 展示完整的應用流程"""
    
    print("\n" + "🚀 系統啟動".center(70, "=") + "\n")
    
    with ConfigManager(startup_file='startup_config.json') as cfg:
        
        # ========================================
        # 1. 顯示啟動信息
        # ========================================
        boot_count = cfg.get_state('boot_count')
        last_boot_interval = cfg.get_state('last_boot_interval', default=0)
        
        print(f"📊 啟動信息:")
        print(f"  啟動次數: {boot_count}")
        if last_boot_interval > 0:
            print(f"  距離上次啟動: {last_boot_interval:.1f} 秒")
        
        # ========================================
        # 2. 加載配置
        # ========================================
        print(f"\n📋 系統配置:")
        
        c_lum = cfg.get('c_lum', default=1.0)
        led_enable = cfg.get('LED_IO.enable', default=1)
        uart_baudrate = cfg.get('UART_IO.baudrate', default=115200)
        
        print(f"  亮度係數: {c_lum}")
        print(f"  LED 啟用: {'是' if led_enable else '否'}")
        print(f"  UART 波特率: {uart_baudrate}")
        
        # ========================================
        # 3. 恢復用戶數據
        # ========================================
        print(f"\n👤 用戶數據:")
        
        user_name = cfg.read('user.name', default='Guest')
        user_score = cfg.read('user.score', default=0)
        user_level = cfg.read('user.level', default=1)
        
        print(f"  用戶名: {user_name}")
        print(f"  分數: {user_score}")
        print(f"  等級: Lv.{user_level}")
        
        # ========================================
        # 4. 模擬運行
        # ========================================
        print(f"\n⚙️  系統運行中...")
        
        start_time = time.time()
        
        # 模擬用戶操作
        if user_score < 5000:
            user_score += 100
            cfg.update('user.score', user_score)
            print(f"  💰 獲得 100 分! 當前分數: {user_score}")
        
        # 檢查升級
        new_level = user_score // 1000 + 1
        if new_level > user_level:
            cfg.update('user.level', new_level)
            print(f"  🎉 恭喜升級! Lv.{user_level} → Lv.{new_level}")
        
        # 模擬運行
        time.sleep(2)
        
        # 更新運行時間
        session_time = time.time() - start_time
        total_runtime = cfg.get_state('total_runtime', default=0)
        total_runtime += session_time
        cfg.set_state('total_runtime', total_runtime)
        
        print(f"  ⏱️  本次運行: {session_time:.1f} 秒")
        print(f"  ⏱️  累計運行: {total_runtime:.1f} 秒")
        
        # ========================================
        # 5. 保存狀態
        # ========================================
        cfg.set_state('last_shutdown', 'normal')
        cfg.set_state('last_shutdown_time', time.time())
        
        print(f"\n✓ 系統正常關閉")
        print("="*70 + "\n")

if __name__ == '__main__':
    main()
```

---

## ❓ 常見問題

### Q1: 配置修改後為什麼重啟會恢復?

**A:** `config.*` 的配置每次開機都會從 `startup_config.json` 重新加載。如果想永久保存修改:

```python
cfg.set('c_lum', 0.8)  # 運行時修改
cfg.save_to_startup()  # 保存到 startup_config.json
```

### Q2: 如何實現斷電恢復?

**A:** 使用 `state.*` 或 `user.*` 存儲需要持久化的數據:

```python
# ❌ 錯誤: 使用 config (會被重置)
cfg.set('user_score', 1000)

# ✅ 正確: 使用 state 或 user (斷電保留)
cfg.set_state('user_score', 1000)
# 或
cfg.update('user.score', 1000)
```

### Q3: 如何提高寫入性能?

**A:** 使用批量寫入:

```python
# 延遲 flush
cfg.update('key1', 'value1', auto_flush=False)
cfg.update('key2', 'value2', auto_flush=False)
cfg.update('key3', 'value3', auto_flush=False)

# 一次性寫入
cfg.db.flush()
```

### Q4: 如何查看所有數據?

**A:** 使用 `print_info()`:

```python
cfg.print_info()  # 顯示所有信息

cfg.print_info(show_config=False)  # 不顯示配置
cfg.print_info(show_state=True, show_user=False)  # 只顯示狀態
```

### Q5: 數據庫文件在哪裡?

**A:** 默認是 `config.db`,可以自定義:

```python
cfg = ConfigManager(db_file='my_data.db')
```

### Q6: 如何重置所有數據?

**A:** 刪除數據庫文件:

```python
import os

# 刪除數據庫
os.remove('config.db')

# 重新啟動程序
```

### Q7: 支持哪些數據類型?

**A:** 所有 JSON 可序列化的類型:

```python
cfg.update('str_value', 'hello')           # 字符串
cfg.update('int_value', 123)               # 整數
cfg.update('float_value', 3.14)            # 浮點數
cfg.update('bool_value', True)             # 布爾值
cfg.update('list_value', [1, 2, 3])        # 列表
cfg.update('dict_value', {'a': 1, 'b': 2}) # 字典
cfg.update('none_value', None)             # None
```

---

## 📌 快速參考

### 常用操作

```python
# 讀取
value = cfg.get('key')
value = cfg.get_state('key')
value = cfg.read('user.key')

# 寫入 (不存在會自動創建)
cfg.set('key', value)
cfg.set_state('key', value)
cfg.update('user.key', value)

# 檢查存在
if cfg.exists('user.key'):
    pass

# 刪除
cfg.delete('user.key')
cfg.delete('user.key', silent=True)  # 不報錯

# 查詢
keys = cfg.keys('user.')
items = cfg.items('user.')

# 清除
cfg.clear('user.')
```

### 最佳實踐

1. ✅ 使用 `with` 語句管理資源
2. ✅ 使用 `state.*` 存儲需要斷電恢復的數據
3. ✅ 批量操作時延遲 `flush`
4. ✅ 定期調用 `save_to_startup()` 保存重要配置
5. ❌ 避免在循環中頻繁 `flush`
6. ❌ 避免存儲過大的數據 (> 1KB)

