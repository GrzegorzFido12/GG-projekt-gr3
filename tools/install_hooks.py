import os
import sys
import stat

def install_hooks():
    hooks_dir = os.path.join('.git', 'hooks')
    
    if not os.path.exists(hooks_dir):
        print("❌ Error: .git directory not found. Initialize git first.")
        sys.exit(1)

    # 1. Define the commands
    # We use 'sys.executable' to ensure we use the active python environment (venv)
    python_cmd = sys.executable
    script_name = "tools/obfuscate_g5.py" 

    # Pre-commit: Curse the file, then add the cursed version to staging
    pre_commit_content = f"""#!/bin/sh
echo "💀 Cursing files before commit..."
"{python_cmd}" "{script_name}" curse
git add .
"""

    # Post-commit: Bless the file back to normal immediately
    post_commit_content = f"""#!/bin/sh
echo "✨ Blessing files after commit..."
"{python_cmd}" "{script_name}" bless
"""

    # 2. Write the files
    create_hook(os.path.join(hooks_dir, 'pre-commit'), pre_commit_content)
    create_hook(os.path.join(hooks_dir, 'post-commit'), post_commit_content)
    
    print("✅ Git hooks installed! Your code will now auto-obfuscate on commit.")

def create_hook(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
    # Make the file executable (chmod +x equivalent)
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)
    print(f"   - Created {path}")

if __name__ == "__main__":
    install_hooks()