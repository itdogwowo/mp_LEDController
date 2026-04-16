import gc

import boot

# 可在 REPL / WebREPL 執行:
# >>> import main
# >>> main.stop()
RUN = True


def stop():
    global RUN
    RUN = False
    try:
        boot.ledC.keep_run = False
    except Exception:
        pass


def _build_wave_led_init(led_list):
    expanded_leds = []
    for led in led_list:
        if hasattr(led, "set_buf"):
            expanded_leds.append(led)
            continue
        try:
            for led_item in led:
                expanded_leds.append(led_item)
        except TypeError:
            expanded_leds.append(led)

    led_count = len(expanded_leds)
    if led_count == 0:
        return []

    led_init = []
    one_cycle = 120

    for idx, led in enumerate(expanded_leds):
        phi = (idx * 360) // led_count
        pattern = [
            {
                "type": "math_now",
                "F": 1,
                "l_max": 3200,
                "l_lim": 100,
                "phi": phi,
                "end_Time": one_cycle,
            }
        ]
        led_init.append({"type": "LED", "GPIO": [led], "pattern": pattern})

    return led_init


def _preview_wave():
    preview_pattern = [
        {"type": "math_now", "F": 1, "l_max": 3200, "l_lim": 100, "phi": 0, "end_Time": 16}
    ]
    gen = boot.ledC.mt.is_math_pattern_next(preview_pattern, stop=True)
    values = [next(gen) for _ in range(8)]
    print("[preview wave]", values)


def run():
    global RUN
    RUN = True

    led_init = _build_wave_led_init(boot.all_led_list)
    if not led_init:
        print("沒有可用 LED，跳過播放")
        return

    _preview_wave()

    while RUN:
        boot.ledC.keep_run = True
        boot.ledC.run_Pattern(
            led_init=led_init,
            gap_Time=20,
            encoder=4095,
            debug=False,
        )
        gc.collect()


try:
    run()
except KeyboardInterrupt:
    stop()
    print("Pattern stopped")
