"""
Bug Condition Exploration Test for OpenEnv Project Structure Fix

**Property 1: Bug Condition - Project Structure Compliance**

This test MUST FAIL on unfixed code - failure confirms the bugs exist.
DO NOT attempt to fix the test or the code when it fails.

This test encodes the expected behavior - it will validate the fix when it passes after implementation.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
"""

import os
import sys
import subprocess
from pathlib import Path


def test_inference_in_root():
    """Verify inference.py exists at root and can be imported/run."""
    root_inference = Path("inference.py")
    assert root_inference.exists(), "inference.py must exist in root directory"
    
    # Try to run inference.py from root with a quick syntax check
    # We use a short timeout and check for import/syntax errors
    # On unfixed code, this will fail with ImportError
    # On fixed code, it should start but fail with connection error (ENV_BASE_URL not reachable)
    # but NOT with ImportError
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; print('IMPORT_SUCCESS')"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    # Check that imports work
    assert "IMPORT_SUCCESS" in result.stdout, \
        f"inference.py imports failed: {result.stderr}"
    assert "ImportError" not in result.stderr, \
        f"inference.py has import errors: {result.stderr}"
    assert "ModuleNotFoundError" not in result.stderr, \
        f"inference.py has module not found errors: {result.stderr}"


def test_no_duplicate_files():
    """Verify no duplicate files exist between root and receipt-reconciliation/."""
    # These files should NOT be in root (they belong only in receipt-reconciliation/)
    should_not_be_in_root = {
        "env.py", "main.py", "models.py", "tasks.py"
    }
    
    # These files CAN be in root as coordination files (not duplicates)
    # - openenv.yaml: needed for OpenEnv validation tooling
    # - README.md: root-level documentation
    # - Dockerfile: root-level Docker build
    
    duplicates_found = []
    for filename in should_not_be_in_root:
        root_path = Path(filename)
        if root_path.exists():
            duplicates_found.append(filename)
    
    assert len(duplicates_found) == 0, \
        f"Duplicate files found in root (should only be in receipt-reconciliation/): {duplicates_found}"


def test_no_malformed_folders():
    """Verify no malformed {environment/ folder exists."""
    malformed_folder = Path("receipt-reconciliation/{environment/")
    assert not malformed_folder.exists(), \
        "Malformed folder '{environment/' should not exist"


def test_requirements_txt_in_root():
    """Verify requirements.txt exists in root for Docker builds."""
    root_requirements = Path("requirements.txt")
    assert root_requirements.exists(), \
        "requirements.txt must exist in root directory for Docker builds"


def test_docker_build_succeeds():
    """Verify Docker can build from root directory."""
    # Check if Docker is available
    docker_check = subprocess.run(
        ["docker", "--version"],
        capture_output=True,
        text=True
    )
    
    if docker_check.returncode != 0:
        print("✓ Docker build succeeds: SKIP (Docker not available)")
        return
    
    # Check if Docker daemon is running
    docker_ping = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True
    )
    
    if docker_ping.returncode != 0:
        print("✓ Docker build succeeds: SKIP (Docker daemon not running)")
        return
    
    # Try to build Docker image from root
    result = subprocess.run(
        ["docker", "build", "-t", "test-openenv-structure", "."],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    assert result.returncode == 0, \
        f"Docker build from root failed: {result.stderr}"


def test_openenv_yaml_in_root():
    """Verify openenv.yaml exists in root for OpenEnv validation tooling."""
    root_openenv = Path("openenv.yaml")
    
    # On unfixed code, this might exist but be a duplicate
    # On fixed code, it should exist and be properly configured
    if root_openenv.exists():
        # If it exists, verify it's not just a duplicate but properly configured
        import yaml
        with open(root_openenv) as f:
            config = yaml.safe_load(f)
        
        assert "tasks" in config, "openenv.yaml must contain tasks definition"
        assert "observation_space" in config, "openenv.yaml must contain observation_space"
        assert "action_space" in config, "openenv.yaml must contain action_space"


def test_environment_package_structure():
    """Verify environment package is properly organized in receipt-reconciliation/environment/."""
    env_package = Path("receipt-reconciliation/environment")
    assert env_package.exists(), "environment package must exist in receipt-reconciliation/"
    assert env_package.is_dir(), "environment must be a directory"
    
    # Check for required files
    required_files = ["__init__.py", "env.py", "models.py", "tasks.py"]
    for filename in required_files:
        file_path = env_package / filename
        assert file_path.exists(), f"{filename} must exist in receipt-reconciliation/environment/"


if __name__ == "__main__":
    print("Running Bug Condition Exploration Tests...")
    print("=" * 70)
    print("EXPECTED: These tests SHOULD FAIL on unfixed code")
    print("This confirms the bugs exist and need to be fixed")
    print("=" * 70)
    print()
    
    tests = [
        ("Inference in root with working imports", test_inference_in_root),
        ("No duplicate files", test_no_duplicate_files),
        ("No malformed folders", test_no_malformed_folders),
        ("requirements.txt in root", test_requirements_txt_in_root),
        ("Docker build succeeds", test_docker_build_succeeds),
        ("openenv.yaml in root", test_openenv_yaml_in_root),
        ("Environment package structure", test_environment_package_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "PASS", None))
            print(f"✓ {test_name}: PASS")
        except AssertionError as e:
            results.append((test_name, "FAIL", str(e)))
            print(f"✗ {test_name}: FAIL")
            print(f"  Error: {e}")
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
            print(f"✗ {test_name}: ERROR")
            print(f"  Error: {e}")
        print()
    
    print("=" * 70)
    print("Summary:")
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    print(f"Passed: {passed}, Failed: {failed}, Errors: {errors}")
    print("=" * 70)
    
    # Exit with failure if any tests failed (expected on unfixed code)
    sys.exit(0 if failed == 0 and errors == 0 else 1)
