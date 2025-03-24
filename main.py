import os
import tkinter as tk
from tkinter import filedialog, messagebox, font
import ctypes
from threading import Thread, Event
import sys
import win32api
import win32con
from auto_task import auto_task

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 请求管理员权限重新启动程序
def run_as_admin():
    if not is_admin():
        # 获取当前脚本的完整路径
        script = os.path.abspath(sys.argv[0])
        # 请求管理员权限重新启动程序
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
        sys.exit()

# 在程序启动时检查管理员权限
if __name__ == "__main__":
    run_as_admin()

# 全局变量存储文件夹路径
app_road = ""

# 创建一个事件对象，用于线程间通信
task_completed_event = Event()

# 打开文件夹选择对话框
def select_folder():
    global app_road
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        app_road = folder_selected
        folder_label.config(text=f"已选择文件夹: {app_road}")
    else:
        folder_label.config(text="未选择文件夹")


def MP(x, y):
    try:
        # 获取当前鼠标位置
        current_x, current_y = win32api.GetCursorPos()
        # 计算相对移动距离
        dx = x - current_x
        dy = y - current_y
        # 使用MOUSEEVENTF_ABSOLUTE标志进行绝对坐标移动
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, 
                           int(x * 65535 / win32api.GetSystemMetrics(0)),  # 将x坐标转换为绝对坐标
                           int(y * 65535 / win32api.GetSystemMetrics(1)),  # 将y坐标转换为绝对坐标
                           0, 0)
    except Exception as e:
        print(f'Move Error: {str(e)}')


# 运行选定文件夹中的 exe 文件，并关闭 GUI
def run_exe():
    global app_road
    if not app_road:
        messagebox.showerror("错误", "请先选择一个文件夹")
        return

    print(f"选择的文件夹路径: {app_road}")
    
    # 获取文件夹中的 leigod.exe 文件
    exe_files = [f for f in os.listdir(app_road) if f == "leigod.exe"]
    print(f"找到的exe文件: {exe_files}")

    if not exe_files:
        messagebox.showerror("错误", "该文件夹中没有找到 leigod.exe 文件")
        return

    # 如果有多个 exe 文件，选择第一个
    exe_to_run = os.path.join(app_road, exe_files[0])
    print(f"准备运行exe文件: {exe_to_run}")

    try:
        print("尝试以管理员权限运行exe文件...")
        # 使用管理员权限运行目标exe文件
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_to_run, "", None, 1)
        print("exe文件启动成功")
        
        # 启动耗时任务
        def task():
            print("开始执行自动任务线程...")
            result = auto_task()
            if result:
                print("任务执行成功，设置完成标志")
                task_completed_event.set()
            else:
                print("任务执行失败")

        print("创建并启动任务线程...")
        # 使用线程运行耗时任务，避免阻塞 GUI
        Thread(target=task).start()

        print("开始检查任务完成状态...")
        # 定期检查任务是否完成
        check_task_completion()

    except Exception as e:
        error_msg = f"无法运行 {exe_files[0]}: {str(e)}"
        print(error_msg)
        import traceback
        print("详细错误信息:")
        print(traceback.format_exc())
        messagebox.showerror("错误", error_msg)

# 定期检查任务是否完成
def check_task_completion():
    if task_completed_event.is_set():
        show_completion_popup()
    else:
        root.after(100, check_task_completion)  # 每隔 100ms 检查一次

# 弹出任务完成的提示窗口
def show_completion_popup():
    # 创建一个新的弹窗
    popup = tk.Toplevel(root)
    popup.title("任务完成")
    popup.geometry("300x150")
    popup.resizable(False, False)

    # 设置弹窗内容
    label = tk.Label(popup, text="程序执行完毕！", font=("微软雅黑", 12))
    label.pack(pady=20)

    # 确认按钮
    confirm_button = tk.Button(popup, text="确认", command=lambda: close_all(popup), width=10, height=1)
    confirm_button.pack(pady=10)

# 关闭所有程序
def close_all(popup=None):
    if popup:
        popup.destroy()  # 关闭弹窗
    root.quit()  # 关闭主窗口

# 创建 GUI 界面
root = tk.Tk()
root.title("运行文件夹中的 exe 程序")

# 设置窗口的初始大小
window_width = 500
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# 设置全局字体样式
default_font = font.Font(family="微软雅黑", size=12)
root.option_add("*Font", default_font)

# 标签显示当前选择的文件夹
folder_label = tk.Label(root, text="未选择文件夹", wraplength=400, justify="center")
folder_label.pack(pady=20)

# 按钮用于选择文件夹
select_button = tk.Button(root, text="选择文件夹", command=select_folder, width=20, height=2)
select_button.pack(pady=10)

# 按钮用于运行 exe 文件
run_button = tk.Button(root, text="执行自动抓取程序", command=run_exe, width=20, height=2)
run_button.pack(pady=20)

# 启动 GUI 主循环
root.mainloop()