ATLAS = 2048
ZONES = dict(panel=(0, 0, 1024, 512), hex=(1024, 0, 512, 512), floor=(1536, 0, 512, 512), ceil=(0, 512, 512, 512), bench=(512, 512, 512, 256), wood=(512, 768, 512, 256), console=(1024, 512, 512, 512),
             door=(1536, 512, 512, 512), locker=(0, 1024, 512, 512), curtain=(512, 1024, 256, 512), suit=(768, 1024, 256, 512), screen=(1024, 1024, 1024, 256))
for _i, _n in enumerate(('white', 'grey', 'dark', 'black', 'metal', 'led', 'orange', 'blue', 'green', 'pillow', 'yellow', 'red')):
    ZONES[_n] = (1024 + (_i % 8) * 128, 1280 + (_i // 8) * 128, 128, 128)
# Cabins. Heights are in the part's own frame. Each deck: floor, ceiling, theme, seats, windows (z, count, half-span, w, h) or 'big'.
VARIANTS = {
    'hls': dict(part='STMS_HLS_Crew', title='HLS', decks=[
        dict(floor=3.45, ceil=None, theme='flight', seats=8, win=(4.376, 10, 36.0, .31, .74)),
        dict(floor=.48, ceil=1.80, theme='airlock', seats=0, win=None)]),
    'crew': dict(part='STMS_B3_NoseCrew', title='Crew', decks=[
        dict(floor=2.22, ceil=None, theme='flight', seats=4, win='big'),
        dict(floor=.92, ceil=2.12, theme='commons', seats=4, win=(1.70, 9, 40, .3125, .2625)),
        dict(floor=-.40, ceil=.82, theme='bunks', seats=2, win=(.40, 9, 40, .3125, .2625)),
        dict(floor=-1.70, ceil=-.50, theme='bunks', seats=2, win=(-.90, 11, 48, .3125, .2625))]),
    'crewcargo': dict(part='STMS_B3_NoseCrewCargo', title='Crew-Cargo', decks=[
        dict(floor=2.22, ceil=None, theme='flight', seats=4, win='big'),
        dict(floor=.92, ceil=2.12, theme='commons', seats=0, win=(1.70, 9, 40, .3125, .2625))]),
}
