
from .panda_node import PandaNode
from .typed_objects import CopyOnWriteObject
from math import sqrt


dot2 = lambda a, b: a[0] * b[0] + a[1] * b[1]
dot3 = lambda a, b: a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


class CollisionNode(PandaNode):

    __slots__ = 'solids', 'from_collide_mask'

    def __init__(self, name):
        super().__init__(name)

        self.solids = []
        self.from_collide_mask = 0b011111111111111111111
        self.into_collide_mask = 0b011111111111111111111

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        num_solids = len(self.solids)
        if num_solids > 0xffff:
            dg.add_uint16(0xffff)
            dg.add_uint32(num_solids)
        else:
            dg.add_uint16(num_solids)

        for solid in self.solids:
            manager.write_pointer(dg, solid)

        dg.add_uint32(self.from_collide_mask)


class CollisionSolid(CopyOnWriteObject):

    __slots__ = 'tangible', 'effective_normal', 'respect_effective_normal'

    def __init__(self):
        super().__init__()

        self.tangible = True
        self.effective_normal = None
        self.respect_effective_normal = True

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        flags = 0x14
        if self.tangible:
            flags |= 0x01
        if self.effective_normal is not None:
            flags |= 0x02
        if not self.respect_effective_normal:
            flags |= 0x08
        dg.add_uint8(flags)

        if self.effective_normal is not None:
            dg.add_vec3(self.effective_normal)


class CollisionSphere(CollisionSolid):

    __slots__ = 'center', 'radius'

    def __init__(self, center, radius):
        super().__init__()

        self.center = tuple(center)
        self.radius = float(radius)

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_vec3(self.center)
        dg.add_stdfloat(self.radius)


class CollisionPlane(CollisionSolid):

    __slots__ = 'plane'

    def __init__(self, plane):
        super().__init__()

        self.plane = tuple(plane)

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_vec4(self.plane)


class CollisionPolygon(CollisionPlane):

    __slots__ = '_points', '_vectors', '_to_2d_mat'

    def __init__(self, *points):
        normal = [0, 0, 0]

        for i in range(len(points)):
            p0 = points[i]
            p1 = points[(i + 1) % len(points)]
            normal[0] += p0[1] * p1[2] - p0[2] * p1[1]
            normal[1] += p0[2] * p1[0] - p0[0] * p1[2]
            normal[2] += p0[0] * p1[1] - p0[1] * p1[0]

        length = sqrt(dot3(normal, normal))
        normal[0] /= length
        normal[1] /= length
        normal[2] /= length

        super().__init__(normal + [-dot3(normal, points[0])])

        z = [-normal[0], -normal[1]]
        d = dot2(z, z)
        if d == 0.0:
            z = (0.0, 1.0)
        else:
            sqrt_d = sqrt(d)
            z[0] /= sqrt_d
            z[1] /= sqrt_d

        x = [-normal[0] * z[0] + -normal[1] * z[1], -normal[2]]
        d = dot2(x, x)
        if d == 0.0:
            x = (1.0, 0.0)
        else:
            sqrt_d = sqrt(d)
            x[0] /= sqrt_d
            x[1] /= sqrt_d

        y = [0.0, x[0]]
        d = dot2(y, y)
        if x[0] == 0.0:
            y = (0.0, 1.0)
        else:
            sqrt_d = sqrt(d)
            #y[0] /= sqrt_d
            y[1] /= sqrt_d

        #if abs(self.plane[0]) >= abs(self.plane[1]) and abs(self.plane[0]) >= abs(self.plane[2]):
        #    plane_point = (-self.plane[3] / self.plane[0], 0.0, 0.0)
        #elif abs(self.plane[1]) >= abs(self.plane[2]):
        #    plane_point = (0.0, -self.plane[3] / self.plane[1], 0.0)
        #else:
        #    plane_point = (0.0, 0.0, -self.plane[3] / self.plane[2])

        #to_3d_mat = (
        #    (
        #        y[1] * z[1],
        #        y[1] * -z[0],
        #        0,
        #        0,
        #    ),
        #    (
        #        x[0] * z[0],
        #        x[0] * z[1],
        #        x[1],
        #        0,
        #    ),
        #    (
        #        y[1] * -x[1] * z[0],
        #        y[1] * -x[1] * z[1],
        #        y[1] * x[0],
        #        0,
        #    ),
        #    (
        #        plane_point[0],
        #        plane_point[1],
        #        plane_point[2],
        #        0,
        #    ),
        #)

        # Yes, we have to compute the whole to_2d_mat, because it's stored
        # verbatim in the bam file.  Sigh.
        to_2d_mat = [
            (
                x[0] * x[0] * y[1] * z[1] + x[1] * x[1] * y[1] * z[1],
                x[0] * y[1] * y[1] * z[0],
                -x[1] * y[1] * z[0],
                0,
            ),
            (
                -x[0] * x[0] * y[1] * z[0] - x[1] * x[1] * y[1] * z[0],
                x[0] * y[1] * y[1] * z[1],
                -x[1] * y[1] * z[1],
                0,
            ),
            (
                0,
                x[1] * y[1] * y[1] * z[0] * z[0] + x[1] * y[1] * y[1] * z[1] * z[1],
                x[0] * y[1] * z[1] * z[1] + x[0] * y[1] * z[0] * z[0],
                0,
            ),
        ]

        if abs(self.plane[0]) >= abs(self.plane[1]) and abs(self.plane[0]) >= abs(self.plane[2]):
            p = self.plane[3] / self.plane[0]
            to_2d_mat.append((
                p * to_2d_mat[0][0],
                p * to_2d_mat[0][1],
                p * to_2d_mat[0][2],
                1,
            ))
        elif abs(self.plane[1]) >= abs(self.plane[2]):
            p = self.plane[3] / self.plane[1]
            to_2d_mat.append((
                p * to_2d_mat[1][0],
                p * to_2d_mat[1][1],
                p * to_2d_mat[1][2],
                1,
            ))
        else:
            p = self.plane[3] / self.plane[2]
            to_2d_mat.append((
                0,
                p * to_2d_mat[2][1],
                p * to_2d_mat[2][2],
                1,
            ))

        self._points = [(
            point[0] * to_2d_mat[0][0] + point[1] * to_2d_mat[1][0] + point[2] * to_2d_mat[2][0] + to_2d_mat[3][0],
            point[0] * to_2d_mat[0][2] + point[1] * to_2d_mat[1][2] + point[2] * to_2d_mat[2][2] + to_2d_mat[3][2],
        ) for point in points]

        self._vectors = []
        num_points = len(points)
        for i in range(num_points):
            next_point = self._points[(i + 1) % num_points]
            this_point = self._points[i]
            v = (next_point[0] - this_point[0], next_point[1] - this_point[1])
            v_len = sqrt(dot2(v, v))
            self._vectors.append((v[0] / v_len, v[1] / v_len))

        self._to_2d_mat = to_2d_mat

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(len(self._points))

        for p, v in zip(self._points, self._vectors):
            dg.add_vec2(p)
            dg.add_vec2(v)

        dg.add_vec4(self._to_2d_mat[0])
        dg.add_vec4(self._to_2d_mat[1])
        dg.add_vec4(self._to_2d_mat[2])
        dg.add_vec4(self._to_2d_mat[3])
