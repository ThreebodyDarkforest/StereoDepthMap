import cv2
import os
import numpy as np
from pydantic import BaseModel
from scipy.io import loadmat

class CameraConfig(BaseModel):
    criteria: tuple = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    square_size: tuple = (8, 6)
    board_size: tuple = (10, 7)

class CaliConfig(BaseModel):
    minDisparity: int = 0
    numDisparities: int = 128
    blockSize: int = 5
    uniquenessRatio: int = 5
    speckleRange: int = 2
    speckleWindowSize: int = 50
    preFilterCap: int = 63
    disp12MaxDiff: int = 100
    mode: int = cv2.STEREO_SGBM_MODE_SGBM_3WAY
    P1: int = 8 * 3 * blockSize ** 2
    P2: int = 32 * 3 * blockSize ** 2

class GlobalConfig(CameraConfig):
    equalization: bool = True
    undisort: bool = True
    remap: bool = True

def calibrate(cfg: CameraConfig, left_path: str = None, right_path: str = None, file_path: str = None):

    assert (left_path is not None and right_path is not None) or file_path is not None, 'Please select a way to load camera data.'

    if left_path is not None and right_path is not None:
        imgpoints_l = []
        imgpoints_r = []
        objpoints = []

        # 创建对象点
        objp = np.zeros((1, cfg.square_size[0] * cfg.square_size[1], 3), np.float32)
        objp[0, :, :2] = np.mgrid[0:cfg.square_size[0], 0:cfg.square_size[1]].T.reshape(-1, 2)
        objp[0, :, 0] *= cfg.square_size[0]
        objp[0, :, 1] *= cfg.square_size[1]

        # 遍历左右相机图像并进行棋盘格角点检测
        for l, r in zip(os.listdir(left_path), os.listdir(right_path)):
            # 读取左相机图像并转换为灰度图像
            img_l = cv2.imread(os.path.join(left_path, l))
            gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)

            # 读取右相机图像并转换为灰度图像
            img_r = cv2.imread(os.path.join(right_path, r))
            gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

            # 在左相机图像中检测棋盘格角点
            ret_l, corners_l = cv2.findChessboardCorners(gray_l, cfg.square_size)

            # 在右相机图像中检测棋盘格角点
            ret_r, corners_r = cv2.findChessboardCorners(gray_r, cfg.square_size)

            # 如果左右相机图像中都成功检测到了角点
            if ret_l and ret_r:
                objpoints.append(objp)

                # 对左相机图像中的角点进行亚像素级别的精确化
                corners2_l = cv2.cornerSubPix(gray_l, corners_l, (11, 11), (-1, -1), cfg.criteria)
                imgpoints_l.append(corners2_l)

                # 对右相机图像中的角点进行亚像素级别的精确化
                corners2_r = cv2.cornerSubPix(gray_r, corners_r, (11, 11), (-1, -1), cfg.criteria)
                imgpoints_r.append(corners2_r)

        # 确保至少有一对有效的图像
        assert len(objpoints) > 0, 'invalid imgs.'
        print(f'valid img pair: {len(objpoints)}')

        # 分别对左相机和右相机进行摄像机标定
        ret, mtx_l, dist_l, rvecs_l, tvecs_l = cv2.calibrateCamera(objpoints, imgpoints_l, gray_l.shape[::-1], None, None)
        ret, mtx_r, dist_r, rvecs_r, tvecs_r = cv2.calibrateCamera(objpoints, imgpoints_r, gray_r.shape[::-1], None, None)

        # 进行立体标定，计算相机矩阵、畸变系数、旋转矩阵、平移向量、本质矩阵和基础矩阵
        retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = \
            cv2.stereoCalibrate(objpoints, imgpoints_l, imgpoints_r, mtx_l, dist_l, mtx_r, dist_r, gray_l.shape[::-1])
    else:
        # 加载 Matlab 摄像机标定参数
        data = loadmat(file_path)
        retval = 0.0
        cameraMatrix1 = data['cameraMatrix1'].T
        cameraMatrix2 = data['cameraMatrix2'].T
        distCoeffs1 = np.concatenate((data['TangentialDistortion1'], \
                                     data['RadialDistortion1']), axis = 1)
        distCoeffs2 = np.concatenate((data['TangentialDistortion2'], \
                                     data['RadialDistortion2']), axis = 1)
        R = data['R'].T
        T = data['T'].T
        E = data['E'].T
        F = data['F'].T

    return {
        "retval": retval,
        "cameraMatrix1": cameraMatrix1,
        "cameraMatrix2": cameraMatrix2,
        "distCoeffs1": distCoeffs1,
        "distCoeffs2": distCoeffs2,
        "R": R,
        "T": T,
        "E": E,
        "F": F,
    }

if __name__ == '__main__':
    print(calibrate(CameraConfig(), 'imgs/left-camera', 'imgs/right-camera'))