"""Entry point shim — delegates to src/__main__.py."""
import runpy

if __name__ == "__main__":
    runpy.run_module("src", run_name="__main__", alter_sys=True)
