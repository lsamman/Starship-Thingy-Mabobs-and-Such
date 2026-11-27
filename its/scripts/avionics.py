"""The Avionics cockpit option (B9 'Cockpit: Classic / Avionics'): ASET Props and ASET Avionics panels run by RasterPropMonitor,
with the capabilities of ASET's ALCOR cockpit. None of ASET's files are shipped; the props are placed by name, as the cabins
already place HabTechProps. Each prop sits on our boards the way ALCOR mounts it (its rotation against the panel, the height of its
origin over the panel and its scale, from ALCOR's cockpit by alexustas, maintained by JonnyOThan, CC BY-NC-SA 3.0); its footprint
comes from its model. Both are in its/data/aset_mounts.json (its/scripts/aset_mounts.py rebuilds it from an ALCOR and ASET install).
The panels below are ours: which props, in which rows, on which station."""
import json, os

K = 1.5             # ALCOR's props are sized for a 1.2 m capsule; ours are SEP-scale cabins with Orion-style seats
GAP = .010          # between props in a row, and between rows
PAD = .022          # board margin round a panel

# Panels: rows, top to bottom; a row is props left to right ('' leaves a prop-sized gap of the row's first prop).
PANELS = {
    'sas': [['Lable_ATTITUDE', 'Lable_StabMode'],
            ['onSASIndicator', 'onRCSIndicator', 'onRCSACTIVEIndicator', 'OnPREC_MODE', 'DigitalIndicator_SASMode'],
            ['pb_SAS_ON-FD1-B2', 'pb_sas_STAB-FD2-G1', 'pb_sas_MANEUVER-FD2-G1', 'pb_sas_PROGRADE-FD2-G1', 'pb_sas_RETROGRADE-FD2-G1', 'pb_sas_NORMAL-FD2-G1'],
            ['SwitchRotary_SAS_SpeedMode_Selector-01', 'pb_sas_ANTINORMAL-FD2-G1', 'pb_sas_RADIALIN-FD2-G1', 'pb_sas_RADIALOUT-FD2-G1', 'pb_sas_TARGET-FD2-G1', 'pb_sas_ANTITARGET-FD2-G1'],
            ['pb_RCS-SH02-B6-C2', 'pb_INPUT_CTRL-SH02-B5', 'pb_GIMBAL_LOCK-FD1-B2', 'pb_CLEAR_TARGET-F01-B1-G1', 'pb_CLEAR_MNVR_NODE-F01-B1-G1']],
    'stage': [['Lable_PROPULSION'],
              ['MasterAlarm', 'onStageReadyIndicator', 'onMECOIndicator', 'onENGFAILUREIndicator'],
              ['StageSwitch', 'switchRotary_StageLock', 'tggl_ABORT_T1-G3-B4-C1Y-S', 'tggl_UNDOCK_T1-G3-B4-C1Y-S', 'onVESSEL_DOCKED_ONIndicator'],
              ['swToggleEngines', 'tggl_ENGINE_MODE_T1_G1-B3-S', 'THRUST_LIMIT_Selector', 'pb_RESET_THRUST_LIMIT-F01-B1-G1', 'pb_THRTL_CUT-FT-G1', 'pb_THRTL_FULL-FT-G1']],
    'gear': [['Lable_LGear', 'onLANDINGGEAR_DEPLOYED_Indicator', 'onLANDINGGEAR_DEPLOYING_Indicator', 'onLANDINGGEAR_RETRACTING_Indicator', 'onLANDINGGEAR_RETRACTED_Indicator', 'onLANDINGGEAR_BROKEN_ONIndicator'],
             ['tggl_GEAR_CTRL_T5W-B14-S', 'pb_GEAR_DN_AUTO-SH01-B6-C2', 'pb_BRAKE_SET-F01-B2', 'OnBrakesIndicator', 'ASET_BRAKEFORCE_Dial', 'DigitalIndicator_BrakeForce_Display'],
             ['Lable_PARACHUTE', 'tggl_CHUTE_ARM_T1_G1-B2-S', 'pb_CHUTE_DEPLOY-F02-B6-C2', 'pb_CHUTE_CUT-F01-B6-C2', 'On_CHUTE_SAFE_TO_DEPLOY'],
             ['Lable_Wheels_Brakes'],
             ['switchTumble_Lights', 'onLIGHTIndicator', 'pb_FLOOD_LIGHT-FD4', 'pb_PANEL_LIGHT-FD4', 'pb_FLIGHTDECKLIGHT-FD4', 'pb_ENGINEERDECK_LIGHT-FD']],
    'ag': [['ActionGroupPlate01', 'ActionGroupPlate02', 'ActionGroupPlate03', 'ActionGroupPlate04', 'ActionGroupPlate05'],
           ['pb_AG01-F03-G1', 'pb_AG02-F03-G1', 'pb_AG03-F03-G1', 'pb_AG04-F03-G1', 'pb_AG05-F03-G1'],
           ['ActionGroupPlate06', 'ActionGroupPlate07', 'ActionGroupPlate08', 'ActionGroupPlate09', 'ActionGroupPlate00'],
           ['pb_AG06-F03-G1', 'pb_AG07-F03-G1', 'pb_AG08-F03-G1', 'pb_AG09-F03-G1', 'pb_AG10-F03-G1'],
           ['DigitalIndicator_CURRENT_WARP', 'OnWARP', 'pb_Warp_Dec', 'pb_Warp_Inc', 'pb_Warp_Next', 'pb_Warp_Kill']],
    'mj': [['Lable_AP_Orbit', 'pb_MJ_PROGRADE-FD5-G1', 'pb_MJ_RETROGRADE-FD5-G1', 'pb_MJ_NMLplus-FD5-G1', 'pb_MJ_NMLminus-FD5-G1', 'pb_MJ_RADplus-FD5-G1', 'pb_MJ_RADminus-FD5-G1'],
           ['Lable_AP_Target', 'pb_MJ_TGTplus-FD5-G1', 'pb_MJ_TGTminus-FD5-G1', 'pb_MJ_PARplus-FD5-G1', 'pb_MJ_PARminus-FD5-G1', 'pb_MJ_RVELplus-FD5-G1', 'pb_MJ_RVELminus-FD5-G1'],
           ['Lable_Surface', 'pb_MJ_SURF_UP-FD5-G1', 'pb_MJ_SURF_PROGRADE-FD5-G1', 'pb_MJ_SURF_RETROGRADE-FD5-G1', 'pb_MJ_SURF_HORZVELplus-FD5-G1', 'pb_MJ_SURF_HORZVELminus-FD5-G', 'pb_MJ_MNVR_NODE-FD5-G1'],
           ['pb_MJ_ROLL_0-FT', 'pb_MJ_ROLL_90-FT', 'pb_MJ_ROLL_180-FT', 'pb_MJ_ROLL_270-FT', 'pb_MJ_HOLD_ROLL-F03G-B2', 'pb_MJ_KILLROTATION-F03-G1', 'pb_MJ_AP_OFF-F03R-G1'],
           ['pb_MJ_HOHMANN_TRNSF-F03G-B2', 'pb_MJ_CIRCULARIZE-F03G-B2', 'pb_MJ_CHANGE_PE-F03G-B2', 'pb_MJ_CHANGE_AP-F03G-B2', 'pb_MJ_SET_LAUNCH_INCL-F03G-B2', 'pb_MJ_SET_LAUNCH_ALT-F03G-B2', 'pb_MJ_EXEC_MNVR-F03B-B3'],
           ['pb_MJ_AUTO_ASCENT-F03B-C2', 'pb_MJ_AUTO_RNDZ-F03B-C2', 'pb_MJ_AUTO_DOCK-F03B-C2', 'pb_MJ_AUTO_LAND-F03B-C2']],
    'numin': [['DigitalIndicator_ORBIT_NUM_INPUT'],
              ['tggl_NUM_INPUT_1M-T1-D', 'tggl_NUM_INPUT_100K-T1-D', 'tggl_NUM_INPUT_10K-T1-D', 'tggl_NUM_INPUT_1K-T1-D', 'tggl_NUM_INPUT_100-T1-D', 'tggl_NUM_INPUT_10-T1-D'],
              ['pb_NUM_INPUT_RESET-F02', 'pb_NUM_INPUT_GET_ATM-F02', 'pb_NUM_INPUT_GET_AP-F02', 'pb_NUM_INPUT_GET_PE-F02'],
              ['pb_NUM_INPUT_GET_INCL-F02', 'pb_NUM_INPUT_GET_TGT_AP-F02', 'pb_NUM_INPUT_GET_TGT_PE-F02', 'pb_NUM_INPUT_GET_TGT_INCL-F02']],
    'caution': [['SmallPlate_CAUTIONS_and_WARNINGS'],
                ['AlarmGroundProximityIndicator', 'LowALTIndicator', 'AlarmHighSlopeIndicator', 'AlarmTurnOverIndicator', 'onHighGIndicator', 'AlarmHEATIndicator'],
                ['AlarmEngineOverheatIndicator', 'LowFuelIndicator', 'LowOxidizerIndicator', 'LowMonopropIndicator', 'LowChargeIndicator', 'LowTWRIndicator'],
                ['onCONTACTIndicator', 'onDESIndicator', 'onAirBrakingIndicator', 'AlarmLLegsIndicator', 'onLLEGSIndicator', 'onBattChargingIndicator'],
                ['gpws10', 'pb_GPWS_ON-OFF-SH01-B6-C2', 'pb_AVAS_ON-OFF-FT-B2', 'pb_WARN_HIGH_G_ON-OFF-FT-B2', 'pb_WARN_SLOPE_ON-OFF-FT-B2', 'pb_WARN_TUMBLE_ON-OFF-FT-B2'],
                ['ASET_ALT_WARN_Dial', 'DigitalIndicator_ALT_WARN_SetupDisplay', 'DigitalIndicator_ImpactSPEED', 'DigitalIndicator_Multi01', 'DigitalIndicator_Multi02']],
    'prop': [['Lable_Propellants'],
             ['IndicatorADV_FUEL', 'IndicatorADV_OXIDIZER', 'IndicatorADV_MONOPROP', 'IndicatorADV_XENONGAS', 'IndicatorADV_SolidFuel', 'IndicatorADV_FUELSTAGE', 'IndicatorADV_OXIDIZERSTAGE', 'IndicatorADV_STAGE'],
             ['IndicatorADV_THROTTLE', 'IndicatorADV_THRUST', 'IndicatorADV_THRUSTLIMIT', 'IndicatorADV_HEAT', 'IndicatorADV_EngineTemp', 'IndicatorADV_PodTemp', 'IndicatorADV_FUEL_consumption', 'IndicatorADV_OXIDIZER_consumption'],
             ['DigitalIndicator_TWR', 'DigitalIndicator_TWRMAX', 'DigitalIndicator_ISP', 'DigitalIndicator_THRUST', 'DigitalIndicator_THRUSTMAX'],
             ['DigitalIndicator_DELTAV', 'DigitalIndicator_DELTAVTOTAL', 'DigitalIndicator_GFORCE', 'DigitalIndicator_EngineTemp', 'DigitalIndicator_Throttle']],
    'env': [['Lable_ENVIRONMENTAL', 'Lable_Temperature', 'Lable_Atmosphere'],
            ['DigitalIndicator_EXTTemp', 'DigitalIndicator_AMB_Temp', 'DigitalIndicator_SURF_Temp', 'DigitalIndicator_Temp'],
            ['DigitalIndicator_AtmDen', 'DigitalIndicator_DYNAMICPRESSURE', 'DigitalIndicator_EFFECTIVEACCEL', 'GforceDisplay']],
    'power': [['Lable_PowerSupply', 'IndicatorADV_CHARGE', 'IndADV_2Scales_ChargeCons', 'SwitchRotary-5pos-ElecOutput_Selector', 'DigitalIndicator_Elec_Output'],
              ['swTumble_SOLAR_DEPLOY', 'onSOLARARRAY_DEPLOYED_ONIndicator', 'onSOLARARRAY_RETRACTED_ONIndicator', 'onSOLARARRAY_ACTIVE_ONIndicator', 'onSOLARARRAY_BROKEN_ONIndicator', 'onSOLARARRAY_AVAILABLE_ONIndicator'],
              ['swTumbleFUELCELL', 'onFUELCELL_ACTIVE_ONIndicator', 'onFUELCELL_AVAILABLE_ONIndicator', 'onGENERATOR_ACTIVE_ONIndicator', 'onGENERATOR_AVAILABLE_ONIndicator', 'onALTERNATOR_ACTIVE_ONIndicator']],
    'comms': [['SwitchFlatPanel_CommNet', 'On_COMMNET_CONNECTED', 'On_NO_SIGNAL', 'DI_CommNet_Signal_Strength'],
              ['SwitchFlatPanel_VoiceComm', 'On_CHATTERER_ON', 'On_CHATTERER_STBY', 'On_CHATTERER_RECV', 'On_CHATTERER_XMIT', 'pb_CHATTERER_PTT-F03-G1'],
              ['DI_Chatterer_XMIT_Level', 'DI_Chatterer_RECV_Level']],
    'dock': [['DigitalIndicator_DockingMulti01', 'On_DOCKPORT_ISREF', 'OnTGT_DOCKPORT_SELECTED', 'onAPPROACHIndicator', 'onDEAPRTIndicator'],
             ['On_DOCKING_MODE_UI', 'On_STAGING_MODE_UI']],
    'mfd': [['ALCORMFD40x20']],
    'mfd2': [['ALCORMFD40x20', 'ALCORMFD40x20']],
    # camera monitors (its/patches/STMS_CamMonitors.cfg): the pilot gets the landing camera, the commander the docking camera
    'mfdL': [['STMS_CamMFD_Landing', 'ALCORMFD40x20']],
    'mfdD': [['ALCORMFD40x20', 'STMS_CamMFD_Docking']],
    'mfd60': [['ALCORMFD60x30']],
    'ctrl': [['RCS_Stick_ADV', 'ALCORThrottleCtrl', 'ALCORRotationCtrl']],      # translation (left), throttle, rotation (right)
    'aux': [['JSIMainCompUnit'],
            ['IndicatorPanel5x3-plugins01', 'IndicatorPanel5x3-plugins02', 'FuelMonitor', 'switchRotary_ResLock']],
    # on the cabin walls, as ALCOR stows things: on velcro, checklists and books, timers, a camera, safety kit
    'manuals': [['VelcroPad', 'CrewManual_AscentChklist', 'CrewManual_OrbChklist', 'CrewManual_EVAChklist', 'CrewManual_MalfunctionChklist'],
                ['CrewManual_FlightPlan', 'CrewManual_SystemsDataBook', 'CrewManual_ReferenceDataBook', 'CrewManual_DeorbitPreparationBook']],
    'desk': [['PortableTimer', 'PortableTimer']],
    'kit': [['SmallExtinguisher', 'MediumBag_FirstAid', 'FireEqupStorage'], ['BigBag_EVAsupply01', 'BigBagFood02', 'BigBagExtraWater']],
}
# Stations along a console, left to right as seen from the seats: (panels on the sloped face, panels on the knee board below it).
STATIONS = [(['mfd60', 'caution'], ['gear', 'dock']), (['mfdL', 'sas'], ['stage', 'ctrl']), (['mfdD', 'mj', 'comms'], ['numin', 'ag']), (['mfd', 'prop', 'env'], ['power', 'aux'])]
WALLS = [['manuals', 'desk'], ['kit']]      # boards on the walls beside the console's ends, left and right
MOUNTS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'aset_mounts.json')))['props']


def used():
    return sorted({n for p in PANELS.values() for r in p for n in r if n})


def panel_size(name, f):
    """Width, height of a panel at scale f (ALCOR's scale x f), with each row's height."""
    rows = []
    for r in PANELS[name]:
        ps = [MOUNTS[n] for n in r if n]
        w = sum((p['hi'][0] - p['lo'][0]) * f for p in ps) + GAP * (len(r) - 1); h = max((p['hi'][1] - p['lo'][1]) * f for p in ps)
        rows.append((w, h))
    return max(w for w, _ in rows) + 2 * PAD, sum(h for _, h in rows) + GAP * (len(rows) - 1) + 2 * PAD, rows


def layout(panels, W, H):
    """Panels flowed into columns, top to bottom then left to right, centred on a W x H board; shrunk until they fit.
    Returns (scale, [(panel, x0, y_top, w, h)]) with x from the board's left edge and y down from its top edge."""
    f = K
    while True:
        cols, col, ch = [], [], 0.0
        for p in panels:
            w, h, _ = panel_size(p, f)
            if col and ch + GAP + h > H: cols.append(col); col, ch = [], 0.0
            col.append((p, w, h)); ch += h + (GAP if len(col) > 1 else 0)
        cols.append(col)
        tw = sum(max(w for _, w, _ in c) for c in cols) + GAP * (len(cols) - 1); th = max(sum(h for _, _, h in c) + GAP * (len(c) - 1) for c in cols)
        if (tw <= W and th <= H) or f < .4: break
        f *= .96
    out, x = [], (W - tw) / 2
    for c in cols:
        cw = max(w for _, w, _ in c); y = (H - (sum(h for _, _, h in c) + GAP * (len(c) - 1))) / 2
        for p, w, h in c: out.append((p, x + (cw - w) / 2, y, w, h)); y += h + GAP
        x += cw + GAP
    return f, out


def props_of(name, f, w):
    """The props of a panel w wide at scale f: (prop, x, y, z, rotation (9, board frame), scale), x right from the panel's left
    edge, y down from its top edge (both to the prop's origin), z its origin's height over the board. Rows centred."""
    _, _, rows = panel_size(name, f); y = PAD; out = []
    for r, (rw, rh) in zip(PANELS[name], rows):
        x = (w - rw) / 2
        for n in r:
            m = MOUNTS[n]; pw = (m['hi'][0] - m['lo'][0]) * f; ph = (m['hi'][1] - m['lo'][1]) * f
            out.append((n, x - m['lo'][0] * f, y + (rh - ph) / 2 + m['hi'][1] * f, m['h'] * f, m['R'], m['s'] * f)); x += pw + GAP
        y += rh + GAP
    return out
