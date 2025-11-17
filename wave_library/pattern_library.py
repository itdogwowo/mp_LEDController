import time
import random
import math

phi0 = 0
phi90 = 1023
phi180 = 2047
phi270 = 3071
phi360 = 4095


DEFINE_GRADIENT_PALETTE=(
    0,   0,   0,   0,
    46,  18,  0,   0,
    96,  113, 0,   0,
    108, 142, 3,   1,
    119, 175, 17,  1,
    146, 213, 44,  2,
    174, 255, 82,  4,
    188, 255, 115, 4,
    202, 255, 156, 4,
    218, 255, 203, 4,
    234, 255, 255, 4,
    244, 255, 255, 71,
    255, 255, 255, 255
    )

DEFINE_GRADIENT_PALETTE=(
    0,   1,   1,   0,
    76,  32,  5,   0,
    146, 192, 24,  0,
    197, 220, 105, 5,
    240, 252, 255, 31,
    250, 252, 255, 111,
    255, 255, 255, 255
    )

DEFINE_GRADIENT_PALETTE=(
    0,   200, 200, 200,  // #00b8ff
    85,  0,   184, 255,  // #001eff
    170, 0,   30,  255,  // #bd00ff
    255, 214, 0,   255   // #d600ff
    )

DEFINE_GRADIENT_PALETTE=(
    0,   200, 80, 0,  // Bright orange
    128, 100, 25, 0,  // Yellow-orange
    255, 200, 80, 0   // Bright orange
    )

DEFINE_GRADIENT_PALETTE=(
    0,   200, 200, 200,  // rgb(200, 200, 200)
    128, 180, 180, 180, //rgb(200, 200, 200)
    255, 200, 200, 200
    )

# DEFINE_GRADIENT_PALETTE(red_orange_gp){
#     0, 5, 0, 0,        //rgb(0, 0, 0)
#     128, 255, 10, 0,   //rgb(180, 50, 0)
#     255, 5, 0, 0,      //rgb(0, 0, 0)
# };
# 
# DEFINE_GRADIENT_PALETTE(rainbow_gp){
#     0,   255, 0,   0,    // #FF0000
#     42,  255, 127, 0,    // #FF7F00
#     85,  255, 255, 0,    // #FFFF00
#     128, 0,   255, 0,    // #00FF00
#     170, 0,   0,   255,  // #0000FF
#     213, 75,  0,   130,  // #4B0082
#     255, 148, 0,   211   // #9400D3
# };
# 
# DEFINE_GRADIENT_PALETTE(white_gold1_Vent){
#     // Extreme brightness variations while maintaining similar colors
#     0,   42,  28,  3,     // ~20% brightness - very dark gold
#     16,  168, 113, 10,    // ~65% brightness - medium dark
#     32,  255, 209, 98,    // ~82% brightness - bright
#     48,  63,  53,  15,    // ~25% brightness - very dark
#     
#     64,  210, 141, 13,    // ~55% brightness - medium
#     80,  255, 255, 200,   // ~98% brightness - very bright
#     96,  84,  71,  20,    // ~33% brightness - dark
#     112, 244, 255, 158,   // ~95% brightness - very bright
#     
#     128, 51,  51,  16,    // ~20% brightness - very dark
#     144, 255, 230, 120,   // ~90% brightness - bright
#     160, 126, 106, 31,    // ~50% brightness - medium dark
#     176, 244, 205, 42,    // ~80% brightness - bright
#     
#     192, 35,  30,  9,     // ~15% brightness - very dark
#     208, 200, 168, 50,    // ~70% brightness - medium
#     224, 255, 255, 100,   // ~95% brightness - very bright
#     240, 76,  64,  19,    // ~30% brightness - dark
#     
#     255, 255, 141, 13      // ~50% brightness - medium
# };
# 
# // White Gold Palettes
# // DEFINE_GRADIENT_PALETTE(white_gold1_gp){
# //     0, 255, 253, 184,               // #fffdb8	(255,253,184)
# //     64, 253, 246, 140,            // #fdf68c	(253,246,140)
# //     128, 244, 205, 42,            // #f4cd2a	(244,205,42)
# //     192, 237, 163, 35,           // #eda323	(237,163,35)
# //     255, 210, 141, 13           // #d28d0d	(210,141,13)
# // };
# 
# DEFINE_GRADIENT_PALETTE(white_gold1_gp){
#     0,   255, 255, 255,   // Pure white
#     64,  250, 250, 250,   // Very slightly cooler white
#     128, 255, 255, 255,   // Pure white
#     192, 245, 245, 245,   // Very slightly warmer white
#     255, 255, 255, 255    // Pure white
# };
# 
# DEFINE_GRADIENT_PALETTE(sasabi_green_gp){
#     0, 0, 3, 0,
#     128, 0, 80, 0,
#     255, 0, 3, 0
# };
# 
# 
# DEFINE_GRADIENT_PALETTE(storing_energy_gp){
#     0,   0,   0,   0,
#     32,  0,   0,   0,
#     128, 0,   80, 0,
#     216, 0,   0,   0,
#     255, 0,   0,   0
# };
# 
# DEFINE_GRADIENT_PALETTE(waving_energy_gp){
#     0,   0,   120,   0,
#     32,  0,   120,   0,
#     128, 0,   220,  0,
#     216, 0,   120,   0,
#     255, 0,   120,   0
# };
# 
# CRGBPalette16 OYPalette = orange_yellow_gp;
# CRGBPalette16 cyberPalette = cyber_gp;
# CRGBPalette16 redOrangePalette = red_orange_gp;
# CRGBPalette16 whitePalette = white_gp;
# CRGBPalette16 VentPalette = white_gold1_Vent;
# CRGBPalette16 rainbowPalette = rainbow_gp;
# CRGBPalette16 white_gold1_palette = white_gold1_gp;
# CRGBPalette16 sasabi_green_palette = sasabi_green_gp;
# CRGBPalette16 storing_energy_palette = storing_energy_gp;
# CRGBPalette16 waving_energy_palette = waving_energy_gp;
# CRGBPalette16 pure_red_orange_palette =
#     CRGBPalette16(CRGB(50, 0, 0), CRGB(255, 10, 0));
# CRGBPalette16 pure_green_orange_palette =
#     CRGBPalette16(CRGB(0, 50, 0), CRGB(0, 100, 0));
# CRGBPalette16 footplate_flash1_palette =
#     CRGBPalette16(CRGB(100, 0, 0), CRGB(72, 26, 0));
# CRGBPalette16 footplate_flash2_palette =
#     CRGBPalette16(CRGB(72, 26, 0), CRGB(82, 20, 0), CRGB(82, 16, 0));
# CRGBPalette16 footplate_flash3_palette =
#     CRGBPalette16(CRGB(86, 28, 0), CRGB(86, 16, 40));
# CRGBPalette16 footplate_flash4_palette =
#     CRGBPalette16(CRGB(84, 16, 40), CRGB(24, 50, 60));
# CRGBPalette16 footplate_flash5_palette = CRGBPalette16(
#     CRGB(25, 30, 80), CRGB(82, 16, 40), CRGB(72, 10, 0), CRGB(84, 16, 40));
# CRGBPalette16 footplate_flash6_palette =
#     CRGBPalette16(CRGB(84, 16, 40), CRGB(50, 12, 76), CRGB(100, 0, 0));
# 
# 
#     // A mostly red palette with green accents and white trim.
# // "CRGB::Gray" is used as white to keep the brightness more uniform.
# const TProgmemRGBPalette16 RedGreenWhite_p FL_PROGMEM ={
#   CRGB::Red, CRGB::Red, CRGB::Red, CRGB::Red, 
#   CRGB::Red, CRGB::Red, CRGB::Red, CRGB::Red, 
#   CRGB::Red, CRGB::Red, CRGB::Gray, CRGB::Gray, 
#   CRGB::Green, CRGB::Green, CRGB::Green, CRGB::Green 
# };
#  
# // A mostly (dark) green palette with red berries.
# #define Holly_Green 0x00580c
# #define Holly_Red   0xB00402
# const TProgmemRGBPalette16 Holly_p FL_PROGMEM = {
#   Holly_Green, Holly_Green, Holly_Green, Holly_Green, 
#   Holly_Green, Holly_Green, Holly_Green, Holly_Green, 
#   Holly_Green, Holly_Green, Holly_Green, Holly_Green, 
#   Holly_Green, Holly_Green, Holly_Green, Holly_Red 
# };
#  
# // A red and white striped palette
# // "CRGB::Gray" is used as white to keep the brightness more uniform.
# const TProgmemRGBPalette16 RedWhite_p FL_PROGMEM = {
#   CRGB::Red,  CRGB::Red,  CRGB::Red,  CRGB::Red, 
#   CRGB::Gray, CRGB::Gray, CRGB::Gray, CRGB::Gray,
#   CRGB::Red,  CRGB::Red,  CRGB::Red,  CRGB::Red, 
#   CRGB::Gray, CRGB::Gray, CRGB::Gray, CRGB::Gray 
# };
#  
# // A mostly blue palette with white accents.
# // "CRGB::Gray" is used as white to keep the brightness more uniform.
# const TProgmemRGBPalette16 BlueWhite_p FL_PROGMEM = {
#   CRGB::Blue, CRGB::Blue, CRGB::Blue, CRGB::Blue, 
#   CRGB::Blue, CRGB::Blue, CRGB::Blue, CRGB::Blue, 
#   CRGB::Blue, CRGB::Blue, CRGB::Blue, CRGB::Blue, 
#   CRGB::Blue, CRGB::Gray, CRGB::Gray, CRGB::Gray
# };
#  
# // A pure "fairy light" palette with some brightness variations
# #define HALFFAIRY ((CRGB::FairyLight & 0xFEFEFE) / 2)
# #define QUARTERFAIRY ((CRGB::FairyLight & 0xFCFCFC) / 4)
# const TProgmemRGBPalette16 FairyLight_p FL_PROGMEM = {
#   CRGB::FairyLight, CRGB::FairyLight, CRGB::FairyLight, CRGB::FairyLight, 
#   HALFFAIRY,        HALFFAIRY,        CRGB::FairyLight, CRGB::FairyLight, 
#   QUARTERFAIRY,     QUARTERFAIRY,     CRGB::FairyLight, CRGB::FairyLight, 
#   CRGB::FairyLight, CRGB::FairyLight, CRGB::FairyLight, CRGB::FairyLight
# };
#  
# // A palette of soft snowflakes with the occasional bright one
# const TProgmemRGBPalette16 Snow_p FL_PROGMEM = {
#   0x304048, 0x304048, 0x304048, 0x304048,
#   0x304048, 0x304048, 0x304048, 0x304048,
#   0x304048, 0x304048, 0x304048, 0x304048,
#   0x304048, 0x304048, 0x304048, 0xE0F0FF 
# };
#  
# // A palette reminiscent of large 'old-school' C9-size tree lights
# // in the five classic colors: red, orange, green, blue, and white.
# #define C9_Red    0xB80400
# #define C9_Orange 0x902C02
# #define C9_Green  0x046002
# #define C9_Blue   0x070758
# #define C9_White  0x606820
# const TProgmemRGBPalette16 RetroC9_p FL_PROGMEM = {
#   C9_Red,    C9_Orange, C9_Red,    C9_Orange,
#   C9_Orange, C9_Red,    C9_Orange, C9_Red,
#   C9_Green,  C9_Green,  C9_Green,  C9_Green,
#   C9_Blue,   C9_Blue,   C9_Blue,
#   C9_White
# };
#  
# // A cold, icy pale blue palette
# #define Ice_Blue1 0x0C1040
# #define Ice_Blue2 0x182080
# #define Ice_Blue3 0x5080C0
# const TProgmemRGBPalette16 Ice_p FL_PROGMEM = {
#   Ice_Blue1, Ice_Blue1, Ice_Blue1, Ice_Blue1,
#   Ice_Blue1, Ice_Blue1, Ice_Blue1, Ice_Blue1,
#   Ice_Blue1, Ice_Blue1, Ice_Blue1, Ice_Blue1,
#   Ice_Blue2, Ice_Blue2, Ice_Blue2, Ice_Blue3
# };
# 
# // A palette simulating warm white city building lights at night
# // Captures the golden glow from office windows, apartment lights, and
# // occasional cooler fluorescent fixtures found in urban high-rises
# #define Building_Warm1    0xFFD060  // Golden warm white (strong yellow tone)
# #define Building_Warm2    0xFFC040  // Amber warm white (incandescent)
# #define Building_Warm3    0xFFE080  // Soft golden white
# #define Building_Warm4    0xFFE4AA  // Bright yellow-white
# #define Building_Warm5    0xFFCE00  // Deep amber (slight orange)
# #define Building_Warm6    0xFFC850  // Honey warm white
# #define Building_Warm7    0xFFB50F  // Rich golden yellow
# #define Building_Orange   0xFFBB7C  
# #define Building_Cool     0xC0D0E0  // Occasional cool fluorescent
# const TProgmemRGBPalette16 BuildingWarmWhite_p FL_PROGMEM = {
#   Building_Warm1, Building_Warm2, Building_Warm3, Building_Warm4,
#   Building_Warm5, Building_Warm1, Building_Warm6, Building_Warm2,
#   Building_Warm7, Building_Warm3, Building_Warm1, Building_Warm5,
#   Building_Warm2, Building_Orange, Building_Cool, Building_Warm1
# };
# 
# const NamedPalette namedPalettes[] = {
#     {"Heat", HeatColors_p},
#     {"lava", lava_gp},
#     {"fire", fire_gp},
# };
# 
# uint8_t paletteCount = ARRAY_SIZE(namedPalettes);

eyes_start = [
     {'type': 'keep'    , 'F': 1, 'l_max': 0   , 'l_lim': 0   , 'phi': phi0  , 'end_Time': 60  },
     {'type': 'math_now', 'F': 5, 'l_max': 100 , 'l_lim': 0   , 'phi': phi270, 'end_Time': 100 },
     {'type': 'math_now', 'F': 5, 'l_max': 1023, 'l_lim': 100 , 'phi': phi270, 'end_Time': 110 },
     {'type': 'math_now', 'F': 5, 'l_max': 1023, 'l_lim': 200 , 'phi': phi90 , 'end_Time': 150 },
     {'type': 'keep'    , 'F': 5, 'l_max': 200 , 'l_lim': 200 , 'phi': phi0  , 'end_Time': 300 },

]