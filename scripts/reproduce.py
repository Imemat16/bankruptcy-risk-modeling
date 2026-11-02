"""Execute the notebook in a fresh kernel; verify the frozen model against recorded results."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

import nbformat
from nbclient import NotebookClient


class ProgressNotebookClient(NotebookClient):
    """Surface fold progress while retaining complete outputs in the local report."""

    def process_message(self, msg, cell, cell_index):
        if msg.get('msg_type') == 'stream' and msg['content'].get('name') == 'stdout':
            for line in msg['content'].get('text', '').splitlines():
                if len(line) < 180 and 'fold' in line.lower():
                    print('  ' + line, flush=True)
        return super().process_message(msg, cell, cell_index)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--mode', choices=['final', 'full'], default='final')
    parser.add_argument('--kernel', default='python3')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data_dir = args.data_dir.resolve()
    manifest = json.loads((root / 'results/input_manifest.json').read_text())
    for name, record in manifest['data'].items():
        path = data_dir / name
        if not path.is_file():
            raise FileNotFoundError(f'Missing {name}; see data/README.md.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f'Input checksum differs: {name}. Reference results require the original inputs.')
    os.environ['BANKRUPTCY_DATA_DIR'] = str(data_dir)
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS']:
        os.environ[key] = '1'
    notebook = nbformat.read(root / 'notebooks/bankruptcy_risk.ipynb', as_version=4)
    if args.mode == 'final':
        notebook.cells = [c for c in notebook.cells if c.cell_type == 'code'
                          and 'final_rebuild' in c.metadata.get('tags', [])]
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    # Aggregate evidence only: never export per-company inputs, probabilities, IDs, or fitted models.
    evidence = r'''
import json, sys, platform, importlib.metadata
from pathlib import Path
assert (int(tn),int(fp),int(fn),int(tp)) == (870,32,9,53), 'Confusion matrix differs from reference'
assert int(final_cost) == 77 and int(baseline_cost) == 310
assert X_features_final.shape[1] == 59
assert len(final_base_fitted.named_steps['imputer'].indicator_.features_) == 57
assert np.isclose(proba_test.mean(), final_pipeline.predict_proba(X_test)[:,1].mean())
assert np.isclose(roc_auc_score(y_test,proba_test),0.9725877977254846,atol=5e-5)
assert np.isclose(average_precision_score(y_test,proba_test),0.857104,atol=5e-5)
assert int(overlap.sum()) == 11
payload = {
    'mode': RUN_MODE, 'verified_reference_match': True,
    'python': platform.python_version(),
    'packages': {name: importlib.metadata.version(name) for name in
        ['numpy','pandas','scipy','scikit-learn','matplotlib','nbformat','nbclient','ipykernel','threadpoolctl','joblib']},
    'train_rows':len(y_train), 'test_rows':len(y_test), 'test_bankruptcies':int(y_test.sum()),
    'train':metric_row(y_train,y_train_pred,proba_train),
    'test':metric_row(y_test,y_test_pred,proba_test),
    'baseline_cost':int(baseline_cost),
    'cost_reduction_fraction':float(1-final_cost/baseline_cost),
    'bootstrap_95_percent': {'cost_savings':bounds[:,0].tolist(),'recall':bounds[:,1].tolist()},
    'test_profile_overlap_rows':int(overlap.sum()),
    'nonoverlapping_test':metric_row(yt[~overlap],yp[~overlap],proba_test[~overlap]),
    'holdout_rows':len(X_hold),'holdout_flagged':int(np.sum(y_hold_pred)),
    'retained_financial_features':int(X_features_final.shape[1]),
    'missingness_flags':len(final_base_fitted.named_steps['imputer'].indicator_.features_),
    'threshold':float(FINAL_SPEC['threshold']),
    'full_searches_rerun':RUN_MODE == 'full'
}
Path(RESULT_PATH).write_text(json.dumps(payload,indent=2,default=lambda x:x.item())+'\n',encoding='utf-8')
print('Reference results and prediction contracts verified.')
'''
    reports = root / 'reports'
    reports.mkdir(exist_ok=True)
    result_path = reports / f'{args.mode}_metrics.json'
    notebook.cells.append(nbformat.v4.new_code_cell(
        f'RUN_MODE = {args.mode!r}\nRESULT_PATH = {str(result_path)!r}\n' + evidence))
    count = sum(c.cell_type == 'code' for c in notebook.cells)
    start = time.monotonic()
    print(f'Executing {count} code cells ({args.mode}) in a fresh kernel.', flush=True)

    def progress(cell, cell_index, **kwargs):
        if cell.cell_type == 'code':
            print(f'Cell {cell_index + 1}/{len(notebook.cells)}: {cell.source.splitlines()[0][:90]}', flush=True)

    # An empty working directory ensures execution does not rely on local notebook state.
    with tempfile.TemporaryDirectory(prefix='bankruptcy-rebuild-') as working:
        client = ProgressNotebookClient(notebook, timeout=7200, kernel_name=args.kernel,
            resources={'metadata': {'path':working}}, on_cell_start=progress)
        try:
            client.execute()
        except Exception:
            nbformat.write(notebook, reports / f'{args.mode}_failed.ipynb')
            raise
    nbformat.write(notebook, reports / f'{args.mode}_executed.ipynb')
    print(f'Passed in {time.monotonic()-start:.1f}s. Aggregate evidence: {result_path}', flush=True)


if __name__ == '__main__':
    main()
