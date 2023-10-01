import cv2
import numpy as np
from utils import calibrate, CaliConfig, CameraConfig, GlobalConfig

# 读取配置
cfg = CaliConfig()
global_cfg = GlobalConfig()

# 读入图片
l_img = cv2.imread('imgs/left-camera/left_017.png')
r_img = cv2.imread('imgs/right-camera/right_017.png')

# 转为灰度图
l_img = cv2.cvtColor(l_img, cv2.COLOR_BGR2GRAY)
r_img = cv2.cvtColor(r_img, cv2.COLOR_BGR2GRAY)

# 进行直方图均衡化
if global_cfg.equalization:
    l_img = cv2.equalizeHist(l_img)
    r_img = cv2.equalizeHist(r_img)

# 进行摄像机标定
cameras = calibrate(global_cfg, 'imgs/left-camera', 'imgs/right-camera')
# cameras = calibrate(global_cfg, file_path='stereoParams.mat') # 直接读取 .mat 文件

# 进行摄像机畸变矫正
if global_cfg.undisort:
    l_img = cv2.undistort(l_img, cameras["cameraMatrix1"], cameras["distCoeffs1"])
    r_img = cv2.undistort(r_img, cameras["cameraMatrix2"], cameras["distCoeffs2"])

if global_cfg.remap:
    # 获取畸变校正和立体校正的映射变换矩阵、重投影矩阵，计算校正变换
    left_map1, left_map2 = cv2.initUndistortRectifyMap(cameras["cameraMatrix1"], cameras["distCoeffs1"],
                                                    None, cameras["cameraMatrix1"], (l_img.shape[1], l_img.shape[0]), cv2.CV_16SC2)

    right_map1, right_map2 = cv2.initUndistortRectifyMap(cameras["cameraMatrix2"], cameras["distCoeffs2"],
                                                        None, cameras["cameraMatrix2"], (r_img.shape[1], r_img.shape[0]), cv2.CV_16SC2)

    # 畸变校正和立体校正
    l_img = cv2.remap(l_img, left_map1, left_map2, cv2.INTER_AREA)
    r_img = cv2.remap(r_img, right_map1, right_map2, cv2.INTER_AREA)

# 计算视差图
stereo = cv2.StereoSGBM_create(**cfg.__dict__)
disp = stereo.compute(l_img, r_img).astype(np.float32) / 16.0
#disp = cv2.normalize(disp, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

cv2.imwrite('disparity.jpg', disp)

# 计算深度图
depth = cameras["cameraMatrix1"][0, 0] * (np.sqrt(np.sum(cameras["T"] ** 2)) / 100) / (disp + (cameras["cameraMatrix1"][0, 2] - cameras["cameraMatrix2"][0, 2]))
depth = cv2.normalize(-depth, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

cv2.imwrite('output.jpg', depth)