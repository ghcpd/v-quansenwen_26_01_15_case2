from .config import load_config
from .workflow import WorkflowEngine


def run_workflow(path: str) -> dict:
    """Run workflow and return a summary."""
    config = load_config(path)
    engine = WorkflowEngine(config)
    results = engine.run()
    ok = all(item.get("ok") for item in results)
    return {
        "name": config.get("name", "workflow"),
        "status": "ok" if ok else "failed",
        "results": results,
    }
