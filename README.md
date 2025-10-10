# LED 控制系統 (LED Control System)

[![MicroPython](https://img.shields.io/badge/MicroPython-3.4+-blue.svg)](https://micropython.org/)
[![Platform](https://img.shields.io/badge/Platform-ESP32-green.svg)](https://www.espressif.com/en/products/socs/esp32)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一個基於 MicroPython 的高性能 LED 控制系統,支援多種 LED 類型(PWM LED、I2C LED、WS2812 RGB LED)和豐富的動畫效果。

## ✨ 核心特性

### 🎯 硬體支援
- **ESP32 PWM LED** - 透過 PWM 控制的單色 LED
- **I2C LED** - 透過 I2C 介面控制的 LED 驅動器
- **WS2812/NeoPixel** - 可編程 RGB LED 燈帶
- **混合控制** - 同時控制多種類型 LED

### 🎨 動畫引擎
- **數學波形生成器**
  - 正弦波 (`math_now`)
  - 方波 (`square_wave_now`)
  - 脈衝波 (`pulse_wave`)
  - 定值輸出 (`keep`)
- **HSV 色彩空間** - 直覺的顏色控制
- **高精度定時** - 基於查找表的優化演算法
- **Generator 模式** - 記憶體高效的串流處理

### ⚡ 性能優化
- `@micropython.native` - 原生程式碼編譯
- `@micropython.viper` - 型別標註加速
- **預計算正弦表** - 65536 點查找表
- **緩衝區管理** - 減少記憶體分配

## 📦 系統架構

```
┌─────────────────────────────────────┐
│     Main Application (main.py)      │
├─────────────────────────────────────┤
│         LEDcommander                │  ← 統一控制介面
│  ┌──────────┬──────────┬──────────┐ │
│  │  Pattern │  Buffer  │  Timing  │ │
│  │  Engine  │  Manager │  Control │ │
│  └──────────┴──────────┴──────────┘ │
├─────────────────────────────────────┤
│       LEDController (抽象層)         │
│  ┌──────────┬──────────┬──────────┐ │
│  │ esp_LED  │ i2c_LED  │   RGB    │ │
│  └──────────┴──────────┴──────────┘ │
├─────────────────────────────────────┤
│      LEDMathMethod (數學核心)        │
│  • 正弦波生成  • HSV轉換             │
│  • 查找表加速  • 定點數運算          │
└─────────────────────────────────────┘
```

## 🚀 快速開始

### 1. 硬體準備
```json
{
    "LED_IO": {
        "enable": 1,
        "GPIO": [11, 12, 13, 14]
    },
    "RGB_IO": {
        "enable": 1,
        "GPIO": [
            {"GPIO": 5, "Q": 10}  // GPIO5, 10顆LED
        ]
    }
}
```

### 2. 基礎使用

#### 初始化系統
```python
from lib.LEDcommander import LEDcommander
from lib.LEDController import init_led, init_rgb

# 載入配置
with open('startup_config.json', 'r') as f:
    config = json.load(f)

# 初始化硬體
led_list = init_led(config['LED_IO'])
rgb_list = init_rgb(config['RGB_IO'])

# 建立控制器
ledC = LEDcommander(led_list, rgb_list)
ledC.init_all()
```

#### 簡單控制
```python
# 設定亮度 (0-4095)
ledC.show_all(channel=3, bright=2048)

# 單獨控制
led_list[0].set_buf(4095)  # 最亮
led_list[0].show()

# RGB LED
rgb_list[0][0][0] = 180  # Hue
rgb_list[0][0][1] = 255  # Saturation
rgb_list[0][0][2] = 128  # Value
rgb_list[0].show()
```

### 3. Pattern 動畫

#### 定義動畫模式
```python
pattern = [
    {
        'type': 'math_now',      # 正弦波
        'F': 2,                   # 頻率 2Hz
        'l_max': 4095,           # 最大亮度
        'l_lim': 0,              # 最小亮度
        'phi': 0,                # 相位偏移 (0-4095)
        'end_Time': 100          # 持續幀數
    },
    {
        'type': 'square_wave_now',
        'F': 1,
        'l_max': 4095,
        'l_lim': 0,
        'phi': 2048,             # 180度相位差
        'end_Time': 200
    }
]

led_init = [
    {
        'type': 'esp_LED',
        'GPIO': led_list[0:4],   # 控制前4顆LED
        'pattern': pattern
    }
]
```

#### 執行動畫
```python
ledC.run_Pattern(
    led_init,
    gap_Time=20,      # 每幀20ms (50 FPS)
    run_time=200,     # 總幀數
    encoder=4095,     # 全域亮度
    debug=True        # 顯示性能資訊
)
```

## 📖 進階功能

### Pattern 類型完整列表

| 類型 | 說明 | 參數 |
|------|------|------|
| `keep` | 恆定輸出 | `l_max`, `end_Time` |
| `math_now` | 正弦波 | `F`, `l_max`, `l_lim`, `phi`, `end_Time` |
| `square_wave_now` | 方波 | 同上 |
| `pulse_wave` | 可調占空比脈衝 | 額外: `pulse` (0-4095) |
| `pulse` | 固定寬度脈衝 | 額外: `pulse` (脈衝寬度幀數) |

### HSV 色彩控制

```python
# 方法 1: 直接設定
rgb_led = rgb_list[0][0]
rgb_led[0] = 120    # Hue (0-360)
rgb_led[1] = 255    # Saturation (0-255)
rgb_led[2] = 128    # Value (0-255)

# 方法 2: 使用數學方法
from lib.LEDMathMethod import LEDMathMethod
mt = LEDMathMethod()

grb = mt.hsv_to_grb(180, 255, 128)
rgb_list[0].led.buf[0:3] = grb
```

### 緩衝區管理

```python
# 從檔案載入預計算動畫
buffer_gen = ledC.buffer_next('animations/rainbow_grbBuf_60_100.bin')

led_init = [{
    'type': 'RGB',
    'GPIO': rgb_list,
    '_generators': buffer_gen
}]

ledC.run_Pattern(led_init, gap_Time=20)
```

### 回調函數系統

```python
def fade_effect(commander, frame):
    """每幀降低1點亮度"""
    for led in commander.led_list:
        current = led.LED_Buffer[0]
        led.LED_Buffer[0] = max(0, current - 1)

def stop_condition(commander, frame):
    """100幀後停止"""
    if frame >= 100:
        commander.keep_run = False
        return True
    return False

ledC.run_Pattern(
    led_init,
    headers=[stop_condition],     # 條件檢查
    set_buffer=[fade_effect]      # 每幀回調
)
```

## 🔧 配置檔案說明

### startup_config.json
```json
{
    "Network": {
        "enable": 0,
        "pcName": "ESP32_LED",
        "ssid": "your_wifi",
        "password": "your_password"
    },
    "c_lum": 1.0,                    // 全域亮度係數
    "LED_IO": {
        "enable": 1,
        "GPIO": [11, 12, 13, 14, 15, 16, 17, 18]
    },
    "i2c_IO": {
        "enable": 1,
        "i2c_List": [
            {
                "GPIO": {"scl": 47, "sda": 48},
                "address": ["0x40"]
            }
        ]
    },
    "RGB_IO": {
        "enable": 1,
        "GPIO": [
            {"GPIO": 5, "Q": 60},    // GPIO5, 60顆LED
            {"GPIO": 6, "Q": 30}
        ]
    }
}
```

## 📊 性能基準

測試環境: ESP32 @ 240MHz, MicroPython v1.20

| 操作 | 時間 | 說明 |
|------|------|------|
| 正弦波計算 (查表) | ~5μs | 65536點表 |
| HSV→RGB 轉換 | ~15μs | Viper優化 |
| 60 LED 更新 | ~800μs | WS2812 |
| Pattern 幀處理 | ~2ms | 包含顯示 |

記憶體使用:
- 正弦查找表: 128KB (一次性)
- 單個 LED 控制器: ~200 bytes
- Pattern Generator: ~100 bytes

## 🛠️ API 參考

### LEDcommander 主要方法

```python
class LEDcommander:
    def init_all(self) -> None:
        """重置所有LED到初始狀態"""
    
    def show_all(self, channel: int, bright: int = 4095) -> None:
        """
        顯示所有LED
        channel: 0=偶數, 1=奇數, 3=全部, 4=全部(不更新RGB)
        bright: 全域亮度 (0-4095)
        """
    
    def run_Pattern(
        self,
        led_init: List[dict],
        gap_Time: int = 20,
        run_time: int = 0,
        encoder: int = 4095,
        headers: List[Callable] = [],
        set_buffer: List[Callable] = [],
        debug: bool = False
    ) -> None:
        """執行動畫模式"""
```

### LEDController 屬性

```python
class LEDController:
    led_Type: str           # 'esp_LED' | 'i2c_LED' | 'RGB'
    LED_Buffer: array       # 亮度緩衝區
    brightness: int         # 全域亮度 (0-4095)
    
    # RGB 專用
    led_H: array            # Hue 緩衝區 (0-360)
    led_S: array            # Saturation 緩衝區 (0-255)
    
    def duty(self, lum: int, ledQ: List[int] = []) -> None:
        """設定亮度並立即顯示"""
    
    def set_be_light(self) -> None:
        """RGB: 將 HSV 轉換到緩衝區"""
    
    def show(self) -> None:
        """更新硬體輸出"""
```

## 🎓 範例程式

### 彩虹流水燈
```python
def rainbow_chase():
    pattern = []
    for i in range(60):
        pattern.append({
            'type': 'math_now',
            'F': 1,
            'l_max': 255,
            'l_lim': 0,
            'phi': int(4095 * i / 60),  # 相位梯度
            'end_Time': 100
        })
    
    led_init = []
    for i, led in enumerate(rgb_list[0]):
        led[0] = int(360 * i / 60)  # Hue 梯度
        led[1] = 255
        led_init.append({
            'type': 'RGB',
            'GPIO': [led],
            'pattern': [pattern[i]]
        })
    
    ledC.run_Pattern(led_init, gap_Time=20)

rainbow_chase()
```

### 呼吸燈效
```python
breathing = [{
    'type': 'math_now',
    'F': 0.5,           # 2秒週期
    'l_max': 4095,
    'l_lim': 100,
    'phi': 0,
    'end_Time': 200     # 4秒總時長
}]

led_init = [{
    'type': 'esp_LED',
    'GPIO': led_list,
    'pattern': breathing
}]

ledC.run_Pattern(led_init, gap_Time=20, run_time=200)
```

## 🐛 故障排除

### 常見問題

**Q: LED 閃爍不穩定**
```python
# 增加幀間隔
ledC.run_Pattern(led_init, gap_Time=30)  # 從20ms增加到30ms

# 檢查時序
ledC.run_Pattern(led_init, debug=True)   # 查看實際幀時間
```

**Q: RGB 顏色不正確**
```python
# 確認 HSV 範圍
# H: 0-360, S: 0-255, V: 0-4095 (內部會轉換)

# 手動校正
rgb_list[0].set_be_light()  # 強制更新
rgb_list[0].show()
```

**Q: 記憶體不足**
```python
import gc
gc.collect()  # 執行垃圾回收

# 減少同時執行的 Pattern
# 或使用緩衝區模式
```

## 📝 最佳實踐

1. **初始化順序**
   ```python
   init_Network()  # 先初始化網路
   gc.collect()    # 回收記憶體
   init_led()      # 再初始化硬體
   ```

2. **Pattern 設計**
   - 使用 `end_Time` 控制總時長,避免無限循環
   - 相位差 `phi` 使用 0-4095 範圍 (會映射到 0-360度)
   - 頻率 `F` 建議 0.1-10 Hz

3. **性能優化**
   ```python
   # 預先計算常數
   PHI_STEP = 4095 // LED_COUNT
   
   # 批次更新
   ledC.show_all(3, encoder_value)  # 一次更新所有
   ```

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request!

## 📮 聯絡方式

- 問題回報: [GitHub Issues](https://github.com/yourname/led-control/issues)
- 文件: [Wiki](https://github.com/yourname/led-control/wiki)

---

**注意**: 本系統針對 ESP32 優化,其他 MicroPython 平台可能需要調整。