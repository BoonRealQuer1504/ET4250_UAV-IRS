"""
Tham số hệ thống UAV mang IRS hỗ trợ downlink
Phiên bản FINAL:
- Geometric IRS channel (array response, theta/phi)
- Mobility & Doppler (time-selective fading)
- BER, capacity, optimization-ready
- Physical Layer + Optimization
"""

import numpy as np

# ===================================================================
# 1. UAV & TIME PARAMETERS
# ===================================================================
h_uav = 300.0                 # UAV altitude (m)
T_pass = 600                  # UAV pass duration (s)
delta_t = 1.0                 # Trajectory update step (s)
num_points = int(T_pass / delta_t) + 1

# ===================================================================
# 2. CARRIER & BANDWIDTH
# ===================================================================
f = 10e9                      # Carrier frequency (10 GHz)
c = 3e8
lambda_w = c / f              # Wavelength (≈ 0.03 m)

B = 50e6                      # Bandwidth (50 MHz)

# ===================================================================
# 3. IRS CONFIGURATION (GEOMETRIC MODEL)
# ===================================================================
M = 1024                      # Total IRS elements
Mx = 32                       # Rows
My = 32                       # Columns
assert Mx * My == M, "Mx * My must equal M"

d_IRS = lambda_w / 2          # Element spacing (half-wavelength)

# IRS hardware characteristics
eta_IRS = 0.9                 # Reflection efficiency (amplitude)
L_IRS_dB = 2.0                # IRS hardware loss (dB)

# ===================================================================
# 4. MOBILITY & DOPPLER
# ===================================================================
v_uav = 20.0                  # UAV horizontal speed (m/s)

# Maximum Doppler shift (upper bound)
# f_d,max = v / lambda
f_doppler_max = v_uav / lambda_w
# At 10 GHz & 20 m/s -> ~ 666 Hz (fast time-varying channel)

# ===================================================================
# 5. NOISE POWER (PHYSICAL CALCULATION)
# ===================================================================
T_sys = 290.0                 # System noise temperature (K)
k_B = 1.380649e-23            # Boltzmann constant (J/K)
Noise_Figure_dB = 5.0         # Receiver noise figure (dB)

# Thermal noise power
noise_power_watts = k_B * T_sys * B * (10 ** (Noise_Figure_dB / 10))
noise_power_dbw = 10 * np.log10(noise_power_watts)

# ===================================================================
# 6. CHANNEL MODEL PARAMETERS
# ===================================================================
# Rician fading (LoS-dominant UAV channel)
K_rician_dB = 10.0
K_rician_linear = 10 ** (K_rician_dB / 10)

# ===================================================================
# 7. TRANSMIT / RECEIVE PARAMETERS
# ===================================================================
EIRP_dBW = 25.0               # UAV EIRP (effective transmit power)
G_r_dBi = 15.0                # Ground station antenna gain

# Optional path-loss exponents (for extended models)
alpha_LoS = 2.0
alpha_NLoS = 3.5

# Fixed losses (polarization, atmosphere, pointing, etc.)
L_total_fixed_dB = 5.0

# ===================================================================
# 8. BLOCKAGE & GEOMETRY
# ===================================================================
blockage_loss_dB = 30.0
blockage_elevation_threshold = 25.0  # degrees

# UAV Tx -> IRS distance
# Assumed FAR-FIELD to justify array-response model
d_UI = 5.0                    # meters

# ===================================================================
# 9. MODULATION, BER & OPTIMIZATION METRICS
# ===================================================================
# Modulation: QPSK
MOD_ORDER = 4
BITS_PER_SYMBOL = int(np.log2(MOD_ORDER))

# Coverage threshold (metric only, not optimization objective)
CNR_threshold_dB = 20.0

# ===================================================================
# 10. OPTIMIZATION PARAMETERS (AO / SCA)
# ===================================================================
MAX_ITER_AO = 20              # Max iterations for AO/SCA
TOLERANCE = 1e-3              # Convergence tolerance

# ===================================================================
# LOGGING (for quick verification)
# ===================================================================
if __name__ == "__main__":
    print("=== UAV - IRS SYSTEM PARAMETERS (FINAL) ===")
    print(f"Carrier frequency : {f/1e9:.2f} GHz")
    print(f"Wavelength        : {lambda_w*1000:.1f} mm")
    print(f"Bandwidth         : {B/1e6:.1f} MHz")
    print(f"IRS configuration : {Mx} x {My} ({M} elements)")
    print(f"IRS spacing       : {d_IRS:.3f} m")
    print(f"UAV speed         : {v_uav:.1f} m/s")
    print(f"Max Doppler shift : {f_doppler_max:.1f} Hz")
    print(f"Noise power       : {noise_power_dbw:.2f} dBW")
    print(f"Rician K-factor   : {K_rician_dB:.1f} dB")
    print(f"AO iterations     : {MAX_ITER_AO}")
    print("========================================")
