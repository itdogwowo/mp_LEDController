import time
import random
import math

phi0 = 0
phi90 = 1023
phi180 = 2047
phi270 = 3071
phi360 = 4095


eyes_start = [
     {'type': 'keep'    , 'F': 1, 'l_max': 0   , 'l_lim': 0   , 'phi': phi0  , 'end_Time': 60  },
     {'type': 'math_now', 'F': 5, 'l_max': 100 , 'l_lim': 0   , 'phi': phi270, 'end_Time': 100 },
     {'type': 'math_now', 'F': 5, 'l_max': 1023, 'l_lim': 100 , 'phi': phi270, 'end_Time': 110 },
     {'type': 'math_now', 'F': 5, 'l_max': 1023, 'l_lim': 200 , 'phi': phi90 , 'end_Time': 150 },
     {'type': 'keep'    , 'F': 5, 'l_max': 200 , 'l_lim': 200 , 'phi': phi0  , 'end_Time': 300 },

]