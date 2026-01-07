"""
Mô hình quỹ đạo UAV bay ngang qua trạm mặt đất (GS)
- UAV bay thẳng với vận tốc cố định
- Tính khoảng cách và góc ngẩng theo thời gian
- d_IG(t) = sqrt(h_uav^2 + d_horizontal(t)^2) – đúng hình học Pythagoras
- Giới hạn vùng phục vụ (d_max) để tránh pass vô hạn
- Trả thêm LOS mask (elevation >= blockage_threshold)
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from params import h_uav, T_pass, delta_t, num_points, blockage_elevation_threshold

# ===================================================================
# Vận tốc UAV ngang – đưa lên đầu file để tránh lỗi scope
# ===================================================================
v_uav = 20.0  # m/s ≈ 72 km/h – tốc độ điển hình UAV (có thể chỉnh 10–30 m/s)

# Giới hạn vùng phục vụ (bán kính cell)
d_max_horizontal = 2000.0  # m – ngoài vùng này coi như outage

def get_uav_geometry():
    """
    Trả về:
        t: thời gian (giây)
        d_uav_gs: khoảng cách UAV → GS (m)
        d_IG: khoảng cách IRS (trên UAV) → GS (m)
        elevation_deg: góc ngẩng (độ)
        d_horizontal: khoảng cách ngang (m)
        in_service: mask vùng phục vụ (True nếu trong cell)
        los_mask: mask LoS (elevation >= blockage_threshold)
    """
    t = np.linspace(0, T_pass, num_points)

    # Khoảng cách ngang từ UAV đến điểm ngay trên GS
    # UAV ở giữa pass (t = T_pass/2) là overhead
    d_horizontal = np.abs(v_uav * (t - T_pass / 2))

    # Giới hạn vùng phục vụ
    in_service = d_horizontal <= d_max_horizontal

    # Khoảng cách slant range UAV → GS (và IRS → GS vì IRS trên UAV)
    d_uav_gs = np.sqrt(h_uav**2 + d_horizontal**2)
    d_IG = d_uav_gs  # Đúng hình học – IRS trên UAV

    # Góc ngẩng
    elevation_rad = np.arctan2(h_uav, d_horizontal)
    elevation_deg = np.degrees(elevation_rad)
    elevation_deg[d_horizontal == 0] = 90.0  # Overhead

    # LOS mask (không bị blockage khi elevation cao)
    los_mask = elevation_deg >= blockage_elevation_threshold

    return t, d_uav_gs, d_IG, elevation_deg, d_horizontal, in_service, los_mask

# ===================================================================
# Test nhanh khi chạy file trực tiếp
# ===================================================================
if __name__ == "__main__":
    t, d_uav_gs, d_IG, elevation_deg, d_horizontal, in_service, los_mask = get_uav_geometry()

    print("=== KIỂM TRA MÔ HÌNH UAV (SỬA HÌNH HỌC) ===")
    print(f"Số điểm: {len(t)}")
    print(f"Độ cao UAV: {h_uav} m")
    print(f"Vận tốc UAV ngang: {v_uav} m/s")
    print(f"Bán kính vùng phục vụ: {d_max_horizontal} m")
    print(f"Khoảng cách tối thiểu (overhead): {d_IG.min():.0f} m")
    print(f"Khoảng cách tối đa (rìa cell): {d_IG.max():.0f} m")
    print(f"Góc ngẩng tối đa: {elevation_deg.max():.1f}°")
    print(f"Góc ngẩng tối thiểu (rìa): {elevation_deg.min():.1f}°")

    # Vẽ đồ thị kiểm tra
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(t/60, elevation_deg, 'b-', linewidth=2)
    plt.axhline(y=blockage_elevation_threshold, color='k', linestyle='--', label=f'Ngưỡng blockage ({blockage_elevation_threshold}°)')
    plt.title('Góc ngẩng (Elevation) theo thời gian')
    plt.ylabel('Elevation (độ)')
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(t/60, d_IG, 'r-', linewidth=2)
    plt.title('Khoảng cách IRS → GS (d_IG(t))')
    plt.ylabel('Khoảng cách (m)')
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(t/60, d_horizontal, 'g-', linewidth=2)
    plt.axvline(x=t[in_service][0]/60, color='gray', linestyle=':', alpha=0.7)
    plt.axvline(x=t[in_service][-1]/60, color='gray', linestyle=':', alpha=0.7)
    plt.title('Khoảng cách ngang UAV → GS và vùng phục vụ')
    plt.xlabel('Thời gian (phút)')
    plt.ylabel('Khoảng cách ngang (m)')
    plt.grid(True)

    plt.tight_layout()

    os.makedirs('./report/figures1', exist_ok=True)
    plt.savefig('./report/figures1/uav_geometry_final.png', dpi=300)
    print("Đã lưu đồ thị kiểm tra vào ../report/figures1/uav_geometry_final.png")
    plt.show()