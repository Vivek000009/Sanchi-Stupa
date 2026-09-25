from ursina import *
from ursina.models.procedural.cylinder import Cylinder
import math
from ursina.shaders import lit_with_shadows_shader

# ============================================================
# APPLICATION
# ============================================================

app = Ursina(
    development_mode=False,
    editor_ui_enabled=False
)

window.title = "Sanchi Stupa | Indian Knowledge Systems"
window.color = color.rgb32(123, 187, 225)
window.fps_counter.enabled = False


# ============================================================
# COLORS
# ============================================================

SANDSTONE = color.rgb32(195, 154, 95)
LIGHT_STONE = color.rgb32(224, 197, 143)
MID_STONE = color.rgb32(184, 143, 87)
DARK_STONE = color.rgb32(133, 92, 54)

GROUND_COLOR = color.rgb32(154, 115, 71)
RAILING_COLOR = color.rgb32(173, 132, 79)

HIGHLIGHT = color.rgb32(255, 205, 65)

# FIXED
PANEL_COLOR = color.rgba32(24, 25, 27, 220)

BUTTON_COLOR = color.rgb32(88, 68, 48)
BUTTON_HOVER = color.rgb32(125, 94, 61)

# ============================================================
# ROOT OBJECT
#
# IMPORTANT:
# Camera remains fixed.
# We rotate the monument instead.
# ============================================================

stupa = Entity(
    position=(0, -2.6, 0)
)

# ============================================================
# CONSTRUCTION GROUPS
# ============================================================

staircase_group = Entity(
    parent=stupa,
    position=(0, 0, 0)
)

vedika_group = Entity(
    parent=stupa,
    position=(0, 0, 0)
)

torana_group = Entity(
    parent=stupa,
    position=(0, 0, 0)
)

# ============================================================
# ARCHITECTURAL INFORMATION
# ============================================================

architecture_info = {

    "anda": {
        "title": "ANDA",
        "subtitle": "Hemispherical Dome",
        "text":
            "The Anda forms the principal mass\n"
            "of the stupa.\n\n"
            "Its rounded mound recalls the early\n"
            "burial mound tradition and encloses\n"
            "the sacred core of the monument.\n\n"
            "It is one of the most recognisable\n"
            "elements of Buddhist stupa architecture."
    },

    "harmika": {
        "title": "HARMIKA",
        "subtitle": "Sacred Square Enclosure",
        "text":
            "The Harmika is the square enclosure\n"
            "positioned above the dome.\n\n"
            "It marks the upper sacred zone and\n"
            "supports the central mast or Yasti."
    },

    "chattra": {
        "title": "CHATTRA",
        "subtitle": "Umbrella Discs",
        "text":
            "The Chattras are umbrella-like discs\n"
            "placed above the Harmika.\n\n"
            "They symbolize honour, protection\n"
            "and spiritual importance."
    },

    "yasti": {
        "title": "YASTI",
        "subtitle": "Central Mast",
        "text":
            "The Yasti is the vertical mast rising\n"
            "from the top of the stupa.\n\n"
            "It supports the Chattra arrangement\n"
            "and emphasizes the monument's\n"
            "vertical axis."
    },

    "vedika": {
        "title": "VEDIKA",
        "subtitle": "Sacred Railing",
        "text":
            "The Vedika is the railing surrounding\n"
            "the stupa.\n\n"
            "It defines the sacred enclosure while\n"
            "guiding movement around the monument."
    },

    "torana": {
        "title": "TORANA",
        "subtitle": "Ceremonial Gateway",
        "text":
            "The Toranas are monumental gateways\n"
            "placed around the stupa.\n\n"
            "At Sanchi they are famous for\n"
            "sculptural narratives and elaborate\n"
            "architectural decoration."
    },

    "pradakshina": {
        "title": "PRADAKSHINA PATHA",
        "subtitle": "Circumambulatory Path",
        "text":
            "The Pradakshina Patha is the route\n"
            "used to walk clockwise around the\n"
            "sacred monument.\n\n"
            "This movement forms an important\n"
            "part of ritual engagement with\n"
            "the structure."
    }
}


# ============================================================
# CLICKABLE ARCHITECTURE SYSTEM
# ============================================================

clickable_groups = {}
selected_group = None


def register_clickable(entity, group_name):

    """
    Add an architectural component to a clickable group.
    """

    entity.collider = 'box'

    entity.original_color = entity.color

    if group_name not in clickable_groups:
        clickable_groups[group_name] = []

    clickable_groups[group_name].append(entity)

    entity.on_click = lambda g=group_name: select_architecture(g)


def clear_highlight():

    for group in clickable_groups.values():

        for entity in group:

            if hasattr(entity, 'original_color'):
                entity.color = entity.original_color


def select_architecture(group_name):

    global selected_group

    clear_highlight()

    selected_group = group_name

    # Highlight selected component
    if group_name in clickable_groups:

        for entity in clickable_groups[group_name]:
            entity.color = HIGHLIGHT

    # Get educational information
    info = architecture_info[group_name]

    # Update right information panel
    info_title.text = info["title"]
    info_subtitle.text = info["subtitle"]
    info_text.text = info["text"]

    # Show floating architectural label
    floating_label.text = (
        info["title"]
        + "\n"
        + info["subtitle"]
    )

    floating_label.enabled = False

# ============================================================
# GROUND
# ============================================================

ground = Entity(
    parent=stupa,
    model='cube',
    scale=(30, 0.35, 30),
    position=(0, -0.3, 0),
    color=GROUND_COLOR
)


# ============================================================
# LOWER PLATFORM
# ============================================================

lower_platform = Entity(
    parent=stupa,
    model=Cylinder(resolution=64),
    scale=(11.2, 0.65, 11.2),
    position=(0, 0.15, 0),
    color=SANDSTONE
)

register_clickable(
    lower_platform,
    "pradakshina"
)


# ============================================================
# UPPER PLATFORM
# ============================================================

upper_platform = Entity(
    parent=stupa,
    model=Cylinder(resolution=64),
    scale=(9.5, 1.05, 9.5),
    position=(0, 0.90, 0),
    color=LIGHT_STONE
)

register_clickable(
    upper_platform,
    "pradakshina"
)

# ============================================================
# STAIRCASE TO UPPER PRADAKSHINA PATHA
# ============================================================

staircase_parts = []

number_of_steps = 7

for i in range(number_of_steps):

    step = Entity(
        parent=staircase_group,
        model='cube',

        position=(
            0,
            0.10 + i * 0.13,
            -7.0 + i * 0.22
        ),

        scale=(
            2.5,
            0.18,
            1.0
        ),

        color=SANDSTONE
    )

    staircase_parts.append(step)

    register_clickable(
        step,
        "pradakshina"
    )

    # Staircase side walls

left_stair_wall = Entity(
    parent=staircase_group,
    model='cube',
    position=(-1.45, 0.62, -6.25),
    scale=(0.30, 1.25, 3.0),
    color=DARK_STONE
)

right_stair_wall = Entity(
    parent=staircase_group,
    model='cube',
    position=(1.45, 0.62, -6.25),
    scale=(0.30, 1.25, 3.0),
    color=DARK_STONE
)

staircase_parts.extend([
    left_stair_wall,
    right_stair_wall
])

register_clickable(
    left_stair_wall,
    "pradakshina"
)

register_clickable(
    right_stair_wall,
    "pradakshina"
)

# ============================================================
# MAIN DOME / ANDA
# ============================================================

anda = Entity(
    parent=stupa,
    model='sphere',
    scale=(7.6, 5.1, 7.6),
    position=(0, 3.15, 0),
    color=color.rgb32(205, 170, 112)
)

dome_bands = [
    (2.0, 7.55),
    (2.6, 7.35),
    (3.2, 6.95),
    (3.8, 6.35),
    (4.4, 5.45),
    (4.9, 4.35),
]

for y, width in dome_bands:
    Entity(
        parent=stupa,
        model='cylinder',
        scale=(width, 0.015, width),
        position=(0, y, 0),
        color=MID_STONE
    )

register_clickable(
    anda,
    "anda"
)



# Band hides some of the sphere's lower curvature
dome_band = Entity(
    parent=stupa,
    model=Cylinder(resolution=64),
    scale=(7.75, 0.95, 7.75),
    position=(0, 1.45, 0),
    color=color.rgb32(205, 170, 112)
)

register_clickable(
    dome_band,
    "anda"
)

# ============================================================
# HARMIKA GROUP
# ============================================================

harmika_group = Entity(
    parent=stupa,
    position=(0, 5.79, 0)
)


# ============================================================
# HARMIKA BASE
# ============================================================

harmika = Entity(
    parent=harmika_group,
    model='cube',
    scale=(1.9, 0.18, 1.9),
    position=(0, 0, 0),
    color=MID_STONE
)

register_clickable(
    harmika,
    "harmika"
)


# ============================================================
# HARMIKA RAILING
# ============================================================

harmika_parts = []


# Four corner posts
for x in [-0.9, 0.9]:
    for z in [-0.9, 0.9]:

        post = Entity(
            parent=harmika_group,
            model='cube',
            scale=(0.12, 0.65, 0.12),
            position=(x, 0.415, z),
            color=DARK_STONE
        )

        harmika_parts.append(post)
        register_clickable(post, "harmika")


# Front and back rails
for z in [-0.9, 0.9]:

    for y in [0.27, 0.52]:

        rail = Entity(
            parent=harmika_group,
            model='cube',
            scale=(1.9, 0.10, 0.10),
            position=(0, y, z),
            color=DARK_STONE
        )

        harmika_parts.append(rail)
        register_clickable(rail, "harmika")


# Left and right rails
for x in [-0.9, 0.9]:

    for y in [0.27, 0.52]:

        rail = Entity(
            parent=harmika_group,
            model='cube',
            scale=(0.10, 0.10, 1.9),
            position=(x, y, 0),
            color=DARK_STONE
        )

        harmika_parts.append(rail)
        register_clickable(rail, "harmika")


# ============================================================
# YASTI
# ============================================================

mast = Entity(
    parent=stupa,
    model='cube',
    scale=(0.13, 2.2, 0.13),
   # YASTI
    position=(0, 7.28, 0),
    color=DARK_STONE
)

register_clickable(
    mast,
    "yasti"
)

# ============================================================
# CHATTRAS
# ============================================================

chattra1 = Entity(
    parent=stupa,
    model=Cylinder(resolution=64),
    scale=(2.25, 0.18, 2.25),
    position=(0, 6.68, 0),
    color=DARK_STONE
)

chattra2 = Entity(
    parent=stupa,
    model=Cylinder(resolution=64),
    scale=(1.75, 0.16, 1.75),
    position=(0, 7.38, 0),
    color=DARK_STONE
)

chattra3 = Entity(
    parent=stupa,
    model=Cylinder(resolution=64),
    scale=(1.25, 0.14, 1.25),
    position=(0, 7.98, 0),
    color=DARK_STONE
)

for chattra in [
    chattra1,
    chattra2,
    chattra3
]:

    register_clickable(
        chattra,
        "chattra"
    )


# ============================================================
# VEDIKA RAILING
# ============================================================

railing_radius = 6.25
number_of_posts = 48

vedika_parts = []


# ============================================================
# VEDIKA POSTS WITH STAIRCASE OPENING
# ============================================================

for i in range(number_of_posts):

    angle = math.radians(
        i * 360 / number_of_posts
    )

    x = math.sin(angle) * railing_radius
    z = math.cos(angle) * railing_radius

    # --------------------------------------------------------
    # Leave an opening for the staircase.
    #
    # Staircase is located on the negative Z side.
    # Do not create railing directly in front of it.
    # --------------------------------------------------------

    if z < -5.2 and abs(x) < 1.8:
        continue

    post = Entity(
    parent=vedika_group,
    model='cube',
    scale=(0.17, 1.35, 0.17),
    position=(x, 1.25, z),
    color=RAILING_COLOR
)

    vedika_parts.append(post)

    register_clickable(
        post,
        "vedika"
    )
# Horizontal railing segments
segments = 48

# ============================================================
# VEDIKA HORIZONTAL RAILS WITH STAIRCASE OPENING
# ============================================================

for i in range(segments):

    angle = math.radians(
        i * 360 / segments
    )

    x = math.sin(angle) * railing_radius
    z = math.cos(angle) * railing_radius

    rotation = i * 360 / segments

    # Leave opening for staircase
    if z < -5.2 and abs(x) < 1.8:
        continue

    for y in [0.92, 1.48]:

        beam = Entity(
            parent=vedika_group,
            model='cube',
            scale=(0.90, 0.12, 0.12),
            position=(x, y, z),
            rotation_y=rotation,
            color=RAILING_COLOR
        )

        vedika_parts.append(beam)

        register_clickable(
            beam,
            "vedika"
        )

# ============================================================
# TORANA FUNCTION
# ============================================================

torana_parts = []


def create_torana(x, z, rotation):

    gate = Entity(
        parent=torana_group,
        position=(x, 0, z),
        rotation_y=rotation
    )

    # ========================================================
    # TWO MAIN PILLARS
    # ========================================================

    for pillar_x in [-1.65, 1.65]:

        # Base
        base = Entity(
            parent=gate,
            model='cube',
            position=(pillar_x, 0.18, 0),
            scale=(0.62, 0.32, 0.62),
            color=MID_STONE
        )

        # Main vertical pillar
        pillar = Entity(
            parent=gate,
            model='cube',
            position=(pillar_x, 2.0, 0),
            scale=(0.36, 3.7, 0.36),
            color=DARK_STONE
        )

        # Capital
        capital = Entity(
            parent=gate,
            model='cube',
            position=(pillar_x, 3.90, 0),
            scale=(0.70, 0.30, 0.58),
            color=MID_STONE
        )

        for part in [base, pillar, capital]:

            torana_parts.append(part)

            register_clickable(
                part,
                "torana"
            )


    # ========================================================
    # THREE ARCHITRAVES
    # ========================================================

    architraves = [

        # height, width
        (3.80, 4.55),
        (4.50, 4.85),
        (5.20, 5.15)

    ]

    for height, width in architraves:

        beam = Entity(
            parent=gate,
            model='cube',
            position=(0, height, 0),
            scale=(width, 0.23, 0.36),
            color=SANDSTONE
        )

        torana_parts.append(beam)
        register_clickable(beam, "torana")


        # --------------------------------------------
        # SMALL UP-TURNED ENDS
        # --------------------------------------------

        for side in [-1, 1]:

            end_x = side * (width / 2 + 0.20)

            end_piece = Entity(
                parent=gate,
                model='cube',
                position=(
                    end_x,
                    height + 0.05,
                    0
                ),
                scale=(
                    0.48,
                    0.25,
                    0.38
                ),
                rotation_z=side * 7,
                color=DARK_STONE
            )

            torana_parts.append(end_piece)

            register_clickable(
                end_piece,
                "torana"
            )


    # ========================================================
    # SUPPORTS BETWEEN ARCHITRAVES
    # ========================================================

    for support_x in [-1.65, 1.65]:

        support1 = Entity(
            parent=gate,
            model='cube',
            position=(
                support_x,
                4.15,
                0
            ),
            scale=(
                0.18,
                0.45,
                0.28
            ),
            color=DARK_STONE
        )

        support2 = Entity(
            parent=gate,
            model='cube',
            position=(
                support_x,
                4.85,
                0
            ),
            scale=(
                0.18,
                0.45,
                0.28
            ),
            color=DARK_STONE
        )

        for part in [
            support1,
            support2
        ]:

            torana_parts.append(part)

            register_clickable(
                part,
                "torana"
            )


    # ========================================================
    # SMALL CENTRAL DECORATIVE MEDALLIONS
    # ========================================================

    for height in [
        3.80,
        4.50,
        5.20
    ]:

        ornament = Entity(
            parent=gate,
            model='cube',
            position=(
                0,
                height,
                -0.22
            ),
            scale=(
                0.38,
                0.38,
                0.12
            ),
            rotation_z=45,
            color=MID_STONE
        )

        torana_parts.append(ornament)

        register_clickable(
            ornament,
            "torana"
        )


    return gate
# ============================================================
# FOUR TORANAS
# ============================================================

north_gate = create_torana(0, 7.4, 0)
south_gate = create_torana(0, -7.8, 0)
east_gate = create_torana(7.4, 0, 90)
west_gate = create_torana(-7.4, 0, 90)


# ============================================================
# CAMERA
#
# DO NOT replace this with EditorCamera.
# This is the setup known to work on your PC.
# ============================================================

camera.position = (
    0,
    2,
    -27
)

camera.rotation = (
    0,
    0,
    0
)

camera.fov = 60

# ============================================================
# LIGHTING
# ============================================================

sun = DirectionalLight(
    parent=scene,
    shadows=True
)

sun.look_at(
    Vec3(1, -1, -1)
)

ambient = AmbientLight(
    parent=scene,
    color=color.rgba(120, 120, 120, 0.35)
)

# ============================================================
# UI HEADER
# ============================================================

Text(
    text="SANCHI STUPA",
    position=(-0.87, 0.46),
    scale=1.5,
    color=color.black
)

Text(
    text="Interactive Reconstruction | Indian Knowledge Systems",
    position=(-0.87, 0.41),
    scale=0.72,
    color=color.rgb32(50, 50, 50)
)


# ============================================================
# INFORMATION PANEL
# ============================================================

info_panel = Entity(
    parent=camera.ui,
    model='quad',
    scale=(0.38, 0.36),
    position=(0.68, -0.20),
    color=PANEL_COLOR
)

info_title = Text(
    parent=camera.ui,
    text="EXPLORE SANCHI",
    position=(0.52, -0.07),
    scale=0.75,
    color=color.white
)

info_subtitle = Text(
    parent=camera.ui,
    text="Interactive Architectural Model",
    position=(0.52, -0.115),
    scale=0.48,
    color=color.rgb32(225, 190, 125)
)

info_text = Text(
    parent=camera.ui,
    text=(
        "Click an architectural component\n"
        "to learn about its role in the\n"
        "structure of the Sanchi Stupa.\n\n"
        "Try clicking the dome, gateway,\n"
        "railing or upper structure."
    ),
    position=(0.52, -0.165),
    scale=0.43,
    color=color.white
)

# ============================================================
# FLOATING ARCHITECTURAL LABEL
# ============================================================

floating_label = Text(
    parent=camera.ui,
    text="",
    origin=(0, 0),
    position=(0, 0.20),
    scale=0.75,
    color=color.white,
    background=True
)

floating_label.background.color = color.rgba32(
    25, 25, 25, 210
)

floating_label.enabled = False

# ============================================================
# CONTROL LABEL
# ============================================================

control_text = Text(
    parent=camera.ui,
    text=
        "Right Mouse + Drag : Rotate\n"
        "Mouse Wheel : Zoom\n"
        "Click Structure : Learn",
    position=(-0.87, -0.38),
    scale=0.60,
    color=color.black
)


# ============================================================
# BUTTONS
# ============================================================

button_y = -0.45


def make_button(text, x, width=0.15):

    button = Button(
        parent=camera.ui,
        text=text,
        position=(x, button_y),
        scale=(width, 0.055),
        color=BUTTON_COLOR,
        highlight_color=BUTTON_HOVER,
        text_color=color.white
    )

    return button


explore_button = make_button(
    "EXPLORE",
    -0.34,
    0.13
)

build_button = make_button(
    "CONSTRUCTION",
    -0.18,
    0.17
)

explode_button = make_button(
    "EXPLODED",
    0.00,
    0.14
)

tour_button = make_button(
    "GUIDED TOUR",
    0.17,
    0.17
)

reset_button = make_button(
    "RESET",
    0.33,
    0.11
)

# ============================================================
# ROTATION
# ============================================================

rotation_speed = 90
interaction_enabled = True
construction_running = False

def update():

    if welcome_screen.enabled:
        return

    if not interaction_enabled:
        return

    if held_keys['right mouse']:

        # Don't rotate while interacting with UI
        if mouse.hovered_entity:
            try:
                if mouse.hovered_entity.has_ancestor(camera.ui):
                    return
            except:
                pass

        # Horizontal rotation
        stupa.rotation_y -= mouse.velocity[0] * 80

        # Small vertical tilt only
        stupa.rotation_x += mouse.velocity[1] * 35

        # Prevent visitors from flipping the monument
        stupa.rotation_x = clamp(
            stupa.rotation_x,
            -5,
            12
        )

# ============================================================
# NORMAL POSITIONS
# ============================================================

normal_positions = {

    anda: 3.15,
    dome_band: 1.45,

    harmika_group: 5.79,

    mast: 7.28,

    chattra1: 6.68,
    chattra2: 7.38,
    chattra3: 7.98
}

# ============================================================
# EXPLODED VIEW
# ============================================================

exploded = False


def exploded_view():

    global exploded

    floating_label.enabled = False

    exploded = not exploded

    clear_highlight()

    if exploded:

        anda.animate_y(
            4.2,
            duration=0.7
        )

        dome_band.animate_y(
            2.0,
            duration=0.7
        )

        harmika_group.animate_y(
    8.0,
    duration=0.7
)

        mast.animate_y(
            11.3,
            duration=0.7
        )

        chattra1.animate_y(
            9.7,
            duration=0.7
        )

        chattra2.animate_y(
            11.0,
            duration=0.7
        )

        chattra3.animate_y(
            12.5,
            duration=0.7
        )

        info_title.text = "EXPLODED VIEW"

        info_subtitle.text = \
            "Architectural Components"

        info_text.text = (
            "The upper elements are separated\n"
            "to reveal how the monument is\n"
            "organized vertically.\n\n"
            "Press EXPLODED again to return\n"
            "to the complete monument."
        )

    else:

        return_from_exploded()


def return_from_exploded():

    global exploded

    exploded = False

    for entity, target_y in \
            normal_positions.items():

        entity.animate_y(
            target_y,
            duration=0.7
        )

    info_title.text = "EXPLORE SANCHI"

    info_subtitle.text = \
        "Interactive Architectural Model"

    info_text.text = (
        "Click an architectural component\n"
        "to learn about its role in the\n"
        "structure of the Sanchi Stupa."
    )


# ============================================================
# CONSTRUCTION MODE
# ============================================================

construction_parts = [

    lower_platform,
    upper_platform,

    staircase_group,

    dome_band,
    anda,

    vedika_group,

    harmika_group,

    mast,
    chattra1,
    chattra2,
    chattra3,

    torana_group
]

construction_original_y = {
    entity: entity.y
    for entity in construction_parts
}

construction_original_z = {
    staircase_group: staircase_group.z
}

def restore_main_structure():

    for entity in construction_parts:

        entity.enabled = True
        entity.y = construction_original_y[entity]

    staircase_group.z = construction_original_z[
        staircase_group
    ]
    
def show_build_part(entity):

    if not construction_running:
        return

    entity.enabled = True

    target_y = construction_original_y[entity]

    # -----------------------------------------
    # STAIRCASE
    # Slides slightly forward + upward
    # -----------------------------------------
    if entity == staircase_group:

        target_z = 0

        entity.y = target_y - 2
        entity.z = -2

        entity.animate_y(
            target_y,
            duration=0.7
        )

        entity.animate_z(
            target_z,
            duration=0.7
        )

    # -----------------------------------------
    # VEDIKA
    # Rises gently around the monument
    # -----------------------------------------
    elif entity == vedika_group:

        entity.y = target_y - 2.5

        entity.animate_y(
            target_y,
            duration=0.8
        )

    # -----------------------------------------
    # TORANAS
    # Rise last and more dramatically
    # -----------------------------------------
    elif entity == torana_group:

        entity.y = target_y - 4

        entity.animate_y(
            target_y,
            duration=1.0
        )

# ============================================================
# REALISTIC LIGHTING SHADER
# ============================================================

for entity in scene.entities:

    if isinstance(entity, Entity):

        try:
            if entity.has_ancestor(stupa):
                entity.shader = lit_with_shadows_shader
        except:
            pass

    # -----------------------------------------
    # HARMika
    # Small controlled rise
    # -----------------------------------------
    elif entity == harmika_group:

        entity.y = target_y - 1.5

        entity.animate_y(
            target_y,
            duration=0.65
        )

    # -----------------------------------------
    # YASTI
    # Vertical mast rises upward
    # -----------------------------------------
    elif entity == mast:

        entity.y = target_y - 2

        entity.animate_y(
            target_y,
            duration=0.65
        )

    # -----------------------------------------
    # CHATTRAS
    # Stack individually
    # -----------------------------------------
    elif entity in [
        chattra1,
        chattra2,
        chattra3
    ]:

        entity.y = target_y - 1.5

        entity.animate_y(
            target_y,
            duration=0.55
        )

    # -----------------------------------------
    # EVERYTHING ELSE
    # Platforms, dome band, Anda
    # -----------------------------------------
    else:

        entity.y = target_y - 3

        entity.animate_y(
            target_y,
            duration=0.7
        )


def construction_mode():

    global exploded
    global interaction_enabled
    global construction_running

    construction_running = True

    exploded = False

    clear_highlight()
    floating_label.enabled = False

    interaction_enabled = False
    

    stupa.rotation = (
        0,
        0,
        0
    )

    info_title.text = "CONSTRUCTION MODE"

    info_subtitle.text = \
        "Building the Stupa"

    info_text.text = (
        "The monument is being assembled\n"
        "from its foundation upward.\n\n"
        "Observe the sequence of major\n"
        "architectural components."
    )


    # Hide major structure
    for entity in construction_parts:
        entity.enabled = False


    delay_time = 0.3

    for entity in construction_parts:

        invoke(
            show_build_part,
            entity,
            delay=delay_time
        )

        delay_time += 0.55


    invoke(
        finish_construction,
        delay=delay_time + 0.5
    )


def finish_construction():

    global interaction_enabled
    global construction_running

    if not construction_running:
        return

    construction_running = False
    interaction_enabled = True

    info_title.text = "CONSTRUCTION COMPLETE"

    info_subtitle.text = \
        "Sanchi Stupa"

    info_text.text = (
        "The principal architectural layers\n"
        "have been assembled.\n\n"
        "You can now rotate the monument\n"
        "or click its components."
    )


# ============================================================
# EXPLORE MODE
# ============================================================

def explore_mode():

    global interaction_enabled
    global tour_running
    global construction_running
    global exploded

    interaction_enabled = True
    tour_running = False
    construction_running = False
    exploded = False

    restore_main_structure()

    clear_highlight()
    floating_label.enabled = False

    info_title.text = "EXPLORE SANCHI"

    info_subtitle.text = \
        "Click an Architectural Element"

    info_text.text = (
        "Anda\n"
        "Harmika\n"
        "Chattra\n"
        "Yasti\n"
        "Vedika\n"
        "Torana\n"
        "Pradakshina Patha"
    )
    
# ============================================================
# GUIDED TOUR
# ============================================================

tour_running = False

tour_sequence = [
    "torana",
    "vedika",
    "pradakshina",
    "anda",
    "harmika",
    "yasti",
    "chattra"
]

tour_delay = 4.0


def show_tour_step(group_name):

    global tour_running

    if not tour_running:
        return

    # Rotate model depending on architectural component
    rotations = {
        "torana": 0,
        "vedika": 25,
        "pradakshina": 45,
        "anda": 0,
        "harmika": 0,
        "yasti": 0,
        "chattra": 0
    }

    target_rotation = rotations.get(
        group_name,
        0
    )

    stupa.animate_rotation_y(
        target_rotation,
        duration=1.0
    )

    select_architecture(
        group_name
    )

def guided_tour():

    global tour_running
    global interaction_enabled

    if tour_running:
        return

    tour_running = True
    interaction_enabled = False
    clear_highlight()

    floating_label.enabled = False

    stupa.rotation = (
        0,
        0,
        0
    )

    info_title.text = "GUIDED TOUR"

    info_subtitle.text = "Architecture of Sanchi"

    info_text.text = (
        "The guided tour will explain\n"
        "the main architectural elements\n"
        "of the Sanchi Stupa."
    )

    delay = 1.5

    for group_name in tour_sequence:

        invoke(
            show_tour_step,
            group_name,
            delay=delay
        )

        delay += tour_delay

    invoke(
        finish_guided_tour,
        delay=delay
    )


def finish_guided_tour():

    global tour_running
    global interaction_enabled

    if not tour_running:
        return

    tour_running = False
    interaction_enabled = True

    clear_highlight()
    floating_label.enabled = False

    info_title.text = "TOUR COMPLETE"
    info_subtitle.text = "Sanchi Stupa"

    info_text.text = (
        "You have explored the main\n"
        "architectural elements of the\n"
        "Sanchi Stupa.\n\n"
        "You can now explore the model\n"
        "manually."
    )

# ============================================================
# RESET
# ============================================================

def reset_view():

    global exploded
    global interaction_enabled
    global tour_running
    global construction_running
    global selected_group

    exploded = False
    tour_running = False
    construction_running = False
    interaction_enabled = True
    selected_group = None

    clear_highlight()
    floating_label.enabled = False

    stupa.rotation = (
        0,
        0,
        0
    )

    camera.position = (
        0,
        2,
        -27
    )

    # Restore all construction objects
    for entity in construction_parts:

        entity.enabled = True
        entity.y = construction_original_y[entity]

    # Restore staircase position
    staircase_group.z = construction_original_z[
        staircase_group
    ]

    info_title.text = "EXPLORE SANCHI"

    info_subtitle.text = \
        "Interactive Architectural Model"

    info_text.text = (
        "Click an architectural component\n"
        "to learn about its role in the\n"
        "structure of the Sanchi Stupa."
    )

# ============================================================
# BUTTON FUNCTIONS
# ============================================================



explore_button.on_click = explore_mode
build_button.on_click = construction_mode
explode_button.on_click = exploded_view
reset_button.on_click = reset_view
tour_button.on_click = guided_tour


# ============================================================
# KEYBOARD / MOUSE INPUT
# ============================================================

def input(key):

    if welcome_screen.enabled:
        return
    
    # Zoom in
    if key == 'scroll up':

        camera.z += 1

        camera.z = min(
            camera.z,
            -18
        )


    # Zoom out
    if key == 'scroll down':

        camera.z -= 1

        camera.z = max(
            camera.z,
            -38
        )


    if key == 'r':
        reset_view()

    if key == 'e':
        exploded_view()

    if key == 'c':
        construction_mode()

    if key == 'g':
        guided_tour()

# ============================================================
# WELCOME / EXHIBITION SCREEN
# ============================================================

welcome_screen = Entity(
    parent=camera.ui,
    model='quad',
    scale=(2, 1),
    color=color.rgb32(32, 25, 20),
    z=-10
)

welcome_title = Text(
    parent=welcome_screen,
    text="SANCHI STUPA",
    origin=(0, 0),
    y=0.23,
    scale=2.3,
    color=color.rgb32(235, 193, 110)
)

welcome_subtitle = Text(
    parent=welcome_screen,
    text="AN INTERACTIVE EXPLORATION OF\nANCIENT INDIAN ARCHITECTURE",
    origin=(0, 0),
    y=0.10,
    scale=0.85,
    color=color.white
)

welcome_iks = Text(
    parent=welcome_screen,
    text="INDIAN KNOWLEDGE SYSTEMS",
    origin=(0, 0),
    y=-0.02,
    scale=0.75,
    color=color.rgb32(235, 193, 110)
)

welcome_description = Text(
    parent=welcome_screen,
    text=(
        "Explore the architecture, symbolism and sacred spatial\n"
        "organization of the Great Stupa at Sanchi."
    ),
    origin=(0, 0),
    y=-0.11,
    scale=0.60,
    color=color.rgb32(225, 225, 225)
)

start_button = Button(
    parent=welcome_screen,
    text="START EXPLORING",
    origin=(0, 0),
    y=-0.26,
    scale=(0.24, 0.07),
    color=color.rgb32(154, 105, 55),
    highlight_color=color.rgb32(195, 145, 75),
    text_color=color.white
)

welcome_footer = Text(
    parent=welcome_screen,
    text="Interactive 3D Reconstruction",
    origin=(0, 0),
    y=-0.39,
    scale=0.48,
    color=color.rgb32(175, 175, 175)
)

def start_exploring():

    welcome_screen.enabled = False

    stupa.rotation = (
        0,
        0,
        0
    )

    camera.position = (
        0,
        2,
        -27
    )

    info_title.text = "EXPLORE SANCHI"

    info_subtitle.text = \
        "Interactive Architectural Model"

    info_text.text = (
        "Click an architectural component\n"
        "to learn about its role in the\n"
        "structure of the Sanchi Stupa."
    )


start_button.on_click = start_exploring


# ============================================================
# RUN APPLICATION
# ============================================================

app.run()