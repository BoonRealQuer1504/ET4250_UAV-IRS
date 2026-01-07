"""
Tính link budget UAV IRS downlink (PHIÊN BẢN CHUẨN)
- Direct link: có blockage ở low elevation
- IRS link: phase optimized, bypass blockage
- Power combining đúng vật lý
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from params import *
from platform_model import get_uav_geometry
from irs_model import calculate_p_r_irs

# ==============================================================
# HÀM CHUNG
# ==============================================================
def calculate_fspl(d_m, freq_hz):
    return 20 * np.log10(d_m / 1000) + 20 * np.log10(freq_hz / 1e6) + 32.44

def calculate_cnr(p_r_dbw):
    noise_dbw = k_B_dBW_per_K_Hz + 10 * np.log10(T_sys) + 10 * np.log10(B)
    return p_r_dbw - noise_dbw

def apply_rician_fading(p_r_dbw, n_points):
    if not apply_fading:
        return p_r_dbw

    from scipy.stats import rice

    K = K_rician_linear
    sigma = np.sqrt(1 / (2 * (K + 1)))
    v = np.sqrt(K / (K + 1))
    b = v / sigma

    fading_mc = []
    for _ in range(num_monte_carlo):
        h = rice.rvs(b, scale=sigma, size=n_points)
        fading_mc.append(10 * np.log10(h**2))

    return p_r_dbw + np.mean(fading_mc, axis=0)

# ==============================================================
# MAIN SIMULATION
# ==============================================================
if __name__ == "__main__":

    # ----------------------------------------------------------
    # Geometry
    # ----------------------------------------------------------
    t, d_uav_gs, d_IG, elevation_deg, d_horizontal, in_service, los_mask = get_uav_geometry()

    # ----------------------------------------------------------
    # DIRECT LINK (có blockage)
    # ----------------------------------------------------------
    fspl_direct = calculate_fspl(d_uav_gs, f)
    p_r_direct_dbw = (
        EIRP_dBW
        + G_r_dBi
        - fspl_direct
        - L_total_fixed_dB
    )

    # Blockage ở low elevation
    blockage_loss = np.zeros_like(elevation_deg)
    blockage_loss[elevation_deg < blockage_elevation_threshold] = blockage_loss_dB
    p_r_direct_dbw -= blockage_loss

    # Fading
    p_r_direct_dbw = apply_rician_fading(p_r_direct_dbw, len(t))
    cnr_direct = calculate_cnr(p_r_direct_dbw)
    coverage_direct = np.mean(cnr_direct >= CNR_threshold_dB) * 100

    # ----------------------------------------------------------
    # IRS LINK (phase optimized – KHÔNG blockage)
    # ----------------------------------------------------------
    _, p_r_irs_dbw, _, _ = calculate_p_r_irs()

    # IRS chỉ hỗ trợ khi direct bị yếu (low elevation)
    p_r_irs_dbw[elevation_deg >= blockage_elevation_threshold] = -np.inf

    # ----------------------------------------------------------
    # POWER COMBINING (non-coherent)
    # ----------------------------------------------------------
    p_total_lin = (
        10 ** (p_r_direct_dbw / 10) +
        10 ** (p_r_irs_dbw / 10)
    )
    p_total_dbw = 10 * np.log10(p_total_lin)

    cnr_total = calculate_cnr(p_total_dbw)
    coverage_irs = np.mean(cnr_total >= CNR_threshold_dB) * 100

    # ----------------------------------------------------------
    # KẾT QUẢ
    # ----------------------------------------------------------
    print("\n=== KẾT QUẢ LINK BUDGET UAV IRS DOWNLINK (PHASE OPT) ===")
    print(f"Không IRS: Coverage ≥ {CNR_threshold_dB:.1f} dB = {coverage_direct:.1f}%")
    print(f"Có IRS:    Coverage ≥ {CNR_threshold_dB:.1f} dB = {coverage_irs:.1f}%")
    print(f"Cải thiện coverage: +{coverage_irs - coverage_direct:.1f}%")

    # ----------------------------------------------------------
    # PLOT
    # ----------------------------------------------------------
    plt.figure(figsize=(12, 7))
    plt.plot(t / 60, cnr_direct, 'g-', linewidth=2,
             label='Direct link (blockage)')
    plt.plot(t / 60, cnr_total, 'r-', linewidth=2,
             label='Direct + IRS (phase optimized)')

    plt.axhline(
        y=CNR_threshold_dB,
        linestyle='--',
        linewidth=1.5,
        label=f'CNR threshold {CNR_threshold_dB:.1f} dB'
    )

    plt.xlabel('Time (minutes)')
    plt.ylabel('CNR (dB)')
    plt.title('UAV IRS Downlink – Phase Optimized IRS Bypassing Blockage')
    plt.grid(True, alpha=0.3)

    # Vùng blockage
    plt.fill_between(
        t / 60,
        plt.ylim()[0],
        plt.ylim()[1],
        where=elevation_deg < blockage_elevation_threshold,
        color='gray',
        alpha=0.15,
        label='Blockage region (ε < 30°)'
    )

    plt.legend(loc='upper right')

    # Elevation trục phụ
    ax2 = plt.twinx()
    ax2.plot(t / 60, elevation_deg, 'b--', linewidth=1.2, alpha=0.6)
    ax2.set_ylabel('Elevation (deg)', color='b')
    ax2.tick_params(axis='y', labelcolor='b')

    # Save figure
    os.makedirs('./report/figures1', exist_ok=True)
    save_path = './report/figures1/uav_irs_final_result_new.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Đã lưu hình: {save_path}")

    plt.show()
