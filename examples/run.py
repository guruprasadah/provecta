import argparse
import importlib

import uvicorn

from provecta import App

parser = argparse.ArgumentParser(description="Provecta examples runtime")
parser.add_argument("name", help="The name of the example to run.")

args = parser.parse_args()

module = importlib.import_module(f"{args.name}.home", package="examples")
app = App(module.page)

if __name__ == "__main__":
    uvicorn.run("run:app", port=5000, log_level="info")
