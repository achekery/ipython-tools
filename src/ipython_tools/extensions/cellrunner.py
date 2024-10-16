"""cellrunner.py"""

import os
import tempfile

from IPython import get_ipython, InteractiveShell
from IPython.core.interactiveshell import ExecutionInfo, ExecutionResult

from loguru import logger
from loguru_config import LoguruConfig

LoguruConfig.load("loguru_config.yml")


class Cellrunner:
    _instance = None

    def __new__(cls, *ar, **kw):
        if cls._instance is None:
            cls.instance = super().__new__(cls, *ar, **kw)
        return cls.instance

    def __init__(self, ip: InteractiveShell):
        self.shell = ip
        self.sink_debug = lambda msg: print("DEBUG:cellrunner | " + msg)
        self.sink_trace = lambda msg: print("TRACE:cellrunner | " + msg)

    def pre_execute(self):
        pass

    def pre_run_cell(self, info: ExecutionInfo):
        if any(
            l.lstrip().startswith(c)
            for c in ["%", "!"]
            for l in info.raw_cell.split("\n")
        ):
            suffix = ".ipy"
        else:
            suffix = ".py"
        try:
            tempfile_name = None
            with tempfile.NamedTemporaryFile(
                mode="w+t", suffix=suffix, delete=False
            ) as fp:
                tempfile_name = fp.name
                for l in info.raw_cell.split("\n"):
                    fp.write(f"{l}\n")
            if suffix == ".py":
                self.sink_debug(("pre_run_cell:", "pytest start..."))
                cmd = f"pytest -s -vv {tempfile_name}"
                for line in self.shell.run_line_magic("sx", f'bash -xe -c "{cmd}"'):
                    self.sink_trace(line + "\n")
                self.sink_debug(("pre_run_cell:", "pytest done."))
        finally:
            os.remove(tempfile_name)

    def post_execute(self):
        pass

    def post_run_cell(self, result: ExecutionResult):
        pass


def load_ipython_extension(ip: InteractiveShell):
    ctx = Cellrunner(ip)
    ip.events.register("pre_execute", ctx.pre_execute)
    ip.events.register("pre_run_cell", ctx.pre_run_cell)
    ip.events.register("post_execute", ctx.post_execute)
    ip.events.register("post_run_cell", ctx.post_run_cell)


def unload_ipython_extension(ip: InteractiveShell):
    ctx = Cellrunner(ip)
    ip.events.unregister("pre_execute", ctx.pre_execute)
    ip.events.unregister("pre_run_cell", ctx.pre_run_cell)
    ip.events.unregister("post_execute", ctx.post_execute)
    ip.events.unregister("post_run_cell", ctx.post_run_cell)
