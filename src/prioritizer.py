import json, os

def get_prioritized_tests(changed_lines: dict, coverage_path: str) -> list:
    # Nolasa coverage.json failu
    data = json.load(open(coverage_path))

    scores = {}

    for test_id, files in data.items():
        score = 0

        # Katram failam ko tests pārklāj, saskaita sakritušās rindiņas
        for file_path, covered_lines in files.items():
            if file_path in changed_lines:
                score += len(set(covered_lines) & set(changed_lines[file_path]))

        scores[test_id] = score

    # Sakārto testus dilstošā secībā pēc score
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
