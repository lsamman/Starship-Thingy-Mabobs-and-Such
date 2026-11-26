using Expansions.Serenity;
using UnityEngine;

namespace STMS
{
    /// <summary>Keeps a bay door and the crane frame on one of its nodes out of each other: the door will not close while the frame is
    /// out, and the frame will not run out while the door is not fully open. Either way it says why on screen.</summary>
    public class ModuleSTMSDoorGuard : PartModule
    {
        [KSPField] public string animationName = "CargoDoor";
        [KSPField] public string guardNode = "crane";
        [KSPField] public float outLimit = -0.15f;

        private ModuleAnimateGeneric door;
        private AttachNode node;
        private float lastTime = -1f, lastSay;

        public override void OnStart(StartState state)
        {
            foreach (ModuleAnimateGeneric m in part.FindModulesImplementing<ModuleAnimateGeneric>())
                if (m.animationName == animationName) door = m;
            node = part.FindAttachNode(guardNode);
        }

        private ModuleRoboticServoPiston Frame()
        {
            Part p = node != null ? node.attachedPart : null;
            if (p == null)
                foreach (Part c in part.children)
                    if (c.srfAttachNode != null && c.FindAttachNode("mount") != null && c.partInfo.name == "STMS.HLS.Crane") p = c;
            return p != null ? p.FindModuleImplementing<ModuleRoboticServoPiston>() : null;
        }

        private void Say(string s)
        {
            if (Time.realtimeSinceStartup - lastSay < 3f) return;
            lastSay = Time.realtimeSinceStartup;
            ScreenMessages.PostScreenMessage(s, 4f, ScreenMessageStyle.UPPER_CENTER);
        }

        public void Update()
        {
            if (door == null || !(HighLogic.LoadedSceneIsFlight || HighLogic.LoadedSceneIsEditor)) return;
            ModuleRoboticServoPiston f = Frame();
            if (f == null) { lastTime = door.animTime; return; }
            bool frameOut = f.currentExtension < outLimit || f.targetExtension < outLimit;
            float t = door.animTime;
            if (frameOut && lastTime >= 0f && t < lastTime - 1e-4f)
            {
                door.Toggle();                                   // closing on the frame: back up again
                Say("Bring the crane frame in (Target Extension 0) before closing the door");
            }
            else if (!frameOut || t > 0.999f) { }
            else if (f.targetExtension < outLimit)
            {
                f.targetExtension = 0f;                          // running out through a door that is not open
                Say("Open the door fully before running the crane frame out");
            }
            lastTime = door.animTime;
        }
    }
}
