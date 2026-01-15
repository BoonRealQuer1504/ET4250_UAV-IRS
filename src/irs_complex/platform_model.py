"""
UAV geometry & mobility model for UAV–IRS system
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from params import (
    h_uav, T_pass, delta_t, num_points,
    v_uav, lambda_w, blockage_elevation_threshold
)

# ================================================================
# CONSTANTS
# ================================================================
GS_POS = np.array([0.0, 0.0, 0.0])  # Ground station at origin


def get_uav_geometry():
    """
    Returns:
        t                    : time (s)
        d_uav_gs             : distance UAV–GS (m)
        elevation_rad        : elevation angle (rad) – for blockage/path loss
        theta_zenith_rad     : zenith angle (rad) – for IRS array response
        azimuth_rad          : azimuth angle φ (rad)
        psi_rad              : Doppler angle ψ (rad)
        doppler_hz           : Doppler shift (Hz)
        in_service           : service mask
        los_mask             : LoS mask
    """

    # ------------------------------------------------------------
    # Time
    # ------------------------------------------------------------
    t = np.linspace(0, T_pass, num_points)

    # ------------------------------------------------------------
    # UAV trajectory (straight flight along x-axis)
    # ------------------------------------------------------------
    x_uav = v_uav * (t - T_pass / 2)
    y_uav = np.zeros_like(x_uav)
    z_uav = h_uav * np.ones_like(x_uav)

    UAV_POS = np.stack((x_uav, y_uav, z_uav), axis=1)

    # Vector from UAV to GS
    vec_UG = GS_POS - UAV_POS
    d_uav_gs = np.linalg.norm(vec_UG, axis=1)

    # ------------------------------------------------------------
    # Elevation angle θ_elev (from horizontal plane)
    # ------------------------------------------------------------
    horizontal_dist = np.sqrt(x_uav**2 + y_uav**2)
    elevation_rad = np.arctan2(z_uav, horizontal_dist)
    elevation_rad[horizontal_dist == 0] = np.pi / 2

    # ------------------------------------------------------------
    # Zenith angle θ_zenith (for IRS array response)
    # θ_zenith = π/2 − elevation
    # ------------------------------------------------------------
    theta_zenith_rad = np.pi / 2 - elevation_rad

    # ------------------------------------------------------------
    # Azimuth angle φ
    # ------------------------------------------------------------
    azimuth_rad = np.arctan2(y_uav, x_uav)
    # Note: φ jumps from π to 0 when UAV crosses GS – physically correct

    # ------------------------------------------------------------
    # Doppler modeling
    # ------------------------------------------------------------
    v_vec = np.array([v_uav, 0.0, 0.0])  # UAV velocity vector
    los_unit = vec_UG / d_uav_gs[:, None]

    cos_psi = np.dot(los_unit, v_vec) / v_uav
    cos_psi = np.clip(cos_psi, -1.0, 1.0)

    psi_rad = np.arccos(cos_psi)

    # Doppler shift
    doppler_hz = (v_uav / lambda_w) * cos_psi

    # ------------------------------------------------------------
    # Masks
    # ------------------------------------------------------------
    elevation_deg = np.degrees(elevation_rad)
    los_mask = elevation_deg >= blockage_elevation_threshold

# UAV phục vụ trong suốt hành trình
    in_service = np.ones_like(t, dtype=bool)


    return (
        t,
        d_uav_gs,
        elevation_rad,
        theta_zenith_rad,
        azimuth_rad,
        psi_rad,
        doppler_hz,
        in_service,
        los_mask
    )


# ================================================================
# VISUALIZATION (FOR REPORT)
# ================================================================
if __name__ == "__main__":

    (
        t,
        d_uav_gs,
        elevation_rad,
        theta_zenith_rad,
        azimuth_rad,
        psi_rad,
        doppler_hz,
        _,
        _
    ) = get_uav_geometry()

    os.makedirs("./report/figures2", exist_ok=True)

    # ------------------------------------------------------------
    # Elevation vs Zenith
    # ------------------------------------------------------------
    plt.figure()
    plt.plot(t / 60, np.degrees(elevation_rad), label="Elevation θ_elev")
    plt.plot(t / 60, np.degrees(theta_zenith_rad), label="Zenith θ_zenith")
    plt.xlabel("Time (minutes)")
    plt.ylabel("Angle (deg)")
    plt.title("Elevation vs Zenith Angle")
    plt.legend()
    plt.grid(True)
    plt.savefig("./report/figures2/uav_angles_elevation_zenith.png", dpi=300)
    plt.close()

    # ------------------------------------------------------------
    # Doppler shift
    # ------------------------------------------------------------
    plt.figure()
    plt.plot(t / 60, doppler_hz)
    plt.xlabel("Time (minutes)")
    plt.ylabel("Doppler shift (Hz)")
    plt.title("Doppler Shift due to UAV Mobility")
    plt.grid(True)
    plt.savefig("./report/figures2/uav_doppler_shift.png", dpi=300)
    plt.close()

    print("=== UPDATED PLATFORM MODEL FIGURES SAVED ===")
