"""PyInstaller runtime hook — runs before ANY application code.

Layer 1 (Primary): Install stub modules for torch._numpy and all its
submodules into sys.modules.  When torch._dynamo later tries to import
torch._numpy, Python finds the stub and never loads the real module whose
``vars()[name] = ...`` loop pattern is corrupted by PyInstaller's bytecode
compiler.

Layer 1b (Secondary): Set TORCHDYNAMO_DISABLE=1 as a belt-and-suspenders
signal (on its own it does NOT prevent the crash because torch._dynamo
unconditionally imports submodules at module level before reading the var).
"""

import os
import sys
import types

# ---------------------------------------------------------------------------
# Layer 1b: env-var signal (secondary, not sufficient alone)
# ---------------------------------------------------------------------------
os.environ["TORCHDYNAMO_DISABLE"] = "1"

# ---------------------------------------------------------------------------
# Layer 1: torch._numpy stub modules
# ---------------------------------------------------------------------------


class _Dummy:
    """Catch-all dummy returned for any attribute access on stub modules.

    Must survive being placed in tuples, called, used in isinstance(),
    iterated, and bool-tested — all patterns found in torch._dynamo
    module-level code that accesses torch._numpy attributes at import time.
    """

    def __repr__(self):
        return "<pyinstaller-stub-dummy>"

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self

    def __bool__(self):
        return False

    def __iter__(self):
        return iter([])


_dummy = _Dummy()

_TORCH_NUMPY_SUBMODULES = [
    "torch._numpy",
    "torch._numpy._binary_ufuncs_impl",
    "torch._numpy._casting_dicts",
    "torch._numpy._dtypes",
    "torch._numpy._dtypes_impl",
    "torch._numpy._funcs",
    "torch._numpy._funcs_impl",
    "torch._numpy._getlimits",
    "torch._numpy._ndarray",
    "torch._numpy._normalizations",
    "torch._numpy._reductions_impl",
    "torch._numpy._ufuncs",
    "torch._numpy._unary_ufuncs_impl",
    "torch._numpy._util",
    "torch._numpy.fft",
    "torch._numpy.linalg",
    "torch._numpy.random",
    "torch._numpy.testing",
]

# Create stub modules and register them in sys.modules
_stubs = {}
for _mod_name in _TORCH_NUMPY_SUBMODULES:
    _stub = types.ModuleType(_mod_name)
    _stub.__path__ = []  # mark as package so sub-imports resolve
    _stub.__file__ = f"<pyinstaller-stub:{_mod_name}>"
    _stub.__loader__ = None
    _stub.__spec__ = None
    # Return a safe dummy for any attribute access (e.g. tnp.issubdtype,
    # tnp.ndarray) that torch._dynamo performs at module-level import time.
    _stub.__getattr__ = lambda name, _d=_dummy: _d
    _stubs[_mod_name] = _stub

# Wire parent→child attribute relationships so that e.g. ``tnp.fft``
# resolves correctly (torch/_dynamo/utils.py lines 133-135 access these).
_root = _stubs["torch._numpy"]
for _mod_name, _stub in _stubs.items():
    if _mod_name == "torch._numpy":
        continue
    _attr = _mod_name.rsplit(".", 1)[-1]
    setattr(_root, _attr, _stub)

# Install all stubs into sys.modules
sys.modules.update(_stubs)
