import subprocess
from pathlib import Path

def get_project_root():
    return Path(__file__).parent.parent.parent

def run_git_command(args, cwd=None):
    if cwd is None:
        cwd = get_project_root()
        
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8" # Force utf-8 for Windows
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: git {' '.join(args)}")
        print(f"   Error: {e.stderr}")
        return False, e.stderr

def git_add(file_path):
    root = get_project_root()
    # file_path should be relative to root or absolute
    # If absolute, make it relative
    if Path(file_path).is_absolute():
        try:
            rel_path = Path(file_path).relative_to(root)
            file_path = str(rel_path)
        except ValueError:
            print(f"⚠️  File {file_path} is not in the project root {root}")
            return False

    print(f"➕ Git Add: {file_path}")
    return run_git_command(["add", str(file_path)])

def git_commit(message):
    print(f"💾 Git Commit: {message}")
    return run_git_command(["commit", "-m", message])

def git_push():
    print("🚀 Git Push...")
    return run_git_command(["push"])

def commit_and_push_changes(file_path, message, push=False):
    """
    Stages, commits, and optionally pushes changes to a file.
    """
    success, _ = git_add(file_path)
    if not success:
        return False
        
    # Check if there are changes to commit
    success, status = run_git_command(["status", "--porcelain"])
    if not status.strip():
        print("ℹ️  No changes to commit.")
        return True
        
    success, _ = git_commit(message)
    if not success:
        return False
        
    if push:
        success, _ = git_push()
        return success
        
    return True
