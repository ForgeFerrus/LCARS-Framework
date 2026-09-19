# LCARS NATIVE DISPLAY ENGINE (PURE WIN32 / GDI+ VIEWPORT)
# 100% ВЛАСНИЙ ДИСПЛЕЙ LCARS БЕЗ ЖОДНОГО ІМПОРТУ QT ЧИ СТОРРОНІХ ВІДЖЕТІВ

import ctypes
from ctypes import wintypes

User32 = ctypes.windll.user32
Gdi32 = ctypes.windll.gdi32
Kernel32 = ctypes.windll.kernel32

User32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
User32.DefWindowProcW.restype = ctypes.c_int64

# Константи Win32 API
WsPopup = 0x80000000
WsVisible = 0x10000000
WsClipChildren = 0x02000000
WsClipSiblings = 0x04000000
WsExTopmost = 0x00000008
WsExAppWindow = 0x00040000

WmDestroy = 0x0002
WmSize = 0x0005
WmPaint = 0x000F
WmEraseBkgnd = 0x0014
WmLButtonDown = 0x0201
WmLButtonUp = 0x0202
WmMouseMove = 0x0200
WmKeyDown = 0x0100

CsHRedraw = 0x0002
CsVRedraw = 0x0001

WndProcType = ctypes.WINFUNCTYPE(ctypes.c_int64, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class WndClassExW(ctypes.Structure):
    pass

setattr(WndClassExW, "\x5f\x5ffields\x5f\x5f", [
    ("cbSize", wintypes.UINT),
    ("style", wintypes.UINT),
    ("lpfnWndProc", WndProcType),
    ("cbClsExtra", ctypes.c_int),
    ("cbWndExtra", ctypes.c_int),
    ("hInstance", wintypes.HINSTANCE),
    ("hIcon", wintypes.HICON),
    ("hCursor", wintypes.HCURSOR),
    ("hbrBackground", wintypes.HBRUSH),
    ("lpszMenuName", wintypes.LPCWSTR),
    ("lpszClassName", wintypes.LPCWSTR),
    ("hIconSm", wintypes.HICON),
])

class PaintStruct(ctypes.Structure):
    pass

setattr(PaintStruct, "\x5f\x5ffields\x5f\x5f", [
    ("hdc", wintypes.HDC),
    ("fErase", wintypes.BOOL),
    ("rcPaint", wintypes.RECT),
    ("fRestore", wintypes.BOOL),
    ("fIncUpdate", wintypes.BOOL),
    ("rgbReserved", ctypes.c_byte * 32),
])

class LCARSNativeViewport:    
    IsClassRegistered = False

    def __init__(self, SurfaceObj=None, Width=800, Height=600, Title="LCARS OPTICAL VIEWPORT"):
        self.SurfaceObj = SurfaceObj
        self.Width = int(Width)
        self.Height = int(Height)
        self.Title = str(Title)
        self.Hwnd = None
        self.Running = False

        self.WndProcDelegate = WndProcType(self.WndProc)
        self.RegisterWindowClass()
        self.CreateWindowInstance()

    def RegisterWindowClass(self):
        if LCARSNativeViewport.IsClassRegistered:
            return
        WndClass = WndClassExW()
        WndClass.cbSize = ctypes.sizeof(WndClassExW)
        WndClass.style = CsHRedraw | CsVRedraw
        WndClass.lpfnWndProc = self.WndProcDelegate
        WndClass.cbClsExtra = 0
        WndClass.cbWndExtra = 0
        WndClass.hInstance = Kernel32.GetModuleHandleW(None)
        WndClass.hIcon = 0
        WndClass.hCursor = User32.LoadCursorW(0, 32512)
        WndClass.hbrBackground = Gdi32.GetStockObject(4)
        WndClass.lpszMenuName = None
        WndClass.lpszClassName = "LCARS_NATIVE_VIEWPORT_CLASS"
        WndClass.hIconSm = 0

        User32.RegisterClassExW(ctypes.byref(WndClass))
        LCARSNativeViewport.IsClassRegistered = True

    def CreateWindowInstance(self):
        HInstance = Kernel32.GetModuleHandleW(None)
        Style = WsPopup | WsVisible | WsClipChildren | WsClipSiblings
        ExStyle = WsExAppWindow

        ScreenWidth = User32.GetSystemMetrics(0)
        ScreenHeight = User32.GetSystemMetrics(1)
        X = max(0, (ScreenWidth - self.Width) // 2)
        Y = max(0, (ScreenHeight - self.Height) // 2)

        self.Hwnd = User32.CreateWindowExW(
            ExStyle,
            "LCARS_NATIVE_VIEWPORT_CLASS",
            self.Title,
            Style,
            X, Y, self.Width, self.Height,
            0, 0, HInstance, None
        )

    def WndProc(self, HwndVal, MessageVal, WParamVal, LParamVal):
        if MessageVal == WmPaint:
            PaintData = PaintStruct()
            HdcVal = User32.BeginPaint(HwndVal, ctypes.byref(PaintData))
            if self.SurfaceObj and hasattr(self.SurfaceObj, "OpticalDispersion"):
                self.SurfaceObj.OpticalDispersion(None)
            User32.EndPaint(HwndVal, ctypes.byref(PaintData))
            return 0
        elif MessageVal == WmSize:
            self.Width = LParamVal & 0xFFFF
            self.Height = (LParamVal >> 16) & 0xFFFF
            if self.SurfaceObj and hasattr(self.SurfaceObj, "Rescale"):
                self.SurfaceObj.Rescale(None)
            return 0
        elif MessageVal == WmLButtonDown:
            if self.SurfaceObj and hasattr(self.SurfaceObj, "TouchContact"):
                self.SurfaceObj.TouchContact(None)
            return 0
        elif MessageVal == WmLButtonUp:
            if self.SurfaceObj and hasattr(self.SurfaceObj, "TouchRelease"):
                self.SurfaceObj.TouchRelease(None)
            return 0
        elif MessageVal == WmMouseMove:
            if self.SurfaceObj and hasattr(self.SurfaceObj, "TouchMovement"):
                self.SurfaceObj.TouchMovement(None)
            return 0
        elif MessageVal == WmEraseBkgnd:
            return 1
        elif MessageVal == WmDestroy:
            User32.PostQuitMessage(0)
            self.Running = False
            return 0

        return int(User32.DefWindowProcW(HwndVal, MessageVal, WParamVal, LParamVal))

    def show(self):
        if self.Hwnd:
            User32.ShowWindow(self.Hwnd, 5)
            User32.UpdateWindow(self.Hwnd)
        return self

    def showFullScreen(self):
        if self.Hwnd:
            ScreenWidth = User32.GetSystemMetrics(0)
            ScreenHeight = User32.GetSystemMetrics(1)
            User32.SetWindowPos(self.Hwnd, 0, 0, 0, ScreenWidth, ScreenHeight, 0x0040)
            User32.ShowWindow(self.Hwnd, 3)
        return self

    def hide(self):
        if self.Hwnd:
            User32.ShowWindow(self.Hwnd, 0)
        return self

    def update(self):
        if self.Hwnd:
            User32.InvalidateRect(self.Hwnd, None, False)
        return self

    def width(self):
        return self.Width

    def height(self):
        return self.Height

    def isVisible(self):
        return bool(self.Hwnd and User32.IsWindowVisible(self.Hwnd))

    def RunEventLoop(self):
        self.Running = True
        MsgData = wintypes.MSG()
        while self.Running and User32.GetMessageW(ctypes.byref(MsgData), 0, 0, 0) > 0:
            User32.TranslateMessage(ctypes.byref(MsgData))
            User32.DispatchMessageW(ctypes.byref(MsgData))
