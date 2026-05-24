import re
from git import Repo

def get_changed_lines():
    # Atver Git repozitoriju
    repo = Repo("../httpx")

    # Iegūst pēdējo un iepriekšējo commit
    commit = repo.head.commit
    parent = commit.parents[0]

    # Iegūst detalizētas izmaiņas starp commitiem, ieskaitot mainītās rindiņas
    diffs = parent.diff(commit, create_patch=True)

    result = {}

    for diff in diffs:
        lines = []

        # Parsē patch, meklē pievienotās rindiņas (+) un to numurus
        current_line = 0
        for line in diff.diff.decode().splitlines():
            if re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)", line):
                current_line = int(re.search(r"\+(\d+)", line).group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                lines.append(current_line)
                current_line += 1
            elif not line.startswith("-") and not line.startswith("\\"):
                current_line += 1

        result[diff.b_path] = lines

    return result
