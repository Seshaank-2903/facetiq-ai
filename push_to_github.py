"""Helper script to push FacetIQ project to GitHub without requiring native git.exe installed.

Usage:
  d:\Ahoum\facet-scoring-system\.venv\Scripts\python.exe push_to_github.py --token <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>
"""

import sys
import os
import argparse
from dulwich.repo import Repo
from dulwich import porcelain

def push_to_github(token=None, username=None):
    repo_path = r"d:\Ahoum\facet-scoring-system"
    if not os.path.exists(os.path.join(repo_path, ".git")):
        repo_path = os.path.dirname(os.path.abspath(__file__))
    
    repo = Repo(repo_path)

    # Construct Remote URL
    if token:
        user = username or "token"
        remote_url = f"https://{user}:{token}@github.com/Seshaank-2903/facetiq-ai.git"
    else:
        remote_url = "https://github.com/Seshaank-2903/facetiq-ai.git"

    # Set HEAD ref to refs/heads/main
    repo.refs[b"refs/heads/main"] = repo.head()

    print(f"[Git Helper] Pushing commit {repo.head().decode('ascii')[:8]} to {remote_url.split('@')[-1]} (main branch)...")

    try:
        porcelain.push(repo, remote_location=remote_url, refspecs=b"refs/heads/main:refs/heads/main")
        print("\n[SUCCESS] Successfully pushed FacetIQ project to https://github.com/Seshaank-2903/facetiq-ai.git !")
    except Exception as e:
        print("\n[Error] Push failed:", str(e))
        if "No valid credentials" in str(e) or "401" in str(e) or "403" in str(e):
            print("\nGitHub authentication required.")
            print("Please pass your GitHub Personal Access Token using:")
            print("  python push_to_github.py --token <YOUR_GITHUB_TOKEN>")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push repository to GitHub.")
    parser.add_argument("--token", "-t", type=str, help="GitHub Personal Access Token (PAT)")
    parser.add_argument("--username", "-u", type=str, help="GitHub username")
    args = parser.parse_args()

    token_val = args.token or os.environ.get("GITHUB_TOKEN")
    push_to_github(token=token_val, username=args.username)
