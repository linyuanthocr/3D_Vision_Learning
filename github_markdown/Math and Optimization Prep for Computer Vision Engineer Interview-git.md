
This markdown document includes 20 whiteboard-style problems and answers, covering key topics for the role of Computer Vision Engineer with a focus on ****pose estimation****, ****calibration****, and ****multi-sensor fusion****, including ****nonlinear optimization**** concepts relevant to CV technology.

---

## 🔧 Pose Estimation


### 1. Reprojection Cost Function

****Problem:**** Given 3D world points and their 2D projections, write the cost function for pose estimation.  

****Answer:****  


<div class="math">

\min_{R, t} \sum_{i=1}^N \left\| u_i - \pi(K(RX_i + t)) \right\|^2

</div>

![Pasted image 20250404095619.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095619.png)

![Pasted image 20250404095640.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095640.png)
![Pasted image 20250404095654.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095654.png)

![Pasted image 20250404095729.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095729.png)

![Pasted image 20250404095754.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095754.png)

关于 公式7.44：first-order Taylor expansion
![Pasted image 20250404133440.png](3D_Vision_Interview_questions/Pasted%20image%2020250404133440.png)


---


### 2. Distortion-Aware Projection

****Problem:**** How to handle significant distortion in pose estimation?  

****Answer:**** Use distortion-aware model (e.g., radial-tangential) and optimize using LM.
![Pasted image 20250404152529.png](3D_Vision_Interview_questions/Pasted%20image%2020250404152529.png)
  ![Pasted image 20250404152449.png](3D_Vision_Interview_questions/Pasted%20image%2020250404152449.png)
  
![Pasted image 20250404152510.png](3D_Vision_Interview_questions/Pasted%20image%2020250404152510.png)
![Pasted image 20250404153051.png](3D_Vision_Interview_questions/Pasted%20image%2020250404153051.png)

##### Undisort the image first. 

当你知道相机参数，并且只考虑径向畸变和切向（斜向）畸变时，图像去畸变通常采用的是 **将新（未畸变）图像中的每个像素映射回原始（畸变）图像中寻找对应位置，然后进行像素插值** 的方法。

让我详细解释一下这个过程，并说明为什么通常不采用“每个畸变点映射到新点”的方法：

**为什么不直接将每个畸变点映射到新点？**

- **目标图像像素的完整性:** 你的目标是生成一个**新的、未畸变的图像**。这个新图像的像素网格是规则的。如果只将原始畸变图像中的每个像素映射到一个新的位置，可能会在新图像中留下“空洞”或者像素分布不均匀的情况。因为原始畸变像素的分布是不规则的，映射后很难保证新图像的每个像素都有一个对应的原始像素。
- **插值的必要性:** 即使每个原始像素都能映射到一个新的位置，新位置的坐标很可能不是整数像素坐标。为了在新图像的整数像素位置上赋予合理的颜色值，仍然需要进行插值。

**标准的去畸变流程：**

1. **创建新的、未畸变的图像:** 首先，你需要创建一个与原始畸变图像尺寸相同（或者根据需求进行调整）的新图像，用于存储去畸变后的结果。这个新图像的像素坐标是规则的整数网格。
    
2. **遍历新图像的每个像素:** 遍历这个新图像中的每一个像素点 (uundistorted​,vundistorted​)。
    
3. **反向投影到归一化图像平面:** 对于新图像中的每个像素点，你需要使用相机内参（例如焦距 fx​,fy​ 和主点 cx​,cy​）将其反向投影到**归一化图像平面**上的坐标 (xn​,yn​)：
    
    ```
    x_n = (u_{undistorted} - c_x) / f_x
    y_n = (v_{undistorted} - c_y) / f_y
    ```
    
    这里的 (xn​,yn​) 是假设没有畸变的情况下，3D世界点投影到图像平面上的坐标。
    
4. **应用畸变模型（反向畸变）:** 接下来，你需要使用已知的径向畸变和切向畸变模型以及它们的系数，计算出在原始畸变图像中，哪个归一化坐标 (xd​,yd​) 对应于当前的无畸变归一化坐标 (xn​,yn​)。这个过程是**反向**应用畸变模型。
    
    畸变模型通常描述的是如何从无畸变的点 (xn​,yn​) 映射到畸变的点 (xd​,yd​)：
    
    ```
    r^2 = x_n^2 + y_n^2
    x_d = x_n (1 + k_1 r^2 + k_2 r^4 + k_3 r^6 + ...) + 2p_1 x_n y_n + p_2 (r^2 + 2x_n^2) + ...
    y_d = y_n (1 + k_1 r^2 + k_2 r^4 + k_3 r^6 + ...) + p_1 (r^2 + 2y_n^2) + 2p_2 x_n y_n + ...
    ```
    
    其中 k1​,k2​,k3​ 是径向畸变系数， p1​,p2​ 是切向畸变系数。
    
    **反向畸变是一个求解过程。** 对于给定的 (xn​,yn​)，你需要找到 (xd​,yd​) 使得它在经过畸变后会变成 (xn​,yn​)。这个过程可能没有直接的解析解，通常需要使用迭代方法（例如牛顿法）来近似求解 (xd​,yd​)。
    
5. **投影回原始畸变图像像素坐标:** 一旦你找到了对应的归一化畸变坐标 (xd​,yd​)，你需要使用相同的相机内参将其投影回原始畸变图像的像素坐标 (udistorted​,vdistorted​)：
    
    ```
    u_{distorted} = f_x * x_d + c_x
    v_{distorted} = f_y * y_d + c_y
    ```
    
    这里的 (udistorted​,vdistorted​) 是原始畸变图像中对应于新图像像素 (uundistorted​,vundistorted​) 的浮点数坐标。
    
6. **像素插值:** 由于计算出的 (udistorted​,vdistorted​) 往往不是整数像素坐标，你需要从原始畸变图像中，根据这个浮点数坐标周围的像素值进行插值，以确定新图像像素 (uundistorted​,vundistorted​) 的颜色值。常用的插值方法包括：
    
    - **最近邻插值 (Nearest Neighbor Interpolation):** 选择距离最近的原始像素值。简单但可能产生锯齿感。
    - **双线性插值 (Bilinear Interpolation):** 使用周围 2x2 的原始像素进行加权平均。平滑效果较好，常用。
    - **双三次插值 (Bicubic Interpolation):** 使用周围 4x4 的原始像素进行更复杂的加权平均。平滑效果更好但计算量更大。

**总结:**

去畸变的过程通常是“反向映射”和“插值”的结合：

1. 遍历**未畸变图像**的每个像素。
2. 计算该像素在**归一化无畸变平面**上的坐标。
3. 通过**反向畸变模型**找到对应的**归一化畸变平面**上的坐标。
4. 将该畸变平面坐标投影回**原始畸变图像**的像素坐标。
5. 使用**插值**方法从原始畸变图像中获取该浮点数坐标处的像素值，并将其赋给未畸变图像的当前像素。

这种方法能够保证生成一个完整且规则的未畸变图像，并且通过插值能够有效地利用原始图像的像素信息。这也是 OpenCV 等库中 `cv::undistort()` 和 `cv::remap()` 等函数背后实现的主要逻辑。


---
### 3. Minimal PnP

****Problem:**** What is the minimum number of correspondences for pose estimation?  

****Answer:**** 3 for P3P, 4+ for RANSAC-PnP.

  

---

  

### 4. SE(3) Pose Update

****Problem:**** How do you update pose using Lie algebra?  

****Answer:****  

  

<div class="math">

T \leftarrow \exp(\delta\xi^\wedge) T

</div>

  

---

  

### 5. Rodrigues’s Formula

****Problem:**** What does the function look like?  

****Answer:****  
  ![Pasted image 20250404104752.png](3D_Vision_Interview_questions/Pasted%20image%2020250404104752.png)

李群上表示：

![Pasted image 20250404110516.png](3D_Vision_Interview_questions/Pasted%20image%2020250404110516.png)
#### SE(3)
Let's break down why the upper right element of the matrix exponential `exp(ξ^)` is as shown. The matrix `ξ^` is likely a 4x4 matrix in the form used in rigid body transformations, where the upper left 3x3 block represents an angular velocity and the upper right 3x1 block represents a linear velocity.

Given:

```
exp(ξ^) = [ Σ (1/n!) (φ^)^n     Σ (1/(n+1)!) (φ^)^n ρ ]
          [      0^T                 1          ]
```

And we know that `ξ^` can be decomposed (in a simplified view for this explanation) into:

```
ξ^ = [ φ^   ρ ]
     [ 0    0 ]
```

Where:

- `φ^` is a 3x3 skew-symmetric matrix representing the angular velocity vector `ω` (such that `φ^v = ω × v`).
- `ρ` is a 3x1 column vector representing the linear velocity.
- `0^T` is a 1x3 zero row vector.
- `0` in the bottom right is a scalar zero.

Now let's consider the exponential series expansion of `exp(ξ^)`:

```
exp(ξ^) = I + ξ^ + (1/2!) ξ^2 + (1/3!) ξ^3 + ... + (1/n!) ξ^n + ...
```

Let's compute the powers of `ξ^`:

```
ξ^2 = [ φ^   ρ ] [ φ^   ρ ] = [ φ^2    φ^ρ ]
      [ 0    0 ] [ 0    0 ]   [  0     0  ]

ξ^3 = ξ^2 ξ^ = [ φ^2    φ^ρ ] [ φ^   ρ ] = [ φ^3    φ^2ρ ]
              [  0     0  ] [ 0    0 ]   [  0     0  ]

...

ξ^n = [ φ^n    φ^(n-1)ρ ]
      [  0     0      ]
```

Now, let's look at the upper right 3x1 block of the `exp(ξ^)` series:

Upper Right = `0` (from I) + `ρ` (from ξ^) + `(1/2!) φ^ρ` (from ξ^2) + `(1/3!) φ^2ρ` (from ξ^3) + ... + `(1/n!) φ^(n-1)ρ` + ...

We can factor out `ρ` from all terms except the first (which is 0):

Upper Right = `ρ + (1/2!) φ^ρ + (1/3!) φ^2ρ + ... + (1/n!) φ^(n-1)ρ + ...`

Now, let's look at the second term in the given `exp(ξ^)` matrix:

```
Σ (1/(n+1)!) (φ^)^n ρ = (1/1!) φ^0 ρ + (1/2!) φ^1 ρ + (1/3!) φ^2 ρ + ... + (1/(n+1)!) φ^n ρ + ...
                     = I ρ + (1/2!) φ^ρ + (1/3!) φ^2 ρ + ... + (1/(n+1)!) φ^n ρ + ...
                     = ρ + (1/2!) φ^ρ + (1/3!) φ^2 ρ + ... + (1/(n+1)!) φ^n ρ + ...
```

Notice that the power of `φ^` in each term of our derived "Upper Right" block is one less than the power of `φ^` in the corresponding term of the given matrix's upper right block's summation index. This is precisely accounted for by the `(n+1)!` in the denominator instead of `n!` and the `φ^n` instead of `φ^(n-1)`.

Therefore, the upper right block of the exponential of `ξ^` is indeed `Σ (1/(n+1)!) (φ^)^n ρ`. This form arises naturally from the matrix exponential series when `ξ^` has the specific block structure shown (or a related form depending on the exact definition of `ξ^` used in your context, which seems to be related to twist coordinates in screw theory or Lie group exponentials for rigid body motion).

The structure of `ξ^` and the properties of the matrix exponential lead to this specific form in the upper right block, which is related to the integrated effect of the angular velocity on the linear velocity over the "time" parameter (which is often represented by `θ` or `φ` in rotation contexts). This is also connected to the concept of the **Jacobian of the exponential map** in Lie group theory.
![Pasted image 20250404125526.png](3D_Vision_Interview_questions/Pasted%20image%2020250404125526.png)
![Pasted image 20250404132836.png](3D_Vision_Interview_questions/Pasted%20image%2020250404132836.png)
## 📷 Calibration

  

### 6. 3D to 2D Projection Equation

****Problem:**** Derive the basic projection formula.  

****Answer:****  

  

<div class="math">

u = K [R|t] X

</div>

  

---

  

### 7. IMU-Camera Calibration

****Problem:**** How to spatially calibrate IMU and camera?  

****Answer:****  

  

<div class="math">

T_{W}^{I}(t) = T_{IC} \cdot T_{W}^{C}(t)

</div>

  

---

  

### 8. Hand-Eye Calibration

****Problem:**** Define the hand-eye problem.  

****Answer:****  

  ![Pasted image 20250404161646.png](3D_Vision_Interview_questions/Pasted%20image%2020250404161646.png)
  ![Pasted image 20250404163634.png](3D_Vision_Interview_questions/Pasted%20image%2020250404163634.png)
  ![Pasted image 20250404163707.png](3D_Vision_Interview_questions/Pasted%20image%2020250404163707.png)
  ![Pasted image 20250404163839.png](3D_Vision_Interview_questions/Pasted%20image%2020250404163839.png)
  ![Pasted image 20250404171938.png](3D_Vision_Interview_questions/Pasted%20image%2020250404171938.png)
  

<div class="math">

AX = XB

</div>
---

  

### 9. Camera Intrinsics from Chessboard

****Problem:**** How to estimate intrinsics from a checkerboard?  

****Answer:**** Zhang’s method: detect corners, estimate homographies, solve for K.

  

---

  

### 10. Multi-Camera Calibration

****Problem:**** How to calibrate multiple cameras?  

****Answer:**** Minimize joint reprojection error across all views.

  

---

  

## 🔁 Multi-Sensor Fusion / VIO

  

### 11. VIO Measurement Model

****Problem:**** What are the models for VIO?  

****Answer:****  

Visual: reprojection error  

Inertial: preintegration error  

  

<div class="math">
r_{imu} = \hat{x}_{i+1} - f(\hat{x}_i, \hat{u}_{i \rightarrow i+1})
</div>

  

---

  

### 12. IMU-Camera Fusion via EKF

****Problem:**** How to fuse IMU and camera in filtering?  

****Answer:**** EKF: IMU predicts, camera updates.

  

---

  

### 13. IMU Preintegration

****Problem:**** What is it and why useful?  

****Answer:**** Avoids re-integrating during each iteration.

  

---

  

### 14. Monocular VIO Scale Init

****Problem:**** How to estimate scale?  

****Answer:**** Align visual motion to IMU preintegration.

  

---

  

### 15. Accelerometer Bias

****Problem:**** How to handle it?  

****Answer:**** Model bias in state and optimize/filter.

  

---

  

## 🧮 Nonlinear Optimization

  

### 16. Gauss-Newton vs LM

****Problem:**** What’s the difference?  

****Answer:**** LM adds damping:  

  

<div class="math">

(J^T J + \lambda I)\delta = -J^T r

</div>

  

---

  

### 17. Cost Function Linearization

****Problem:**** How to linearize nonlinear cost?  

****Answer:****  

  

<div class="math">

r(x + \delta) \approx r(x) + J \delta

</div>

  

---

  

### 18. Schur Complement in BA

****Problem:**** Where is Schur used?  

****Answer:**** To marginalize landmarks:  

  

<div class="math">

S = A - BC^{-1}B^T

</div>

  

---

  

### 19. Observability in VIO

****Problem:**** How to ensure it?  

****Answer:**** Motion excitation, overlapping landmarks, good baseline.

  

---

  

### 20. Null Space in VIO

****Problem:**** What’s unobservable?  

****Answer:**** Global position, yaw, scale (in monocular)

  

---

### 21.  Bundle Adjustment
  ![Pasted image 20250404095619.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095619.png)

---

  ![Pasted image 20250404095640.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095640.png)
![Pasted image 20250404095654.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095654.png)
![Pasted image 20250404095729.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095729.png)
![Pasted image 20250404095754.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095754.png)
![Pasted image 20250404095812.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095812.png)

![Pasted image 20250404095828.png](3D_Vision_Interview_questions/Pasted%20image%2020250404095828.png)

### 22.  李群和李代数

反对称阵：Skew-symmetric matrix
A skew-symmetric matrix transforms a cross product into a matrix multiplication.


![Pasted image 20250404105553.png](3D_Vision_Interview_questions/Pasted%20image%2020250404105553.png)
![Pasted image 20250404105635.png](3D_Vision_Interview_questions/Pasted%20image%2020250404105635.png)
![Pasted image 20250404105516.png](3D_Vision_Interview_questions/Pasted%20image%2020250404105516.png)

![Pasted image 20250404110321.png](3D_Vision_Interview_questions/Pasted%20image%2020250404110321.png)

### 22.  NLS, Gaussian Newton and LM

![Pasted image 20250404140014.png](3D_Vision_Interview_questions/Pasted%20image%2020250404140014.png)
![Pasted image 20250404140133.png](3D_Vision_Interview_questions/Pasted%20image%2020250404140133.png)
![Pasted image 20250404140152.png](3D_Vision_Interview_questions/Pasted%20image%2020250404140152.png)

![Pasted image 20250404140247.png](3D_Vision_Interview_questions/Pasted%20image%2020250404140247.png)
![Pasted image 20250404140316.png](3D_Vision_Interview_questions/Pasted%20image%2020250404140316.png)
**Jacobian matrix** contains all the **first-order partial derivatives**

![Pasted image 20250404141407.png](3D_Vision_Interview_questions/Pasted%20image%2020250404141407.png)
![Pasted image 20250404141454.png](3D_Vision_Interview_questions/Pasted%20image%2020250404141454.png)

![Pasted image 20250404141526.png](3D_Vision_Interview_questions/Pasted%20image%2020250404141526.png)
![Pasted image 20250404141546.png](3D_Vision_Interview_questions/Pasted%20image%2020250404141546.png)

### 23.  Camera Calibration

The principle behind camera calibration is to **mathematically model the mapping between a 3D point in the real world and its 2D projection onto the image sensor**, and then to **estimate the parameters of this model** using known correspondences between 3D points and their 2D image locations.

Here's a breakdown of the underlying principles:

**1. Camera Model:**

The foundation of camera calibration is a mathematical model that describes how a 3D world point (X,Y,Z)w​ is projected to a 2D pixel coordinate (u,v) in the image. The most common model is the **pinhole camera model**, which is often augmented to account for lens distortions.

- **Pinhole Model:**
    
    - Assumes that light rays from the 3D world pass through a single point (the pinhole or optical center) and project onto the image plane.
    - The relationship between a 3D point in the camera coordinate system (X,Y,Z)c​ and its ideal projection (x,y) on the image plane (in metric units) is given by perspective projection:
        
        ```
        x = f * (X / Z)
        y = f * (Y / Z)
        ```
        
        where f is the focal length (the distance between the optical center and the image plane).
    - These ideal image plane coordinates (x,y) are then converted to pixel coordinates (u,v) using the camera's intrinsic parameters:
        
        ```
        u = f_x * x + c_x
        v = f_y * y + c_y
        ```
        
        where fx​ and fy​ are the focal lengths in pixel units along the u and v axes, and (cx​,cy​) is the principal point (the center of the image in pixel coordinates).
- **Lens Distortion Model:**
    
    - Real lenses introduce distortions that cause deviations from the ideal pinhole projection. The most common distortions are radial and tangential.
    - **Radial Distortion:** Causes straight lines to appear curved. It's typically modeled using polynomial terms of the radial distance from the image center:
        
        ```
        x_d = x_n (1 + k_1 r^2 + k_2 r^4 + k_3 r^6 + ...)
        y_d = y_n (1 + k_1 r^2 + k_2 r^4 + k_3 r^6 + ...)
        ```
        
        where (xn​,yn​) are the normalized image coordinates, (xd​,yd​) are the distorted normalized coordinates, r2=xn2​+yn2​, and k1​,k2​,k3​,... are the radial distortion coefficients.
    - **Tangential Distortion:** Occurs due to imperfect alignment of lens elements. It's typically modeled as:
        
        ```
        x_d = x_d + (2p_1 x_n y_n + p_2 (r^2 + 2x_n^2) + ...)
        y_d = y_d + (p_1 (r^2 + 2y_n^2) + 2p_2 x_n y_n + ...)
        ```
        
        where p1​,p2​,... are the tangential distortion coefficients.

**2. Establishing Correspondences:**

Camera calibration requires knowing the 3D coordinates of a set of points in the real world and their corresponding 2D pixel coordinates in one or more images. A common way to achieve this is by using a calibration pattern with known geometry, such as a checkerboard.

- **Checkerboard:** The corners of the squares on a checkerboard have well-defined 3D relative positions. By placing the checkerboard in the camera's field of view and capturing images from different angles, we can extract the 2D pixel coordinates of these corners in each image.
- **Object Points:** The 3D coordinates of the checkerboard corners are known relative to the checkerboard itself. We can define a world coordinate system where the checkerboard lies on a plane (e.g., Z=0).
- **Image Points:** The 2D pixel coordinates of the detected checkerboard corners in each image are the corresponding image points.

**3. Parameter Estimation (Optimization):**

The goal of calibration is to find the intrinsic parameters (fx​,fy​,cx​,cy​,k1​,k2​,p1​,p2​,...) and the extrinsic parameters (rotation R and translation t for each camera pose relative to the world coordinate system) that best explain the observed correspondences between the 3D object points and their 2D image points.

This is typically formulated as a **non-linear least squares optimization problem**. The error function to be minimized is the **reprojection error**, which is the squared difference between the observed 2D image points and the 2D image points predicted by the camera model using the current estimates of the parameters.

- **Reprojection:** For each known 3D object point, we project it into the 2D image plane using the current camera model parameters (including intrinsics, extrinsics, and distortion).
- **Error Calculation:** We calculate the distance between the predicted 2D point and the actually observed 2D point in the image.
- **Minimization:** An optimization algorithm (like the Levenberg-Marquardt algorithm) iteratively adjusts the camera parameters to minimize the sum of the squared reprojection errors over all the calibration images and all the detected points.

**4. Mathematical Formulation:**
![Pasted image 20250404160027.png](3D_Vision_Interview_questions/Pasted%20image%2020250404160027.png)
**In essence, camera calibration is about finding the set of camera parameters that best explains how 3D points in the world are mapped to 2D points in the image by minimizing the discrepancy between the predicted and observed image locations of known 3D points.** This process allows us to correct for lens distortions and to establish the relationship between the camera's coordinate system and the real world.

In camera calibration, the **camera pose (extrinsic parameters)** and the **camera parameters (intrinsic parameters and distortion coefficients)** are typically optimized **together** in a process that often involves **iterative optimization**.

Here's a breakdown of how this works:

**1. The Optimization Problem:**

As explained previously, the goal of camera calibration is to minimize the **reprojection error**, which is the difference between the observed 2D image points and the 2D projections of the corresponding 3D world points using the current estimates of both camera pose and camera parameters. The total error to minimize is the sum of squared reprojection errors over all calibration images and all detected feature points.

**2. The Variables to Optimize:**

The optimization process aims to find the values for the following variables that minimize the reprojection error:

- **Intrinsic Parameters:**
    - Focal lengths (fx​,fy​)
    - Principal point (cx​,cy​)
    - Distortion coefficients (k1​,k2​,k3​,p1​,p2​, and potentially higher-order terms)
- **Extrinsic Parameters (for each calibration image):**
    - Rotation matrix (R) or rotation vector (e.g., Rodrigues vector) representing the camera's orientation relative to the world coordinate system (often defined by the calibration pattern).
    - Translation vector (t) representing the camera's position relative to the world coordinate system.

**3. Iterative Optimization:**

Due to the non-linear nature of the camera model (especially with the inclusion of distortion) and the relationship between the parameters and the reprojection error, the optimization problem is typically solved using **iterative non-linear least squares algorithms**. The most common algorithm used for this purpose is the **Levenberg-Marquardt (LM) algorithm**.

**How the Levenberg-Marquardt (LM) Algorithm Works (Simplified):**

The LM algorithm is an iterative technique that combines aspects of two other optimization methods:

- **Gradient Descent:** When far from the minimum, the algorithm behaves more like gradient descent, taking small steps in the direction of the negative gradient of the error function. This helps to move towards the general vicinity of the optimal solution.
- **Gauss-Newton:** When closer to the minimum, the algorithm behaves more like the Gauss-Newton method, which uses a second-order approximation of the error function (based on the Jacobian) to take larger, more direct steps towards the minimum. This often leads to faster convergence near the optimal solution.

The LM algorithm adaptively adjusts a damping parameter (λ) to control the balance between gradient descent and Gauss-Newton behavior.

- **Large λ:** Favors gradient descent (smaller steps, more stable).
- **Small λ:** Favors Gauss-Newton (larger steps, faster convergence near the minimum).

At each iteration of the LM algorithm:
![Pasted image 20250404160253.png](3D_Vision_Interview_questions/Pasted%20image%2020250404160253.png)

**In summary, camera calibration optimizes camera pose and camera parameters simultaneously using iterative non-linear least squares methods like the Levenberg-Marquardt algorithm. This algorithm iteratively refines the parameter estimates by minimizing the reprojection error, considering the influence of both intrinsic and extrinsic parameters on the final image projection.**

What's the dimension of J? (2mn)\*(4+d+6m) (m is the image numbers, n is the checkboard corners)
N\*M checker board only contains (N-1)\*(M-1) corners.

### 24.  Hand Eye Calibration
