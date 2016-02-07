
from .typed_objects import TypedWritableReferenceCount

class RenderEffects(TypedWritableReferenceCount):

    __slots__ = 'effects',

    def __init__(self):
        super().__init__()

        self.effects = []

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(len(self.effects))

        for effect in self.effects:
            manager.write_pointer(dg, effect)

RenderEffects.empty = RenderEffects()


class RenderEffect(TypedWritableReferenceCount):

    __slots__ = ()


class BillboardEffect(TypedWritableReferenceCount):

    __slots__ = ('off', 'up_vector', 'eye_relative', 'axial_rotate', 'offset',
                 'look_at_point')

    def __init__(self, up_vector, eye_relative, axial_rotate, offset=0,
                 look_at_point=(0, 0, 0)):
        super().__init__()

        self.off = False
        self.up_vector = up_vector
        self.eye_relative = eye_relative
        self.axial_rotate = axial_rotate
        self.offset = offset
        self.look_at_point = look_at_point

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_bool(self.off)
        dg.add_vec3(self.up_vector)
        dg.add_bool(self.eye_relative)
        dg.add_bool(self.axial_rotate)
        dg.add_stdfloat(self.offset)
        dg.add_vec3(self.look_at_point)

BillboardEffect.axis = BillboardEffect((0, 0, 1), False, True)
BillboardEffect.point_eye = BillboardEffect((0, 0, 1), True, False)
BillboardEffect.point_world = BillboardEffect((0, 0, 1), False, False)

# Pre-made RenderEffects for use in bam exporter
RenderEffects.billboard_axis = RenderEffects()
RenderEffects.billboard_axis.effects.append(BillboardEffect.axis)

RenderEffects.billboard_point_eye = RenderEffects()
RenderEffects.billboard_point_eye.effects.append(BillboardEffect.point_eye)

RenderEffects.billboard_point_world = RenderEffects()
RenderEffects.billboard_point_world.effects.append(BillboardEffect.point_world)
