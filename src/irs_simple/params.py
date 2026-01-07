"""
params.py - Tham số hệ thống UAV mang IRS hỗ trợ downlink
(Đã chỉnh sửa: IRS gain đến từ phase optimization, KHÔNG cộng tay)
"""
import numpy as np

# ===================================================================
# 1. THAM SỐ UAV VÀ THỜI GIAN MÔ PHỎNG
# ===================================================================
h_uav = 300.0                 # Độ cao UAV (m)
T_pass = 600                  # Thời gian pass (s)
delta_t = 1.0
num_points = int(T_pass / delta_t) + 1

# ===================================================================
# 2. THAM SỐ TRUYỀN DẪN
# ===================================================================
f = 10e9                      # 10 GHz
c = 3e8
lambda_w = c / f

B = 50e6                      # 50 MHz
EIRP_dBW = 25.0               # EIRP UAV
G_r_dBi = 15.0                # Gain anten GS

# ===================================================================
# 3. SUY HAO HỆ THỐNG
# ===================================================================
L_atm_dB = 1.0
L_impl_dB = 2.0
L_pol_dB = 1.0
L_point_dB = 1.0
L_total_fixed_dB = L_atm_dB + L_impl_dB + L_pol_dB + L_point_dB

# ===================================================================
# 4. THAM SỐ IRS (PHASE OPTIMIZATION)
# ===================================================================
M = 1024                       # Số phần tử IRS 
eta_IRS = 0.9                 # Hiệu suất phản xạ (chỉ ảnh hưởng biên độ)
L_IRS_dB = 2.0                # Loss phần cứng IRS

# ❌ KHÔNG cộng G_IRS_dB nữa
# Gain IRS sẽ đến từ coherent combining khi optimize phase

# ===================================================================
# 5. THAM SỐ TỐI ƯU PHA IRS (QUAN TRỌNG)
# ===================================================================
max_iter_sca = 30             # Số vòng lặp tối ưu pha
tol_sca = 1e-4                # Ngưỡng hội tụ

sigma_channel = 0.3           # Mức fading (0 = LoS lý tưởng)

# ===================================================================
# 6. KÊNH, BLOCKAGE
# ===================================================================
apply_fading = True
K_rician_dB = 10.0
K_rician_linear = 10**(K_rician_dB / 10)
num_monte_carlo = 100

blockage_loss_dB = 30.0
blockage_elevation_threshold = 25.0

# ===================================================================
# 7. NHIỄU & NGƯỠNG
# ===================================================================
T_sys = 250.0
k_B_dBW_per_K_Hz = -228.6

CNR_threshold_dB = 20.0

# ===================================================================
# 8. HÌNH HỌC IRS
# ===================================================================
d_UI = 1.0                    # Khoảng cách UAV Tx → IRS (m)

# ===================================================================
# LOG
# ===================================================================
print("=== ĐÃ TẢI THAM SỐ UAV IRS DOWNLINK (PHASE OPTIMIZATION) ===")
print(f"EIRP: {EIRP_dBW} dBW")
print(f"Gain anten GS: {G_r_dBi} dBi")
print(f"Độ cao UAV: {h_uav} m")
print(f"Số phần tử IRS: {M}")
print("IRS gain đến từ phase alignment (không cộng tay)")
print("==========================================================")
