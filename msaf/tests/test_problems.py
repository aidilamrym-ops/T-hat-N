import pathlib, subprocess

def test_problem_files():
    base = pathlib.Path(__file__).resolve().parents[2] / "problems"
    for md in base.rglob("*.md"):
        txt = md.read_text(encoding="utf-8")
        assert "# Problem" in txt, f"{md} missing header"
        assert "## Statement" in txt, f"{md} missing statement"

def test_problem_lean():
    base = pathlib.Path(__file__).resolve().parents[2] / "problems"
    for lean_dir in base.rglob("lean"):
        lakefile = lean_dir / "lakefile.toml"
        if not lakefile.is_file():
            continue  # skip folders without lake configuration
        result = subprocess.run(["lake", "build"], cwd=str(lean_dir), capture_output=True, text=True)
        assert result.returncode == 0, f"{lean_dir} build fail: {result.stderr}"

