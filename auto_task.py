from fake_mouse import fake_mouse
from template_matching import template_match
import cv2
from time import sleep
from extracter import extract_text,save_result,filter_result
import os, sys

def resource_path(relative_path):
    """ 获取资源文件的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 会将资源文件解压到 _MEIPASS 目录
        base_path = sys._MEIPASS
    else:
        # 开发环境中的路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def auto_task():
    try:
        print("开始执行自动任务...")
        mouse_controller = fake_mouse()

        screenshot_path = resource_path("photo/screenshot.png")
        template_path = resource_path("photo/template.png")
        template3_path = resource_path("photo/template3.png")
        example_image_path = resource_path("photo/example.png")
        sleep(3)
        
        # 切换到游戏窗口，第一次匹配循环
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            mouse_controller.get_screenshot(screenshot_path)
            target_color = cv2.imread(screenshot_path)
            template_color = cv2.imread(template_path)
            
            if target_color is None or template_color is None:
                attempt += 1
                sleep(3)
                continue
                
            center_x, center_y = template_match(template_color, target_color)
            
            if center_x is not None and center_y is not None:
                break
            else:
                attempt += 1
                sleep(3)
        
        if attempt >= max_attempts:
            print("错误：达到最大尝试次数，匹配失败")
            return False
            
        mouse_controller.move_to(center_x, center_y)
        sleep(1)
        mouse_controller.left_click()
        sleep(0.5)
        mouse_controller.left_click()
        sleep(2)

        # 将鼠标移到正确的位置便于后续的滚动
        # 第二次匹配循环
        attempt = 0
        while attempt < max_attempts:
            mouse_controller.get_screenshot(screenshot_path)
            target_color = cv2.imread(screenshot_path)
            template_color = cv2.imread(template_path)
            
            if target_color is None or template_color is None:
                attempt += 1
                sleep(3)
                continue
                
            center_x, center_y = template_match(template_color, target_color)
            
            if center_x is not None and center_y is not None:
                break
            else:
                attempt += 1
                sleep(3)
        
        if attempt >= max_attempts:
            print("错误：达到最大尝试次数，第二次匹配失败")
            return False
            
        mouse_controller.move_to(center_x - 50, center_y)
        

        # 滚动抓取截图
        mouse_controller.scroll(0, 1000)
        scroll_distance = 3250
        scroll_count = 10
        for i in range(scroll_count):
            mouse_controller.scroll(0, scroll_distance)
            sleep(1)
            screenshot_path = resource_path(f"photo/rank{i}.png")
            mouse_controller.get_window_screenshot(screenshot_path)
            sleep(0.5)
        
        result = ""
        for i in range(scroll_count):
            print(f'正在处理第{i+1}张图片')
            screenshot_path = resource_path(f"photo/rank{i}.png")
            # example_image_path = f'./photo/example.png'
            # image_path = f'./photo/rank{i}.png'
            current_result = extract_text(example_image_path,screenshot_path)
            result= result +  str(i+1)+":"+ current_result + "\n"
            print(current_result)
            

        print(f'正在过滤结果')
        result=filter_result(result)
        save_result(result)

        #  删除photo文件夹中的图片
        # for i in range(scroll_count):
        #     os.remove(f'./photo/rank{i}.png')
        
        print("任务执行完成！")
        return True
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print("详细错误信息:")
        print(traceback.format_exc())
        return False