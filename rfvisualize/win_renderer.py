import win32gui, win32ui, win32api, win32con

dc = win32gui.GetDC(0)
dc_obj = win32ui.CreateDCFromHandle(dc)
hwnd = win32gui.WindowFromPoint((0, 0))
monitor = (0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
red = win32api.RGB(255, 0, 0)

class win_renderer:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def setXY(self, x, y):
        self.x = x
        self.y = y

    def render(self, width, height):
        try:
            m = self.x, self.y
            brush = win32ui.CreateBrush()
            brush.CreateSolidBrush(red)
            dc_obj.FrameRect((m[0], m[1], m[0]+width, m[1]+height), brush)
            dc_obj.FrameRect((m[0]-1, m[1]-1, m[0]+width+1, m[1]+height+1), brush)

        except:
            print("render error.")

    def stop_render(self):
        win32gui.InvalidateRect(None, monitor, True)
        win32gui.UpdateWindow(hwnd)
        win32gui.ValidateRect(hwnd, monitor)
        
if __name__ == "__main__":
    r = win_renderer(900, 500)
    r.render(100, 30)
    r.stop_render()