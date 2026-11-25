using System.Collections.Generic;
using UnityEngine;

namespace STMS
{
    /// <summary>Sits beside a ModuleDeployableSolarPanel: locks its sun tracking on demand, and swings the extended array between straight
    /// out and hanging down the hull. Before it swings, tracking is off and the pivot is back at centre; it stays locked until the array is
    /// straight out again. A retraction waits for that too.</summary>
    public class ModuleSTMSArrayTilt : PartModule
    {
        [KSPField] public string tiltTransform = "tilt";
        [KSPField] public float downAngle = -90f;
        [KSPField] public float tiltSpeed = 6f;
        [KSPField] public float centreSpeed = 20f;

        [KSPField(isPersistant = true)] public bool locked;
        [KSPField(isPersistant = true)] public bool down;
        [KSPField(isPersistant = true)] public float angle;

        [KSPField(guiActive = true, guiActiveEditor = true, guiName = "Array")] public string arrayState = "";

        private ModuleDeployableSolarPanel panel;
        private Transform tilt, pivot;
        private Quaternion tiltRest;
        private AnimationState deployAnim;
        private bool tracks, holding;
        private float heldSpeed = -1f;

        public override void OnStart(StartState state)
        {
            panel = part.FindModuleImplementing<ModuleDeployableSolarPanel>();
            tilt = part.FindModelTransform(tiltTransform);
            if (panel == null || tilt == null)
            {
                Debug.LogError("[STMS] array tilt: panel or transform missing on " + part.name);
                enabled = isEnabled = false;
                return;
            }
            tracks = panel.part.partInfo.partPrefab.FindModuleImplementing<ModuleDeployableSolarPanel>().isTracking;
            pivot = part.FindModelTransform(panel.pivotName);
            // rest poses come from the prefab: a copy made in the editor (symmetry, alt-click) starts with its source's pose, tilt included
            Transform tilt0 = part.partInfo.partPrefab.FindModelTransform(tiltTransform), pivot0 = part.partInfo.partPrefab.FindModelTransform(panel.pivotName);
            tiltRest = tilt0 != null ? tilt0.localRotation : tilt.localRotation;
            if (pivot0 != null) panel.originalRotation = pivot0.localRotation;
            Animation[] anims = part.FindModelAnimators(panel.animationName);
            if (anims.Length > 0) deployAnim = anims[0][panel.animationName];
            if (panel.deployState == ModuleDeployablePart.DeployState.RETRACTED)
            {
                down = false;
                angle = 0f;
            }
            Pose();
            panel.isTracking = tracks && !locked && !down && angle == 0f;
            UpdateUi();
        }

        public void Update()
        {
            if (panel == null || tilt == null || pivot == null) return;
            ModuleDeployablePart.DeployState s = panel.deployState;
            if (s == ModuleDeployablePart.DeployState.BROKEN) return;
            float dt = HighLogic.LoadedSceneIsEditor ? Time.deltaTime * 6f : TimeWarp.deltaTime;

            if (s == ModuleDeployablePart.DeployState.RETRACTING)
            {
                // retract asked for while hanging down: hold the clip on its last frame until the array is straight out
                down = false;
                if (angle != 0f && deployAnim != null)
                {
                    if (!holding)
                    {
                        heldSpeed = deployAnim.speed < 0f ? deployAnim.speed : -1f;
                        holding = true;
                    }
                    deployAnim.speed = 0f;
                    deployAnim.normalizedTime = 1f;
                }
            }
            else if (s != ModuleDeployablePart.DeployState.EXTENDED) down = false;

            bool moving = false;
            if (down && angle != downAngle)
            {
                Quaternion centre = panel.originalRotation;
                pivot.localRotation = Quaternion.RotateTowards(pivot.localRotation, centre, centreSpeed * dt);
                if (Quaternion.Angle(pivot.localRotation, centre) < 0.05f)
                {
                    pivot.localRotation = centre;
                    angle = Mathf.MoveTowards(angle, downAngle, tiltSpeed * dt);
                }
                moving = true;
            }
            else if (!down && angle != 0f)
            {
                angle = Mathf.MoveTowards(angle, 0f, tiltSpeed * dt);
                moving = true;
            }
            if (holding && angle == 0f)
            {
                if (deployAnim != null) deployAnim.speed = heldSpeed;
                holding = false;
            }
            if (moving) Pose();
            panel.isTracking = tracks && !locked && !down && angle == 0f;
            UpdateUi();
        }

        private void Pose()
        {
            tilt.localRotation = tiltRest * Quaternion.Euler(angle, 0f, 0f);
        }

        private void UpdateUi()
        {
            bool ext = panel.deployState == ModuleDeployablePart.DeployState.EXTENDED;
            bool straight = !down && angle == 0f;
            Events["ToggleDown"].active = ext;
            Events["ToggleDown"].guiName = down ? "Rotate Array Out" : "Rotate Array Down";
            Events["ToggleLock"].active = ext && straight && tracks;
            Events["ToggleLock"].guiName = locked ? "Unlock Tracking" : "Lock Tracking";
            Fields["arrayState"].guiActive = Fields["arrayState"].guiActiveEditor = ext;
            arrayState = straight ? (locked ? "Out, tracking locked" : "Out, tracking") : angle == downAngle ? "Down, locked" : "Moving";
        }

        private IEnumerable<ModuleSTMSArrayTilt> Group()
        {
            yield return this;
            foreach (Part p in part.symmetryCounterparts)
            {
                ModuleSTMSArrayTilt m = p.FindModuleImplementing<ModuleSTMSArrayTilt>();
                if (m != null && m.panel != null) yield return m;
            }
        }

        private void SetDown(bool value)
        {
            down = value && panel != null && panel.deployState == ModuleDeployablePart.DeployState.EXTENDED;
        }

        [KSPEvent(guiActive = true, guiActiveEditor = true, guiActiveUnfocused = true, externalToEVAOnly = true, unfocusedRange = 4f, guiName = "Rotate Array Down")]
        public void ToggleDown()
        {
            bool value = !down;
            foreach (ModuleSTMSArrayTilt m in Group()) m.SetDown(value);
        }

        [KSPEvent(guiActive = true, guiActiveEditor = true, guiName = "Lock Tracking")]
        public void ToggleLock()
        {
            bool value = !locked;
            foreach (ModuleSTMSArrayTilt m in Group()) m.locked = value;
        }

        [KSPAction("Toggle Array Down")] public void ToggleDownAction(KSPActionParam p) { SetDown(!down); }
        [KSPAction("Rotate Array Down")] public void DownAction(KSPActionParam p) { SetDown(true); }
        [KSPAction("Rotate Array Out")] public void OutAction(KSPActionParam p) { SetDown(false); }
        [KSPAction("Toggle Tracking Lock")] public void LockAction(KSPActionParam p) { locked = !locked; }
    }
}
