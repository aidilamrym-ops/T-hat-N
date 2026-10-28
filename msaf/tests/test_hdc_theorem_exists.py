import subprocess, pathlib

def test_hdc_theorem_exists():
    """Run `lake build` in the Lean directory and ensure no errors for HDC theorem stub."""
    lean_dir = pathlib.Path(__file__).resolve().parents[2] / "lean"
    result = subprocess.run(["lake", "build"], cwd=str(lean_dir), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


