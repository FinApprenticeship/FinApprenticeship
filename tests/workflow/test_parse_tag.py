import subprocess

def run_script(*args):
    return subprocess.run(
        ["./scripts/workflow/parse-tag.sh", *args],
        capture_output=True, text=True
    )

def test_parse_tag_with_stage():
    result = run_script("streamlit-beta-v1.0.0")
    assert result.returncode == 0, "Check that the script succeeds when the tag is valid"
    assert "artifact=streamlit" in result.stdout, "Check that the script extracts the artifact"
    assert "artifact_capitalized=Streamlit" in result.stdout, "Check that the script capitalizes the artifact"
    assert "stage=beta" in result.stdout, "Check that the script extracts the stage"
    assert "version=1.0.0" in result.stdout, "Check that the script extracts the version"
    assert "tag_name=streamlit-beta-v1.0.0" in result.stdout, "Check that the script returns the tag name"

def test_parse_tag_without_stage():
    result = subprocess.run(
        ["./scripts/workflow/parse-tag.sh", "streamlit-v1.0.0"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, "Check that the script succeeds when the tag is valid"
    assert "artifact=streamlit" in result.stdout, "Check that the script extracts the artifact"
    assert "artifact_capitalized=Streamlit" in result.stdout, "Check that the script capitalizes the artifact"
    assert "stage=main" in result.stdout, "Check that the script sets the stage to main when no stage is provided"
    assert "version=1.0.0" in result.stdout, "Check that the script extracts the version"
    assert "tag_name=streamlit-v1.0.0" in result.stdout, "Check that the script returns the tag name"

def test_parse_tag_no_argument():
    result = run_script()
    assert result.returncode == 1, "Check that the script fails when no argument is passed"

def test_parse_tag_help():
    result = run_script("-h")
    assert result.returncode == 0, "Check that the script succeeds when -h is passed"
    assert "Usage" in result.stdout, "Check that the script prints the help message when -h is passed"

def test_parse_tag_no_dash():
    result = run_script("no_dash")
    assert result.returncode != 0, "Check that the script fails when the tag does not contain a dash"

def test_parse_tag_starts_with_dash():
    result = run_script("-dash_at_start")
    assert result.returncode != 0, "Check that the script fails when the tag starts with a dash"

def test_parse_tag_ends_with_dash():
    result = run_script("dash_at_end-")
    assert result.returncode != 0, "Check that the script fails when the tag ends with a dash"

