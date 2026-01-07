"""
LINK BUDGET UAV–IRS DOWNLINK (FINAL – PHYSICALLY CONSISTENT)

- Direct link: blockage at low elevation
- IRS link: phase-optimized, bypass blockage
- Correct power combining (linear domain)
- Coverage computed over FULL UAV pass
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.special import erfc

from params import *
from platform_model import get_uav_geometry
from irs_model import calculate_p_r_irs

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def calculate_fspl(d_m, freq_hz):
    return 20 * np.log10(d_m) + 20 * np.log10(freq_hz) - 147.55


def calculate_cnr(p_r_dbw):
    return p_r_dbw - noise_power_dbw


def ber_qpsk(cnr_db):
    cnr_lin = 10 ** (cnr_db / 10)
    return 0.5 * erfc(np.sqrt(cnr_lin))


def capacity_bps(cnr_db):
    cnr_lin = 10 ** (cnr_db / 10)
    return B * np.log2(1 + cnr_lin)


# ==========================================================
# MAIN
# ==========================================================
def main():

    os.makedirs("./report/figures2", exist_ok=True)

    # ------------------------------------------------------
    # Geometry
    # ------------------------------------------------------
    (
        t,
        d_uav_gs,
        elevation_rad,
        _,
        _,
        _,
        _,
        _,
        _
    ) = get_uav_geometry()

    elevation_deg = np.degrees(elevation_rad)
    blockage_mask = elevation_deg < blockage_elevation_threshold

    # ------------------------------------------------------
    # DIRECT LINK (WITH BLOCKAGE)
    # ------------------------------------------------------
    fspl_direct = calculate_fspl(d_uav_gs, f)

    p_r_direct_dbw = (
        EIRP_dBW
        + G_r_dBi
        - fspl_direct
        - L_total_fixed_dB
    )

    # Apply blockage loss
    p_r_direct_dbw[blockage_mask] -= blockage_loss_dB

    cnr_direct = calculate_cnr(p_r_direct_dbw)

    # ------------------------------------------------------
    # IRS LINK (PHASE OPTIMIZED – NO BLOCKAGE)
    # ------------------------------------------------------
    _, p_r_irs_dbw, _ = calculate_p_r_irs()

    # IRS only contributes in blockage region
    p_r_irs_dbw[~blockage_mask] = -np.inf

    # ------------------------------------------------------
    # POWER COMBINING (LINEAR DOMAIN)
    # ------------------------------------------------------
    

    h_direct = np.sqrt(10 ** (p_r_direct_dbw / 10))
    h_irs = np.sqrt(10 ** (np.maximum(p_r_irs_dbw, -100) / 10))
    p_total_dbw = 10 * np.log10((h_direct + h_irs)**2)
    cnr_total = calculate_cnr(p_total_dbw)

    # ------------------------------------------------------
    # COVERAGE (FULL UAV PASS)
    # ------------------------------------------------------
    coverage_direct = np.mean(cnr_direct >= CNR_threshold_dB) * 100
    coverage_total = np.mean(cnr_total >= CNR_threshold_dB) * 100

    print("\n=== COVERAGE RESULTS (PHYSICALLY CORRECT) ===")
    print(f"Direct link coverage : {coverage_direct:.2f} %")
    print(f"With IRS coverage    : {coverage_total:.2f} %")
    print(f"Coverage improvement: {coverage_total - coverage_direct:.2f} %")

    # ------------------------------------------------------
    # BER & CAPACITY
    # ------------------------------------------------------
    ber_direct = ber_qpsk(cnr_direct)
    ber_total = ber_qpsk(cnr_total)

    cap_direct = capacity_bps(cnr_direct)
    cap_total = capacity_bps(cnr_total)

    # ------------------------------------------------------
    # PLOT 1: CNR COVERAGE
    # ------------------------------------------------------
    plt.figure(figsize=(12, 7))
    plt.plot(t / 60, cnr_direct, linewidth=2, label="Direct link (blockage)")
    plt.plot(t / 60, cnr_total, linewidth=2, label="Direct + IRS")

    plt.axhline(
        y=CNR_threshold_dB,
        linestyle="--",
        label=f"CNR threshold {CNR_threshold_dB:.1f} dB"
    )

    plt.fill_between(
        t / 60,
        plt.ylim()[0],
        plt.ylim()[1],
        where=blockage_mask,
        color="gray",
        alpha=0.15,
        label="Blockage region"
    )

    plt.xlabel("Time (minutes)")
    plt.ylabel("CNR (dB)")
    plt.title("UAV–IRS Downlink Coverage (Phase Optimized IRS)")
    plt.grid(True, alpha=0.3)
    plt.legend()

    ax2 = plt.twinx()
    ax2.plot(t / 60, elevation_deg, "--", alpha=0.6)
    ax2.set_ylabel("Elevation (deg)")

    plt.savefig("./report/figures2/uav_irs_downlink_cnr_coverage.png",
                dpi=300, bbox_inches="tight")
    plt.show()

    # ------------------------------------------------------
    # PLOT 2: BER
    # ------------------------------------------------------
    plt.figure(figsize=(10, 5))
    plt.semilogy(t / 60, ber_direct, label="Direct")
    plt.semilogy(t / 60, ber_total, label="Direct + IRS")
    plt.xlabel("Time (minutes)")
    plt.ylabel("BER (QPSK)")
    plt.title("BER vs Time")
    plt.grid(True, which="both")
    plt.legend()
    plt.savefig("./report/figures2/ber_vs_time.png", dpi=300)
    plt.show()

    # ------------------------------------------------------
    # PLOT 3: CAPACITY
    # ------------------------------------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(t / 60, cap_direct / 1e6, label="Direct")
    plt.plot(t / 60, cap_total / 1e6, label="Direct + IRS")
    plt.xlabel("Time (minutes)")
    plt.ylabel("Capacity (Mbps)")
    plt.title("Capacity vs Time")
    plt.grid(True)
    plt.legend()
    plt.savefig("./report/figures2/capacity_vs_time.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
