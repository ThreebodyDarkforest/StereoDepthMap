# 基于 opencv 的双目测距实践

## 概述

本项目是一个用于计算视差图和深度图的摄像机标定和畸变矫正工具。它通过使用两个相机的图像，进行摄像机标定和畸变矫正，然后计算视差图和深度图。

注意，由于本项目是一次课后作业，作者无法保证代码完全正确。

## 快速开始

按照如下步骤进行操作，您可以运行本项目的代码。

- 通过如下方法克隆本仓库

```shell
git clone https://github.com/ThreebodyDarkforest/StereoDepthMap.git
```

- 运行如下命令以安装依赖

```shell
pip install -r requirements.txt
```

- 执行 `main.py`

```shell
python main.py
```

值得注意的是，您可以在 `utils.py` 的三个 `Config` 类中修改参数以尝试获得不同的结果。

## 实现方法和流程

本项目的实现思路大致如下：

1. 数据采集和准备
    - 使用双目相机拍摄多组照片，将左相机的照片保存到`imgs/left-camera`目录下，将右相机的照片保存到`imgs/right-camera`目录下。

2. 相机标定
    - 可选步骤，使用Matlab或OpenCV对左相机和右相机进行相机标定。
    - 首先对左相机和右相机分别进行相机标定，获取相机的内参和畸变系数。
    - 然后利用相机标定结果进行双目标定，计算得到左右相机之间的外参和立体校正矩阵。

3. 畸变矫正和立体校正
    - 利用相机的内参和外参，对左右相机的图像进行畸变矫正和立体校正。
    - 对左相机的图像进行畸变矫正，得到校正后的左图像。
    - 对右相机的图像进行畸变矫正，得到校正后的右图像。
    - 利用立体校正矩阵对左右图像进行立体校正，保证两个图像的对应行在同一水平线上。

4. 视差计算
    - 使用OpenCV自带的视差计算算法，对校正后的左右图像进行匹配，得到视差图。
    - 视差图表示了同一点在左右图像中的像素位移，可以用来计算深度信息。

5. 深度计算
    - 利用视差图和其他参数，可以计算出深度图。
    - 使用公式 Z = baseline * f / (d + doffs) 计算深度图，其中：
        - Z：深度图
        - baseline：两相机光心之间的距离，也称为基线长度（单位：毫米）
        - f：相机的焦距（单位：像素）
        - d：视差图（单位：像素），是一个矩阵
        - doffs：两相机相平面原点在世界坐标系下的 x 方向距离

更详细的解释请参阅代码注释。

## 项目结构

本项目的目录树如下

```
├── imgs
│   ├── left_017.png
│   ├── left-camera
│   ├── right_017.png
│   └── right-camera
├── main.py
├── README.md
├── requirements.txt
├── stereoParams.mat
└── utils.py
```

其中 `main.py` 为项目入口文件，`utils.py` 存放配置文件和常用函数，`stereoParams.mat` 是在 Matlab 中标定相机得到的结果。

`imgs` 文件夹中，`xxx-camera` 目录中为用于相机标定的图片。

## 参考链接

- [Matlab双目标定与python-opencv配置标定参数](https://blog.csdn.net/tqptr_opqww/article/details/115358266)
- [python读取matlab数据(.mat文件)](https://blog.csdn.net/qq_44946715/article/details/119932640)
- [OpenCV Camera Calibration](https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html)
- [【OpenCV-Python】16 使用同一物体的两幅图像来计算视差图](https://blog.csdn.net/weixin_45839039/article/details/111997517)
- [单、双目相机标定及畸变校正、立体矫正的python实现（含拍照程序）](https://blog.csdn.net/qq_22059843/article/details/103400094)
- [opencv进行双目标定以及极线校正 python代码](https://blog.csdn.net/qq_30234963/article/details/121908465)