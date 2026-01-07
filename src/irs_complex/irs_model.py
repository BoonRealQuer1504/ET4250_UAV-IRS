"""
irs_model.py
Final IRS model for UAV–IRS downlink
- Double path loss (UAV → IRS → GS)
- Separate AoA / AoD
- Doppler-aware geometric channel
- Alternating Optimization (AO)
- Plot & save figures for report
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from params import (
    f, lambda_w, d_IRS,
    M, Mx, My,
    EIRP_dBW, L_total_fixed_dB,
    MAX_ITER_AO, TOLERANCE,
    d_UI
)

from platform_model import get_uav_geometry


# ==========================================================
# FSPL (dB)
# ==========================================================
def calculate_fspl(d_m, freq_hz):
    return 20 * np.log10(d_m) + 20 * np.log10(freq_hz) - 147.55


# ==========================================================
# UPA Steering Vector
# ==========================================================
def get_steering_vector(theta, phi):
    """
    theta : zenith angle (rad)
    phi   : azimuth angle (rad)
    """
    k = 2 * np.pi / lambda_w

    ax = np.exp(1j * k * d_IRS *
                np.arange(Mx) * np.sin(theta) * np.cos(phi))
    ay = np.exp(1j * k * d_IRS *
                np.arange(My) * np.sin(theta) * np.sin(phi))

    a = np.kron(ax, ay)
    return a / np.sqrt(M)


# ==========================================================
# IRS Channel + AO Optimization
# ==========================================================
def calculate_p_r_irs():

    (
        t,
        d_IG,
        _,
        theta_zenith,
        azimuth,
        _,
        doppler,
        in_service,
        _
    ) = get_uav_geometry()

    num_t = len(t)
    p_r_irs_dbw = np.full(num_t, -np.inf)
    converge_history = []

    # ------------------------------------------------------
    # Fixed UAV → IRS geometry (AoA)
    # ------------------------------------------------------
    theta_ui = 0.0
    phi_ui = 0.0
    a_ui = get_steering_vector(theta_ui, phi_ui)

    fspl_ui = calculate_fspl(d_UI, f)

    # ------------------------------------------------------
    # Loop over time
    # ------------------------------------------------------
    for ti in range(num_t):

        if not in_service[ti]:
            continue

        # IRS → GS geometry (AoD)
        theta_ig = theta_zenith[ti]
        phi_ig = azimuth[ti]
        a_ig = get_steering_vector(theta_ig, phi_ig)

        fspl_ig = calculate_fspl(d_IG[ti], f)
        fspl_total = fspl_ui + fspl_ig

        # Doppler phase
        doppler_phase = np.exp(
            1j * 2 * np.pi * doppler[ti] * t[ti]
        )

        # Initialize IRS phase
        theta_irs = np.exp(1j * 2 * np.pi * np.random.rand(M))
        prev_gain = 0.0

        # --------------------------------------------------
        # Alternating Optimization
        # --------------------------------------------------
        for it in range(MAX_ITER_AO):

            # Phase update (AO step)
            theta_irs = np.exp(
                1j * np.angle(np.conj(a_ig) * a_ui)
            )

            # Effective cascaded channel
            h_eff = np.vdot(a_ig, theta_irs * a_ui) * doppler_phase
            gain = np.abs(h_eff) ** 2
            converge_history.append(gain)

            if np.abs(gain - prev_gain) < TOLERANCE:
                break
            prev_gain = gain

        # --------------------------------------------------
        # Received power via IRS
        # --------------------------------------------------
        p_r_irs_dbw[ti] = (
            EIRP_dBW
            - fspl_total
            - L_total_fixed_dB
            + 10 * np.log10(gain)
        )

    return t, p_r_irs_dbw, converge_history


# ==========================================================
# MAIN TEST + PLOTS
# ==========================================================
if __name__ == "__main__":

    os.makedirs("./report/figures2", exist_ok=True)

    t, p_r_irs_dbw, converge = calculate_p_r_irs()

    # ------------------------------------------------------
    # Plot 1: AO Convergence
    # ------------------------------------------------------
    plt.figure(figsize=(8, 5))
    plt.plot(10 * np.log10(converge), linewidth=2)
    plt.xlabel("AO Iteration")
    plt.ylabel("IRS Gain (dB)")
    plt.title("Convergence of IRS Phase Optimization (AO)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./report/figures2/irs_ao_convergence.png", dpi=300)
    plt.show()

    # ------------------------------------------------------
    # Plot 2: IRS Received Power vs Time
    # ------------------------------------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(t / 60, p_r_irs_dbw, linewidth=2)
    plt.xlabel("Time (minutes)")
    plt.ylabel("IRS Received Power (dBW)")
    plt.title("IRS-Assisted Received Power vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./report/figures2/irs_received_power_vs_time.png", dpi=300)
    plt.show()

    print("=== IRS MODEL COMPLETED ===")
    print("Saved figures:")
    print(" - irs_ao_convergence.png")
    print(" - irs_received_power_vs_time.png")
