from flask import Flask, request, jsonify
import requests
import uuid
import os
import re
from xml.sax.saxutils import escape as xml_escape

app = Flask(__name__)

# =========================
# LOAD YOUR REAL TEMPLATE
# =========================
# Put the real template file next to this main.py as:
# template.rbxlx
def load_template() -> str:
    with open("template.rbxlx", "r", encoding="utf-8") as f:
        return f.read()

# =========================
# HELPERS
# =========================
def esc(v):
    return xml_escape(str(v))

def new_ref():
    return "RBX" + uuid.uuid4().hex.upper()

def num_list(v, n, default):
    if not isinstance(v, list):
        return default
    return [(v[i] if i < len(v) else default[i]) for i in range(n)]

def get_workspace_referent(template_text: str) -> str:
    m = re.search(r'<Item class="Workspace" referent="([^"]+)">', template_text)
    if not m:
        raise ValueError("Workspace referent not found in template")
    return m.group(1)

def find_matching_item_close(template_text: str, open_index: int) -> int:
    """
    Finds the matching </Item> for the <Item ...> starting at open_index.
    Works with nested <Item> elements inside Workspace.
    """
    depth = 0
    i = open_index

    while True:
        next_open = template_text.find("<Item ", i)
        next_close = template_text.find("</Item>", i)

        if next_close == -1:
            raise ValueError("Could not find matching </Item>")

        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 5
        else:
            depth -= 1
            i = next_close + len("</Item>")
            if depth == 0:
                return next_close

# =========================
# ENUM TOKENS
# =========================
def token_material(v):
    s = str(v).lower()

    if "plastic" in s:
        return "256"
    if "smoothplastic" in s:
        return "272"
    if "neon" in s:
        return "288"
    if "wood" in s:
        return "512"
    if "slate" in s:
        return "800"
    if "concrete" in s:
        return "816"
    if "corrodedmetal" in s:
        return "1040"
    if "diamondplate" in s:
        return "1056"
    if "foil" in s:
        return "1072"
    if "grass" in s:
        return "1280"
    if "ice" in s:
        return "1536"

    return "256"

def token_surface(v):
    s = str(v).lower()

    if "smooth" in s:
        return "0"
    if "studs" in s:
        return "1"
    if "inlet" in s:
        return "2"
    if "universal" in s:
        return "3"
    if "glue" in s:
        return "4"
    if "weld" in s:
        return "5"

    return "0"

# =========================
# BUILD INSTANCE
# =========================
def build_instance(data, parent_ref):
    ref = new_ref()

    size = num_list(data.get("Size", [4, 4, 4]), 3, [4, 4, 4])
    color = num_list(data.get("Color", [163, 162, 165]), 3, [163, 162, 165])
    cf = num_list(
        data.get("CFrame", [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]),
        12,
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
    )

    cls = data.get("ClassName", "Part")
    name = data.get("Name", "Part")

    xml = []
    xml.append(f'<Item class="{cls}" referent="{ref}">')
    xml.append("<Properties>")
    xml.append(f'<string name="Name">{esc(name)}</string>')
    xml.append(f'<Vector3 name="Size"><X>{size[0]}</X><Y>{size[1]}</Y><Z>{size[2]}</Z></Vector3>')
    xml.append("<CoordinateFrame name=\"CFrame\">")
    xml.append(f"<X>{cf[0]}</X><Y>{cf[1]}</Y><Z>{cf[2]}</Z>")
    xml.append(f"<R00>{cf[3]}</R00><R01>{cf[4]}</R01><R02>{cf[5]}</R02>")
    xml.append(f"<R10>{cf[6]}</R10><R11>{cf[7]}</R11><R12>{cf[8]}</R12>")
    xml.append(f"<R20>{cf[9]}</R20><R21>{cf[10]}</R21><R22>{cf[11]}</R22>")
    xml.append("</CoordinateFrame>")

    # Match your real template: Color3 + BrickColor
    xml.append(f'<Color3 name="Color3"><R>{color[0]/255}</R><G>{color[1]/255}</G><B>{color[2]/255}</B></Color3>')
    xml.append('<int name="BrickColor">194</int>')

    xml.append(f'<bool name="Anchored">{"true" if data.get("Anchored", True) else "false"}</bool>')
    xml.append(f'<bool name="CanCollide">{"true" if data.get("CanCollide", True) else "false"}</bool>')
    xml.append(f'<bool name="CanTouch">{"true" if data.get("CanTouch", True) else "false"}</bool>')
    xml.append(f'<bool name="CanQuery">{"true" if data.get("CanQuery", True) else "false"}</bool>')
    xml.append(f'<float name="Transparency">{data.get("Transparency", 0)}</float>')
    xml.append(f'<float name="Reflectance">{data.get("Reflectance", 0)}</float>')
    xml.append(f'<bool name="CastShadow">{"true" if data.get("CastShadow", True) else "false"}</bool>')
    xml.append('<bool name="Locked">false</bool>')

    xml.append(f'<token name="TopSurface">{token_surface(data.get("TopSurface"))}</token>')
    xml.append(f'<token name="BottomSurface">{token_surface(data.get("BottomSurface"))}</token>')
    xml.append('<token name="FrontSurface">0</token>')
    xml.append('<token name="BackSurface">0</token>')
    xml.append('<token name="LeftSurface">0</token>')
    xml.append('<token name="RightSurface">0</token>')

    xml.append(f'<token name="Material">{token_material(data.get("Material"))}</token>')
    xml.append('<bool name="Archivable">true</bool>')
    xml.append(f'<Ref name="Parent">{parent_ref}</Ref>')

    if cls == "SpawnLocation":
        xml.append('<float name="Duration">5</float>')
        xml.append('<bool name="Neutral">true</bool>')

    xml.append("</Properties>")
    xml.append("</Item>")
    return "\n".join(xml)

# =========================
# BUILD RBXLX
# =========================
def build_rbxlx(instances):
    template = load_template()
    workspace_ref = get_workspace_referent(template)

    workspace_open = f'<Item class="Workspace" referent="{workspace_ref}">'
    ws_start = template.find(workspace_open)
    if ws_start == -1:
        raise ValueError("Workspace block not found in template")

    props_end = template.find("</Properties>", ws_start)
    if props_end == -1:
        raise ValueError("Workspace </Properties> not found")

    ws_close = find_matching_item_close(template, ws_start)
    if ws_close == -1:
        raise ValueError("Workspace closing </Item> not found")

    content = ""
    for inst in instances:
        content += build_instance(inst, workspace_ref) + "\n"

    # Replace only Workspace children, preserve the rest of the real template
    return template[:props_end + len("</Properties>")] + "\n" + content + template[ws_close:]

# =========================
# ROUTE
# =========================
@app.route("/publish", methods=["POST"])
def publish():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        api_key = data.get("apiKey")
        universe_id = data.get("universeId")
        place_id = data.get("placeId")
        instances = data.get("instances", [])

        if not api_key or not universe_id or not place_id:
            return jsonify({"error": "Missing required fields"}), 400

        xml_data = build_rbxlx(instances)

        url = f"https://apis.roblox.com/universes/v1/{universe_id}/places/{place_id}/versions"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/xml"
        }

        res = requests.post(
            url,
            headers=headers,
            params={"versionType": "Published"},
            data=xml_data,
            timeout=60
        )

        return jsonify({
            "status": res.status_code,
            "response": res.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
