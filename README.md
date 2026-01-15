# UAV–IRS Downlink Communication System

**Course: Telecommunications System - ET4250**

**Lecturers: Nguyen Thanh Chuyen**

**School: Hanoi University of Science and Technology - HUST**

**Students: Nguyen Ho Trieu Duong - 20224280**

**Created: Mon 24 Nov 2025 14:15:36 Hanoi, Vietnam**


## 📡 Giới thiệu
Dự án này nghiên cứu và mô phỏng **hệ thống truyền thông downlink sử dụng UAV được hỗ trợ bởi Intelligent Reflecting Surface (IRS)**.  
Mục tiêu chính là **tối ưu pha phản xạ của IRS** nhằm tăng cường công suất thu, cải thiện CNR và hiệu năng liên kết trong các kịch bản kênh thực tế.

Dự án tập trung vào:
- Mô hình kênh UAV–IRS–Ground Station (GS)
- Beamforming thụ động bằng IRS
- Thuật toán tối ưu pha **Alternating Optimization (AO)**
- So sánh giữa **closed-form solution** và **AO trong môi trường kênh động**

---

## 🧠 Ý tưởng cốt lõi
IRS không phát tín hiệu mà **điều khiển pha phản xạ** của sóng tới, giúp:
- Cộng pha tín hiệu tại trạm thu
- Tăng gain hiệu dụng nhờ coherent combining
- Hỗ trợ liên kết trong trường hợp LoS yếu hoặc bị che khuất

Trong hệ thống này:
- UAV đóng vai trò **bộ phát**
- IRS được gắn trên UAV
- Trạm mặt đất (GS) là **bộ thu**

---

## 🗂️ Cấu trúc thư mục
```
UAV_IRS_Downlink_Simulation/
│
├── params.py # Các tham số hệ thống
├── platform_model.py # Mô hình hình học UAV – GS
├── irs_model.py # Mô hình IRS và steering vector
├── link_budget.py # Tính toán link budget, CNR
├── main.py (nếu có) # File chạy mô phỏng chính
│
├── report/ # Báo cáo học thuật
│ ├── report.pdf
│ └── report.tex
│
├── figures/ # Hình ảnh, đồ thị kết quả
│
└── README.md # File mô tả dự ánV

```



---

## ⚙️ Mô hình hệ thống

### 🔹 Thành phần
- **UAV**: phát tín hiệu downlink ở độ cao cố định
- **IRS**:
  - Cấu hình UPA \(32 \times 32\) (1024 phần tử)
  - Khoảng cách phần tử: \(\lambda/2\)
  - Điều khiển pha phản xạ
- **GS**: trạm thu mặt đất

### 🔹 Kênh truyền
- UAV → IRS: LoS chi phối, mô hình steering vector
- IRS → GS: LoS + fading (Rician)
- Có xét:
  - Fading
  - Doppler
  - Blockage theo góc ngẩng

---

## 📐 Mô hình toán học

### Kênh IRS
$$\mathbf h_{UI} = \alpha_{UI} \mathbf a_{IRS}(\theta_{UI}, \phi_{UI})$$

$$\mathbf h_{IG} = \alpha_{IG} \mathbf a_{IRS}(\theta_{IG}, \phi_{IG})$$


### Tín hiệu thu qua IRS

$$y \propto \mathbf h_{IG}^H \boldsymbol\Phi \mathbf h_{UI}$$


Trong đó:
$$\boldsymbol\Phi = \mathrm{diag}(e^{j\phi_1}, \dots, e^{j\phi_M})$$



---

## 🔁 Thuật toán tối ưu pha IRS (AO)

Dự án triển khai **Alternating Optimization (AO)**:
- Tối ưu pha từng phần tử IRS
- Mỗi bước có nghiệm closed-form
- Hàm mục tiêu tăng đơn điệu và hội tụ

### Tiêu chí dừng:
- Sai khác hàm mục tiêu < tolerance
- Hoặc đạt số vòng lặp tối đa

---

## 📊 Các chỉ số đánh giá
- Công suất thu
- CNR (Carrier-to-Noise Ratio)
- Khả năng duy trì liên kết theo thời gian
- So sánh:
  - Không IRS
  - IRS với closed-form
  - IRS với AO

---

## ▶️ Cách chạy mô phỏng

### 1️⃣ Cài đặt môi trường
```bash
pip install numpy scipy matplotlib
```

### 2️⃣ Chạy mô phỏng

```
python link_budget.py
```