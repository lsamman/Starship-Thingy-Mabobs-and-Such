using UnityEngine;

namespace STMS
{
    /// <summary>Stretches cables between pairs of transforms, whatever moves them: cableTop0.. holds a one-metre cable hanging along its -Y,
    /// cableEnd0.. is where it is tied.</summary>
    public class ModuleSTMSCable : PartModule
    {
        [KSPField] public string topName = "cableTop";
        [KSPField] public string endName = "cableEnd";
        [KSPField] public int count = 4;

        private Transform[] top, end;

        public override void OnStart(StartState state)
        {
            top = new Transform[count];
            end = new Transform[count];
            for (int i = 0; i < count; i++)
            {
                top[i] = part.FindModelTransform(topName + i);
                end[i] = part.FindModelTransform(endName + i);
                if (top[i] == null || end[i] == null) Debug.LogError("[STMS] cable " + i + " missing on " + part.name);
            }
        }

        public void LateUpdate()
        {
            if (top == null) return;
            for (int i = 0; i < count; i++)
            {
                if (top[i] == null || end[i] == null) continue;
                Vector3 d = end[i].position - top[i].position;
                float len = d.magnitude;
                if (len < 0.001f) continue;
                top[i].rotation = Quaternion.FromToRotation(top[i].rotation * Vector3.down, d) * top[i].rotation;
                top[i].localScale = new Vector3(1f, len / Mathf.Max(0.001f, top[i].parent.lossyScale.y), 1f);
            }
        }
    }
}
