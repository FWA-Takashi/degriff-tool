"""Defriff Excel Automation — shared backend logic.

Used by the Vercel serverless functions (api/*.py), the local launcher (run.py),
and the evaluation harness (eval/run_eval.py). Keep this package free of any
web-framework dependency so all three entry points can import it.
"""
