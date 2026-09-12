# lcars_fullscreen.py
import sys, time
import glfw
from OpenGL import GL
import imgui
from imgui.integrations.glfw import GlfwRenderer
from typing import Dict, Any

# ---------- Theme colors ----------
LCARS_BG = (0.02, 0.02, 0.06)
LCARS_PANEL = (0.07, 0.07, 0.16)
LCARS_ACCENT = (0.0, 0.6, 0.9)
LCARS_ACCENT2 = (1.0, 0.55, 0.0)
LCARS_TEXT = (0.92, 0.92, 0.95)

def setup_imgui_style():
    style = imgui.get_style()
    style.window_rounding = 6.0
    style.frame_rounding = 4.0
    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (*LCARS_BG, 1.0)
    style.colors[imgui.COLOR_FRAME_BACKGROUND] = (*LCARS_PANEL, 1.0)
    style.colors[imgui.COLOR_BUTTON] = (*LCARS_ACCENT2, 0.95)
    style.colors[imgui.COLOR_BUTTON_HOVERED] = (*LCARS_ACCENT, 1.0)
    style.colors[imgui.COLOR_TEXT] = (*LCARS_TEXT, 1.0)
    style.colors[imgui.COLOR_HEADER] = (*LCARS_ACCENT, 0.9)
    style.colors[imgui.COLOR_BORDER] = (0.05, 0.05, 0.08, 1.0)

# ---------- Minimal model (replace with your MatrixSubsystem) ----------
class MatrixModel:
    def __init__(self):
        self.nodes = {
            "n1": {"id":"n1","label":"NODE 01","status":"active"},
            "n2": {"id":"n2","label":"NODE 02","status":"active"},
            "n3": {"id":"n3","label":"NODE 03","status":"inactive"},
            "n4": {"id":"n4","label":"NODE 04","status":"active"},
            "n5": {"id":"n5","label":"NODE 05","status":"inactive"},
        }
        self.routes = {"route.a": ["n1","n2","n3","n4","n5"]}
        self.selected_node = None
    def toggle_node(self, nid):
        n = self.nodes.get(nid)
        if n:
            n["status"] = "active" if n["status"] != "active" else "inactive"

model = MatrixModel()

# ---------- UI panels ----------
def draw_topbar(width, height):
    imgui.set_next_window_position(0, 0)
    imgui.set_next_window_size(width, 48)
    flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE
    imgui.begin("TopBar", flags=flags)
    imgui.push_style_color(imgui.COLOR_TEXT, *LCARS_TEXT, 1.0)
    imgui.text("LCARS — Fullscreen Prototype")
    imgui.same_line()
    imgui.set_cursor_pos_x(width - 220)
    imgui.text(f"CORE INTEGRITY: OPTIMAL")
    imgui.same_line()
    imgui.text_colored(time.strftime("%H:%M:%S"), *LCARS_TEXT)
    imgui.pop_style_color()
    imgui.end()

def draw_nav_panel(height):
    imgui.set_next_window_position(0, 48)
    imgui.set_next_window_size(220, height - 48)
    flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE
    imgui.begin("Navigation", flags=flags)
    imgui.push_style_color(imgui.COLOR_TEXT, *LCARS_TEXT, 1.0)
    imgui.text("NAVIGATION")
    imgui.separator()
    if imgui.button("BRIDGE", width=200, height=36): pass
    if imgui.button("ACCESS", width=200, height=36): pass
    if imgui.button("WEATHER", width=200, height=36): pass
    if imgui.button("ENGINEERING", width=200, height=36): pass
    if imgui.button("DESIGNER", width=200, height=36): pass
    imgui.separator()
    imgui.text_colored("TITANIUM MASTER SYSTEM ONLINE...", *LCARS_TEXT)
    imgui.pop_style_color()
    imgui.end()

def draw_inspector_panel(width, height):
    imgui.set_next_window_position(width - 320, 48)
    imgui.set_next_window_size(320, height - 48)
    flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE
    imgui.begin("Inspector", flags=flags)
    imgui.push_style_color(imgui.COLOR_TEXT, *LCARS_TEXT, 1.0)
    imgui.text("INSPECTOR")
    imgui.separator()
    if model.selected_node:
        node = model.nodes[model.selected_node]
        imgui.text(f"ID: {node['id']}")
        imgui.text(f"Label: {node['label']}")
        imgui.text(f"Status: {node['status']}")
        if imgui.button("Toggle status", width=120):
            model.toggle_node(node['id'])
    else:
        imgui.text("No node selected")
    imgui.pop_style_color()
    imgui.end()

def draw_matrix_panel(width, height):
    left = 220
    right = 320
    imgui.set_next_window_position(left, 48)
    imgui.set_next_window_size(width - left - right, height - 48)
    flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE
    imgui.begin("Matrix", flags=flags)
    imgui.push_style_color(imgui.COLOR_TEXT, *LCARS_TEXT, 1.0)
    imgui.text("MATRIX")
    imgui.separator()
    # grid layout
    cols = 3
    i = 0
    for nid, node in model.nodes.items():
        if i % cols != 0:
            imgui.same_line()
        label = f"{node['label']}"
        color = (0.0, 0.8, 0.2) if node["status"] == "active" else (0.7, 0.2, 0.2)
        if imgui.button(label, width=160, height=48):
            model.selected_node = nid
        imgui.same_line()
        imgui.text_colored("●", *color)
        i += 1
    imgui.pop_style_color()
    imgui.end()

# ---------- Main fullscreen loop ----------
def main():
    if not glfw.init():
        print("GLFW init failed")
        return

    # Create fullscreen window on primary monitor
    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    width, height = mode.size.width, mode.size.height
    glfw.window_hint(glfw.DECORATED, glfw.TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    window = glfw.create_window(width, height, "LCARS Fullscreen", monitor, None)
    if not window:
        glfw.terminate()
        print("Window creation failed")
        return

    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window, attach_callbacks=False)
    setup_imgui_style()

    # Optional: hide cursor for immersive UI
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    # handle ESC to close
    def key_callback(win, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, True)
    glfw.set_key_callback(window, key_callback)

    # main loop
    last_time = time.time()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        # draw panels
        draw_topbar(width, height)
        draw_nav_panel(height)
        draw_inspector_panel(width, height)
        draw_matrix_panel(width, height)

        # render
        GL.glViewport(0, 0, width, height)
        GL.glClearColor(*LCARS_BG, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

        # simple frame cap
        time.sleep(max(0.0, 1/60.0 - (time.time() - last_time)))
        last_time = time.time()

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
