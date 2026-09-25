import math
import textwrap

from ursina import (
    Ursina, Entity, Mesh, Text, Button, Vec3, color, camera, window,
    scene, mouse, held_keys, time, application, DirectionalLight,
    AmbientLight, raycast,
)
from ursina.models.procedural.cylinder import Cylinder
from ursina.shaders import lit_with_shadows_shader, basic_lighting_shader


# Turn on shadows for a capable exhibition PC. Default lighting is lighter.
ENABLE_SHADOWS = False
WALK_SPEED = 2.2
EYE_HEIGHT = 1.35
PLAYER_RADIUS = 0.18
UPPER_HEIGHT = 1.5
DOME_RADIUS = 3.8
TERRACE_RADIUS = 5.3
RAIL_RADIUS = 6.55
STAIR_START = -7.6
STAIR_END = -5.3
STAIR_HALF_WIDTH = 1.25
STAIR_WALL_X = 1.43
STAIR_WALL_HALF_WIDTH = .10
STAIR_LANDING_END = -4.9
STEP_COUNT = 10
STEP_DEPTH = (STAIR_END - STAIR_START) / STEP_COUNT
GATE_RADIUS = 8.0


def clamp_value(value, low, high):
    return max(low, min(value, high))


def floor_height(x, z):
    """Top of the visible walking surface; staircase takes precedence."""
    if abs(x) <= STAIR_HALF_WIDTH and STAIR_START <= z <= STAIR_END:
        step = min(STEP_COUNT, int((z - STAIR_START) / STEP_DEPTH) + 1)
        return step * UPPER_HEIGHT / STEP_COUNT
    if abs(x) <= STAIR_HALF_WIDTH and STAIR_END < z <= STAIR_LANDING_END:
        return UPPER_HEIGHT
    radius = math.hypot(x, z)
    if radius <= TERRACE_RADIUS:
        return UPPER_HEIGHT
    if radius <= 5.55:
        return .15
    return 0.0


def rail_opening(x, z, radius=RAIL_RADIUS):
    # Four cardinal openings; the north and south use x as their tangent.
    return (abs(x) < 1.35 and abs(z) > radius - .4) or (
        abs(z) < 1.35 and abs(x) > radius - .4)


def valid_walk_position(x, z, previous_height, obstacles=()):
    """Collision and no-fall boundary, with a small automatic step-up."""
    radius = math.hypot(x, z)
    if radius > 20 or radius < DOME_RADIUS + PLAYER_RADIUS:
        return False
    # Continuous railing barrier, including clearance for the visitor body.
    if abs(radius - RAIL_RADIUS) < .12 + PLAYER_RADIUS:
        if not rail_opening(x, z):
            return False
    # Rectangle obstacles are world-aligned pillar bases and stair sidewalls.
    for cx, cz, half_x, half_z in obstacles:
        if abs(x - cx) < half_x + PLAYER_RADIUS and abs(z - cz) < half_z + PLAYER_RADIUS:
            return False
    target_height = floor_height(x, z)
    # Judge the destination, not the height of the previous step. Otherwise
    # an accepted step can activate a narrower boundary and trap the walker.
    # The stair/landing corridor uses the SAME clearance as its sidewalls.
    stair_clearance = STAIR_WALL_X - STAIR_WALL_HALF_WIDTH - PLAYER_RADIUS
    on_stair_route = (abs(x) <= stair_clearance
                      and STAIR_START <= z <= STAIR_LANDING_END)
    if target_height >= UPPER_HEIGHT - .00001 and radius > TERRACE_RADIUS - PLAYER_RADIUS:
        if not on_stair_route:
            return False
    return abs(target_height - previous_height) <= .181


INFO = {
    'site': ('SANCHI STUPA', 'A place of learning and devotion', [
        'Sanchi is in Madhya Pradesh. The site developed over many centuries, '
        'beginning under Emperor Ashoka in the third century BCE. Its monuments '
        'include stupas, temples, pillars and monasteries.',
        'This experience focuses on the Great Stupa. Walk around its exterior, '
        'enter the gateways and explore the upper terrace. The layout and '
        'decorative details are simplified. Source: UNESCO World Heritage Centre.'
    ]),
    'anda': ('ANDA', 'The hemispherical dome', [
        'The anda is the great rounded mound at the centre of the stupa. Its '
        'form recalls ancient burial mounds and encloses the sacred core. '
        'A stupa is a solid monument, not a hall with an interior to enter.',
        'IKS CONNECTION: Observe how a simple curved form establishes a sacred '
        'centre. The surrounding paths organize movement around that centre. '
        'Use MODEL CLOSE-UP to compare the dome with the square harmika above.'
    ]),
    'harmika': ('HARMIKA', 'The square enclosure above the dome', [
        'The harmika is the small square enclosure crowning the anda. It marks '
        'the sacred upper zone and surrounds the base of the central mast.',
        'LOOK CLOSELY: Four sides and corner posts contrast with the curved '
        'dome below. This feature is not a visitor platform. Use the model '
        'close-up to inspect it from above.'
    ]),
    'yasti': ('YASTI', 'The central mast', [
        'The yasti is the vertical mast rising above the harmika. It carries '
        'the umbrella arrangement and makes the vertical centre of the '
        'monument easy to recognize.',
        'IKS CONNECTION: Trace an imaginary line from the middle of the dome '
        'through the mast. Compare this vertical organization with the '
        'circular movement of visitors below.'
    ]),
    'chattra': ('CHATTRAS', 'The umbrella discs', [
        'The umbrella-like discs above the harmika are called chattras. '
        'The umbrella is associated with honour, protection and spiritual '
        'importance in ancient Indian traditions.',
        'LOOK CLOSELY: The discs become smaller toward the top. Exploded '
        'view separates them so you can see their relationship to the mast '
        'and the enclosure underneath.'
    ]),
    'vedika': ('VEDIKA', 'The surrounding stone railing', [
        'The vedika defines the sacred enclosure around the stupa. Posts '
        'and horizontal rails form a boundary while gateways provide '
        'organized points of entry.',
        'IKS CONNECTION: A boundary can guide movement as well as mark a '
        'special place. Walk around the railing and find the four entrances. '
        'This model simplifies the real railing and its decoration.'
    ]),
    'lower_path': ('LOWER PATH', 'Pradakshina at ground level', [
        'Pradakshina is the practice of walking clockwise around a sacred '
        'object, keeping it to the right. The path around the stupa makes '
        'this movement part of the architecture.',
        'TRY IT: From the south entrance, go toward the west side, then north, '
        'east and back south. Keep the dome on your right. You can also '
        'explore freely in either direction in this simulator.'
    ]),
    'upper_path': ('UPPER TERRACE', 'The raised circumambulatory path', [
        'The raised terrace provides another route around the dome. Its '
        'position gives a different view of the monument and gateways. '
        'The staircase connects it with the lower level.',
        'TRY IT: Walk up the southern staircase and circle the dome. The '
        'simulator prevents stepping off the edge. The terrace width and '
        'access are simplified for an exhibition walkthrough.'
    ]),
    'stairs': ('STAIRCASE', 'A connection between two levels', [
        'The stairs connect the lower approach with the upper '
        'circumambulatory terrace. They make vertical movement part of '
        'the route around the monument.',
        'MODEL NOTE: This is a simplified single flight based on your '
        'original model, not a measured reproduction of the historic '
        'staircase. Walk forward to climb; no jump key is needed.'
    ]),
}

for direction in ('south', 'east', 'north', 'west'):
    INFO[direction + '_gate'] = (
        direction.upper() + ' TORANA', 'Ceremonial gateway', [
            'You are exploring the ' + direction + ' gateway. Toranas mark '
            'the approaches to the Great Stupa. Two upright pillars carry '
            'three horizontal architraves in this model.',
            'The real gateways carry elaborate sculptural narratives. '
            'The simple ornaments shown here are placeholders, not '
            'reproductions of particular historical reliefs. Compare the '
            'gateway with the circular railing behind it.'
        ])


def hemisphere_mesh(radius=3.8, rings=24, segments=80):
    """An actual upper hemisphere; smooth vertex normals and mesh picking."""
    vertices, triangles, normals = [], [], []
    for row in range(rings + 1):
        latitude = row / rings * math.pi / 2
        for col in range(segments + 1):
            longitude = col / segments * math.tau
            normal = (math.cos(latitude) * math.sin(longitude),
                      math.sin(latitude),
                      math.cos(latitude) * math.cos(longitude))
            vertices.append(tuple(radius * n for n in normal))
            normals.append(normal)
    for row in range(rings):
        for col in range(segments):
            a = row * (segments + 1) + col
            b = a + segments + 1
            # Ursina's forward axis uses the opposite winding from the usual
            # right-handed XYZ example. The front surface must face outward.
            triangles.extend([(a, b, a + 1), (a + 1, b, b + 1)])
    return Mesh(vertices=vertices, triangles=triangles, normals=normals)


def ui_text(*args, **kwargs):
    # Put glyphs in front of the panel quads, never on the same depth plane.
    kwargs.setdefault('z', -.04)
    return Text(*args, **kwargs)


class SanchiSimulator(Entity):
    def __init__(self):
        super().__init__()
        self.stone = color.rgb32(205, 170, 112)
        self.light = color.rgb32(224, 197, 143)
        self.mid = color.rgb32(184, 143, 87)
        self.dark = color.rgb32(133, 92, 54)
        self.gold = color.rgb32(241, 196, 103)
        self.ink = color.rgb32(27, 33, 35)
        self.groups = {}
        self.build_groups = []
        self.obstacles = []
        self.visited = set()
        self.mode = 'model'
        self.elapsed = 0.0
        self.last_tour_step = -1
        self.selected = 'site'
        self.page = 0
        self.panel_open = False
        self.free_mouse = True
        self.walk_position = Vec3(0, 0, -12)
        self.yaw = 0.0
        self.pitch = 0.0
        self.orbit_yaw = -24.0
        self.orbit_pitch = 18.0
        self.orbit_distance = 28.0
        self.orbit_target = Vec3(0, 3.0, 0)
        self.hovered_key = None
        self.last_aspect = 0
        self.stupa = Entity()
        self.make_world()
        self.base_positions = {part: Vec3(part.position) for part in self.build_groups}
        self.make_ui()
        self.set_model_camera()
        self.show_info('site')
        self.welcome.enabled = True
        self.hud.enabled = False

    def group(self):
        parent = Entity(parent=self.stupa)
        self.build_groups.append(parent)
        return parent

    def part(self, key, parent=None, model='cube', **kwargs):
        if isinstance(model, Mesh) and not model.normals:
            model.generate_normals(smooth=False)
        obj = Entity(parent=parent or self.stupa, model=model, **kwargs)
        obj.collider = 'box' if model == 'cube' else 'mesh'
        obj.architecture_key = key
        obj.original_color = color.Color(*obj.color)
        obj.shader = lit_with_shadows_shader if ENABLE_SHADOWS else basic_lighting_shader
        self.groups.setdefault(key, []).append(obj)
        return obj

    def cylinder(self, key, parent, radius, height, y, tint):
        # Cylinder's default starts at y=0, not its centre. Make that explicit.
        return self.part(key, parent, Cylinder(resolution=80, start=-.5),
                         scale=(radius * 2, height, radius * 2),
                         position=(0, y, 0), color=tint)

    def make_world(self):
        self.part('site', model='cube', scale=(48, .3, 48), y=-.17,
                  color=color.rgb32(135, 143, 92))
        self.cylinder('site', self.stupa, 20.5, .04, -.025, color.rgb32(160, 132, 92))
        # Ground path inside and outside the sacred enclosure.
        self.cylinder('lower_path', self.stupa, 9.6, .025, -.007, self.mid)
        for rotation in (0, 90):
            self.part('site', scale=(2.65, .018, 36), y=.01,
                      rotation_y=rotation, color=color.rgb32(191, 162, 115))

        self.platform_group = self.group()
        self.cylinder('lower_path', self.platform_group, 5.55, .15, .075, self.mid)
        self.cylinder('upper_path', self.platform_group, TERRACE_RADIUS,
                      UPPER_HEIGHT - .15, (UPPER_HEIGHT + .15) / 2, self.light)
        # Thin rim marks the terrace edge but does not obstruct walking.
        self.make_ring(self.platform_group, 'upper_path', TERRACE_RADIUS - .04,
                       UPPER_HEIGHT + .012, .035, self.mid)

        self.stair_group = self.group()
        self.part('stairs', self.stair_group,
                  scale=(STAIR_HALF_WIDTH * 2, UPPER_HEIGHT, STAIR_LANDING_END - STAIR_END),
                  position=(0, UPPER_HEIGHT / 2, (STAIR_END + STAIR_LANDING_END) / 2),
                  color=self.light)
        for i in range(STEP_COUNT):
            height = (i + 1) * UPPER_HEIGHT / STEP_COUNT
            z = STAIR_START + (i + .5) * STEP_DEPTH
            self.part('stairs', self.stair_group, scale=(STAIR_HALF_WIDTH * 2, height, STEP_DEPTH + .005),
                      position=(0, height / 2, z), color=self.light)
        for x in (-STAIR_WALL_X, STAIR_WALL_X):
            # Short separate blocks follow the flight; no inaccessible tall wall.
            for i in range(STEP_COUNT):
                top = (i + 1) * UPPER_HEIGHT / STEP_COUNT + .45
                self.part('stairs', self.stair_group,
                          scale=(STAIR_WALL_HALF_WIDTH * 2, top, STEP_DEPTH + .005),
                          position=(x, top / 2, STAIR_START + (i + .5) * STEP_DEPTH),
                          color=self.dark)
            self.obstacles.append((x, (STAIR_START + STAIR_END) / 2,
                                   STAIR_WALL_HALF_WIDTH, (STAIR_END - STAIR_START) / 2))

        self.dome_group = self.group()
        self.dome_group.y = UPPER_HEIGHT
        self.part('anda', self.dome_group, hemisphere_mesh(), color=self.stone)
        for local_y in (.10, .55, 1.05, 1.55, 2.05, 2.55, 3.05, 3.45):
            radius = math.sqrt(DOME_RADIUS ** 2 - local_y ** 2) + .007
            self.make_ring(self.dome_group, 'anda', radius, local_y, .016, self.mid)

        self.rail_group = self.group()
        count = 64
        for i in range(count):
            angle = i * math.tau / count
            x, z = math.sin(angle) * RAIL_RADIUS, math.cos(angle) * RAIL_RADIUS
            if rail_opening(x, z):
                continue
            self.part('vedika', self.rail_group, scale=(.19, 1.25, .19),
                      position=(x, .625, z), color=self.dark)
            angle_mid = (i + .5) * math.tau / count
            bx, bz = math.sin(angle_mid) * RAIL_RADIUS, math.cos(angle_mid) * RAIL_RADIUS
            if rail_opening(bx, bz):
                continue
            for y in (.38, .82, 1.18):
                self.part('vedika', self.rail_group,
                          scale=(2 * RAIL_RADIUS * math.sin(math.pi / count), .11, .12),
                          position=(bx, y, bz), rotation_y=math.degrees(angle_mid),
                          color=self.mid)

        self.harmika_group = self.group()
        self.harmika_group.y = UPPER_HEIGHT + DOME_RADIUS
        self.part('harmika', self.harmika_group, scale=(1.9, .16, 1.9),
                  y=.04, color=self.mid)
        for x in (-.9, .9):
            for z in (-.9, .9):
                self.part('harmika', self.harmika_group, scale=(.12, .65, .12),
                          position=(x, .4, z), color=self.dark)
        for value in (-.9, .9):
            for y in (.3, .58):
                self.part('harmika', self.harmika_group, scale=(1.9, .10, .10),
                          position=(0, y, value), color=self.dark)
                self.part('harmika', self.harmika_group, scale=(.10, .10, 1.9),
                          position=(value, y, 0), color=self.dark)

        self.mast_group = self.group()
        self.mast_group.y = 6.5
        self.part('yasti', self.mast_group, scale=(.13, 2.6, .13), color=self.dark)
        self.chattra_groups = []
        for radius, y in ((1.13, 6.15), (.88, 6.85), (.63, 7.5)):
            parent = self.group()
            parent.y = y
            self.chattra_groups.append(parent)
            self.cylinder('chattra', parent, radius, .15, 0, self.dark)

        self.gate_group = self.group()
        for direction, x, z, rotation in (
            ('south', 0, -GATE_RADIUS, 0), ('north', 0, GATE_RADIUS, 0),
            ('east', GATE_RADIUS, 0, 90), ('west', -GATE_RADIUS, 0, 90)
        ):
            self.make_gate(direction + '_gate', x, z, rotation)

        # A modest landscape; kept outside the playable circle so it never
        # introduces trees visitors can walk through. Planting is illustrative.
        for i in range(20):
            angle = i * math.tau / 20 + .12
            x, z = 22 * math.sin(angle), 22 * math.cos(angle)
            Entity(model='cube', position=(x, 1.2, z), scale=(.3, 2.4, .3),
                   color=self.dark)
            Entity(model='sphere', position=(x, 3.0, z), scale=(2.7, 3.0, 2.7),
                   color=color.rgb32(81 + i % 4 * 5, 110, 65))
        sun = DirectionalLight(shadows=ENABLE_SHADOWS)
        sun.look_at(Vec3(1, -2, -1))
        AmbientLight(color=color.rgba32(165, 165, 165, 255))

    def make_ring(self, parent, key, radius, y, thickness, tint):
        # A thin ring on the surface, not a full cylinder intersecting the dome.
        vertices, triangles = [], []
        count = 96
        for i in range(count + 1):
            a = i * math.tau / count
            for r in (radius - thickness / 2, radius + thickness / 2):
                vertices.append((r * math.sin(a), y, r * math.cos(a)))
        for i in range(count):
            a = i * 2
            triangles.extend([(a, a + 2, a + 1), (a + 1, a + 2, a + 3)])
        mesh = Mesh(vertices=vertices, triangles=triangles,
                    normals=[(0, 1, 0)] * len(vertices))
        self.part(key, parent, mesh, color=tint, double_sided=True)

    def make_gate(self, key, x, z, rotation):
        gate = Entity(parent=self.gate_group, position=(x, 0, z), rotation_y=rotation)
        for px in (-1.65, 1.65):
            for y, size, tint in ((.16, (.62, .32, .62), self.mid),
                                   (1.98, (.36, 3.64, .36), self.dark),
                                   (3.83, (.70, .30, .58), self.mid)):
                self.part(key, gate, position=(px, y, 0), scale=size, color=tint)
            if rotation == 0:
                self.obstacles.append((x + px, z, .31, .31))
            else:
                self.obstacles.append((x, z - px, .31, .31))
            for y in (4.17, 4.87):
                self.part(key, gate, position=(px, y, 0), scale=(.18, .5, .28),
                          color=self.dark)
        for y, width in ((3.9, 4.55), (4.6, 4.85), (5.3, 5.15)):
            self.part(key, gate, position=(0, y, 0), scale=(width, .24, .36),
                      color=self.stone)
            for side in (-1, 1):
                self.part(key, gate, position=(side * (width / 2 + .18), y + .04, 0),
                          scale=(.45, .23, .38), rotation_z=side * 7, color=self.dark)
            for px in (-.85, 0, .85):
                for side in (-1, 1):
                    self.part(key, gate, position=(px, y, side * .205),
                              scale=(.23, .23, .05), rotation_z=45, color=self.mid)

    def ui_button(self, parent, label, x, y, width, callback):
        button = Button(parent=parent, text=label, position=(x, y, -.02),
                        scale=(width, .048), color=color.rgb32(66, 70, 67),
                        highlight_color=color.rgb32(125, 101, 63),
                        text_color=color.white, on_click=callback)
        button.text_size = .74
        return button

    def make_ui(self):
        self.hud = Entity(parent=camera.ui)
        self.header = Entity(parent=self.hud)
        Entity(parent=self.header, model='quad', scale=(4, .13), y=.435,
               color=self.ink)
        self.title = ui_text(parent=self.header, text='SANCHI STUPA', y=.475,
                          scale=1.25, color=self.gold)
        self.subtitle = ui_text(parent=self.header,
                             text='INDIAN KNOWLEDGE SYSTEMS  /  Interactive exhibition',
                             y=.43, scale=.64)
        self.status = ui_text(parent=self.header, origin=(.5, 0), position=(.82, .466),
                           scale=.73, color=self.gold)

        self.toolbar = Entity(parent=self.hud, y=-.446)
        Entity(parent=self.toolbar, model='quad', scale=(4, .11), color=self.ink)
        entries = [('Walk', lambda: self.set_mode('walk')),
                   ('Model', lambda: self.set_mode('model')),
                   ('Tour', lambda: self.set_mode('tour')),
                   ('Build', lambda: self.set_mode('build')),
                   ('Explode', self.toggle_exploded),
                   ('Info', lambda: self.show_info(self.selected)),
                   ('Reset', self.reset), ('Help', self.show_welcome),
                   ('Quit', application.quit)]
        for i, (label, callback) in enumerate(entries):
            self.ui_button(self.toolbar, label, (i - 4) * .168, 0, .153, callback)

        self.panel = Entity(parent=self.hud, position=(.60, .035, -.08), enabled=False)
        Entity(parent=self.panel, model='quad', scale=(.48, .635), color=self.ink,
               collider='box')
        Entity(parent=self.panel, model='quad', scale=(.48, .006), y=.317, color=self.gold)
        self.info_title = ui_text(parent=self.panel, position=(-.21, .285),
                               scale=.94, color=self.gold)
        self.info_subtitle = ui_text(parent=self.panel, position=(-.21, .241), scale=.66)
        self.info_body = ui_text(parent=self.panel, position=(-.21, .174), scale=.76,
                              line_height=1.15)
        self.page_label = ui_text(parent=self.panel, position=(0, -.083), origin=(0, 0),
                               scale=.65, color=self.gold)
        self.ui_button(self.panel, 'Prev page', -.125, -.132, .18, lambda: self.change_page(-1))
        self.ui_button(self.panel, 'Next page', .125, -.132, .18, lambda: self.change_page(1))
        self.ui_button(self.panel, 'Prev area', -.125, -.19, .18, lambda: self.change_area(-1))
        self.ui_button(self.panel, 'Next area', .125, -.19, .18, lambda: self.change_area(1))
        self.ui_button(self.panel, 'Model close-up', -.103, -.263, .24, self.focus_selected)
        self.ui_button(self.panel, 'Close', .149, -.263, .135, self.close_info)

        self.crosshair = ui_text(parent=self.hud, text='+', origin=(0, 0), scale=.9,
                              color=self.gold, enabled=False)
        self.hint = ui_text(parent=self.hud, origin=(0, 0), y=-.30, scale=.72,
                         color=color.white, background=True)
        self.hint.background.color = color.rgba32(27, 33, 35, 215)
        self.hint.background.model = 'quad'
        self.hint.background.scale = (1.4, .065)
        self.controls = ui_text(parent=self.hud, origin=(0, 0), y=-.368, scale=.63)

        self.map_root = Entity(parent=self.hud, position=(-.70, -.17))
        Entity(parent=self.map_root, model='quad', scale=(.26, .30), color=self.ink)
        ui_text(parent=self.map_root, text='LOCATION', origin=(0, 0), y=.126,
             scale=.59, color=self.gold)
        Entity(parent=self.map_root, model='circle', scale=.063, color=self.mid, z=-.01)
        for label, x, y in (('N', 0, .092), ('S', 0, -.092),
                            ('E', .10, 0), ('W', -.10, 0)):
            ui_text(parent=self.map_root, text=label, origin=(0, 0), position=(x, y), scale=.57)
        self.map_dot = Entity(parent=self.map_root, model='circle', scale=.010,
                              color=self.gold, z=-.04)
        self.map_arrow = Entity(parent=self.map_root, model='quad', scale=(.003, .015),
                                color=color.white, z=-.035)
        ui_text(parent=self.map_root, text='1 S  2 E  3 N  4 W  5 Upper', origin=(0, 0),
             y=-.132, scale=.43)

        self.welcome = Entity(parent=camera.ui, z=-2)
        Entity(parent=self.welcome, model='quad', scale=(4, 2), color=self.ink,
               collider='box')
        ui_text(parent=self.welcome, text='SANCHI STUPA', origin=(0, 0), y=.28,
             scale=2.6, color=self.gold)
        ui_text(parent=self.welcome, text='WALK  /  DISCOVER  /  UNDERSTAND',
             origin=(0, 0), y=.185, scale=.92)
        ui_text(parent=self.welcome, text='An interactive Indian Knowledge Systems exhibition',
             origin=(0, 0), y=.122, scale=.75, color=self.gold)
        ui_text(parent=self.welcome, origin=(0, 0), y=-.005, scale=.82,
             text='WASD or arrow keys to walk. Move the mouse to look.\n'
                  'Click a feature to learn. Esc releases the mouse.\n'
                  'Climb the south stairs and explore the upper path.\n'
                  'Tab switches between walking and the model view.')
        self.ui_button(self.welcome, 'START WALKING', -.18, -.185, .30, self.start_walk)
        self.ui_button(self.welcome, 'EXPLORE MODEL', .18, -.185, .30, self.start_model)
        ui_text(parent=self.welcome, origin=(0, 0), y=-.29, scale=.66,
             text='Educational reconstruction of Great Stupa (Stupa 1).\n'
                  'Proportions, staircase and relief decoration are simplified.\n'
                  'Historical context: UNESCO World Heritage Centre.')
        ui_text(parent=self.welcome, text='F11  Fullscreen      Alt+F4  Exit',
             origin=(0, 0), y=-.40, scale=.63, color=self.gold)
        self.layout_ui()

    def layout_ui(self):
        half_width = window.aspect_ratio / 2
        self.title.x = self.subtitle.x = -half_width + .035
        self.status.x = half_width - .035
        self.panel.x = half_width - .27
        self.map_root.x = -half_width + .16
        # Keep controls usable on narrower displays as well.
        self.toolbar.scale_x = min(1, (2 * half_width - .025) / 1.52)
        self.last_aspect = window.aspect_ratio

    def capture_mouse(self, capture):
        self.free_mouse = not capture
        if application.window_type == 'onscreen':
            mouse.locked = capture
            mouse.visible = not capture
        self.crosshair.enabled = capture

    def highlight(self, key=None):
        for name, parts in self.groups.items():
            for obj in parts:
                # Avoid turning the whole landscape yellow for the site topic.
                obj.color = self.gold if name == key and name != 'site' else obj.original_color

    def show_info(self, key, page=0):
        self.selected = key
        self.page = page % len(INFO[key][2])
        title, subtitle, paragraphs = INFO[key]
        self.info_title.text = title
        self.info_subtitle.text = textwrap.fill(subtitle, width=38)
        self.info_body.text = textwrap.fill(paragraphs[self.page], width=32)
        self.page_label.text = f'{self.page + 1} / {len(paragraphs)}'
        self.panel.enabled = True
        self.panel_open = True
        self.visited.add(key)
        self.highlight(key)
        self.capture_mouse(False)

    def change_page(self, direction):
        self.show_info(self.selected, self.page + direction)

    def change_area(self, direction):
        if self.mode == 'tour':
            self.set_mode('model')
        keys = list(INFO)
        self.show_info(keys[(keys.index(self.selected) + direction) % len(keys)])

    def close_info(self):
        self.panel.enabled = False
        self.panel_open = False
        self.highlight()
        self.capture_mouse(self.mode == 'walk')

    def restore_structure(self):
        for part, position in self.base_positions.items():
            part.enabled = True
            part.position = Vec3(position)

    def set_mode(self, mode):
        self.restore_structure()
        self.elapsed = 0
        self.last_tour_step = -1
        self.mode = mode
        self.highlight()
        self.panel.enabled = False
        self.panel_open = False
        self.orbit_target = Vec3(0, 3, 0)
        self.orbit_distance = 28
        self.orbit_pitch = 18
        self.capture_mouse(mode == 'walk')
        if mode == 'walk':
            self.set_walk_camera(snap=True)
        else:
            camera.fov = 55
            self.set_model_camera()
        if mode == 'build':
            for part in self.build_groups:
                part.enabled = False
        elif mode == 'exploded':
            self.orbit_distance = 29
            self.orbit_target = Vec3(0, 5, 0)
            self.set_model_camera()
        elif mode == 'tour':
            self.show_tour_step(0)

    def toggle_exploded(self):
        self.set_mode('model' if self.mode == 'exploded' else 'exploded')

    def reset(self):
        self.walk_position = Vec3(0, 0, -12)
        self.yaw = self.pitch = 0
        self.orbit_yaw = -24
        self.set_mode('walk' if self.mode == 'walk' else 'model')

    def show_welcome(self):
        self.set_mode('model')
        self.welcome.enabled = True
        self.hud.enabled = False

    def start_walk(self):
        self.welcome.enabled = False
        self.hud.enabled = True
        self.set_mode('walk')

    def start_model(self):
        self.welcome.enabled = False
        self.hud.enabled = True
        self.set_mode('model')
        self.show_info('site')

    def set_walk_camera(self, snap=False, dt=0):
        camera.fov = 72
        target_y = self.walk_position.y + EYE_HEIGHT
        camera.x, camera.z = self.walk_position.x, self.walk_position.z
        camera.y = target_y if snap else camera.y + (target_y - camera.y) * min(1, dt * 15)
        camera.rotation = (self.pitch, self.yaw, 0)

    def set_model_camera(self):
        yaw, pitch = math.radians(self.orbit_yaw), math.radians(self.orbit_pitch)
        r = self.orbit_distance
        camera.position = self.orbit_target + Vec3(
            math.sin(yaw) * r * math.cos(pitch), r * math.sin(pitch),
            -math.cos(yaw) * r * math.cos(pitch))
        camera.look_at(self.orbit_target)

    def focus_selected(self):
        key = self.selected
        self.set_mode('model')
        views = {
            'anda': ((0, 3.5, 0), 14, 20, -25),
            'harmika': ((0, 5.65, 0), 6, 30, -30),
            'yasti': ((0, 6.6, 0), 6, 10, -35),
            'chattra': ((0, 6.9, 0), 7, 22, -30),
            'upper_path': ((0, 1.5, 0), 16, 45, -35),
            'stairs': ((0, 1, -5.7), 8, 25, -30),
        }
        for name, pos, yaw in (('south', (0, 3, -8), 0), ('north', (0, 3, 8), 180),
                               ('east', (8, 3, 0), 90), ('west', (-8, 3, 0), -90)):
            views[name + '_gate'] = (pos, 10, 12, yaw)
        target, distance, pitch, yaw = views.get(key, ((0, 2.5, 0), 21, 30, -25))
        self.orbit_target = Vec3(*target)
        self.orbit_distance, self.orbit_pitch, self.orbit_yaw = distance, pitch, yaw
        self.set_model_camera()
        self.show_info(key)

    def teleport(self, place):
        points = {1: (0, -11, 0), 2: (11, 0, -90),
                  3: (0, 11, 180), 4: (-11, 0, 90), 5: (0, -4.6, 0)}
        x, z, yaw = points[place]
        self.walk_position = Vec3(x, floor_height(x, z), z)
        self.yaw, self.pitch = yaw, 0
        self.set_mode('walk')

    def move_walker(self, dx, dz):
        # Substeps prevent tunnelling through thin rails on slow frames.
        count = max(1, math.ceil(math.hypot(dx, dz) / .045))
        for _ in range(count):
            for step_x, step_z in ((dx / count, 0), (0, dz / count)):
                if abs(step_x) + abs(step_z) < 1e-9:
                    continue
                x = self.walk_position.x + step_x
                z = self.walk_position.z + step_z
                if valid_walk_position(x, z, self.walk_position.y, self.obstacles):
                    self.walk_position = Vec3(x, floor_height(x, z), z)

    def target_key(self):
        if self.mode == 'walk' and not self.free_mouse:
            hit = raycast(camera.world_position, camera.forward, distance=80)
            return getattr(hit.entity, 'architecture_key', None) if hit.hit else None
        hovered = mouse.hovered_entity
        if hovered and not hovered.has_ancestor(camera.ui):
            return getattr(hovered, 'architecture_key', None)
        return None

    def show_tour_step(self, index):
        sequence = ['site', 'south_gate', 'vedika', 'lower_path', 'stairs',
                    'upper_path', 'anda', 'harmika', 'yasti', 'chattra']
        key = sequence[index]
        # Close-up uses the same presets without leaving the tour permanently.
        elapsed = self.elapsed
        self.selected = key
        self.focus_selected()
        self.mode = 'tour'
        self.elapsed = elapsed
        self.last_tour_step = index

    def update_demo(self, dt):
        self.elapsed += dt
        if self.mode == 'build':
            for i, part in enumerate(self.build_groups):
                progress = clamp_value((self.elapsed - i * .65) / .7, 0, 1)
                part.enabled = self.elapsed >= i * .65
                part.position = self.base_positions[part] + Vec3(0, -2.5 * (1 - progress) ** 2, 0)
            if self.elapsed > len(self.build_groups) * .65 + .7:
                self.set_mode('model')
                self.show_info('site', 1)
        elif self.mode == 'exploded':
            progress = 1 - (1 - clamp_value(self.elapsed / .8, 0, 1)) ** 3
            offsets = {self.dome_group: 1.3, self.harmika_group: 3.0,
                       self.mast_group: 4.8}
            offsets.update({part: 4.1 + i * 1.15 for i, part in enumerate(self.chattra_groups)})
            for part, offset in offsets.items():
                part.y = self.base_positions[part].y + progress * offset
        elif self.mode == 'tour':
            index = int(self.elapsed / 14)
            if index >= 10:
                self.set_mode('model')
                self.show_info('site', 1)
            elif index != self.last_tour_step:
                self.show_tour_step(index)
            elif int(self.elapsed % 14) >= 7 and self.page == 0:
                self.show_info(self.selected, 1)

    def update(self):
        if self.welcome.enabled:
            return
        dt = min(time.dt, .08)
        if self.last_aspect != window.aspect_ratio:
            self.layout_ui()
        if self.mode == 'walk' and not self.free_mouse:
            self.yaw += mouse.velocity[0] * 100
            self.pitch = clamp_value(self.pitch - mouse.velocity[1] * 100, -80, 80)
            forward = held_keys['w'] - held_keys['s'] + held_keys['up arrow'] - held_keys['down arrow']
            sideways = held_keys['d'] - held_keys['a'] + held_keys['right arrow'] - held_keys['left arrow']
            magnitude = math.hypot(forward, sideways)
            if magnitude:
                forward, sideways = forward / magnitude, sideways / magnitude
                speed = WALK_SPEED * (1.65 if held_keys['shift'] else 1)
                a = math.radians(self.yaw)
                self.move_walker((math.sin(a) * forward + math.cos(a) * sideways) * speed * dt,
                                 (math.cos(a) * forward - math.sin(a) * sideways) * speed * dt)
            self.set_walk_camera(dt=dt)
        elif self.mode in ('model', 'exploded'):
            hovered = mouse.hovered_entity
            over_ui = hovered and hovered.has_ancestor(camera.ui)
            if held_keys['right mouse'] and not over_ui:
                self.orbit_yaw -= mouse.velocity[0] * 130
                self.orbit_pitch = clamp_value(self.orbit_pitch + mouse.velocity[1] * 100, -5, 80)
                self.set_model_camera()
        if self.mode in ('build', 'exploded', 'tour'):
            self.update_demo(dt)
        self.hovered_key = self.target_key()
        if self.mode == 'walk':
            if self.free_mouse:
                hint = 'Paused / Close the panel or press Esc to resume'
            elif self.hovered_key:
                hint = INFO[self.hovered_key][0] + '  /  Click to learn'
            else:
                hint = 'Look at an architectural feature and click'
            control = 'WASD: walk   Mouse: look   Shift: faster   Esc: cursor   Tab: model'
        else:
            hint = {'build': 'Assembling architectural components - conceptual sequence',
                    'exploded': 'Separated components - click any part to learn',
                    'tour': 'Guided tour - 14 seconds per area; select Model to stop'}.get(
                        self.mode, 'Right-drag to orbit  /  Click an area to learn')
            control = 'Right-drag: orbit   Wheel: zoom   Tab: walk   G: tour   C: build   E: exploded'
        self.hint.text, self.controls.text = hint, control
        self.status.text = self.mode.upper() + f'  /  {len(self.visited)} of {len(INFO)} areas'
        self.map_root.enabled = self.mode == 'walk'
        if self.mode == 'walk':
            self.map_dot.position = (self.walk_position.x * .005, self.walk_position.z * .005, -.04)
            a = math.radians(self.yaw)
            self.map_arrow.position = (self.map_dot.x + math.sin(a) * .009,
                                       self.map_dot.y + math.cos(a) * .009, -.035)
            self.map_arrow.rotation_z = -self.yaw

    def input(self, key):
        if key == 'f11':
            window.fullscreen = not window.fullscreen
            return
        if self.welcome.enabled:
            if key == 'enter':
                self.start_walk()
            return
        if key == 'escape':
            if self.panel_open:
                self.close_info()
            elif self.mode == 'walk':
                self.capture_mouse(self.free_mouse)
            return
        actions = {
            'tab': lambda: self.set_mode('model' if self.mode == 'walk' else 'walk'),
            'f': lambda: self.set_mode('walk'), 'r': self.reset,
            'g': lambda: self.set_mode('tour'), 'c': lambda: self.set_mode('build'),
            'e': self.toggle_exploded, 'i': lambda: self.show_info(self.selected),
            'h': self.show_welcome,
        }
        if key in actions:
            actions[key]()
        elif key in ('1', '2', '3', '4', '5'):
            self.teleport(int(key))
        elif key in ('scroll up', 'scroll down') and self.mode in ('model', 'exploded'):
            if self.panel_open and mouse.hovered_entity and mouse.hovered_entity.has_ancestor(self.panel):
                self.change_page(1 if key == 'scroll down' else -1)
            else:
                self.orbit_distance = clamp_value(self.orbit_distance + (-1 if key == 'scroll up' else 1), 4, 42)
                self.set_model_camera()
        elif key == 'left mouse down' and self.mode not in ('build', 'tour'):
            target = self.target_key()
            if target:
                self.show_info(target)


def main():
    app = Ursina(title='Sanchi Stupa | IKS Exploration Simulator',
                 development_mode=False, editor_ui_enabled=False,
                 fullscreen=False, borderless=False, size=(1366, 768),
                 show_ursina_splash=False)
    window.color = color.rgb32(135, 184, 210)
    window.fps_counter.enabled = False
    # Escape belongs to the simulator; a visible Quit button handles exit.
    application.quit_on_escape = False
    SanchiSimulator()
    app.run()


if __name__ == '__main__':
    main()
