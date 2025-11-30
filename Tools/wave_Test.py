import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import math,array
import matplotlib.pyplot as plt

def keep_next(l_max,fs):
    for i in range(fs):
        yield l_max


def is_math_next(F, l_max, phi, fs):
    A = l_max / 2  # 振幅
    Ts = 1 / fs   # 取樣週期
    t = 0
    math_pi_F = 2 * math.pi * F
    math_radians = math.radians(phi)
    for i in range(fs):
        y = A * math.sin(math_pi_F * t + math_radians) + A
        yield round(y,4)  # 生成當前值
        t += Ts
    # while True:
    #     # 計算正弦波值
    #     y = A * math.sin(math_pi_F * t + math_radians) + A
    #     yield y  # 生成當前值
    #     t = (t + Ts)%1  # 增加時間


def is_math_XXX_next(F,l_max,phi,fs):
    A = l_max  # 振幅
    Ts = 1 / fs   # 取樣週期
    t = 0
    math_pi_F = 2 * math.pi * F
    math_radians = math.radians(phi)

    for i in range(fs):
        y = A * math.sin(math_pi_F * t + math_radians) 
        value = round(y,4)
        yield value if value < 0 else  0
        t += Ts


def is_square_wave_next(F,l_max,phi,fs):
    math_XXX = is_math_XXX_next(F,1,phi,fs)
    for i in range(fs):
        yield l_max if next(math_XXX) >=0 else 0


def is_square_True_next(F,phi,fs):
    math_XXX = is_math_XXX_next(F,1,phi,fs)
    for i in range(fs):
        yield True if next(math_XXX) >=0 else False


def is_math_pattern(led_Pattern, setMax: int = 4095):

    run_time = 0
    
    for i in led_Pattern:
        run_fs = i['end_Time'] - run_time
        run_time = i['end_Time']

        l_max = max(0, min(setMax, i['l_max']))

        l_lim = max(0, min(setMax, i['l_lim']))

        l_range = l_max - l_lim

        if i['type'] == 'keep':
            re_value = keep_next(l_range,run_fs) 
        
        elif i['type'] == 'math_now':
            re_value = is_math_next(i['F'],l_range,i['phi'],run_fs)

        elif i['type'] == 'square_wave_now':
            re_value =  is_square_wave_next(i['F'],l_range ,i['phi'],run_fs)

        elif i['type'] == 'math_XXX_now':
            re_value =  is_math_XXX_next(i['F'],l_range ,i['phi'],run_fs)

        for value in re_value:
            yield int(value) + i['l_lim']



class LEDMathMethod:
    """
    pattern = [
                {'type':'keep',             'F':1,'l_max':10,'l_lim':10, 'phi':1024,                'end_Time':10},
                {'type':'math_now',         'F':2,'l_max':20,'l_lim':40, 'phi':2048,                'end_Time':20},
                {'type':'square_wave_now',  'F':3,'l_max':30,'l_lim':50, 'phi':1024*3,              'end_Time':30},
                {'type':'pulse_wave',       'F':4,'l_max':40,'l_lim':50, 'phi':4096,   'pulse':10, 'end_Time':40},
                {'type':'pulse',            'F':5,'l_max':50,'l_lim':40, 'phi':0,      'pulse':10, 'end_Time':50},

            ]
    """

    def __init__(self):
        self.SCALE = 2048
        self.TABLE_SIZE = 65536
        self.grb = bytearray(3)
        self.sin_table = open('./sin_table.bin', 'rb')
        self._sin_table = array.array('H', self.sin_table.read(16384 * 2))
        self.sin_table.close()


    def keep_now(self,F, l_max, phi, fs,t):
        return l_max

    def is_math_now(self,F:int, l_max:int, phi:int, fs:int,t:int) ->int:
        _step = (phi + ((65536 * F*t) // 10 // fs))%65536
        tbl = ptr16(self._quarter_table) # 本地變數存取更快
        
        if _step < 16384:  # 第一象限
            result = tbl[_step]
        elif _step < 32768:  # 第二象限
            result = tbl[32767 - _step]
        elif _step < 49152:  # 第三象限
            result = 4096 - tbl[_step - 32768]
        else:  # 第四象限
            result = 4096 - tbl[65535 - _step]
        
        return (result * l_max) >> 12
    
    def is_square_wave_now(self,F:int, l_max:int, phi:int, fs:int,t:int) ->int:
        _step = (phi + ((65536 * F*t) // 10 // fs))%65536
        tbl = ptr16(self._sin_table)
        if _step < 16384:  # 第一象限
            result = tbl[_step]
        elif _step < 32768:  # 第二象限
            result = tbl[32767 - _step]
        elif _step < 49152:  # 第三象限
            result = 4096 - tbl[_step - 32768]
        else:  # 第四象限
            result = 4096 - tbl[65535 - _step]
            
            
        return  l_max if (result * l_max) >> 12 >=2048 else 0


    def is_square_True_now(self,F:int, l_max:int, phi:int, fs:int,t:int) ->int:
        _step = (phi + ((65536 * F*t) // 10 // fs))%65536
        tbl = ptr16(self._sin_table)
        if _step < 16384:  # 第一象限
            result = tbl[_step]
        elif _step < 32768:  # 第二象限
            result = tbl[32767 - _step]
        elif _step < 49152:  # 第三象限
            result = 4096 - tbl[_step - 32768]
        else:  # 第四象限
            result = 4096 - tbl[65535 - _step]
            
        return  1 if result >> 12 >=2048 else 0

    ###########################################################################

    def keep_next(self,F, l_max, phi, fs):
        for i in range(fs):
            yield l_max

    def is_math_next(self,F, l_max, phi, fs):
        __step = int(65536 * F) //10 // fs
        _step = (phi + __step )%65536
        tbl = self._sin_table  # 本地變數存取更快
        for i in range(fs):
            if _step < 16384:  # 第一象限
                result = tbl[_step]
            elif _step < 32768:  # 第二象限
                result = tbl[32767 - _step]
            elif _step < 49152:  # 第三象限
                result = 4096 - tbl[_step - 32768]
            else:  # 第四象限
                result = 4096 - tbl[65535 - _step]
            
            yield (result * l_max) >> 12
            _step = (_step + __step)%65536

    def is_square_wave_next(self,F, l_max, phi, fs):
        __step = int(65536 * F) //10 // fs
        _step = (phi + __step )%65536
        tbl = self._sin_table
        for i in range(fs):
            if _step < 16384:  # 第一象限
                result = tbl[_step]
            elif _step < 32768:  # 第二象限
                result = tbl[32767 - _step]
            elif _step < 49152:  # 第三象限
                result = 4096 - tbl[_step - 32768]
            else:  # 第四象限
                result = 4096 - tbl[65535 - _step]
                
            yield  l_max if (result) >> 12 >=2047 else 0
            _step = (_step + __step)%65536


    def is_pulse_wave_next(self,F, l_max, phi, fs,pulse = 2047):
        __step = int(65536 * F) //10 // fs
        _step = (phi + __step )%65536
        tbl = self._sin_table
        for i in range(fs):
            if _step < 16384:  # 第一象限
                result = tbl[_step]
            elif _step < 32768:  # 第二象限
                result = tbl[32767 - _step]
            elif _step < 49152:  # 第三象限
                result = 4096 - tbl[_step - 32768]
            else:  # 第四象限
                result = 4096 - tbl[65535 - _step]
                
            yield  l_max if (result) >> 12 >=pulse else 0
            _step = (_step + __step)%65536

    def is_pulse_next(self,F, l_max, phi, fs,pulse = 1):
        if F <= 0:
            raise ValueError("Frequency F must be greater than zero.")
        p = phi
        gap = int(fs/F)
        if gap == 0:
            gap = 1
        pulse = pulse%gap
        re_value = 0
        for i in range(fs):
            if (i+phi)%gap == 0:
                p = 0
            yield l_max if p <= pulse else 0
            p = p+1


    def is_square_True_next(self,F, l_max, phi, fs):
        __step = int(65536 * F) //10 // fs
        _step = (phi + __step )%65536
        tbl = self._sin_table
        for i in range(fs):
            if _step < 16384:  # 第一象限
                result = tbl[_step]
            elif _step < 32768:  # 第二象限
                result = tbl[32767 - _step]
            elif _step < 49152:  # 第三象限
                result = 4096 - tbl[_step - 32768]
            else:  # 第四象限
                result = 4096 - tbl[65535 - _step]
                
            yield  True if result >> 12 >=2047 else False
            _step = (_step + __step)%65536


    def is_math_pattern_next(self,led_Pattern, setMax: int = 4095, stop:bool= False):
        run_time_List = []
        l_range_List = []
        _run_time = 0
        stop = stop

        if led_Pattern[0]['type'] == 'starter':
            sp = led_Pattern.pop(0)
            for i in range(sp['end_Time']):
                yield 0


        for i in led_Pattern:
            run_fs = i['end_Time'] - _run_time
            _run_time = i['end_Time']
            run_time_List.append(run_fs)
            l_max = max(0, min(setMax, i['l_max']))
            l_lim = max(0, min(setMax, i['l_lim']))
            l_range = l_max - l_lim
            l_range_List.append(l_range)

        _stop = True

        for n, i in enumerate(led_Pattern):
            run_fs = run_time_List[n]
            l_range = l_range_List[n]

            if i['type'] == 'keep':
                re_value = self.keep_next(i['F'],l_range,i['phi']<<4,run_fs)
            
            elif i['type'] == 'math_now':
                re_value = self.is_math_next(i['F'],l_range,i['phi']<<4,run_fs)

            elif i['type'] == 'square_wave_now':
                re_value =  self.is_square_wave_next(i['F'],l_range ,i['phi']<<4,run_fs)

            elif i['type'] == 'pulse_wave':
                re_value =  self.is_pulse_wave_next(i['F'],l_range ,i['phi']<<4,run_fs,i.get('pulse',2047))

            elif i['type'] == 'pulse':
                re_value =  self.is_pulse_next(i['F'],l_range ,i['phi']<<4,run_fs,i.get('pulse',2047))


            for value in re_value:
                yield int(value) + i['l_lim']
        
        return 


def graph_waveform(fs,Plot_point):
    plt.figure(figsize=(10, 6))
    plt.plot(fs, Plot_point)
    plt.title('Changing Frequency Sinusoid over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()
    return


'''
type:
    square_wave_now == 方波
    math_now        == 弦波
    math_XXX_now    == 弦波 --交替
    keep            == 保持

F:
    F == 頻率

l_max:
    l_max == 最大量度
    最大量度:
        ESP32   --> 0-1023
        PCA9685 --> 0-4095

l_lim:
    l_lim == 保持最低量度
    最大量度:
        ESP32   --> 0-1023
        PCA9685 --> 0-4095

phi:
    phi == 初始角度
    初始角度:
        90  ==  最低位開始
        -90 ==  最高位開始

end_Time:
    end_Time == 結束位置

    
*** 暫時會盡量嘗試將每一秒定為50 fps,即是end_Time大約每50就等於1秒,將來可能會有變更 ***

'''




pattern = [
            #{'type':'square_wave_now', 'F':0,'l_max':0,'l_lim':0, 'phi':0, 'end_Time':0},
            {'type':'square_wave_now', 'F':7 ,'l_max':30,'l_lim':10, 'phi':-90, 'end_Time':200},
            {'type':'math_now', 'F':2,'l_max':30,'l_lim':10, 'phi':-90, 'end_Time':200},
            {'type':'keep', 'F':5,'l_max':40,'l_lim':10, 'phi':-90, 'end_Time':300},
            {'type':'math_now', 'F':4,'l_max':50,'l_lim':40, 'phi':-90, 'end_Time':500},
            {'type':'math_now', 'F':1,'l_max':300,'l_lim':50, 'phi':-90, 'end_Time':1000},
            {'type':'math_now', 'F':0.5,'l_max':100,'l_lim':50, 'phi':90, 'end_Time':1200},
            {'type':'math_now', 'F':0.5,'l_max':100,'l_lim':40, 'phi':-90, 'end_Time':1500},
            {'type':'math_XXX_now', 'F':5,'l_max':150,'l_lim':40, 'phi':-90, 'end_Time':2000},
            ]
pattern = [
            {'type':'square_wave_now', 'F':1,'l_max':1,'l_lim':1, 'phi':1, 'end_Time':1},
            {'type':'square_wave_now', 'F':2 ,'l_max':1023,'l_lim':0, 'phi':-90, 'end_Time':150},
            {'type':'keep', 'F':1,'l_max':0,'l_lim':0, 'phi':-90, 'end_Time':250},
            {'type':'square_wave_now', 'F':2 ,'l_max':1023,'l_lim':0, 'phi':-90, 'end_Time':400},
            ]


pattern0000 = [
                {'type':'keep',             'F':3,'l_max':0,'l_lim':50, 'phi':1024*1,              'end_Time':10},
                {'type':'math_now',         'F':5,'l_max':1024*4,'l_lim':0, 'phi':1024*3,                'end_Time':600},
                {'type':'math_now',             'F':20,'l_max':1024*4,'l_lim':3500, 'phi':1024*1,              'end_Time':750},
                {'type':'math_now',         'F':5,'l_max':1024*4,'l_lim':0, 'phi':1024*1,                'end_Time':1150},
                {'type':'keep',            'F':5,'l_max':0,'l_lim':0, 'phi':1024*1,                'end_Time':1550},

            ]

mt = LEDMathMethod()



re_waveform = mt.is_math_pattern_next(pattern0000)
_list = list(re_waveform)
print(len(_list))

# re_waveform = is_math_pattern(pattern) 
# _list = list(re_waveform)
# print(len(_list))


t = [i for i in range(len(_list))]
graph_waveform(t,list(_list))

