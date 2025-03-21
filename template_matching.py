import numpy as np
import cv2

def template_match(template_color, target_color):
    # 读取彩色模板图

    if template_color is None or target_color is None:
        print("图片读取失败")
        return None, None

    # 转为灰度图以提取SIFT特征
    template_gray = cv2.cvtColor(template_color, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.cvtColor(target_color, cv2.COLOR_BGR2GRAY)

    # 创建SIFT对象
    sift = cv2.SIFT_create()

    # 计算关键点和描述符
    kp1, des1 = sift.detectAndCompute(template_gray, None)
    kp2, des2 = sift.detectAndCompute(target_gray, None)

    if des1 is None or des2 is None:
        print("未检测到特征点")
        return None, None

    # 设置FLANN参数
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # KNN匹配
    matches = flann.knnMatch(des1, des2, k=2)

    # Lowe's ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    print(f"有效匹配点数量: {len(good_matches)}")

    # 检查是否有足够的点计算单应性矩阵
    if len(good_matches) < 4:
        print("匹配点不足，无法计算单应性矩阵")
        return None, None

    # 计算单应性矩阵
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if M is not None:
        h, w = template_color.shape[:2]

        # 模板图四个角点
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # 在目标图中的对应坐标
        dst = cv2.perspectiveTransform(pts, M)

        # 计算中心点
        center_x = int(np.mean(dst[:, 0, 0]))
        center_y = int(np.mean(dst[:, 0, 1]))

        print(f"匹配区域中心坐标: ({center_x}, {center_y})")

        return center_x, center_y

    else:
        print("单应性矩阵计算失败")
        return None, None


# # 测试
# target_color = cv2.imread('tem4.png')

# center_x, center_y = template_match(target_color)

# if center_x is not None:
#     print(f"最终目标中心点坐标: ({center_x}, {center_y})")
# else:
#     print("未检测到目标")
