
from .typed_objects import TypedWritableReferenceCount

class RenderEffects(TypedWritableReferenceCount):
    bam_type_name = "RenderEffects"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # For now, just pretend there are 0 render effects.
        dg.add_uint16(0)

RenderEffects.empty = RenderEffects()
