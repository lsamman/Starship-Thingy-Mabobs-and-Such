"""Thrust-to-weight and delta-v per variant, and the flip gyros against the airstream. Masses from the configs."""
import math
G = 9.81
SL, VAC = 613, 674                                   # kN per engine at SL and in vacuum
ISP = dict(sl=327, slv=350, vac=380)
B_DRY = 20.9 + 3 * .5 + 21 * 1.1 + 14 * 1.1 + 7 * 1.15; B_P = 1340
eng = 3 * 1.15 + 6 * 1.5; gear = 3 * .7 + 2 * .3
V = dict(Crew=(16.3, 390), Cargo=(9.5 + 1.9, 390), Tanker=(2.0, 500))
for n, (fwd, prop) in V.items():
    dry = fwd + 5.5 + eng + gear; pay = dict(Crew=40, Cargo=60, Tanker=0)[n]
    m0 = B_DRY + B_P + dry + prop + pay
    tsl = 42 * SL / (m0 * G); f1 = 42 * SL
    mb = m0 - B_P * .93                               # 7% held back for the landing
    dv1 = 338 * G * math.log(m0 / mb); ms = dry + prop + pay
    dv2 = 368 * G * math.log(ms / (dry + pay + prop * .03))
    land = dry + pay * 0 + 12
    print(f'{n}: ship dry {dry:.1f} t, stack {m0:.0f} t, liftoff TWR {tsl:.2f}, ship TWR {(3*675+6*700)/(ms*G):.2f}, dv {dv1:.0f}+{dv2:.0f}={dv1+dv2:.0f} m/s, landing TWR on 3 SL {3*SL/(land*G):.2f}')
# flip: aero moment when the flow is broadside, q at terminal speed and at 3 g
m = 37.5 + 12; W = m * G; I = m * 30.9 ** 2 / 12
for k, name in ((1, 'terminal (drag = weight)'), (3, '3 g deceleration')):
    M = k * W * 3.0                                   # centre of pressure 3 m from the centre of mass
    print(f'{name}: aero moment {M:.0f} kNm, gyros 8000 kNm, net {(8000 - M) / I * 57.3:.0f} deg/s2')
