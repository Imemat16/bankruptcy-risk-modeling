"""Check publishable project integrity without requiring private inputs."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import nbformat


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root/'results/input_manifest.json').read_text())
    included_inputs = set()
    for name, record in manifest['data'].items():
        path = root/'data'/name
        assert path.is_file(), f'Missing included input: {name}'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], f'Input changed: {name}'
        with path.open(newline='', encoding='utf-8-sig') as handle:
            rows = list(csv.reader(handle))
        expected = (4818, 68) if name == 'train/companies.csv' else (1092, 67)
        assert (len(rows)-1, len(rows[0])) == expected, f'Unexpected dimensions: {name}'
        assert all(len(row) == expected[1] for row in rows), f'Ragged CSV: {name}'
        assert 'Id' in rows[0]
        assert ('Bankrupt' in rows[0]) == (name == 'train/companies.csv')
        included_inputs.add(path.relative_to(root).as_posix())
    notebook = nbformat.read(root/'notebooks/bankruptcy_risk.ipynb', as_version=4)
    nbformat.validate(notebook)
    code_cells = [c for c in notebook.cells if c.cell_type == 'code']
    for cell in code_cells:
        source = '\n'.join(line for line in cell.source.splitlines() if not line.lstrip().startswith('%'))
        ast.parse(source)
        assert not any(o.output_type == 'error' for o in cell.outputs), cell.id
    rebuild = [c for c in code_cells if 'final_rebuild' in c.metadata.get('tags', [])]
    assert len(rebuild) == 16, f'Unexpected rebuild route: {len(rebuild)}'
    for path in (root/'scripts').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    metrics_path = root/'results/verified_metrics.json'
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
        test = metrics['test']
        assert test['Cost'] == 5*test['FN']+test['FP'] == 77
        assert sum(test[k] for k in ['TN','FP','FN','TP']) == metrics['test_rows'] == 964
        assert metrics['baseline_cost'] == 310
        assert abs(test['Recall']-53/62) < 1e-12
        assert abs(test['Precision']-53/85) < 1e-12
        assert metrics['verified_reference_match'] is True
        full_path = root/'results/full_replay_metrics.json'
        if full_path.exists():
            full = json.loads(full_path.read_text())
            assert full['mode'] == 'full' and full['full_searches_rerun'] is True
            assert full['verified_reference_match'] is True
            for key, value in test.items():
                assert abs(full['test'][key]-value) < 1e-12, f'Rebuild/replay disagreement: {key}'
    # Inspect intended release files, excluding explicitly local output and Git metadata.
    forbidden = [r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY',
                 r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                 r'AKIA[A-Z0-9]{16}', r'(?i)[A-Z]:[\\/]+Users[\\/]',
                 r'(?i)YOUR CODE HERE|called for grading|we grade|Submission guidelines',
                 r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}']
    issues = []
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if not path.is_file() or any(p in {'.git','reports','.venv','__pycache__'} for p in rel.parts):
            continue
        if path.suffix in {'.csv','.xlsx','.parquet','.pkl','.joblib','.zip'} and rel.as_posix() not in included_inputs:
            issues.append(f'Private/binary artifact in release tree: {rel}')
        if path.suffix in {'.md','.py','.json','.ipynb','.txt','.yml','.csv'}:
            # Pattern literals in this scanner are not actual sensitive content.
            if path.name == 'check_project.py':
                continue
            text = path.read_text(encoding='utf-8')
            for pattern in forbidden:
                if re.search(pattern, text):
                    issues.append(f'Content review required: {rel} ({pattern})')
    assert not issues, '\n'.join(issues)
    print(f'Passed: valid notebook, {len(code_cells)} parseable code cells, 16-cell rebuild route, '
          'metric arithmetic, included input hashes/schema, and release-content scan. Model execution is a separate check.')


if __name__ == '__main__':
    main()
