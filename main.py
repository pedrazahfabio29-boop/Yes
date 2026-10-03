"""
Roblox place publishing backend  -  v2
=====================================

POST /publish   build the .rbxlx from your JSON and upload it through Open Cloud
POST /build     same build, but returns the .rbxlx so you can open it in Studio and inspect it
GET  /health

REQUEST BODY
------------
{
  "apiKey": "...",              (or set env ROBLOX_API_KEY)
  "universeId": 123,
  "placeId": 456,
  "versionType": "Published",   (optional, "Saved" or "Published")
  "unionFallback": "part",      (optional, "part" | "skip", see UNSUPPORTED below)
  "instances": [ <node>, ... ]
}

NODE (everything is optional except ClassName)
----------------------------------------------
{
  "ClassName": "Part",
  "Name": "Lamp",
  "Id": "lamp1",                      # lets other nodes point at this one (Part0, Part1, PrimaryPart ...)
  "Parent": "Workspace",              # top-level nodes only, see SERVICE ROUTING
  "Properties": { "Size": [4,1,4] },  # any property, OR put properties directly on the node (old format still works)
  "Attributes": { "Health": 50, "Team": "Red" },
  "Tags": ["Enemy"],
  "Children": [ <node>, ... ],        # any depth, any class
  "Decals": [ ... ],                  # old format, still supported
  "Scripts": [ ... ]                  # same as Children, ClassName defaults to "Script"
}

PROPERTY VALUES
---------------
  Vector3 [x,y,z]            CFrame [12 numbers] | [x,y,z] | [x,y,z,qx,qy,qz,qw]
                             | {"Position":[..], "Orientation":[degX,degY,degZ]}
  Color   "#rrggbb" | [r,g,b] (0-255, or 0-1 when every value is <= 1) | {"R":..,"G":..,"B":..}
  UDim2   [xs,xo,ys,yo]      Enums  "Neon" | "Enum.Material.Neon" | 288
  Refs    an "Id" from this payload, or the Name of a node inside the same Model
  Content 12345 | "rbxassetid://12345" | "http://www.roblox.com/asset/?id=12345"
  Explicit type for anything exotic: {"type":"Vector2","value":[1,2]}

SERVICE ROUTING (top-level nodes)
---------------------------------
  Parent can be any service from your template: "Workspace", "ServerScriptService", "ReplicatedStorage",
  "StarterGui", "Lighting", "StarterPlayer/StarterPlayerScripts", ...
  If Parent is missing: Script -> ServerScriptService, LocalScript -> StarterPlayerScripts,
  ModuleScript -> ReplicatedStorage, ScreenGui -> StarterGui, Tool -> StarterPack,
  Sky/Atmosphere/Bloom/... -> Lighting, everything else -> Workspace.

NPCs
----
  1) Send the exported Model tree (Parts, Humanoid, Motor6D, Attachments, Accessories, Shirt, Pants,
     BodyColors, scripts ...). Missing Motor6Ds / PrimaryPart / RigType are repaired (R6 and R15).
  2) Or use the shorthand, which builds a complete R6 rig for you:
     {"ClassName":"NPC","Name":"Guard","Position":[0,5,0],"Orientation":[0,90,0],
      "WalkSpeed":16,"Health":100,"DisplayName":"Guard",
      "BodyColors":{"All":[245,205,47],"Torso":[0,0,255]},
      "Shirt":"rbxassetid://TEMPLATE_IMAGE_ID","Pants":"...","Face":"rbxasset://textures/face.png",
      "Accessories":[{"Name":"Hat","AttachmentName":"HatAttachment","MeshId":123,"TextureId":456,"Size":[1,1,1]}],
      "Scripts":[{"ClassName":"Script","Name":"AI","Source":"print('hi')"}]}

UNSUPPORTED (Roblox's place publishing API does not update these, so they are skipped with a warning)
  EditableImage, EditableMesh, SurfaceAppearance, BaseWrap (WrapLayer, WrapTarget ...), PartOperation.
  Unions/PartOperations are replaced by a plain Part of the same size ("unionFallback":"part") or skipped.
"""

import base64
import logging
import math
import os
import re
import struct
import uuid
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("publisher")

# =========================================================
# TEMPLATE  -  PASTE YOUR REAL .rbxlx BETWEEN THE QUOTES
# (if it contains three double quotes in a row, save it as
#  template.rbxlx next to this file instead and leave this as is)
# =========================================================
TEMPLATE = r"""PASTE_YOUR_RBXLX_TEMPLATE_HERE"""
TEMPLATE_PLACEHOLDER = "PASTE_YOUR_RBXLX_TEMPLATE_HERE"

# Everything in the template's Workspace is removed except these classes
WORKSPACE_KEEP = {"Camera", "Terrain"}

# Classes whose "Texture" is converted to rbxthumb (same behaviour as your old backend)
THUMBNAIL_CLASSES = {"Decal", "Texture"}


def get_template():
    t = TEMPLATE
    if TEMPLATE_PLACEHOLDER in t or "<roblox" not in t:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.rbxlx")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
        raise RuntimeError("TEMPLATE is empty: paste your .rbxlx into TEMPLATE (or save it as template.rbxlx next to app.py)")
    return t


# =========================================================
# SMALL HELPERS
# =========================================================
def esc(v):
    return xml_escape(clean_text(v), {'"': "&quot;"})


_BAD_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")


def clean_text(v):
    return _BAD_XML.sub("", str(v))


def cdata(s):
    return "<![CDATA[" + clean_text(s).replace("]]>", "]]]]><![CDATA[>") + "]]>"


def new_ref():
    return "RBX" + uuid.uuid4().hex.upper()


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def num(v, d=0.0):
    try:
        f = float(v)
        return d if math.isnan(f) else f
    except (TypeError, ValueError):
        return d


def fnum(v):
    f = num(v)
    if math.isinf(f):
        return "INF" if f > 0 else "-INF"
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    return repr(f)


def truthy(v):
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "yes", "on")
    return bool(v)


def seq(v, n, keys, default=None):
    """list / dict / scalar -> list of n floats"""
    default = default if default is not None else [0.0] * n
    if isinstance(v, dict):
        out = []
        for k in keys:
            val = v.get(k)
            if val is None:
                val = v.get(k.lower())
            out.append(val)
    elif isinstance(v, (list, tuple)):
        out = list(v)
    else:
        out = [v]
    return [num(out[i], default[i]) if i < len(out) and out[i] is not None else default[i] for i in range(n)]


# ---------- CFrame math (12 number lists: x y z r00 r01 r02 r10 r11 r12 r20 r21 r22) ----------
IDENT = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
CF_KEYS = ["X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22"]


def _m(cf):
    return [cf[3:6], cf[6:9], cf[9:12]]


def _flat(m):
    return [x for r in m for x in r]


def _mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _mat_vec(a, v):
    return [sum(a[i][k] * v[k] for k in range(3)) for i in range(3)]


def cf_mul(a, b):
    p = _mat_vec(_m(a), b[:3])
    return [a[0] + p[0], a[1] + p[1], a[2] + p[2]] + _flat(_mat_mul(_m(a), _m(b)))


def cf_inv(a):
    r = _m(a)
    rt = [[r[j][i] for j in range(3)] for i in range(3)]
    p = _mat_vec(rt, a[:3])
    return [-p[0], -p[1], -p[2]] + _flat(rt)


def cf_pos(x, y, z):
    return [x, y, z] + IDENT[3:]


def euler_to_matrix(rx, ry, rz):
    """Roblox CFrame.fromOrientation (Y * X * Z), radians"""
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    mx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    my = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    mz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return _mat_mul(_mat_mul(my, mx), mz)


def quat_to_matrix(qx, qy, qz, qw):
    n = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw) or 1.0
    qx, qy, qz, qw = qx / n, qy / n, qz / n, qw / n
    return [
        [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
        [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
        [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
    ]


def to_cframe(v):
    if isinstance(v, dict):
        low = {str(k).lower(): x for k, x in v.items()}
        if "position" in low or "orientation" in low:
            p = seq(low.get("position"), 3, "XYZ")
            o = [math.radians(a) for a in seq(low.get("orientation"), 3, "XYZ")]
            return p + _flat(euler_to_matrix(*o))
        if "components" in low:
            v = low["components"]
        else:
            v = [low.get(k.lower(), d) for k, d in zip(CF_KEYS, IDENT)]
    if isinstance(v, (list, tuple)):
        v = [num(x) for x in v]
        if len(v) >= 12:
            return v[:12]
        if len(v) == 7:
            return v[:3] + _flat(quat_to_matrix(*v[3:7]))
        if len(v) == 3:
            return v + IDENT[3:]
    return list(IDENT)


# ---------- colours ----------
def to_rgb01(v):
    vals = None
    if isinstance(v, str):
        s = v.strip().lstrip("#")
        if re.fullmatch(r"[0-9a-fA-F]{6}", s):
            return [int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        vals = [num(x) for x in re.split(r"[,\s]+", s) if x]
    elif isinstance(v, dict):
        vals = [num(v.get(k, v.get(k.lower()))) for k in "RGB"]
    elif isinstance(v, (list, tuple)):
        vals = [num(x) for x in v]
    if not vals or len(vals) < 3:
        vals = [163, 162, 165]
    vals = vals[:3]
    if max(vals) > 1:
        vals = [x / 255 for x in vals]
    return [min(max(x, 0.0), 1.0) for x in vals]


def pack_c3u8(rgb):
    r, g, b = [int(round(x * 255)) for x in rgb]
    return (0xFF << 24) | (r << 16) | (g << 8) | b


# =========================================================
# ENUMS  (values checked against the Roblox creator-docs)
# =========================================================
def _table(d):
    return {_norm(k): v for k, v in d.items()}


MATERIALS = _table({
    "Plastic": 256, "SmoothPlastic": 272, "Neon": 288, "Wood": 512, "WoodPlanks": 528, "Marble": 784,
    "Basalt": 788, "Slate": 800, "CrackedLava": 804, "Concrete": 816, "Limestone": 820, "Granite": 832,
    "Pavement": 836, "Brick": 848, "Pebble": 864, "Cobblestone": 880, "Rock": 896, "Sandstone": 912,
    "CorrodedMetal": 1040, "DiamondPlate": 1056, "Foil": 1072, "Metal": 1088, "Grass": 1280, "LeafyGrass": 1284,
    "Sand": 1296, "Fabric": 1312, "Snow": 1328, "Mud": 1344, "Ground": 1360, "Asphalt": 1376, "Salt": 1392,
    "Ice": 1536, "Glacier": 1552, "Glass": 1568, "ForceField": 1584, "Air": 1792, "Water": 2048,
    "Cardboard": 2304, "Carpet": 2305, "CeramicTiles": 2306, "ClayRoofTiles": 2307, "RoofShingles": 2308,
    "Leather": 2309, "Plaster": 2310, "Rubber": 2311,
})
SURFACES = _table({"Smooth": 0, "Glue": 1, "Weld": 2, "Studs": 3, "Inlet": 4, "Universal": 5, "Hinge": 6,
                   "Motor": 7, "SteppingMotor": 8, "SmoothNoOutlines": 10})
SHAPES = _table({"Ball": 0, "Sphere": 0, "Block": 1, "Cylinder": 2, "Wedge": 3, "CornerWedge": 4})
NORMAL_ID = _table({"Right": 0, "Top": 1, "Back": 2, "Left": 3, "Bottom": 4, "Front": 5})
MESH_TYPES = _table({"Head": 0, "Torso": 1, "Wedge": 2, "Sphere": 3, "Cylinder": 4, "FileMesh": 5, "Brick": 6,
                     "Prism": 7, "Pyramid": 8, "ParallelRamp": 9, "RightAngleRamp": 10, "CornerWedge": 11})
RUN_CONTEXT = _table({"Legacy": 0, "Server": 1, "Client": 2, "Plugin": 3})

ENUMS = {
    "Material": MATERIALS,
    "TopSurface": SURFACES, "BottomSurface": SURFACES, "LeftSurface": SURFACES,
    "RightSurface": SURFACES, "FrontSurface": SURFACES, "BackSurface": SURFACES,
    "Shape": SHAPES,
    "Face": NORMAL_ID, "EmissionDirection": NORMAL_ID,
    "RigType": _table({"R6": 0, "R15": 1}),
    "RunContext": RUN_CONTEXT,
    "DisplayDistanceType": _table({"Viewer": 0, "Subject": 1, "None": 2}),
    "HealthDisplayType": _table({"DisplayWhenDamaged": 0, "AlwaysOn": 1, "AlwaysOff": 2}),
    "NameOcclusion": _table({"NoOcclusion": 0, "EnemyOcclusion": 1, "OccludeAll": 2}),
    "MeshType": MESH_TYPES,
    "RollOffMode": _table({"Inverse": 0, "Linear": 1, "LinearSquare": 2, "InverseTapered": 3}),
    "CollisionFidelity": _table({"Default": 0, "Hull": 1, "Box": 2, "PreciseConvexDecomposition": 3}),
    "RenderFidelity": _table({"Automatic": 0, "Precise": 1, "Performance": 2}),
    "AccessoryType": _table({"Unknown": 0, "Hat": 1, "Hair": 2, "Face": 3, "Neck": 4, "Shoulder": 5, "Front": 6,
                             "Back": 7, "Waist": 8, "TShirt": 9, "Shirt": 10, "Pants": 11, "Jacket": 12,
                             "Sweater": 13, "Shorts": 14, "LeftShoe": 15, "RightShoe": 16, "DressSkirt": 17,
                             "Eyebrow": 18, "Eyelash": 19}),
    "TextXAlignment": _table({"Left": 0, "Right": 1, "Center": 2}),
    "TextYAlignment": _table({"Top": 0, "Center": 1, "Bottom": 2}),
    "ScaleType": _table({"Stretch": 0, "Slice": 1, "Tile": 2, "Fit": 3, "Crop": 4}),
    "ZIndexBehavior": _table({"Global": 0, "Sibling": 1}),
}
ENUM_DEFAULTS = {"Material": 256, "Shape": 1, "Face": 5, "MeshType": 5}


def enum_value(prop, v, build, cls):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip()
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    table = ENUMS.get(prop)
    if table:
        key = _norm(s.split(".")[-1])
        if key in table:
            return table[key]
    build.warn(f"{cls}.{prop}: unknown enum value {v!r}, using default")
    return ENUM_DEFAULTS.get(prop, 0)


# =========================================================
# PROPERTY TYPE TABLES
# =========================================================
PROP_TYPES = {}


def _g(t, names):
    for n in names.split():
        PROP_TYPES[n] = t


_g("bool", """Anchored CanCollide CanTouch CanQuery CastShadow Massless Locked Enabled Shadows Looped Playing Disabled
 Archivable PlatformStand AutoRotate AutoJumpEnabled BreakJointsOnDeath RequiresNeck UseJumpPower EvaluateStateMachine
 DoubleSided PlayOnRemove AlwaysOnTop ResetOnSpawn Visible Active Neutral AllowTeamChangeOnTouch Selectable
 ClipsDescendants RichText TextWrapped TextScaled IgnoreGuiInset LightInfluence Draggable AutoButtonColor Modal
 ManualActivationOnly RequiresLineOfSight Reflectance_ Smooth Archivable_ ClassicDeath CanBeDropped
 RequiresHandle Visible_ AutomaticSize_""")
_g("float", """Transparency Reflectance Brightness Range Angle Volume PlaybackSpeed Health MaxHealth WalkSpeed
 JumpHeight JumpPower HipHeight MaxSlopeAngle Density Elasticity Friction FrictionWeight ElasticityWeight
 RollOffMaxDistance RollOffMinDistance MaxActivationDistance HoldDuration NameDisplayDistance HealthDisplayDistance
 BackgroundTransparency TextTransparency ImageTransparency Rotation TextSize_ Heat LightEmission Rate Drag
 TimeScale Squash Width0 Width1 CurveSize0 CurveSize1 Segments FaceCamera_ MaxDistance MinDistance StudsPerTileU
 StudsPerTileV OffsetStudsU OffsetStudsV Duration""")
_g("double", "TimePosition")
_g("int", """ZIndex LayoutOrder RootPriority BorderSizePixel TextSize Priority CollisionGroupId MaxPlayers
 LineHeight_""")
_g("string", """Name DisplayName CollisionGroup ActionText ObjectText Text ToolTip Title""")
_g("Vector3", """Velocity RotVelocity StudsOffset StudsOffsetWorldSpace VertexColor Axis SecondaryAxis Acceleration
 CameraOffset ExtentsOffset ExtentsOffsetWorldSpace LinearVelocity""")
_g("Vector2", "AnchorPoint SpreadAngle SizeOffset ImageRectOffset ImageRectSize CanvasPosition")
_g("CFrame", "CFrame C0 C1 AttachmentPoint PivotOffset")
_g("OptionalCFrame", "WorldPivot WorldPivotData")
_g("Color3", """Color BackgroundColor3 BorderColor3 TextColor3 ImageColor3 TextStrokeColor3 Ambient OutdoorAmbient
 ColorShift_Top ColorShift_Bottom FogColor Decay FillColor OutlineColor SecondaryColor""")
_g("Color3uint8", "HeadColor3 LeftArmColor3 LeftLegColor3 RightArmColor3 RightLegColor3 TorsoColor3")
_g("Content", """Texture TextureId TextureID MeshId SoundId Image ShirtTemplate PantsTemplate Graphic AnimationId
 SkyboxBk SkyboxDn SkyboxFt SkyboxLf SkyboxRt SkyboxUp MoonTextureId SunTextureId ColorMap NormalMap MetalnessMap
 RoughnessMap""")
_g("Ref", "Part0 Part1 PrimaryPart Attachment0 Attachment1 Adornee CameraSubject Target")
_g("ProtectedString", "Source")
_g("UDim2", "Position_ Size_ CanvasSize")
_g("UDim", "CornerRadius PaddingTop PaddingBottom PaddingLeft PaddingRight Padding_")
_g("BrickColor", "BrickColor TeamColor")
_g("Font", "FontFace")

# type overrides for names that mean different things on different classes
CLASS_PROP_TYPES = {
    ("StringValue", "Value"): "string", ("NumberValue", "Value"): "double", ("IntValue", "Value"): "int64",
    ("BoolValue", "Value"): "bool", ("Color3Value", "Value"): "Color3", ("Vector3Value", "Value"): "Vector3",
    ("CFrameValue", "Value"): "CFrame", ("ObjectValue", "Value"): "Ref", ("BrickColorValue", "Value"): "BrickColor",
    ("ParticleEmitter", "Lifetime"): "NumberRange", ("ParticleEmitter", "Speed"): "NumberRange",
    ("ParticleEmitter", "Rotation"): "NumberRange", ("ParticleEmitter", "RotSpeed"): "NumberRange",
    ("ParticleEmitter", "Size"): "NumberSequence", ("ParticleEmitter", "Transparency"): "NumberSequence",
    ("ParticleEmitter", "Color"): "ColorSequence", ("ParticleEmitter", "Squash"): "NumberSequence",
    ("Beam", "Color"): "ColorSequence", ("Beam", "Transparency"): "NumberSequence",
    ("Trail", "Color"): "ColorSequence", ("Trail", "Transparency"): "NumberSequence",
    ("Trail", "WidthScale"): "NumberSequence", ("Trail", "Lifetime"): "float",
    ("UIGradient", "Color"): "ColorSequence", ("UIGradient", "Transparency"): "NumberSequence",
    ("Sound", "Volume"): "float", ("PointLight", "Range"): "float", ("SpotLight", "Range"): "float",
    ("SurfaceLight", "Range"): "float",
    ("Fire", "Size"): "float", ("Smoke", "Size"): "float", ("Sparkles", "SparkleColor"): "Color3",
    ("UICorner", "CornerRadius"): "UDim", ("UIPadding", "PaddingLeft"): "UDim",
    ("ProximityPrompt", "KeyboardKeyCode"): "token", ("ProximityPrompt", "RequiresLineOfSight"): "bool",
    ("Humanoid", "Health"): "float", ("Seat", "Disabled"): "bool",
    ("Model", "LevelOfDetail"): "token", ("Model", "ModelStreamingMode"): "token",
    ("Atmosphere", "Density"): "float", ("Lighting", "Technology"): "token",
    ("Sky", "StarCount"): "int", ("SpawnLocation", "Duration"): "int",
}

for _n in ENUMS:
    PROP_TYPES.setdefault(_n, "token")
PROP_TYPES["Shape"] = "token"
PROP_TYPES["Style"] = "token"

BASEPARTS = {"Part", "WedgePart", "CornerWedgePart", "TrussPart", "SpawnLocation", "Seat", "VehicleSeat",
             "MeshPart", "SkateboardPlatform", "FlagStand"}
SCRIPT_CLASSES = {"Script", "LocalScript", "ModuleScript"}
UNION_CLASSES = {"UnionOperation", "PartOperation", "NegateOperation", "IntersectOperation"}
UNSUPPORTED = {"EditableImage", "EditableMesh", "SurfaceAppearance", "BaseWrap", "WrapLayer", "WrapTarget",
               "WrapDeformer"}
UNION_ONLY_PROPS = {"UsePartColor", "SmoothingAngle", "RenderFidelity", "CollisionFidelity", "FormFactor",
                    "MeshData", "ChildData", "PhysicsData", "AssetId", "InitialSize", "MeshData2", "ChildData2"}


def is_basepart(cls):
    return cls in BASEPARTS


TYPE_ALIASES = {
    "boolean": "bool", "bool": "bool", "number": "float", "float": "float", "double": "double", "int": "int",
    "int32": "int", "int64": "int64", "string": "string", "protectedstring": "ProtectedString",
    "content": "Content", "contentid": "Content", "token": "token", "enum": "token", "vector3": "Vector3",
    "vector2": "Vector2", "cframe": "CFrame", "coordinateframe": "CFrame", "optionalcframe": "OptionalCFrame",
    "color3": "Color3", "color3uint8": "Color3uint8", "brickcolor": "BrickColor", "udim": "UDim", "udim2": "UDim2",
    "numberrange": "NumberRange", "numbersequence": "NumberSequence", "colorsequence": "ColorSequence",
    "rect": "Rect2D", "rect2d": "Rect2D", "ref": "Ref", "physicalproperties": "PhysicalProperties",
    "font": "Font", "binarystring": "BinaryString", "faces": "Faces", "axes": "Axes", "tags": "Tags",
    "attributes": "Attributes",
}


def canon_type(t):
    return TYPE_ALIASES.get(_norm(t))


def infer_type(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "Content" if re.match(r"^(rbxassetid|rbxasset|rbxthumb|http)", v) else "string"
    if isinstance(v, (list, tuple)):
        return {2: "Vector2", 3: "Vector3", 4: "UDim2", 7: "CFrame", 12: "CFrame"}.get(len(v))
    if isinstance(v, dict):
        ks = {str(k).lower() for k in v}
        if ks & {"xs", "xo", "ys", "yo"}:
            return "UDim2"
        if {"x", "y", "z"} <= ks:
            return "Vector3"
        if {"r", "g", "b"} <= ks:
            return "Color3"
        if {"x", "y"} <= ks:
            return "Vector2"
        if ks & {"position", "components", "orientation"}:
            return "CFrame"
    return None


def resolve_type(cls, name, value):
    if name == "Color" and is_basepart(cls):
        return "Color3uint8"
    t = CLASS_PROP_TYPES.get((cls, name))
    if t:
        return t
    if name in ("Size", "Position"):
        return infer_type(value)
    return PROP_TYPES.get(name) or infer_type(value)


# =========================================================
# NODE MODEL
# =========================================================
class Build:
    def __init__(self, opts=None):
        self.opts = opts or {}
        self.warnings = []
        self.ids = {}       # user supplied Id -> referent
        self.refs = set()   # every referent we generate
        self.counts = {}

    def warn(self, msg):
        if len(self.warnings) < 300:
            self.warnings.append(msg)
        log.warning(msg)


class Node:
    __slots__ = ("cls", "name", "props", "children", "ref", "attributes", "tags", "path")

    def __init__(self, build, cls, name, props=None):
        self.cls = cls
        self.name = name
        self.props = props if props is not None else {}
        self.children = []
        self.ref = new_ref()
        self.attributes = None
        self.tags = None
        self.path = None
        build.refs.add(self.ref)
        build.counts[cls] = build.counts.get(cls, 0) + 1


RESERVED_KEYS = {"ClassName", "Class", "Children", "Decals", "Scripts", "Properties", "Parent", "Id", "ID",
                 "Attributes", "Tags"}

BASEPART_DEFAULTS = {
    "Size": [4, 4, 4], "Color": [163, 162, 165], "Anchored": True, "CanCollide": True, "Material": "Plastic",
    "TopSurface": "Smooth", "BottomSurface": "Smooth",
}


def normalize_basepart(cls, props):
    if "CFrame" not in props and ("Position" in props or "Orientation" in props):
        props["CFrame"] = {"Position": props.get("Position", [0, 0, 0]), "Orientation": props.get("Orientation", [0, 0, 0])}
    props.pop("Position", None)
    props.pop("Orientation", None)
    props.pop("Rotation", None)
    for k, v in BASEPART_DEFAULTS.items():
        props.setdefault(k, v)
    if cls == "Part":
        props.setdefault("Shape", "Block")


def make_node(data, build, default_class="Part"):
    if not isinstance(data, dict):
        build.warn("Skipped an entry that is not an object")
        return None
    cls = str(data.get("ClassName") or data.get("Class") or default_class)
    if cls == "NPC":
        return build_npc(data, build)

    props = {k: v for k, v in data.items() if k not in RESERVED_KEYS}
    props.update(data.get("Properties") or {})
    for alias in ("Code", "Lua", "source"):
        if alias in props and "Source" not in props:
            props["Source"] = props.pop(alias)

    if cls in UNION_CLASSES:
        if build.opts.get("unionFallback", "part") == "part":
            build.warn(f"{cls} '{props.get('Name', '')}' can't be published through the API, replaced with a plain Part of the same size")
            cls = "Part"
            for k in UNION_ONLY_PROPS:
                props.pop(k, None)
        else:
            build.warn(f"{cls} '{props.get('Name', '')}' skipped (not supported by the place publishing API)")
            return None
    if cls in UNSUPPORTED:
        build.warn(f"{cls} '{props.get('Name', '')}' skipped (not supported by the place publishing API)")
        return None
    if cls in THUMBNAIL_CLASSES and not str(props.get("Texture", "")).strip():
        return None

    name = str(props.pop("Name", None) or cls)
    if is_basepart(cls):
        normalize_basepart(cls, props)
    if cls in SCRIPT_CLASSES:
        props.setdefault("Source", "")

    node = Node(build, cls, name, props)
    node.attributes = data.get("Attributes")
    node.tags = data.get("Tags")
    nid = data.get("Id", data.get("ID"))
    if nid is not None:
        build.ids[str(nid)] = node.ref

    for key, dflt in (("Children", "Part"), ("Decals", "Decal"), ("Scripts", "Script")):
        for c in data.get(key) or []:
            if isinstance(c, dict) and not (c.get("ClassName") or c.get("Class")):
                c = dict(c, ClassName=dflt)
            child = make_node(c, build)
            if child:
                node.children.append(child)
    return node


# =========================================================
# NPC SHORTHAND (R6) + CHARACTER REPAIR (R6 / R15)
# =========================================================
R6_PARTS = [
    # name, size, offset from HumanoidRootPart, body colour key, can collide, transparency
    ("HumanoidRootPart", (2, 2, 1), (0, 0, 0), None, True, 1),
    ("Torso", (2, 2, 1), (0, 0, 0), "Torso", True, 0),
    ("Head", (2, 1, 1), (0, 1.5, 0), "Head", True, 0),
    ("Left Arm", (1, 2, 1), (-1.5, 0, 0), "LeftArm", False, 0),
    ("Right Arm", (1, 2, 1), (1.5, 0, 0), "RightArm", False, 0),
    ("Left Leg", (1, 2, 1), (-0.5, -2, 0), "LeftLeg", False, 0),
    ("Right Leg", (1, 2, 1), (0.5, -2, 0), "RightLeg", False, 0),
]
# name, Part0, Part1, C0, C1   (the Motor6D lives inside Part0 for R6)
R6_JOINTS = [
    ("RootJoint", "HumanoidRootPart", "Torso", [0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0], [0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0]),
    ("Neck", "Torso", "Head", [0, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0], [0, -0.5, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0]),
    ("Right Shoulder", "Torso", "Right Arm", [1, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0], [-0.5, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0]),
    ("Left Shoulder", "Torso", "Left Arm", [-1, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0], [0.5, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0]),
    ("Right Hip", "Torso", "Right Leg", [1, -1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0], [0.5, 1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0]),
    ("Left Hip", "Torso", "Left Leg", [-1, -1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0], [-0.5, 1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0]),
]
R6_ATTACHMENTS = {
    "HumanoidRootPart": {"RootRigAttachment": (0, 0, 0)},
    "Head": {"FaceCenterAttachment": (0, 0, 0), "FaceFrontAttachment": (0, 0, -0.6),
             "HairAttachment": (0, 0.6, 0), "HatAttachment": (0, 0.6, 0)},
    "Torso": {"BodyBackAttachment": (0, 0, 0.5), "BodyFrontAttachment": (0, 0, -0.5),
              "LeftCollarAttachment": (-1, 1, 0), "NeckAttachment": (0, 1, 0), "RightCollarAttachment": (1, 1, 0),
              "WaistBackAttachment": (0, -1, 0.5), "WaistCenterAttachment": (0, -1, 0),
              "WaistFrontAttachment": (0, -1, -0.5)},
    "Left Arm": {"LeftGripAttachment": (0, -1, 0), "LeftShoulderAttachment": (0, 1, 0)},
    "Right Arm": {"RightGripAttachment": (0, -1, 0), "RightShoulderAttachment": (0, 1, 0)},
    "Left Leg": {"LeftFootAttachment": (0, -1, 0)},
    "Right Leg": {"RightFootAttachment": (0, -1, 0)},
}
R6_ATTACH_LOOKUP = {a: (part, cf_pos(*xyz)) for part, d in R6_ATTACHMENTS.items() for a, xyz in d.items()}

# name, Part0, Part1, attachment name used in both parts   (the Motor6D lives inside Part1 for R15)
R15_JOINTS = [
    ("Root", "HumanoidRootPart", "LowerTorso", "RootRigAttachment"),
    ("Waist", "LowerTorso", "UpperTorso", "WaistRigAttachment"),
    ("Neck", "UpperTorso", "Head", "NeckRigAttachment"),
    ("LeftShoulder", "UpperTorso", "LeftUpperArm", "LeftShoulderRigAttachment"),
    ("LeftElbow", "LeftUpperArm", "LeftLowerArm", "LeftElbowRigAttachment"),
    ("LeftWrist", "LeftLowerArm", "LeftHand", "LeftWristRigAttachment"),
    ("RightShoulder", "UpperTorso", "RightUpperArm", "RightShoulderRigAttachment"),
    ("RightElbow", "RightUpperArm", "RightLowerArm", "RightElbowRigAttachment"),
    ("RightWrist", "RightLowerArm", "RightHand", "RightWristRigAttachment"),
    ("LeftHip", "LowerTorso", "LeftUpperLeg", "LeftHipRigAttachment"),
    ("LeftKnee", "LeftUpperLeg", "LeftLowerLeg", "LeftKneeRigAttachment"),
    ("LeftAnkle", "LeftLowerLeg", "LeftFoot", "LeftAnkleRigAttachment"),
    ("RightHip", "LowerTorso", "RightUpperLeg", "RightHipRigAttachment"),
    ("RightKnee", "RightUpperLeg", "RightLowerLeg", "RightKneeRigAttachment"),
    ("RightAnkle", "RightLowerLeg", "RightFoot", "RightAnkleRigAttachment"),
]


def build_accessory(acc, world, anchored, build):
    att_name = acc.get("AttachmentName", "HatAttachment")
    owner, owner_cf = R6_ATTACH_LOOKUP.get(att_name, (None, None))
    if owner is None:
        build.warn(f"Accessory '{acc.get('Name', '')}': unknown attachment '{att_name}', using HatAttachment")
        att_name = "HatAttachment"
        owner, owner_cf = R6_ATTACH_LOOKUP[att_name]
    handle_att = to_cframe(acc.get("HandleAttachmentCFrame", IDENT))
    handle_cf = cf_mul(cf_mul(world[owner], owner_cf), cf_inv(handle_att))
    use_meshpart = str(acc.get("HandleClass", "")).lower() == "meshpart"

    handle = {"ClassName": "MeshPart" if use_meshpart else "Part", "Name": "Handle",
              "Size": acc.get("Size", [1, 1, 1]), "CFrame": handle_cf, "CanCollide": False, "Massless": True,
              "Anchored": anchored, "Color": acc.get("Color", [163, 162, 165]),
              "Material": acc.get("Material", "Plastic"), "Children": []}
    if use_meshpart:
        handle["MeshId"] = acc.get("MeshId", "")
        handle["TextureID"] = acc.get("TextureId", "")
    elif acc.get("MeshId"):
        handle["Children"].append({"ClassName": "SpecialMesh", "Name": "Mesh", "MeshType": "FileMesh",
                                   "MeshId": acc["MeshId"], "TextureId": acc.get("TextureId", ""),
                                   "Scale": acc.get("Scale", [1, 1, 1]), "Offset": acc.get("MeshOffset", [0, 0, 0])})
    handle["Children"].append({"ClassName": "Attachment", "Name": att_name, "CFrame": handle_att})
    handle["Children"].append({"ClassName": "Weld", "Name": "AccessoryWeld", "Part0": "Handle", "Part1": owner,
                               "C0": handle_att, "C1": owner_cf})
    return {"ClassName": "Accessory", "Name": acc.get("Name", "Accessory"),
            "AccessoryType": acc.get("AccessoryType", "Hat"), "Children": [handle]}


def build_npc(data, build):
    name = data.get("Name", "NPC")
    if str(data.get("RigType", "R6")).upper() != "R6":
        build.warn(f"NPC '{name}': only R6 shorthand is built. For R15 send the exported Model (Parts + Attachments) and it will be rigged automatically.")

    if "CFrame" in data:
        root_cf = to_cframe(data["CFrame"])
    else:
        root_cf = to_cframe({"Position": data.get("Position", [0, 5, 0]), "Orientation": data.get("Orientation", [0, 0, 0])})
    anchored = truthy(data.get("Anchored", False))
    bc = data.get("BodyColors") or {}
    skin = bc.get("All", data.get("SkinColor", [245, 205, 47]))

    def colour(key):
        return bc.get(key, skin)

    world = {}
    parts = []
    for pname, size, off, ckey, collide, transp in R6_PARTS:
        world[pname] = cf_mul(root_cf, cf_pos(*off))
        kids = []
        for jn, p0, p1, c0, c1 in R6_JOINTS:
            if p0 == pname:
                kids.append({"ClassName": "Motor6D", "Name": jn, "Part0": p0, "Part1": p1, "C0": c0, "C1": c1})
        for an, xyz in R6_ATTACHMENTS.get(pname, {}).items():
            kids.append({"ClassName": "Attachment", "Name": an, "CFrame": cf_pos(*xyz)})
        if pname == "Head":
            kids.append({"ClassName": "SpecialMesh", "Name": "Mesh", "MeshType": "Head", "Scale": [1.25, 1.25, 1.25]})
            kids.append({"ClassName": "Decal", "Name": "face", "Face": "Front",
                         "Texture": data.get("Face", "rbxasset://textures/face.png")})
        parts.append({"ClassName": "Part", "Name": pname, "Size": list(size), "CFrame": world[pname],
                      "Color": colour(ckey) if ckey else skin, "Anchored": anchored, "CanCollide": collide,
                      "Transparency": transp, "Material": "Plastic",
                      "TopSurface": "Smooth", "BottomSurface": "Smooth", "LeftSurface": "Smooth",
                      "RightSurface": "Smooth", "FrontSurface": "Smooth", "BackSurface": "Smooth",
                      "Children": kids})

    hprops = {"RigType": "R6", "HipHeight": 0, "Health": 100, "MaxHealth": 100, "WalkSpeed": 16,
              "JumpPower": 50, "JumpHeight": 7.2, "DisplayName": data.get("DisplayName", name)}
    hprops.update(data.get("Humanoid") or {})
    for k in ("Health", "MaxHealth", "WalkSpeed", "JumpPower", "JumpHeight", "HipHeight", "DisplayDistanceType",
              "HealthDisplayType", "NameDisplayDistance", "HealthDisplayDistance"):
        if k in data:
            hprops[k] = data[k]
    if "MaxHealth" in data or "Health" in data:
        hprops["MaxHealth"] = data.get("MaxHealth", max(num(hprops["MaxHealth"]), num(hprops["Health"])))
    humanoid = {"ClassName": "Humanoid", "Name": "Humanoid"}
    humanoid.update(hprops)

    kids = [humanoid] + parts
    kids.append({"ClassName": "BodyColors", "Name": "Body Colors", "HeadColor3": colour("Head"),
                 "LeftArmColor3": colour("LeftArm"), "LeftLegColor3": colour("LeftLeg"),
                 "RightArmColor3": colour("RightArm"), "RightLegColor3": colour("RightLeg"),
                 "TorsoColor3": colour("Torso")})
    if data.get("Shirt"):
        kids.append({"ClassName": "Shirt", "Name": "Shirt", "ShirtTemplate": data["Shirt"]})
    if data.get("Pants"):
        kids.append({"ClassName": "Pants", "Name": "Pants", "PantsTemplate": data["Pants"]})
    if data.get("ShirtGraphic"):
        kids.append({"ClassName": "ShirtGraphic", "Name": "Shirt Graphic", "Graphic": data["ShirtGraphic"]})
    for acc in data.get("Accessories") or []:
        kids.append(build_accessory(acc, world, anchored, build))
    kids.extend(data.get("Children") or [])
    kids.extend(dict(s, ClassName=s.get("ClassName", "Script")) for s in (data.get("Scripts") or []))

    model = {"ClassName": "Model", "Name": name, "PrimaryPart": "HumanoidRootPart", "Children": kids}
    for k in ("Id", "ID", "Parent", "Attributes", "Tags"):
        if k in data:
            model[k] = data[k]
    return make_node(model, build)


def _walk(node):
    for c in node.children:
        yield c
        yield from _walk(c)


def is_r15(rig):
    s = str(rig).upper()
    return s.endswith("R15") or s == "1"


def repair_character(model, build):
    hum = next((c for c in model.children if c.cls == "Humanoid"), None)
    if hum is None:
        return
    desc = {}
    for d in _walk(model):
        desc.setdefault(d.name, d)

    if "RigType" not in hum.props:
        hum.props["RigType"] = "R15" if "UpperTorso" in desc else "R6"
    r15 = is_r15(hum.props["RigType"])

    if "PrimaryPart" not in model.props:
        for cand in ("HumanoidRootPart", "Torso", "UpperTorso", "Head"):
            if cand in desc and is_basepart(desc[cand].cls):
                model.props["PrimaryPart"] = desc[cand].ref
                break
    if "HumanoidRootPart" not in desc:
        build.warn(f"Character '{model.name}' has no HumanoidRootPart; it may not move or collide correctly")

    if "Health" in hum.props and "MaxHealth" not in hum.props:
        hum.props["MaxHealth"] = max(100.0, num(hum.props["Health"]))

    existing = {d.name for d in _walk(model) if d.cls == "Motor6D"}

    def part_cf(p):
        return to_cframe(p.props["CFrame"]) if "CFrame" in p.props else None

    made = 0
    if not r15:
        for jn, p0, p1, c0, c1 in R6_JOINTS:
            if jn in existing or p0 not in desc or p1 not in desc:
                continue
            a, b = part_cf(desc[p0]), part_cf(desc[p1])
            if a is not None and b is not None:
                c1 = cf_mul(cf_inv(b), cf_mul(a, c0))   # keeps the pose the parts are already in
            j = Node(build, "Motor6D", jn, {"Part0": desc[p0].ref, "Part1": desc[p1].ref, "C0": c0, "C1": c1})
            desc[p0].children.append(j)
            made += 1
    else:
        for jn, p0, p1, an in R15_JOINTS:
            if jn in existing or p0 not in desc or p1 not in desc:
                continue
            a0 = next((c for c in desc[p0].children if c.cls == "Attachment" and c.name == an), None)
            a1 = next((c for c in desc[p1].children if c.cls == "Attachment" and c.name == an), None)
            if not a0 or not a1:
                build.warn(f"Character '{model.name}': can't rebuild joint {jn} (missing {an})")
                continue
            j = Node(build, "Motor6D", jn, {"Part0": desc[p0].ref, "Part1": desc[p1].ref,
                                            "C0": a0.props.get("CFrame", IDENT), "C1": a1.props.get("CFrame", IDENT)})
            desc[p1].children.append(j)
            made += 1
    if made:
        build.warn(f"Character '{model.name}': rebuilt {made} missing Motor6D joint(s)")


def post_process(node, build):
    if node.cls == "Model" and any(c.cls == "Humanoid" for c in node.children):
        repair_character(node, build)
    for c in list(node.children):
        post_process(c, build)


# =========================================================
# PROPERTY -> XML
# =========================================================
def norm_content(v, cls, name):
    if v is None or str(v).strip() == "":
        return ""
    s = str(v).strip()
    if cls in THUMBNAIL_CLASSES and name == "Texture":
        return convert_to_thumbnail(s)
    if re.fullmatch(r"\d+", s):
        return "rbxassetid://" + s
    return s


def convert_to_thumbnail(tex):
    """Same behaviour as the old backend: asset ids become rbxthumb urls so Decal ids resolve to their image"""
    tex = str(tex or "").strip()
    if not tex:
        return ""
    if tex.startswith("rbxasset://textures/") or tex.startswith("rbxthumb://"):
        return tex
    m = re.search(r"(\d+)", tex)
    if not m:
        return tex
    return f"rbxthumb://type=Asset&id={m.group(1)}&w=420&h=420"


def find_by_name(root, name):
    for c in root.children:
        if c.name == name:
            return c
        r = find_by_name(c, name)
        if r:
            return r
    return None


def resolve_ref(value, anc, build):
    if value is None or value == "" or str(value) == "null":
        return "null"
    s = str(value)
    if s in build.ids:
        return build.ids[s]
    if s in build.refs:
        return s
    for a in reversed(anc):
        hit = find_by_name(a, s)
        if hit:
            return hit.ref
    build.warn(f"Reference '{s}' not found, left empty")
    return "null"


def x_cf(tag, name, cf):
    return f'<{tag} name="{name}">' + "".join(f"<{k}>{fnum(v)}</{k}>" for k, v in zip(CF_KEYS, cf)) + f"</{tag}>"


def x_numseq(v):
    if isinstance(v, (int, float)):
        v = [[0, v, 0], [1, v, 0]]
    out = ""
    for kp in v:
        t, val, e = (list(kp) + [0, 0, 0])[:3] if len(kp) < 3 else kp[:3]
        out += f"{fnum(t)} {fnum(val)} {fnum(e)} "
    return out


def x_colseq(v):
    if isinstance(v, (str, dict)) or (isinstance(v, (list, tuple)) and v and isinstance(v[0], (int, float))):
        c = to_rgb01(v)
        v = [[0] + c, [1] + c]
    out = ""
    for kp in v:
        out += f"{fnum(kp[0])} " + " ".join(fnum(x) for x in to_rgb01(kp[1:4])) + " 0 "
    return out


def encode_attributes(d, build):
    entries = []
    for k, v in d.items():
        kb = str(k).encode("utf-8")
        head = struct.pack("<I", len(kb)) + kb
        if isinstance(v, dict) and "type" in v and "value" in v:
            t = _norm(v["type"])
            val = v["value"]
            if t == "color3":
                entries.append(head + b"\x0f" + struct.pack("<3f", *to_rgb01(val)))
            elif t == "vector3":
                entries.append(head + b"\x11" + struct.pack("<3f", *seq(val, 3, "XYZ")))
            elif t == "vector2":
                entries.append(head + b"\x10" + struct.pack("<2f", *seq(val, 2, "XY")))
            else:
                build.warn(f"Attribute '{k}': type {v['type']} not supported, skipped")
        elif isinstance(v, bool):
            entries.append(head + b"\x03" + (b"\x01" if v else b"\x00"))
        elif isinstance(v, (int, float)):
            entries.append(head + b"\x06" + struct.pack("<d", float(v)))
        elif isinstance(v, str):
            vb = v.encode("utf-8")
            entries.append(head + b"\x02" + struct.pack("<I", len(vb)) + vb)
        else:
            build.warn(f"Attribute '{k}': unsupported value, skipped")
    return struct.pack("<I", len(entries)) + b"".join(entries)


def emit_prop(node, name, value, build, anc):
    cls = node.cls
    typ = None
    if isinstance(value, dict) and "type" in value and "value" in value:
        typ = canon_type(value["type"])
        value = value["value"]
    if typ is None:
        typ = resolve_type(cls, name, value)
    if typ is None:
        build.warn(f"{cls}.{name}: can't tell what type this is, skipped (send it as {{\"type\":..., \"value\":...}})")
        return ""
    if value is None:
        return ""

    xn = esc(name)
    if typ == "bool":
        return f'<bool name="{xn}">{"true" if truthy(value) else "false"}</bool>'
    if typ in ("float", "double"):
        return f'<{typ} name="{xn}">{fnum(value)}</{typ}>'
    if typ in ("int", "int64"):
        return f'<{typ} name="{xn}">{int(round(num(value)))}</{typ}>'
    if typ == "string":
        return f'<string name="{xn}">{esc(value)}</string>'
    if typ == "ProtectedString":
        return f'<ProtectedString name="{xn}">{cdata(value)}</ProtectedString>'
    if typ == "Content":
        c = norm_content(value, cls, name)
        inner = f"<url>{esc(c)}</url>" if c else "<null></null>"
        return f'<Content name="{xn}">{inner}</Content>'
    if typ == "token":
        return f'<token name="{xn}">{enum_value(name, value, build, cls)}</token>'
    if typ == "Vector3":
        a = seq(value, 3, "XYZ")
        return f'<Vector3 name="{xn}"><X>{fnum(a[0])}</X><Y>{fnum(a[1])}</Y><Z>{fnum(a[2])}</Z></Vector3>'
    if typ == "Vector2":
        a = seq(value, 2, "XY")
        return f'<Vector2 name="{xn}"><X>{fnum(a[0])}</X><Y>{fnum(a[1])}</Y></Vector2>'
    if typ == "CFrame":
        return x_cf("CoordinateFrame", xn, to_cframe(value))
    if typ == "OptionalCFrame":
        inner = x_cf("CFrame", "", to_cframe(value)).replace(' name=""', "")
        return f'<OptionalCoordinateFrame name="WorldPivotData">{inner}</OptionalCoordinateFrame>'
    if typ == "Color3":
        r, g, b = to_rgb01(value)
        return f'<Color3 name="{xn}"><R>{fnum(r)}</R><G>{fnum(g)}</G><B>{fnum(b)}</B></Color3>'
    if typ == "Color3uint8":
        tag = "Color3uint8" if (name == "Color" and is_basepart(cls)) else xn
        return f'<Color3uint8 name="{tag}">{pack_c3u8(to_rgb01(value))}</Color3uint8>'
    if typ == "BrickColor":
        return f'<int name="{xn}">{int(num(value, 194))}</int>'
    if typ == "UDim2":
        a = seq(value, 4, ["XS", "XO", "YS", "YO"])
        return (f'<UDim2 name="{xn}"><XS>{fnum(a[0])}</XS><XO>{int(a[1])}</XO>'
                f'<YS>{fnum(a[2])}</YS><YO>{int(a[3])}</YO></UDim2>')
    if typ == "UDim":
        a = seq(value, 2, ["S", "O"])
        return f'<UDim name="{xn}"><S>{fnum(a[0])}</S><O>{int(a[1])}</O></UDim>'
    if typ == "NumberRange":
        a = seq(value, 2, ["Min", "Max"]) if not isinstance(value, (int, float)) else [value, value]
        return f'<NumberRange name="{xn}">{fnum(a[0])} {fnum(a[1])} </NumberRange>'
    if typ == "NumberSequence":
        return f'<NumberSequence name="{xn}">{x_numseq(value)}</NumberSequence>'
    if typ == "ColorSequence":
        return f'<ColorSequence name="{xn}">{x_colseq(value)}</ColorSequence>'
    if typ == "Rect2D":
        a = seq(value, 4, ["MinX", "MinY", "MaxX", "MaxY"])
        return (f'<Rect2D name="{xn}"><min><X>{fnum(a[0])}</X><Y>{fnum(a[1])}</Y></min>'
                f'<max><X>{fnum(a[2])}</X><Y>{fnum(a[3])}</Y></max></Rect2D>')
    if typ == "Ref":
        return f'<Ref name="{xn}">{resolve_ref(value, anc + [node], build)}</Ref>'
    if typ == "PhysicalProperties":
        if isinstance(value, dict):
            d = {k: num(value.get(k), dv) for k, dv in (("Density", 0.7), ("Friction", 0.3), ("Elasticity", 0.5),
                                                        ("FrictionWeight", 1), ("ElasticityWeight", 1))}
            body = "<CustomPhysics>true</CustomPhysics>" + "".join(f"<{k}>{fnum(v)}</{k}>" for k, v in d.items())
            return f'<PhysicalProperties name="{xn}">{body}<AcousticAbsorption>1</AcousticAbsorption></PhysicalProperties>'
        return f'<PhysicalProperties name="{xn}"><CustomPhysics>false</CustomPhysics></PhysicalProperties>'
    if typ == "Font":
        if isinstance(value, str):
            value = {"family": value}
        fam = str(value.get("family", value.get("Family", "SourceSansPro")))
        if not fam.startswith("rbxasset") and not fam.startswith("rbxassetid"):
            fam = f"rbxasset://fonts/families/{fam}.json"
        return (f'<Font name="{xn}"><Family><url>{esc(fam)}</url></Family>'
                f'<Weight>{int(num(value.get("weight", value.get("Weight")), 400))}</Weight>'
                f'<Style>{esc(value.get("style", value.get("Style", "Normal")))}</Style></Font>')
    if typ == "BinaryString":
        return f'<BinaryString name="{xn}">{esc(value)}</BinaryString>'
    if typ in ("Faces", "Axes"):
        tag = typ.lower()
        return f'<{typ} name="{xn}"><{tag}>{int(num(value))}</{tag}></{typ}>'
    build.warn(f"{cls}.{name}: type {typ} not supported, skipped")
    return ""


def emit_node(node, build, anc):
    lines = [f'<Item class="{esc(node.cls)}" referent="{node.ref}">', "<Properties>",
             f'<string name="Name">{esc(node.name)}</string>']
    for k, v in node.props.items():
        try:
            x = emit_prop(node, k, v, build, anc)
        except Exception as e:  # one bad property should not kill the whole publish
            build.warn(f"{node.cls}.{k}: {e}")
            x = ""
        if x:
            lines.append(x)
    if node.cls in SCRIPT_CLASSES:
        lines.append(f'<string name="ScriptGuid">{{{str(uuid.uuid4()).upper()}}}</string>')
    if isinstance(node.attributes, dict) and node.attributes:
        raw = encode_attributes(node.attributes, build)
        lines.append(f'<BinaryString name="AttributesSerialize">{base64.b64encode(raw).decode()}</BinaryString>')
    if node.tags:
        tags = "\0".join(str(t) for t in node.tags)
        lines.append(f'<BinaryString name="Tags">{base64.b64encode(tags.encode()).decode()}</BinaryString>')
    lines.append("</Properties>")
    for c in node.children:
        lines.append(emit_node(c, build, anc + [node]))
    lines.append("</Item>")
    return "\n".join(lines)


# =========================================================
# SERVICE ROUTING + TEMPLATE SURGERY
# =========================================================
DEFAULT_PARENT = {
    "Script": "ServerScriptService", "LocalScript": "StarterPlayer/StarterPlayerScripts",
    "ModuleScript": "ReplicatedStorage", "ScreenGui": "StarterGui", "Tool": "StarterPack", "Team": "Teams",
    "Sky": "Lighting", "Atmosphere": "Lighting", "BloomEffect": "Lighting", "BlurEffect": "Lighting",
    "ColorCorrectionEffect": "Lighting", "DepthOfFieldEffect": "Lighting", "SunRaysEffect": "Lighting",
}
PATH_ALIASES = {"StarterPlayerScripts": ("StarterPlayer", "StarterPlayerScripts"),
                "StarterCharacterScripts": ("StarterPlayer", "StarterCharacterScripts")}


def resolve_path(parent, cls):
    if not parent:
        parent = DEFAULT_PARENT.get(cls, "Workspace")
    parts = [p for p in re.split(r"[/.>\\]", str(parent)) if p]
    if parts and parts[0].lower() == "game":
        parts = parts[1:]
    if not parts:
        parts = ["Workspace"]
    if len(parts) == 1 and parts[0] in PATH_ALIASES:
        return PATH_ALIASES[parts[0]]
    return tuple(parts)


TOKEN_RE = re.compile(r"<!\[CDATA\[.*?\]\]>|<Item\b[^>]*>|</Item>", re.S)


def index_items(text):
    """Finds every <Item> and where it starts/ends, skipping CDATA so script sources can't confuse it"""
    root = {"cls": None, "children": []}
    stack = [root]
    for m in TOKEN_RE.finditer(text):
        tok = m.group(0)
        if tok.startswith("<![CDATA["):
            continue
        if tok == "</Item>":
            if len(stack) > 1:
                it = stack.pop()
                it["close_start"], it["end"] = m.start(), m.end()
            continue
        cm = re.search(r'class="([^"]*)"', tok)
        it = {"cls": cm.group(1) if cm else "", "start": m.start(), "children": [], "selfclose": tok.endswith("/>")}
        stack[-1]["children"].append(it)
        if it["selfclose"]:
            it["close_start"], it["end"] = m.end(), m.end()
        else:
            stack.append(it)
    return root


def wrap_item(cls, inner):
    return (f'<Item class="{esc(cls)}" referent="{new_ref()}">\n<Properties>\n'
            f'<string name="Name">{esc(cls)}</string>\n</Properties>\n{inner}\n</Item>')


def apply_template(template, groups, build):
    root = index_items(template)
    ops = []  # (start, end, replacement)

    ws = next((c for c in root["children"] if c["cls"] == "Workspace"), None)
    if ws and not ws["selfclose"]:
        for ch in ws["children"]:
            if ch["cls"] not in WORKSPACE_KEEP:
                ops.append((ch["start"], ch["end"], ""))

    tail = template.rfind("<SharedStrings>")
    if tail == -1:
        tail = template.rfind("</roblox>")

    for path, chunks in groups.items():
        xml = "\n".join(chunks)
        cur, k = root, 0
        while k < len(path):
            nxt = next((c for c in cur["children"] if c["cls"] == path[k]), None)
            if nxt is None:
                break
            cur, k = nxt, k + 1
        if k == len(path):
            if cur.get("selfclose"):
                build.warn(f"{'/'.join(path)} is a self-closing item in the template; its content was skipped")
                continue
            ops.append((cur["close_start"], cur["close_start"], xml))
        else:
            for seg in reversed(path[k:]):
                xml = wrap_item(seg, xml)
            pos = tail if cur is root else cur["close_start"]
            ops.append((pos, pos, xml))

    out = template
    for s, e, t in sorted(ops, key=lambda o: (o[0], o[1]), reverse=True):
        out = out[:s] + t + out[e:]
    return out


def normalize_input(instances):
    if isinstance(instances, dict):   # {"Workspace":[...], "ServerScriptService":[...]}
        flat = []
        for svc, items in instances.items():
            for it in items or []:
                if isinstance(it, dict):
                    flat.append(dict(it, Parent=it.get("Parent", svc)))
        return flat
    return instances if isinstance(instances, list) else []


def build_rbxlx(instances, build):
    template = get_template()
    groups = {}
    tops = []
    for item in normalize_input(instances):
        node = make_node(item, build)
        if node is None:
            continue
        node.path = resolve_path(item.get("Parent") if isinstance(item, dict) else None, node.cls)
        tops.append(node)
    for node in tops:
        post_process(node, build)
    for node in tops:
        groups.setdefault(node.path, []).append(emit_node(node, build, []))
    return apply_template(template, groups, build)


# =========================================================
# ROUTES
# =========================================================
def _run_build(body):
    build = Build({"unionFallback": body.get("unionFallback", "part")})
    xml_data = build_rbxlx(body.get("instances", []), build)
    ET.fromstring(xml_data.encode("utf-8"))  # fail here (not at Roblox) if the XML is malformed
    return xml_data, build


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/build", methods=["POST"])
def build_only():
    try:
        body = request.get_json(force=True, silent=True) or {}
        xml_data, build = _run_build(body)
        resp = Response(xml_data, mimetype="application/xml")
        resp.headers["Content-Disposition"] = "attachment; filename=place.rbxlx"
        resp.headers["X-Warnings"] = str(len(build.warnings))
        return resp
    except Exception as e:
        log.exception("build failed")
        return jsonify({"error": str(e)}), 500


@app.route("/publish", methods=["POST"])
def publish():
    try:
        body = request.get_json(force=True, silent=True) or {}
        api_key = body.get("apiKey") or os.environ.get("ROBLOX_API_KEY")
        universe_id = body.get("universeId")
        place_id = body.get("placeId")
        if not (api_key and universe_id and place_id):
            return jsonify({"error": "apiKey, universeId and placeId are required"}), 400

        xml_data, build = _run_build(body)
        stats = {"classes": build.counts, "bytes": len(xml_data.encode("utf-8"))}

        if body.get("dryRun"):
            return jsonify({"status": 0, "dryRun": True, "stats": stats, "warnings": build.warnings})

        res = requests.post(
            f"https://apis.roblox.com/universes/v1/{universe_id}/places/{place_id}/versions",
            headers={"x-api-key": api_key, "Content-Type": "application/xml"},
            params={"versionType": body.get("versionType", "Published")},
            data=xml_data.encode("utf-8"),
            timeout=180,
        )
        return jsonify({"ok": res.ok, "status": res.status_code, "response": res.text,
                        "stats": stats, "warnings": build.warnings})
    except Exception as e:
        log.exception("publish failed")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
