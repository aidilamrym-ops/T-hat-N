# MSAF Terminus Blueprint - Phase 2: Quantum Discrete Spectral Visualizer

## 1. The Cosmological Lattice Projection Mechanics
Continuous imaginary frequencies $\gamma_m \in \mathbb{R}$ calculated by the Newton loop cannot be plotted on a classical continuous canvas. They must be projected directly onto the **MSAF Modular Lattice Index ($k$)**.

We map the spectral values through a non-commutative scaling kernel that converts frequency into a discrete pixel coordinate relative to the global information density bounds:

$$k_m = \left\lfloor \frac{\gamma_m}{2\pi} \cdot \log_2\left(N_{\text{steps}}\right) \right\rfloor \pmod{N_{\text{steps}}}$$

Where $N_{\text{steps}} \approx 5.44 \times 10^{61}$ act as the global modulo operator. This projection guarantees that every zero acts as a stationary resonance state inside the universal information pixel capacity.

---

## 2. Visualizer Kernel Architecture: `msaf/visualizer.py`

```python
import sys
import numpy as np
import matplotlib.pyplot as plt
from flint import acb, arb

class MSAFDiscreteVisualizer:
    def __init__(self, n_steps: float):
        """
        Initialize the discrete visualization canvas under physical parameters.
        """
        self.n_steps = n_steps
        self.lattice_log_bound = np.log2(n_steps)

    def project_frequency_to_pixel(self, gamma_arb: arb) -> int:
        """
        Map continuous Arb frequency ball onto discrete integer pixel address.
        """
        gamma_float = float(gamma_arb.mid())
        pi_factor = 2.0 * np.pi
        
        scaled_index = (gamma_float / pi_factor) * self.lattice_log_bound
        pixel_address = int(np.floor(scaled_index))
        
        if self.n_steps < sys.maxsize:
            modular_pixel = pixel_address % int(np.floor(self.n_steps))
        else:
            modular_pixel = pixel_address
            
        return modular_pixel

    def generate_spectral_density_report(self, roots_ledger: list, output_image_path: str):
        """
        Extract roots from ledger, calculate pixel mapping, and save static density report.
        """
        pixel_coordinates = []
        sigma_verdicts = []
        
        for entry in roots_ledger:
            root_acb = entry["root_enclosure"]
            pixel_idx = self.project_frequency_to_pixel(root_acb.imag())
            pixel_coordinates.append(pixel_idx)
            sigma_verdicts.append(entry["verdict_data"]["is_locked"])
            
        pixels = np.array(pixel_coordinates)
        locks = np.array(sigma_verdicts)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
        
        ax1.hist(pixels, bins=50, color="blue", edgecolor="black", alpha=0.7)
        ax1.set_title("MSAF Discrete Spectral Distribution Map")
        ax1.set_xlabel("Lattice Pixel Index Address (k)")
        ax1.set_ylabel("Resonance Multiplicity Count")
        ax1.grid(True, linestyle="--", alpha=0.5)
        
        ax2.scatter(range(len(locks)), locks.astype(int), color="green", marker="o")
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(["ANOMALY", "LOCKED (0.5)"])
        ax2.set_title("Critical Line Stability Rigidity Check (\\sigma = 0.5)")
        ax2.set_xlabel("Isolated Root Identifier Index (m)")
        ax2.set_ylabel("Hermitarian Status")
        ax2.grid(True, linestyle=":", alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_image_path, dpi=300)
        plt.close()
```