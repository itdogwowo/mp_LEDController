import os
import gc
import machine ,time

class VideoStreamReader:
    def __init__(self, filename, frame_size=1024 * 1024):
        self.filename = filename
        self.frame_size = frame_size
        self.file_size = os.stat(filename)[6]
        self.total_frames = self.file_size // frame_size
        
        # 保持文件打开状态避免重复打开开销
        self.file = open(self.filename, "rb")
        
        # 预分配可重用缓冲区
        self._buffer = bytearray(frame_size)
        self._buf_mv = memoryview(self._buffer)
        
    def read_frame(self, frame_index):
        """读取单个指定索引的帧"""
        if frame_index < 0 or frame_index >= self.total_frames:
            return None
            
        offset = frame_index * self.frame_size
        bytes_to_read = min(self.frame_size, self.file_size - offset)
        
        self.file.seek(offset)
        bytes_read = self.file.readinto(self._buf_mv)
        return self._buf_mv[:bytes_read] if bytes_read < self.frame_size else self._buf_mv

    def read_sequential(self):
        """顺序读取下一帧（最高效的方法）"""
        bytes_read = self.file.readinto(self._buf_mv)
        if bytes_read == 0:
            # 文件结束，重置到开头
            self.file.seek(0)
            bytes_read = self.file.readinto(self._buf_mv)
        
        return self._buf_mv[:bytes_read] if bytes_read < self.frame_size else self._buf_mv

    def stream_frames_in_range(self, start_frame=0, end_frame=None, step=1, loop=False):
        """
        生成器：按指定范围流式读取帧
        优化：使用顺序读取方法提高性能
        """
        # 参数校验和默认值处理
        if start_frame < 0:
            start_frame = 0
            
        if end_frame is None or end_frame > self.total_frames:
            end_frame = self.total_frames
            
        # 计算实际需要读取的帧数
        frame_count = end_frame - start_frame
        if frame_count <= 0 or start_frame >= self.total_frames:
            return

        # 直接使用顺序读取方法
        self.file.seek(start_frame * self.frame_size)
        
        frames_to_read = frame_count
        while True:
            # 读取指定范围内的帧
            for _ in range(frames_to_read):
                frame = self.read_sequential()
                if frame is not None:
                    yield frame
            
            # 如果不是循环模式，则退出
            if not loop:
                break
                
            # 重置文件指针到起始位置
            self.file.seek(start_frame * self.frame_size)

    # 上下文管理器支持
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


# ====== 通用TFT驅動類 ======
class TFT:
    def __init__(self, spi, dc, cs, rst, width, height):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.width = width
        self.height = height
        
        # 初始化引腳
        self.dc.init(machine.Pin.OUT, value=0)
        self.cs.init(machine.Pin.OUT, value=1)
        self.rst.init(machine.Pin.OUT, value=1)
        
        self.reset()
        time.sleep_ms(100)
    
    def reset(self):
        self.rst(0)
        time.sleep_ms(50)
        self.rst(1)
        time.sleep_ms(50)
    
    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)
    
    def write_data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)
            
    def set_window(self, x0, y0):
        x1 = x0 + self.width-1
        y1 = y0 + self.height-1
        
        self.write_cmd(0x2A)  # 列地址設置
        self.write_data(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        
        self.write_cmd(0x2B)  # 行地址設置
        self.write_data(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        
        self.write_cmd(0x2C)  # 內存寫入

    def display_bin(self, filename,x,y):
        self.set_window( x, y)
        with open(filename, 'rb') as f:
            start_time = utime.ticks_ms()
            
            buf = memoryview(bytearray(os.stat(filename)[6]))
            f.readinto(buf)
            self.write_data(buf)
            end_time = utime.ticks_ms()
            
            
            ticks_time = time.ticks_diff(end_time, start_time)
            print(ticks_time)
            
    def display_img_bin(self, filename,x,y):
        self.set_window( x, y)
        with open(filename, 'rb') as f:
            start_time = utime.ticks_ms()
            buf = memoryview(bytearray(os.stat(filename)[6]))
            f.readinto(buf)
            self.write_data(buf)
            end_time = utime.ticks_ms()

            
         

class ST7735(TFT):
    def __init__(self, spi, dc, cs, rst,width,height, rotation=0):
        super().__init__(spi, dc, cs, rst, width, height)
        self._rotation = rotation
        self.init()
    
    def init(self):
        init_cmds = [
            (0x01, None),       # 軟復位
            (0x11, None),       # 退出睡眠模式
            (0xB1, b'\x01\x2C\x2D'),  # 幀率控制
            (0xB2, b'\x01\x2C\x2D'),
            (0xB3, b'\x01\x2C\x2D\x01\x2C\x2D'),
            (0xB4, b'\x07'),    # 反轉掃描
            (0xC0, b'\xA2\x02\x84'),
            (0xC1, b'\xC5'),
            (0xC2, b'\x0A\x00'),
            (0xC3, b'\x8A\x2A'),
            (0xC4, b'\x8A\xEE'),
            (0x36, b'\xC0'),    # 內存訪問控制
            (0x3A, b'\x05'),    # 16位像素
            (0x21, None),       # 顯示反轉
            (0x29, None)        # 開啟顯示
        ]
        
        for cmd, data in init_cmds:
            self.write_cmd(cmd)
            if data:
                self.write_data(data)
            time.sleep_ms(10)
        self.set_window(0,0)

# ====== ST7789專用驅動 ======
class ST7789(TFT):
    def __init__(self, spi, dc, cs, rst, width, height,rotation=0):
        super().__init__(spi, dc, cs, rst, width, height)
        self._rotation = rotation
        self.init()
    
    def init(self):
        init_cmds = [
            (0x01, None),       # 軟復位
            (0x11, None),       # 退出睡眠模式
            (0x3A, b'\x55'),    # 16位像素
            (0x36, b'\x60'),
            # (0x36, b'\x00'),    # 內存訪問控制
            (0xB2, b'\x0C\x0C\x00\x33\x33'),
            (0xB7, b'\x35'),    # 門控制
            (0xBB, b'\x19'),    # VCOM設置
            (0xC0, b'\x2C'),    # LCM控制
            (0xC2, b'\x01'),
            (0xC3, b'\x12'),
            (0xC4, b'\x20'),
            (0xC6, b'\x0F'),
#             (0x21, None),
            (0xD0, b'\xA4\xA1'),
            (0x29, None)        # 開啟顯示
        ]
        
        for cmd, data in init_cmds:
            self.write_cmd(cmd)
            if data:
                self.write_data(data)
            time.sleep_ms(10)
        self.set_window(0,0)


    def _get_rotation_cmd(self):
        """根據旋轉角度返回記憶體存取控制值"""
        # MADCTL寄存器位定義:
        # [MY:行地址方向, MX:列地址方向, MV:行列交換, ML:垂直刷新順序, RGB:RGB順序, MH:水平刷新順序]
        rotation_settings = {
            # MY MX MV ML RGB MH
            0:   0x48,   # 橫向模式 (0°) - RGB順序
            90:  0x28,   # 縱向模式 (90°)
            180: 0x88,   # 橫向反轉 (180°)
            270: 0xE8    # 縱向反轉 (270°)
        }
        return bytes([rotation_settings.get(self._rotation, 0x48)])


class GC9A01(TFT):
    def __init__(self, spi, dc, cs, rst, width, height,rotation=0):
        super().__init__(spi, dc, cs, rst, width, height)
        self._rotation = rotation
        self.init()
    
    def init(self):
        init_cmds = [
            (0xEF, None),       # 系統功能啟用
            (0xEB, b'\x14'),     # 調整內部電壓
            (0xFE, None),        # 切換命令頁
            (0xEF, None),        # 重複啟用系統
            (0xEB, b'\x14'),     # 電壓參數
            (0x84, b'\x40'),     # VCI電壓設定
            (0x85, b'\xFF'),     # VCOM電壓
            (0x86, b'\xFF'),     # VCOM偏移
            (0x87, b'\xFF'),     # 電源控制
            (0x88, b'\x0A'),     # 面板驅動電壓
            (0x89, b'\x21'),     # 時序控制
            (0x8A, b'\x00'),     # 預充電時間
            (0x8B, b'\x80'),     # 接口控制
            (0x8C, b'\x01'),     # 驅動能力
            (0x8D, b'\x01'),     # 預充電電流
            (0x8E, b'\xFF'),     # COM腳掃描
            (0x8F, b'\xFF'),     # COM腳配置
            (0xB6, b'\x00\x00'), # 顯示功能控制
            # (0x36, b'\x08'),     # 記憶體存取控制 (MY=0, MX=0, MV=1, ML=0, BGR=0)
            (0x3A, b'\x55'),     # 像素格式 (16-bits/pixel)
            (0x90, b'\x08\x08\x08\x08'),  # 框架速率控制
            (0xBD, b'\x06'),     # 命令保護
            (0xBC, b'\x00'),     # 接口模式
            (0xFF, b'\x60\x01\x04'), # Gamma校正
            (0xC3, b'\x13'),     # 電源控制1
            (0xC4, b'\x13'),     # 電源控制2
            (0xC9, b'\x22'),     # 電源控制3
            (0xBE, b'\x11'),     # 電壓補償
            (0xE1, b'\x10\x0E'), # 正極Gamma校正
            (0xDF, b'\x21\x0c\x02'), # 時序控制
            (0xF0, b'\x45\x09\x08\x08\x26\x2A'), # Gamma曲線設定
            (0xF1, b'\x43\x70\x72\x36\x37\x6F'), # Gamma參數
            (0xF2, b'\x45\x09\x08\x08\x26\x2A'), # Gamma曲線設定
            (0xF3, b'\x43\x70\x72\x36\x37\x6F'), # Gamma參數
            (0xED, b'\x1B\x0B'), # 電壓保護
            (0xAE, b'\x77'),     # 電源優化
            (0xCD, b'\x63'),     # 背光控制
            (0x70, b'\x07\x07\x04\x0E\x0F\x09\x07\x08\x03'), # 面板設定
            (0xE8, b'\x34'),     # 時序控制
            (0x62, b'\x18\x0D\x71\xED\x70\x70\x18\x0F\x71\xEF\x70\x70'), # Gamma校正
            (0x63, b'\x18\x11\x71\xF1\x70\x70\x18\x13\x71\xF3\x70\x70'), # Gamma校正
            (0x64, b'\x28\x29\xF1\x01\xF1\x00\x07'), 
            (0x66, b'\x3C\x00\xCD\x67\x45\x45\x10\x00\x00\x00'),
            (0x67, b'\x00\x3C\x00\x00\x00\x01\x54\x10\x32\x98'),
            (0x36, b'\x08'),
            (0x74, b'\x10\x85\x80\x00\x00\x4E\x00'),
            (0x98, b'\x3e\x07'),
            (0x35,None),
            (0x21,None),
            (0x29, None),        # 開啟顯示
            (0x11, None),        # 退出睡眠模式 (必須在最後)
   
        ]
        
        for cmd, data in init_cmds:
            self.write_cmd(cmd)
            if data:
                self.write_data(data)
            time.sleep_ms(10)

        self.set_window(0,0)
        


class ILI9341(TFT):
    def __init__(self, spi, dc, cs, rst, width=240, height=320, rotation=0):
        super().__init__(spi, dc, cs, rst, width, height)
        self._rotation = rotation  # 螢幕旋轉角度 (0, 90, 180, 270)
        self.init()

    def init(self):
        # 硬體復位序列
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(20)
        self.rst(1)
        time.sleep_ms(150)
        
        # ILI9341 初始化命令序列
        init_cmds = [
            (0xCF, b'\x00\xC1\x30'),   # 電源控制B
            (0xED, b'\x64\x03\x12\x81'),# 電源時序控制
            (0xE8, b'\x85\x00\x78'),    # 驅動時序控制A
            (0xCB, b'\x39\x2C\x00\x34\x02'), # 電源控制A
            (0xF7, b'\x20'),             # 泵比控制
            (0xEA, b'\x00\x00'),         # 驅動時序控制B
            (0xC0, b'\x23'),             # 電源控制1
            (0xC1, b'\x10'),             # 電源控制2
            (0xC5, b'\x3E\x28'),         # VCOM控制1
            (0xC7, b'\x86'),             # VCOM控制2
            (0x36, self._get_rotation_cmd()),  # 記憶體存取控制 (旋轉設定)
            (0x3A, b'\x55'),             # 像素格式 (16位)
            (0xB1, b'\x00\x18'),         # 幀率控制
            (0xB6, b'\x08\x82\x27'),     # 顯示功能控制
            (0xF2, b'\x00'),             # 3G控制 (禁用)
            (0x26, b'\x01'),             # Gamma曲線設置
            (0xE0, b'\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00'), # 正極Gamma校正
            (0xE1, b'\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F'), # 負極Gamma校正
            (0x11, None),               # 退出睡眠模式
            (0x29, None)                # 開啟顯示
        ]
        
        # 發送初始化命令
        for cmd, data in init_cmds:
            self.write_cmd(cmd)
            if data:
                self.write_data(data)
            time.sleep_ms(10)  # 命令間延時
        
        # 額外延時確保初始化完成
        time.sleep_ms(120)
        self._set_window(0, 0, self.width - 1, self.height - 1)

    def _get_rotation_cmd(self):
        """根據旋轉角度返回記憶體存取控制值"""
        # MADCTL寄存器位定義:
        # [MY:行地址方向, MX:列地址方向, MV:行列交換, ML:垂直刷新順序, RGB:RGB順序, MH:水平刷新順序]
        rotation_settings = {
            # MY MX MV ML RGB MH
            0:   0x48,   # 橫向模式 (0°) - RGB順序
            90:  0x28,   # 縱向模式 (90°)
            180: 0x88,   # 橫向反轉 (180°)
            270: 0xE8    # 縱向反轉 (270°)
        }
        return bytes([rotation_settings.get(self._rotation, 0x48)])

    def _set_window(self, x0, y0, x1, y1):
        """設置顯示區域"""
        # 根據旋轉方向調整座標
        if self._rotation in [90, 270]:
            x0, y0, x1, y1 = y0, x0, y1, x1
        
        self.write_cmd(0x2A)  # 列地址設置
        self.write_data(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self.write_cmd(0x2B)  # 行地址設置
        self.write_data(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self.write_cmd(0x2C)  # 寫入記憶體命令

    def display(self, image):
        """顯示圖像"""
        self._set_window(0, 0, self.width - 1, self.height - 1)
        # 將圖像數據轉換為RGB565字節流
        # 此處應添加具體的圖像數據傳輸代碼
        self.write_data(image)