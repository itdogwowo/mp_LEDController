import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import math
import matplotlib.pyplot as plt
# from Lib.LEDcontroller import *

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


pattern1 = [
            #{'type':'square_wave_now', 'F':0,'l_max':0,'l_lim':0, 'phi':0, 'end_Time':0},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':200},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':400},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':500},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':600},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':650},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':700},
            {'type':'math_now', 'F':0.5,'l_max':3,'l_lim':0, 'phi':90, 'end_Time':720},
            ]

rgb_pattern = [

            {'type':'hsv', 'value':[150, 0.5, 0.7], 'end_Time':200},
            {'type':'hsv', 'value':[200, 0.5, 0.7], 'end_Time':400},
            {'type':'hsv', 'value':[360, 0.5, 0.7], 'end_Time':500},
            {'type':'hsv', 'value':[151, 1.0, 0.5], 'end_Time':600},
            {'type':'hsv', 'value':[360, 0.5, 0.7], 'end_Time':1000},
            {'type':'hsv', 'value':[151, 1.0, 0.5], 'end_Time':1200},
            {'type':'hsv', 'value':[10, 0.5, 0.7], 'end_Time':1300},
            ]

led_init = [
#             {'type':'esp_LED', 'GPIO':[led_list[0],led_list[2]], 'patter':pattern3(1000), 'value':{}},
#             {'type':'i2c_LED', 'GPIO':[{'i2cIO':i2c_led_list[0],'IO':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]},{'i2cIO':i2c_led_list[1],'IO':[15]}], 'patter':pattern3(4000), 'value':{}},
#             {'type':'RGB', 'GPIO':[rgb_list[0]], 'patter':rgb_pattern, 'value':{'mode':'Pattern_now','ledQ':10,'gap_multiplier':1 ,'gap_Plus':0}},
            # {'type':'RGB', 'GPIO':[rgb_list[1],rgb_list[2]], 'patter':rgb_pattern, 'value':{'mode':'zip_Pattern','ledQ':10,'gap_multiplier':5 ,'gap_Plus':1}},
#             {'type':'RGB', 'GPIO':[rgb_list[1],rgb_list[2]], 'patter':rgb_pattern, 'value':{'mode':'Pattern_now','ledQ':10,'gap_multiplier':30 ,'gap_Plus':1}},
            ]

#rgb_waveform = is_RGB_Pattern(rgb_pattern) 
re_waveform = is_math_pattern(pattern) 
pppp2 = is_RGB_Pattern(rgb_pattern)
# print(len(pppp2[0]))
# print(len(zip_data(pppp2[0])))
ppp=is_RGB_Pattern_II(rgb_pattern)
print(len(re_waveform))

t = [i for i in range(len(re_waveform))]
graph_waveform(t,re_waveform)


import struct

# 将 RGB 数据打包成二进制格式


rest= [
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
    [654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],[654,684],
]   

# 打包数据并保存到文件
#zip_rgb_data(ppp, '.\\wave_library\\rgb_pattern\\compressed_rgb_data.bin')
#zip_led_data(rest, '.\\wave_library\\rgb_pattern\\123.bin')
col_m = 100
print(len(rest))
rgb_value = read_led_zip_data('.\\wave_library\\rgb_pattern\\123.bin',  col_m)
print(rgb_value)


col_m = 0
rgb_value = read_rgb_zip_data('.\\wave_library\\rgb_pattern\\compressed_rgb_data.bin',  col_m)
print(rgb_value)


