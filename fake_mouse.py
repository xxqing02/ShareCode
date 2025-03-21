import time
import win32api
import win32con
import win32gui
import win32ui
from ctypes import windll
import numpy as np
import cv2
from PIL import ImageGrab
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class fake_mouse():
    def __init__(self):
        self.save_path = "./photo/screenshot.png"
        if not is_admin():
            print("警告：程序未以管理员权限运行，某些功能可能无法正常工作")
    
    def left_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def move_to(self, x, y):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, 
                           int(x * 65535 / win32api.GetSystemMetrics(0)),  # 将x坐标转换为绝对坐标
                           int(y * 65535 / win32api.GetSystemMetrics(1)),  # 将y坐标转换为绝对坐标
                           0, 0)

    def scroll(self, x, y):
        """
        模拟鼠标滚轮
        :param x: 水平滚动量（通常为0）
        :param y: 垂直滚动量（正数向下滚动，负数向上滚动）
        """
        if not is_admin():
            print("错误：需要管理员权限才能执行滚动操作")
            return
            
        # 将滚动量转换为滚轮单位（一个滚轮单位是10）
        wheel_units = int(-y / 10)  # 添加负号来反转方向
        if wheel_units != 0:
            # 使用MOUSEEVENTF_WHEEL标志，第三个参数是滚轮单位
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, wheel_units, 0)
            time.sleep(0.1)  # 添加短暂延时确保滚动完成

    def get_screenshot(self,path):
        # 获取屏幕DC
        hwnd = win32gui.GetDesktopWindow()
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        
        # 创建位图对象
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
        cDC.SelectObject(dataBitMap)
        
        # 复制屏幕内容到位图
        cDC.BitBlt((0, 0), (win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)), dcObj, (0, 0), win32con.SRCCOPY)
        
        # 转换为numpy数组
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (win32api.GetSystemMetrics(1), win32api.GetSystemMetrics(0), 4)
        
        # 转换为BGR格式
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 保存图片到指定路径
        cv2.imwrite(path, img)
        
        # 释放资源
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

    
    # 获取当前焦点窗口的截图
    def get_window_screenshot(self, save_path):
        """
        使用 hwnd 获取窗口位置，并用 Pillow 截图保存到指定路径。
        :param save_path: 截图保存路径
        """
        hwnd = win32gui.GetForegroundWindow()

        # 获取窗口的位置和大小
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # 如果窗口大小无效，抛出异常
            if width <= 0 or height <= 0:
                raise ValueError("窗口大小无效")
        except Exception as e:
            raise RuntimeError(f"无法获取窗口位置: {e}")

        # 使用 Pillow 截取指定区域
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

        # 保存截图
        screenshot.save(save_path)

if __name__ == "__main__":
    if not is_admin():
        # 如果不是管理员权限，则请求提升权限
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    fake_mouse = fake_mouse()
    
    # 获取当前窗口
    # hwnd = win32gui.GetForegroundWindow()
    # fake_mouse.get_window_screenshot(hwnd, "./photo/test.png")

    # 测试滚动
    time.sleep(5)
    fake_mouse.scroll(0, 1000)
    time.sleep(1)
    fake_mouse.scroll(0, 3300)
    time.sleep(1)
    fake_mouse.scroll(0, 3300)
    time.sleep(1)
    fake_mouse.scroll(0, 3300)
    time.sleep(1)
    fake_mouse.scroll(0, 3300)
    time.sleep(1)
    fake_mouse.scroll(0, 3300)
    time.sleep(1)
    fake_mouse.scroll(0, 3300)
    
    
    print("滚动完成")