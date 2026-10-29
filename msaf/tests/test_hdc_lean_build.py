import subprocess
import pathlib

def test_lean_hdc_build():
    """Run lake build on lean/HDC_Orthogonality.lean and ensure success."""
    root = pathlib.Path(__file__).resolve().parents[2]
    lean_dir = root / "lean"
    result = subprocess.run(["lake", "build"], cwd=str(lean_dir), capture_output=True, text=True)
    assert result.returncode == 0, f"Lake build failed: {result.stderr}"


