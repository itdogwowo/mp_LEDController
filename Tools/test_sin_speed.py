import time
import math
from lib.LEDMathMethod import LEDMathMethod

def run_accuracy(samples=4096):
    led_math = LEDMathMethod()
    pi = 3.14159265359

    max_abs_sin = 0
    sum_abs_sin = 0
    sum_sq_sin = 0

    max_abs_wave = 0
    sum_abs_wave = 0
    sum_sq_wave = 0

    for i in range(samples):
        phase = (i * 65536) // samples
        s = math.sin(phase * pi / 32768.0)

        ref_sin_q12 = int((s * 4096.0) + (0.5 if s >= 0 else -0.5))
        got_sin_q12 = int(led_math._sin_q12(phase))
        e = got_sin_q12 - ref_sin_q12
        ae = e if e >= 0 else -e
        if ae > max_abs_sin:
            max_abs_sin = ae
        sum_abs_sin += ae
        sum_sq_sin += e * e

        ref_wave_q12 = int(((s + 1.0) * 4095.0 / 2.0) + 0.5)
        got_wave_q12 = int(led_math._wave01_q12(phase))
        e2 = got_wave_q12 - ref_wave_q12
        ae2 = e2 if e2 >= 0 else -e2
        if ae2 > max_abs_wave:
            max_abs_wave = ae2
        sum_abs_wave += ae2
        sum_sq_wave += e2 * e2

    mean_abs_sin = sum_abs_sin / samples
    rmse_sin = math.sqrt(sum_sq_sin / samples)

    mean_abs_wave = sum_abs_wave / samples
    rmse_wave = math.sqrt(sum_sq_wave / samples)

    print(f"=== 準確率測試 ({samples} 個取樣點) ===")
    print("-" * 40)
    print(f"_sin_q12:    max_abs={max_abs_sin}  mean_abs={mean_abs_sin:.2f}  rmse={rmse_sin:.2f}   (Q12: -4096..4096)")
    print(f"_wave01_q12: max_abs={max_abs_wave}  mean_abs={mean_abs_wave:.2f}  rmse={rmse_wave:.2f} (0..4095)")
    print("-" * 40)
    print(f"_sin_q12:    max_abs 約 {max_abs_sin/4096*100:.2f}%FS")
    print(f"_wave01_q12: max_abs 約 {max_abs_wave/4096*100:.2f}%FS")

def run_benchmark():
    led_math = LEDMathMethod()
    ITERATIONS = 50000
    
    print(f"=== 效能測試開始 ({ITERATIONS} 次迴圈) ===")
    
    # 1. 測試 math.sin (標準浮點數運算)
    # 為了公平起見，我們模擬實際場景中「相位轉徑度」的乘法運算
    start = time.ticks_ms()
    for i in range(ITERATIONS):
        # 將 0-65535 的相位轉為 0-2pi 的浮點數
        v = math.sin((i % 65536) * 3.14159265359 / 32768.0)
    time_math = time.ticks_diff(time.ticks_ms(), start)
    
    # 2. 測試 Viper 定點數 _sin_q12 (回傳 -4096 ~ +4096)
    start = time.ticks_ms()
    for i in range(ITERATIONS):
        # 直接使用整數運算
        v = led_math._sin_q12(i)
    time_viper = time.ticks_diff(time.ticks_ms(), start)
    
    # 3. 測試 Viper 定點數 _wave01_q12 (平移到 0 ~ 4096)
    start = time.ticks_ms()
    for i in range(ITERATIONS):
        v = led_math._wave01_q12(i)
    time_viper_wave = time.ticks_diff(time.ticks_ms(), start)

    print("-" * 40)
    print(f"math.sin:             {time_math} ms")
    print(f"Viper _sin_q12:       {time_viper} ms")
    print(f"Viper _wave01_q12:    {time_viper_wave} ms")
    print("-" * 40)
    
    if time_viper > 0:
        print(f"結論: Viper 定點運算速度約為 math.sin 的 {time_math / time_viper:.2f} 倍")
    else:
        print("結論: Viper 運算速度極快，測量時間接近 0 ms")

if __name__ == "__main__":
    run_benchmark()
    run_accuracy()
