# lcars_opengl.py
import sys
import time
import glfw
from OpenGL import GL
import imgui
from imgui.integrations.glfw import GlfwRenderer

# ---------- Simple LCARS theme helpers ----------
LCARS_BG = (0.02, 0.02, 0.06)
LCARS_PANEL = (0.08, 0.08, 0.18)
LCARS_ACCENT = (0.0, 0.6, 0.9)
LCARS_TEXT = (0.9, 0.9, 0.95)

def setup_imgui_style():
    style = imgui.get_style()
    style.window_rounding = 6.0
    style.frame_rounding = 4.0
    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (*LCARS_BG, 1.0)
    style.colors[imgui.COLOR_FRAME_BACKGROUND] = (*LCARS_PANEL, 1.0)
    style.colors[imgui.COLOR_BUTTON] = (*LCARS_ACCENT, 0.9)
    style.colors[imgui.COLOR_TEXT] = (*LCARS_TEXT, 1.0)

# ---------- Application state ----------
class MatrixModel:
    def __init__(self):
        self.nodes = {"n1": {"id":"n1","label":"Node 1","status":"active"},
                      "n2": {"id":"n2","label":"Node 2","status":"inactive"}}
        self.routes = {"route.a": ["n1","n2"]}
        self.selected_node = None

    def toggle_node(self, nid):
        n = self.nodes.get(nid)
        if n:
            n["status"] = "active" if n["status"] != "active" else "inactive"

model = MatrixModel()

# ---------- UI panels ----------
def draw_topbar():
    imgui.begin("TopBar", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE |
                imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR)
    imgui.text_colored("LCARS Prototype", *LCARS_TEXT)
    imgui.same_line()
    imgui.text("  |  ")
    imgui.same_line()
    imgui.text("Status: OK")
    imgui.end()

def draw_nav_panel():
    imgui.begin("Navigation", flags=imgui.WINDOW_NO_TITLE_BAR)
    imgui.text_colored("Navigation", *LCARS_TEXT)
    if imgui.button("Dashboard"):
        pass
    if imgui.button("Matrix"):
        pass
    if imgui.button("Nodes"):
        pass
    imgui.separator()
    imgui.text("Quick actions")
    if imgui.button("Reload spec"):
        # placeholder: load spec from file/registry
        pass
    imgui.end()

def draw_matrix_panel():
    imgui.begin("Matrix", flags=imgui.WINDOW_NO_TITLE_BAR)
    imgui.text_colored("Matrix", *LCARS_TEXT)
    # simple grid of nodes
    cols = 4
    i = 0
    for nid, node in model.nodes.items():
        if i % cols != 0:
            imgui.same_line()
        color = (0.0, 0.8, 0.2) if node["status"] == "active" else (0.6, 0.2, 0.2)
        if imgui.button(node["label"], width=120, height=40):
            model.selected_node = nid
        # draw small colored indicator
        imgui.same_line()
        imgui.text_colored("●", *color)
        i += 1
    imgui.end()

def draw_inspector_panel():
    imgui.begin("Inspector", flags=imgui.WINDOW_NO_TITLE_BAR)
    imgui.text_colored("Inspector", *LCARS_TEXT)
    if model.selected_node:
        node = model.nodes[model.selected_node]
        imgui.text(f"ID: {node['id']}")
        imgui.text(f"Label: {node['label']}")
        imgui.text(f"Status: {node['status']}")
        if imgui.button("Toggle status"):
            model.toggle_node(node['id'])
    else:
        imgui.text("No node selected")
    imgui.end()

# ---------- Main loop ----------
def main():
    if not glfw.init():
        print("Could not initialize GLFW")
        return

    width, height = 1200, 720
    window = glfw.create_window(width, height, "LCARS OpenGL Prototype", None, None)
    if not window:
        glfw.terminate()
        print("Failed to create window")
        return

    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window)
    setup_imgui_style()

    # layout hints: we'll use ImGui windows docked manually by positions
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        # top bar (fixed height)
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(width, 40)
        draw_topbar()

        # left nav
        imgui.set_next_window_position(0, 40)
        imgui.set_next_window_size(220, height - 40)
        draw_nav_panel()

        # inspector (right)
        imgui.set_next_window_position(width - 300, 40)
        imgui.set_next_window_size(300, height - 40)
        draw_inspector_panel()

        # matrix center
        imgui.set_next_window_position(220, 40)
        imgui.set_next_window_size(width - 220 - 300, height - 40)
        draw_matrix_panel()

        imgui.render()
        GL.glViewport(0, 0, width, height)
        GL.glClearColor(*LCARS_BG, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        time.sleep(1/60.0)

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
