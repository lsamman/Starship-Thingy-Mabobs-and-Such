"""Shared by the three winch parts."""
import bpy
from mathutils import Matrix, Vector as V
from sl import *
import layout as L


def start(name):
    enable_addon(); clean_scene()
    P = Part(name)
    M = P.material('sep_cw', spec=(.8, .8, .8), shininess=.45)
    return P, M, {k: Zone(*v, atlas=L.ATLAS, ppm=300) for k, v in L.Z.items()}


def bar(g, x0, x1, y0, y1, z0, z1, zone, bevel=.008):
    """Axis-aligned box between two corners."""
    g.add(box(x1 - x0, y1 - y0, z1 - z0, zone=zone, bevel=bevel), T((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def channel(g, x, w, y0, y1, z0, z1, zone, t=.018):
    """A rail open underneath: top plate and two webs, so a lug can run along its slot."""
    bar(g, x - w / 2, x + w / 2, y0, y1, z1 - t, z1, zone)
    for s in (-1, 1):
        bar(g, x + s * w / 2 - t / 2, x + s * w / 2 + t / 2, y0, y1, z0, z1, zone)


def rig(name, P, M, owner_anchor, owner_servo, anchor_pos, servo_pos, skin, weights, far):
    """An armature with a fixed bone and the piston bone, and one skinned mesh. weights[i] is the piston's share of
    vertex i. `far` adds a zero-area triangle on the fixed bone: Unity culls a skinned mesh by its rest bounds, and
    without this the moved end would vanish whenever the rest position is off screen.
    KSP writes the servo transform's localPosition as axis * extension, so the piston bone sits at zero in the armature. And in flight
    its joint's anchor is servoParentTransform * Vector3, which Unity takes with w = 0: the parent's own position is lost. So the armature
    must sit at the part's origin too (servo_pos = the origin), or the stages jump by its offset as soon as physics starts."""
    arm = bpy.data.armatures.new(name)
    ao = bpy.data.objects.new(name, arm)
    P.coll.objects.link(ao)
    P.place(ao, T(*servo_pos), P.model)
    bpy.context.view_layer.objects.active = ao
    bpy.ops.object.mode_set(mode='EDIT')
    for nm, pos in ((owner_anchor, V(anchor_pos) - V(servo_pos)), (owner_servo, V((0, 0, 0)))):
        b = arm.edit_bones.new(nm); b.head = pos; b.tail = (pos[0], pos[1] + .1, pos[2])
    bpy.ops.object.mode_set(mode='OBJECT')
    n = len(skin.v)
    skin.v += [tuple(far), tuple(far), tuple(far)]
    skin.face([n, n + 1, n + 2], [(0, 0), (0, 0), (0, 0)])
    weights = list(weights) + [0.0] * 3
    so = P.mesh(name + '_skin', skin, M, parent=ao)
    mod = so.modifiers.new('arm', 'ARMATURE'); mod.object = ao
    ga = so.vertex_groups.new(name=owner_anchor); gs = so.vertex_groups.new(name=owner_servo)
    for i, w in enumerate(weights):
        if w < 1:
            ga.add([i], 1 - w, 'REPLACE')
        if w > 0:
            gs.add([i], w, 'REPLACE')
    return so
