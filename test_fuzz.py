import random
import copy
from pprint import pprint
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "evaluator" / "src"))
from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.constants import CORE_GATES

from main.stress_test_ablation import generate_bad_hypotheses

res = evaluate_bundle(Path("main/output/real_multi_task/ioi_v0_gpt2-small"))
fams = generate_bad_hypotheses(res, 20)
for k, v in fams.items():
    print(k, len(v), sum(1 for x in v if x is None))
