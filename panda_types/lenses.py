__all__ = ['Lens', 'PerspectiveLens', 'OrthographicLens', 'MatrixLens']

from .typed_objects import TypedWritableReferenceCount

class Lens(TypedWritableReferenceCount):

    UF_film_width           = 0x0001
    UF_film_height          = 0x0002
    UF_focal_length         = 0x0004
    UF_hfov                 = 0x0008
    UF_vfov                 = 0x0010
    UF_aspect_ratio         = 0x0020
    UF_view_hpr             = 0x0040
    UF_view_vector          = 0x0080
    UF_interocular_distance = 0x0100
    UF_convergence_distance = 0x0200
    UF_view_mat             = 0x0400
    UF_keystone             = 0x0800
    UF_min_fov              = 0x1000
    UF_custom_film_mat      = 0x2000

    __slots__ = ('change_event', 'coordinate_system', 'film_width', 'film_height',
                 'film_offset', 'focal_length', 'hfov', 'vfov', 'min_fov',
                 'aspect_ratio', 'near_distance', 'far_distance',
                 'interocular_distance', 'convergence_distance', 'view_hpr',
                 'view_vector', 'up_vector', 'view_mat', 'keystone',
                 'custom_film_mat')

    def __init__(self):
        super().__init__()

        self.change_event = None
        self.coordinate_system = 0 # CS_default
        self.film_width = None
        self.film_height = None
        self.film_offset = (0.0, 0.0)
        self.focal_length = None
        self.hfov = None
        self.vfov = None
        self.min_fov = None
        self.aspect_ratio = None
        self.near_distance = 1.0
        self.far_distance = 100000.0

        self.interocular_distance = None
        self.convergence_distance = None
        self.view_hpr = None
        self.view_vector = None
        self.up_vector = (0.0, 0.0, 1.0)
        self.view_mat = None
        self.keystone = None
        self.custom_film_mat = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        user_flags = 0

        dg.add_string(self.change_event or "")
        dg.add_uint8(self.coordinate_system)

        def _write_prop(prop, default):
            if prop is not None:
                dg.add_stdfloat(prop)
                return 1
            else:
                dg.add_stdfloat(default)
                return 0

        user_flags |= _write_prop(self.film_width, 1.0) and Lens.UF_film_width
        user_flags |= _write_prop(self.film_height, 1.0) and Lens.UF_film_height
        dg.add_vec2(self.film_offset)
        user_flags |= _write_prop(self.focal_length, 1.0) and Lens.UF_focal_length
        user_flags |= _write_prop(self.hfov, 30.0) and Lens.UF_hfov
        user_flags |= _write_prop(self.vfov, 30.0) and Lens.UF_vfov
        user_flags |= _write_prop(self.aspect_ratio, 1.0) and Lens.UF_aspect_ratio
        dg.add_stdfloat(self.near_distance)
        dg.add_stdfloat(self.far_distance)

        if manager.file_version < (6, 41):
            dg.add_uint16(user_flags)
            return

        if self.view_hpr is not None:
            user_flags |= Lens.UF_view_hpr
        if self.view_vector is not None:
            user_flags |= Lens.UF_view_vector
        if self.interocular_distance is not None:
            user_flags |= Lens.UF_interocular_distance
        if self.convergence_distance is not None:
            user_flags |= Lens.UF_convergence_distance
        if self.view_mat is not None:
            user_flags |= Lens.UF_view_mat
        if self.keystone is not None:
            user_flags |= Lens.UF_keystone
        if self.min_fov is not None:
            user_flags |= Lens.UF_min_fov
        if self.custom_film_mat is not None:
            user_flags |= Lens.UF_custom_film_mat

        dg.add_uint16(user_flags)

        if self.min_fov is not None:
            dg.add_stdfloat(self.min_fov)
        else:
            dg.add_stdfloat(30.0)

        dg.add_stdfloat(self.interocular_distance or 0.0)
        dg.add_stdfloat(self.convergence_distance or 0.0)

        if self.view_hpr:
            dg.add_vec3(self.view_hpr)
        if self.view_vector:
            dg.add_vec3(self.view_vector)
            dg.add_vec3(self.up_vector)
        if self.view_mat:
            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.view_mat[j][i])
        if self.keystone:
            dg.add_vec2(self.keystone)
        if self.custom_film_mat:
            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.custom_film_mat[j][i])


class PerspectiveLens(Lens):

    __slots__ = ()

    def __init__(self, fov=None):
        super().__init__()
        if fov:
            self.hfov, self.vfov = fov


class OrthographicLens(Lens):

    __slots__ = ()


class MatrixLens(Lens):

    __slots__ = 'user_mat', 'left_eye_mat', 'right_eye_mat'

    def __init__(self):
        super().__init__()

        self.film_width = 2.0
        self.film_height = 2.0
        self.user_mat = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
        self.left_eye_mat = None
        self.right_eye_mat = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if manager.file_version < (6, 41):
            return

        flags = 0
        if self.left_eye_mat:
            flags |= 1
        if self.right_eye_mat:
            flags |= 2

        dg.add_uint8(flags)

        for i in (0, 1, 2, 3):
            for j in (0, 1, 2, 3):
                dg.add_stdfloat(self.user_mat[j][i])

        if self.left_eye_mat:
            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.left_eye_mat[j][i])

        if self.right_eye_mat:
            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.right_eye_mat[j][i])
