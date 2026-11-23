"""Shared by the three crane parts (after StarshipThingyMabobsAndSuch' cargo winch). Frame: origin on the ceiling node, boom runs along -y."""
from common import *
V = Vector


def bar(g, x0, x1, y0, y1, z0, z1, zone, bevel=.012):
    g.add(box(x1 - x0, y1 - y0, z1 - z0, zone=zone, bevel=bevel), T((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def channel(g, x, w, y0, y1, z0, z1, zone, t=.02):
    bar(g, x - w / 2, x + w / 2, y0, y1, z1 - t, z1, zone)
    for s in (-1, 1):
        bar(g, x + s * w / 2 - t / 2, x + s * w / 2 + t / 2, y0, y1, z0, z1, zone)


def rig(name, P, M, owner_anchor, owner_servo, anchor_pos, servo_pos, skin, weights, far):
    """An armature with a fixed bone and the piston bone, and one skinned mesh (see StarshipThingyMabobsAndSuch). KSP writes the servo
    transform's localPosition, so the armature carries the rest position and the piston bone sits at zero inside it.
    `far` adds a zero-area triangle so Unity's culling bounds cover the full travel."""
    arm = bpy.data.armatures.new(name); ao = bpy.data.objects.new(name, arm)
    P.coll.objects.link(ao); P.place(ao, T(*servo_pos), P.model)
    bpy.context.view_layer.objects.active = ao
    bpy.ops.object.mode_set(mode='EDIT')
    for nm, pos in ((owner_anchor, V(anchor_pos) - V(servo_pos)), (owner_servo, V((0, 0, 0)))):
        b = arm.edit_bones.new(nm); b.head = pos; b.tail = (pos[0], pos[1] + .1, pos[2])
    bpy.ops.object.mode_set(mode='OBJECT')
    n = len(skin.v); skin.v += [tuple(far)] * 3; skin.face([n, n + 1, n + 2], [(0, 0)] * 3)
    weights = list(weights) + [0.0] * 3
    so = P.mesh(name + '_skin', skin, M, parent=ao)
    mod = so.modifiers.new('arm', 'ARMATURE'); mod.object = ao
    ga = so.vertex_groups.new(name=owner_anchor); gs = so.vertex_groups.new(name=owner_servo)
    for i, w in enumerate(weights):
        if w < 1: ga.add([i], 1 - w, 'REPLACE')
        if w > 0: gs.add([i], w, 'REPLACE')
    return so
