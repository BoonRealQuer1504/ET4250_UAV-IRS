"""
IRS model cho UAV-IRS downlink
- Double path loss: UAV → IRS → GS
- IRS gain sinh ra từ phase alignment (KHÔNG cộng tay)
"""
import os
import numpy as np
from params import (
    f, EIRP_dBW, L_total_fixed_dB, d_UI,
    M, sigma_channel
)
from platform_model import get_uav_geometry

# ============================================================
# FSPL
# ============================================================
def calculate_fspl(d_m, freq_hz):
    d_km = d_m / 1000.0
    f_MHz = freq_hz / 1e6
    return 20 * np.log10(d_km) + 20 * np.log10(f_MHz) + 32.44


# ============================================================
# IRS PHASE OPTIMIZATION (CLOSED-FORM – LoS dominant)
# ============================================================
def optimize_phase_los(h_ui, h_ig):
    """
    Optimal IRS phase for coherent combining:
    theta_m = -angle(h_ig_m * h_ui_m)
    """
    return np.exp(-1j * np.angle(h_ig * h_ui))


# ============================================================
# IRS RECEIVED POWER
# ============================================================
def calculate_p_r_irs():
    t, d_uav_gs, d_IG, elevation_deg, d_horizontal, in_service, los_mask = \
        get_uav_geometry()

    # ----------------------------
    # Path loss
    # ----------------------------
    fspl_ui = calculate_fspl(d_UI, f)
    fspl_ig = calculate_fspl(d_IG, f)

    p_r_base_dbw = (
        EIRP_dBW
        - fspl_ui
        - fspl_ig
        - L_total_fixed_dB
    )

    # ----------------------------
    # IRS channel + phase gain
    # ----------------------------
    p_r_irs_dbw = np.zeros_like(p_r_base_dbw)

    for i in range(len(t)):
        # Channel UAV → IRS
        h_ui = (1 + sigma_channel *
                (np.random.randn(M) + 1j * np.random.randn(M))) / np.sqrt(2)

        # Channel IRS → GS
        h_ig = (1 + sigma_channel *
                (np.random.randn(M) + 1j * np.random.randn(M))) / np.sqrt(2)

        # Optimal phase (closed-form)
        theta = optimize_phase_los(h_ui, h_ig)

        # Effective channel
        h_eff = np.sum(h_ig * theta * h_ui)

        irs_gain_db = 10 * np.log10(np.abs(h_eff)**2)

        p_r_irs_dbw[i] = p_r_base_dbw[i] + irs_gain_db

    # IRS chỉ hoạt động trong vùng phục vụ
    p_r_irs_dbw[~in_service] = -np.inf

    return t, p_r_irs_dbw, elevation_deg, in_service


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    t, p_r_irs_dbw, elevation_deg, _ = calculate_p_r_irs()

    print("=== KIỂM TRA IRS MODEL (PHASE OPTIMIZED) ===")
    print(f"P_r IRS max: {np.max(p_r_irs_dbw[np.isfinite(p_r_irs_dbw)]):.1f} dBW")
    print(f"P_r IRS min: {np.min(p_r_irs_dbw[np.isfinite(p_r_irs_dbw)]):.1f} dBW")

    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(t/60, p_r_irs_dbw)
    plt.xlabel("Time (min)")
    plt.ylabel("P_r_IRS (dBW)")
    plt.title("IRS received power with phase optimization")
    plt.grid(True)
    
    os.makedirs('./report/figures1', exist_ok=True)
    plt.savefig('./report/figures1/irs_power.png', dpi=300)
    print("Đã lưu đồ thị kiểm tra vào ../report/figures1/irs_power.png")
    plt.show()
