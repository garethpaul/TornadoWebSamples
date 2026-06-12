#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-tornado-web-samples-baseline.md"
COMET_DISPATCH_PLAN = DOCS_PLANS / "2026-06-09-comet-callback-dispatch-snapshot.md"
COMET_EXCEPTION_PLAN = DOCS_PLANS / "2026-06-09-comet-callback-exception-isolation.md"
SOCKET_EXCEPTION_PLAN = DOCS_PLANS / "2026-06-09-websocket-callback-exception-isolation.md"
CI_PLAN = DOCS_PLANS / "2026-06-10-ci-baseline.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "check.yml"


def main():
    failures = []

    if not CANONICAL_PLAN.exists():
        failures.append("docs/plans/2026-06-08-tornado-web-samples-baseline.md is missing")
    if not COMET_DISPATCH_PLAN.exists():
        failures.append("docs/plans/2026-06-09-comet-callback-dispatch-snapshot.md is missing")
    if not COMET_EXCEPTION_PLAN.exists():
        failures.append("docs/plans/2026-06-09-comet-callback-exception-isolation.md is missing")
    if not SOCKET_EXCEPTION_PLAN.exists():
        failures.append("docs/plans/2026-06-09-websocket-callback-exception-isolation.md is missing")
    if not CI_PLAN.exists():
        failures.append("docs/plans/2026-06-10-ci-baseline.md is missing")
    if not CI_WORKFLOW.exists():
        failures.append(".github/workflows/check.yml is missing")

    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.exists() else []
    if not plans:
        failures.append("docs/plans must contain at least one completed plan")

    for plan_path in plans:
        plan = plan_path.read_text(encoding="utf-8")
        if "Status: Completed" not in plan or "make check" not in plan:
            failures.append(f"{plan_path.relative_to(ROOT)} must record completed status and make check verification")

    if CI_WORKFLOW.exists():
        workflow = CI_WORKFLOW.read_text(encoding="utf-8")
        for phrase in [
            "actions/setup-python@v5",
            'python-version: "3.9"',
            "requirements.txt",
            "test-requirements.txt",
            "make check",
        ]:
            if phrase not in workflow:
                failures.append(f".github/workflows/check.yml must include {phrase}")

    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "VISION.md", "SECURITY.md"]
    )
    if "GitHub Actions" not in docs:
        failures.append("project docs must mention the GitHub Actions baseline")

    comet = (ROOT / "comet_chat" / "application.py").read_text(encoding="utf-8")
    if "def remove_callback(self, callback):" not in comet:
        failures.append("comet Messages must support removing abandoned callbacks")
    if "def on_connection_close(self):" not in comet:
        failures.append("comet MessageHandler must clean up callbacks on connection close")
    if "callbacks = self.callbacks" not in comet or "self.callbacks = [] # reset before callbacks fire" not in comet:
        failures.append("comet Messages.add must snapshot and clear callbacks before dispatch")
    if "logger.exception(\"Could not deliver comet chat message\")" not in comet:
        failures.append("comet Messages.add must log callback delivery failures")
    if "except Exception:" not in comet:
        failures.append("comet Messages.add must isolate callback delivery exceptions")

    socket = (ROOT / "socket_chat" / "application.py").read_text(encoding="utf-8")
    if "logger.exception(\"Could not deliver websocket chat message\")" not in socket:
        failures.append("socket MessageHandler.on_message must log callback delivery failures")
    if "except Exception:" not in socket:
        failures.append("socket MessageHandler.on_message must isolate callback delivery exceptions")
    if "self.callbacks.discard(cb)" not in socket:
        failures.append("socket MessageHandler.on_message must discard callbacks that fail delivery")

    if failures:
        print("Documentation plan checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Documentation plan checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
