import time
import random
import math

phi0 = 0
phi90 = 1023
phi180 = 2047
phi270 = 3071
phi360 = 4095

def set_LED_list(io_list, led_list_buf):
    for n, led_list in enumerate(io_list):
        if type(led_list) == list:
            for led in led_list:
                led.set_buf(led_list_buf[n])
        else:
            led_list.set_buf(led_list_buf[n])

def return_control(_tempbuf,speed = 1,reverse = False):
    for i in range(speed):
        if reverse:
            yield _tempbuf[::-1]
        else:
            yield _tempbuf

def stepping_engine_next(led_no=1,pattern=[],speed = 1,reverse = False):
    l_max = 0
    l_lim = 4095
    for i in pattern:
        t_l_max = i['l_max']
        t_l_lim = i['l_lim']

        l_max = l_max if t_l_max  < l_max else t_l_max
        l_lim = l_lim if t_l_lim  > l_lim else t_l_lim

    _gen = ledC.mt.is_math_pattern_next(pattern)

    io_no = led_no
    _tempbuf = [0]*(io_no)
    _stepping = phi%io_no
    while 1 :
        l_run = next(_gen)
        _tempbuf[_stepping] = l_run
        _tempbuf[_stepping-1] = l_lim
        _stepping = (_stepping+1)%io_no
        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf
        


def stepping_up_next(led_no=1,pattern=[],speed = 1,reverse = False):
    l_max = 0
    l_lim = 4095
    for i in pattern:
        t_l_max = i['l_max']
        t_l_lim = i['l_lim']

        l_max = l_max if t_l_max  < l_max else t_l_max
        l_lim = l_lim if t_l_lim  > l_lim else t_l_lim

    _gen = ledC.mt.is_math_pattern_next(pattern)

    io_no = led_no
    _tempbuf = [0]*(io_no)
    _stepping = phi%io_no
    while 1 :
        l_run = next(_gen)
        _tempbuf[_stepping] = l_run
        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf
        _stepping = (_stepping+1)%io_no

def stepping_engine_list_next(led_no=1,pattern=[],pulse_list=[],reverse = False):
    # pulse_list = [(10,13),(10,2)]

    l_max = 0
    l_lim = 4095
    for i in pattern:
        t_l_max = i['l_max']
        t_l_lim = i['l_lim']

        l_max = l_max if t_l_max  < l_max else t_l_max
        l_lim = l_lim if t_l_lim  > l_lim else t_l_lim

    _gen = ledC.mt.is_math_pattern_next(pattern)

    io_no = led_no
    _tempbuf = [0]*(io_no)
    _stepping = 0
    while 1 :
        for pulse in pulse_list:
            l_run = next(_gen)
            for _ in range(pulse[1]):
                _tempbuf[_stepping] = l_run
                _tempbuf[_stepping-1] = l_lim
                _stepping = (_stepping+1)%io_no
                for i in range(pulse[0]):
                    if reverse:
                        yield _tempbuf[::-1]
                    else:
                        yield _tempbuf
                


def wave_stepping_engine_next(led_no=1,pattern=[],speed = 1,reverse = False ):
    _gen = ledC.mt.is_math_pattern_next(pattern)

    l_lim = 4095
    for i in pattern:
        t_l_lim = i['l_lim']
        l_lim = l_lim if t_l_lim  > l_lim else t_l_lim

    io_no = led_no
    _tempbuf = [0]*(io_no)
    _stepping = 0
    _temp = 0
    while 1 :

        l_run = next(_gen)
        if l_run == l_lim and not _temp:
            _temp = 1
            _stepping = (_stepping+1)%io_no
        elif l_run != l_lim and _temp:
            _temp = 0

        _tempbuf[_stepping] = l_run
        _tempbuf[_stepping-1] = l_lim

        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf
        

            
def pulse_wave_next(led_no=1,pattern=[],speed = 1,reverse = False ):
    _gen = ledC.mt.is_math_pattern_next(pattern)
    io_no = led_no
    _tempbuf = [0]*(io_no)
    while 1 :
        l_run = next(_gen)
        _tempbuf = _tempbuf[1:] + [l_run]
        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf



def pwm_gine_next(led_no=1,pattern=[],speed = 1,reverse = False ):
    re_init = []

    _gen = ledC.mt.is_math_pattern_next(pattern)

    l_temp = 0
    io_no = led_no
    _tempbuf = [0]*(io_no)
    
    _stepping = 0
    _temp = 0
    _tempS = 0

    while 1 :
        l_run = next(_gen)
        if l_temp <= l_run:
            _temp = 1
        elif l_temp >= l_run :
            _temp = 0
    
        if _temp and _tempS:
            _stepping = (_stepping +1)%io_no
            _tempbuf[_stepping] = l_run
            _tempS = 0
        elif _temp and not _tempS :
            _tempbuf[_stepping] = l_run
            
        elif not _temp and not _tempS :
            _tempbuf[_stepping-1] = l_temp
            _tempS = 1
        elif not _temp and _tempS :
            _tempbuf[_stepping-1] = l_run
            
        l_temp = l_run
        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf


def stepper_motor_next(l_max = 4095,step=4,speed = 1,reverse = False ):
    _tempbuf = [0]*4
    _temp = 0
    while 1 :
        if step == 4 :
            _tempbuf[_temp-1] = 0
            _tempbuf[_temp] = l_max
        elif step == 8 :
            _tempS = _temp//2
            if _temp%2 == 0:
                _tempbuf[_tempS-1] = 0
                _tempbuf[_tempS] = l_max
            else:
                _tempbuf[(_tempS+1)%4] = l_max
        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf
        _temp = (_temp+1)%step



def gradual_wave_next(led_no=1 ,pattern=[], speed= 1, reverse = False ):

    l_max = 0
    l_lim = 4095
    for i in pattern:
        t_l_max = i['l_max']
        t_l_lim = i['l_lim']

        l_max = l_max if t_l_max  < l_max else t_l_max
        l_lim = l_lim if t_l_lim  > l_lim else t_l_lim

    _gen = ledC.mt.is_math_pattern_next(pattern)

    _tempbuf = [0]*led_no
    _temp = 0
    while 1 :
        if step == 4 :
            _tempbuf[_temp-1] = 0
            _tempbuf[_temp] = l_max
        elif step == 8 :
            _tempS = _temp//2
            if _temp%2 == 0:
                _tempbuf[_tempS-1] = 0
                _tempbuf[_tempS] = l_max
            else:
                _tempbuf[(_tempS+1)%4] = l_max
        for i in range(speed):
            if reverse:
                yield _tempbuf[::-1]
            else:
                yield _tempbuf
        _temp = (_temp+1)%step


def thunder_lightning(led_no=1,speed=1):
    n = led_no
    # 闪电状态: 0=准备 1=主闪电 2=余辉 3=传播
    
    speed = speed
    speed_n = n//speed
    state = 0
    brightness = [0] * n  # 每个LED的亮度值
    main_flash = 0        # 主闪电亮度
    wait_counter = 0      # 等待计数器
    decay = 0             # 衰减率
    propagation_index = 0 # 传播当前索引
    propagation_direction = 1  # 传播方向 (1=正方向, -1=反方向)
    
    while True:
        if state == 0:  # 准备状态
            # 随机等待时间 (0.5-2秒)
            wait_counter -= 1
            if wait_counter <= 0:
                state = 1  # 进入主闪电状态
                main_flash = 255  # 初始亮度
                decay = 30  # 主闪电衰减率
                wait_counter = random.randint(10, 40)  # 下次闪电等待时间
        
        elif state == 1:  # 主闪电状态
            # 设置所有LED为主闪电亮度
            for i in range(speed_n):
                i_speed = i*speed
                brightness[i_speed:i_speed+speed] = [main_flash]*speed
            
            # 快速衰减
            main_flash = max(0, main_flash - decay)
            if main_flash == 0:
                # 随机选择传播起点和方向
                propagation_index = random.randint(0, n-1)
                propagation_direction = speed if random.random() > 0.5 else -speed
                state = 3  # 进入传播状态
                decay = 15  # 传播衰减率
        
        elif state == 2:  # 余辉状态
            # 所有LED继续衰减
            all_dark = True
            for i in range(speed_n):
                i_speed = i*speed
                brightness[i_speed:i_speed+speed] = [max(0, brightness[i_speed] - decay)]*speed
                
                if brightness[i_speed] > 0:
                    all_dark = False
            
            # 如果所有LED都暗了，返回准备状态
            if all_dark:
                state = 0
        
        elif state == 3:  # 传播状态
            # 衰减所有LED
            
            for i in range(speed_n):
                i_speed = i*speed
                brightness[i_speed:i_speed+speed] = [max(0, brightness[i_speed] - decay)]*speed
                
                
            
            # 在传播位置创建新闪光
            brightness[propagation_index] = 200
            
            # 移动到下一个位置
            propagation_index += propagation_direction
            
            # 检查边界，如果到达边界进入余辉状态
            if propagation_index < 0 or propagation_index >= n:
                state = 2  # 进入余辉状态
                decay = 10  # 余辉衰减率
        
        yield brightness


def thunder(led_no=1):
    n = led_no
    # 初始化每個LED的亮度值 (0-4095)
    brightness = [0] * n
    # 衰減率 (每次減少5%亮度)
    decay = 5
    
    thunder_n = 3
    Lum_range_l = 150
    Lum_range_m = 255
    
    while True:
        # 隨機觸發新閃電 (10% 概率)
        if random.randint(0, 10) == 0:
            # 隨機選擇1-3個LED
            for _ in range(random.randint(1, thunder_n)):
                idx = random.randint(0, n-1)
                # 設置隨機高亮度 (70-100)
                brightness[idx] = random.randint(Lum_range_l, Lum_range_m)
        
        # 亮度衰減並更新LED
        for i in range(n):
            # 應用衰減
            brightness[i] = max(0, brightness[i] - decay)
            
        
        yield brightness


def lightning(led_no=1):
    n = led_no
    # 初始化每個LED的亮度值 (0-4095)
    brightness = [0] * n
    
    # 閃電狀態: 0=等待 1=主閃電 2=餘輝
    state = 0
    lun_brightness = 0
    wait_counter = 0
    
    while True:
        if state == 0:  # 等待狀態
            # 設置所有LED為0
            brightness = [0] * n
            
            # 隨機等待時間 (1-3秒)
            wait_counter -= 1
            if wait_counter <= 0:
                state = 1  # 進入主閃電
                lun_brightness = 100  # 初始亮度
                wait_counter = random.randint(20, 60)  # 下次閃電等待時間
        
        elif state == 1:  # 主閃電
            # 設置所有LED高亮
            brightness = [lun_brightness] * n
            
            # 快速衰減 (每次減少30%亮度)
            lun_brightness = max(0, lun_brightness - 30)
            if lun_brightness == 0:
                state = 2  # 進入餘輝階段
                lun_brightness = 50  # 餘輝初始亮度
                decay = 10  # 餘輝衰減率
        
        elif state == 2:  # 餘輝狀態
            # 設置餘輝亮度
            brightness = [lun_brightness] * n
            
            # 餘輝衰減
            lun_brightness = max(0, lun_brightness - decay)
            if lun_brightness == 0:
                state = 0  # 返回等待狀態
                
#         print(brightness)
        
        yield brightness
        
        
def vulcan_cannon_aggressive(led_no=1):
    """火神炮燈效 - 激進閃爍版"""
    n = led_no
    brightness = [0] * n
    
    state = "idle"
    state_timer = 0
    current_barrel = 0
    fire_delay = 0
    
    # 參數
    max_brightness = 255
    fire_interval = 3  # 每2個循環發射一次
    
    while True:
        # 狀態控制
        if state == "idle":
            # 外部觸發時才開始
            trigger = yield brightness
            if trigger:
                state = "warming"
                state_timer = 15  # 縮短預熱時間
                # print("火神炮預熱...")
        
        elif state == "warming":
            state_timer -= 1
            # 預熱動畫 - 逐個點亮
            warm_idx = (state_timer * n // 15) % n
            brightness[warm_idx] = 100
            
            # 衰減
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 40)
            
            if state_timer <= 0:
                state = "firing"
                state_timer = 50  # 開火持續時間
                # print("開火！")
        
        elif state == "firing":
            state_timer -= 1
            fire_delay -= 1
            
            # 先清除所有LED（造成完全黑暗的間隔）
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 100)
            
            # 定時發射
            if fire_delay <= 0:
                fire_delay = fire_interval
                
                # 當前槍管全亮
                brightness[current_barrel] = max_brightness
                
                # 小範圍濺射
                if random.randint(0, 2) == 0:
                    side = (current_barrel + random.choice([-1, 1])) % n
                    brightness[side] = random.randint(50, 150)
                
                # 移動到下一個槍管
                current_barrel = (current_barrel + 1) % n
            
            if state_timer <= 0:
                state = "cooling"
                state_timer = 20
                # print("冷卻中...")
        
        elif state == "cooling":
            state_timer -= 1
            
            # 冷卻時的零星閃爍
#             if random.randint(0, 5) == 0:
#                 idx = random.randint(0, n-1)
#                 brightness[idx] = random.randint(30, 80)
            
            # 緩慢衰減
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 15)
            
            if state_timer <= 0:
                state = "idle"
                current_barrel = 0
                # print("就緒")
        
        else:
            # 待機衰減
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 10)
        
        yield brightness
        
        
def heat_wave(led_no=1):
    """散熱器熱浪燈效"""
    n = led_no
    brightness = [0] * n
    
    # 熱量分布陣列
    heat_map = [0.0] * n
    
    # 熱源參數
    heat_sources = []
    max_heat = 255
    heat_decay = 3
    conduction_rate = 0.2
    
    # 對流參數
    convection_direction = 1
    convection_speed = 0.2
    convection_timer = 0
    
    # 脈動參數
    pulse_phase = 0
    pulse_speed = 0.1
    
    while True:
        pulse_phase += pulse_speed
        
        # 產生新熱源
        if random.randint(0, 15) == 0:
            pos = random.randint(0, n-1)
            intensity = random.randint(150, max_heat)
            lifetime = random.randint(20, 40)
            heat_sources.append([pos, intensity, lifetime])
        
        # 更新熱源
        for source in heat_sources[:]:
            pos, intensity, lifetime = source
            
            heat_map[pos] = min(max_heat, heat_map[pos] + intensity)
            
            pulse = math.sin(pulse_phase) * 0.3 + 0.7
            heat_map[pos] = heat_map[pos] * pulse
            
            source[2] -= 1
            source[1] = max(0, source[1] - 5)
            
            if source[2] <= 0:
                heat_sources.remove(source)
        
        # 熱傳導
        new_heat_map = heat_map.copy()
        for i in range(n):
            left = (i - 1) % n
            right = (i + 1) % n
            
            avg_neighbor_heat = (heat_map[left] + heat_map[right]) / 2
            heat_diff = avg_neighbor_heat - heat_map[i]
            new_heat_map[i] += heat_diff * conduction_rate
        
        heat_map = new_heat_map
        
        # 對流效果
        convection_timer += 1
        if convection_timer >= 5:
            convection_timer = 0
            if random.randint(0, 30) == 0:
                convection_direction *= -1
            
            if convection_direction > 0:
                heat_map = [heat_map[-1]] + heat_map[:-1]
            else:
                heat_map = heat_map[1:] + [heat_map[0]]
        
        # 熱量自然衰減
        for i in range(n):
            heat_map[i] = max(0, heat_map[i] - heat_decay)
            
            if heat_map[i] > 200:
                brightness[i] = int(heat_map[i])
            elif heat_map[i] > 100:
                brightness[i] = int(heat_map[i] * 0.9)
            else:
                brightness[i] = int(heat_map[i] * 0.7)
            
            if heat_map[i] > 150 and random.randint(5, 10) == 0:
                brightness[i] = min(255, brightness[i] + random.randint(10, 30))
        
        yield brightness
        
#####
def vulcan_cannon_aggressive(led_no=1):
    """火神炮燈效 - 激進閃爍版"""
    n = led_no
    brightness = [0] * n
    
    state = "idle"
    state_timer = 0
    current_barrel = 0
    fire_delay = 0
    
    max_brightness = 255
    fire_interval = 2
    
    while True:
        if state == "idle":
            trigger = yield brightness
            if trigger:
                state = "warming"
                state_timer = 15
        
        elif state == "warming":
            state_timer -= 1
            warm_idx = (state_timer * n // 15) % n
            brightness[warm_idx] = 100
            
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 20)
            
            if state_timer <= 0:
                state = "firing"
                state_timer = 40
        
        elif state == "firing":
            state_timer -= 1
            fire_delay -= 1
            
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 100)
            
            if fire_delay <= 0:
                fire_delay = fire_interval
                brightness[current_barrel] = max_brightness
                
                if random.randint(0, 2) == 0:
                    side = (current_barrel + random.choice([-1, 1])) % n
                    brightness[side] = random.randint(50, 150)
                
                current_barrel = (current_barrel + 1) % n
            
            if state_timer <= 0:
                state = "cooling"
                state_timer = 20
        
        elif state == "cooling":
            state_timer -= 1
            
            if random.randint(0, 5) == 0:
                idx = random.randint(0, n-1)
                brightness[idx] = random.randint(30, 80)
            
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 15)
            
            if state_timer <= 0:
                state = "idle"
                current_barrel = 0
        else:
            for i in range(n):
                brightness[i] = max(0, brightness[i] - 10)
        
        yield brightness

def heat_wave(led_no=1):
    """散熱器熱浪燈效"""
    n = led_no
    brightness = [0] * n
    heat_map = [0.0] * n
    heat_sources = []
    max_heat = 255
    heat_decay = 3
    conduction_rate = 0.2
    convection_direction = 1
    convection_timer = 0
    pulse_phase = 0
    pulse_speed = 0.1
    
    while True:
        pulse_phase += pulse_speed
        
        if random.randint(0, 15) == 0:
            pos = random.randint(0, n-1)
            intensity = random.randint(150, max_heat)
            lifetime = random.randint(20, 40)
            heat_sources.append([pos, intensity, lifetime])
        
        for source in heat_sources[:]:
            pos, intensity, lifetime = source
            heat_map[pos] = min(max_heat, heat_map[pos] + intensity)
            pulse = math.sin(pulse_phase) * 0.3 + 0.7
            heat_map[pos] = heat_map[pos] * pulse
            source[2] -= 1
            source[1] = max(0, source[1] - 5)
            if source[2] <= 0:
                heat_sources.remove(source)
        
        new_heat_map = heat_map.copy()
        for i in range(n):
            left = (i - 1) % n
            right = (i + 1) % n
            avg_neighbor_heat = (heat_map[left] + heat_map[right]) / 2
            heat_diff = avg_neighbor_heat - heat_map[i]
            new_heat_map[i] += heat_diff * conduction_rate
        heat_map = new_heat_map
        
        convection_timer += 1
        if convection_timer >= 5:
            convection_timer = 0
            if random.randint(0, 30) == 0:
                convection_direction *= -1
            if convection_direction > 0:
                heat_map = [heat_map[-1]] + heat_map[:-1]
            else:
                heat_map = heat_map[1:] + [heat_map[0]]
        
        for i in range(n):
            heat_map[i] = max(0, heat_map[i] - heat_decay)
            if heat_map[i] > 200:
                brightness[i] = int(heat_map[i])
            elif heat_map[i] > 100:
                brightness[i] = int(heat_map[i] * 0.9)
            else:
                brightness[i] = int(heat_map[i] * 0.7)
            if heat_map[i] > 150 and random.randint(0, 10) == 0:
                brightness[i] = min(255, brightness[i] + random.randint(10, 30))
        
        yield brightness

def standby_effect(led_no=1):
    """待機燈效 - 柔和的呼吸燈效果"""
    n = led_no
    phase = 0
    wave_offset = 0
    
    while True:
        brightness = []
        phase += 0.05
        wave_offset += 0.1
        
        for i in range(n):
            wave_phase = phase + (i / n) * math.pi * 2
            base_brightness = (math.sin(wave_phase) + 1) * 0.5
            pulse_pos = (wave_offset / 10) % n
            distance = min(abs(i - pulse_pos), n - abs(i - pulse_pos))
            pulse = max(0, 1 - distance / (n / 4))
            value = base_brightness * 30 + pulse * 50
            brightness.append(int(min(80, value)))
        
        yield brightness

def startup_sequence(led_no=1):
    """啟動序列燈效 - 充能效果"""
    n = led_no
    charge_level = 0
    max_charge = 100
    spark_positions = []
    
    for frame in range(max_charge):
        brightness = [0] * n
        charge_level = frame / max_charge
        
        if frame < 40:
            for i in range(n):
                distance_from_edge = min(i, n - 1 - i)
                if distance_from_edge < frame:
                    brightness[i] = int(100 * (frame / 40))
        
        elif frame < 70:
            pulse_intensity = (frame - 40) / 30
            for i in range(n):
                center = n // 2
                distance = abs(i - center)
                wave = max(0, 1 - distance / (n / 2))
                brightness[i] = int(wave * pulse_intensity * 200)
            
            if random.randint(0, 2) == 0:
                spark_positions.append([random.randint(0, n-1), 255])
        
        else:
            flash_intensity = 1 - (frame - 70) / 30
            for i in range(n):
                brightness[i] = int(255 * flash_intensity)
        
        for spark in spark_positions[:]:
            pos, intensity = spark
            brightness[pos] = min(255, brightness[pos] + intensity)
            spark[1] = max(0, intensity - 20)
            if spark[1] <= 0:
                spark_positions.remove(spark)
        
        yield brightness

def shutdown_sequence(led_no=1):
    """關閉序列燈效 - 能量消散效果"""
    n = led_no
    dissipate_particles = []
    
    for i in range(n):
        dissipate_particles.append({
            'pos': i,
            'brightness': random.randint(150, 255),
            'decay_rate': random.uniform(2, 5),
            'float_speed': random.uniform(-0.5, 0.5)
        })
    
    for frame in range(80):
        brightness = [0] * n
        
        for particle in dissipate_particles:
            particle['brightness'] = max(0, particle['brightness'] - particle['decay_rate'])
            particle['pos'] += particle['float_speed']
            led_idx = int(particle['pos']) % n
            brightness[led_idx] = max(brightness[led_idx], int(particle['brightness']))
            
            if particle['brightness'] > 50:
                for offset in [-1, 1]:
                    neighbor = (led_idx + offset) % n
                    brightness[neighbor] = max(brightness[neighbor], 
                                              int(particle['brightness'] * 0.3))
        
        fade_factor = max(0, 1 - frame / 80)
        for i in range(n):
            brightness[i] = int(brightness[i] * fade_factor)
        
        yield brightness

