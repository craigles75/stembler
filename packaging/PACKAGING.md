# Stembler Packaging Documentation

This document covers the macOS and Windows packaging process, known issues, and their solutions.

## macOS Packaging

### Build Commands

```bash
# Build the .app bundle
./packaging/macos/build.sh

# Create DMG installer
./packaging/macos/build_dmg.sh
```

### Architecture Overview

- **PyInstaller** compiles Python to a standalone `.app` bundle
- **BUNDLE step** creates proper macOS app structure (`Contents/MacOS/`, `Contents/Frameworks/`, etc.)
- **Runtime hook** (`runtime_hook.py`) runs before any application code
- **Static ffmpeg/ffprobe** binaries are bundled for audio file reading

---

## Known PyInstaller Issues and Solutions

### 1. "name 'name' is not defined" Error

**Symptom:** App crashes during stem separation with `NameError: name 'name' is not defined`

**Root Cause:** PyInstaller's bytecode compiler corrupts certain dynamic code patterns. The error occurs in `torch/_numpy/_ufuncs.py` lines 233-235 and 329-331:

```python
for name in _binary:
    ufunc = getattr(_binary_ufuncs_impl, name)
    vars()[name] = deco_binary_ufunc(ufunc)  # crashes here
```

This standard Python pattern (iterating and dynamically creating module variables) doesn't survive PyInstaller's bytecode compilation. The loop variable `name` isn't available when `vars()[name]` runs in compiled bytecode.

**Import Chain That Triggers It:**
```
demucs/htdemucs.py forward()
  -> einops.rearrange()
    -> einops._torch_specific (allow_ops_in_compiled_graph at module level)
      -> torch._dynamo (line 13: unconditional `from . import ...`)
        -> torch._dynamo.utils (line 116: import torch._numpy as tnp)
          -> torch._numpy._ufuncs -> CRASH
```

**Why TORCHDYNAMO_DISABLE alone doesn't work:** `torch/_dynamo/__init__.py` line 13 is an unconditional `from . import config, convert_frame, eval_frame...` statement. The env var is only checked later in `eval_frame.py` functions, long after the import chain has already triggered the crash.

**Solution: Three-Layer Defense**

**Layer 1 (Primary) — Runtime Module Stubs** (`runtime_hook.py`):
Pre-populate `sys.modules` with stub `types.ModuleType` objects for `torch._numpy` and all 17 submodules. When `torch._dynamo.utils` later executes `import torch._numpy as tnp`, Python finds the stub in `sys.modules` and never imports the real module. The bytecode-corrupted `_ufuncs.py` is never executed.

```python
import sys, types
for mod_name in ["torch._numpy", "torch._numpy._ufuncs", ...]:
    stub = types.ModuleType(mod_name)
    stub.__path__ = []
    sys.modules[mod_name] = stub
```

Safety: `torch._numpy` is only used by `torch._dynamo` internals for numpy-to-torch tracing in `torch.compile()`, which demucs never uses.

**Layer 2 (Backup) — Build-Time Source Patching** (`build.sh`):
Before PyInstaller runs, the build script patches `torch/_numpy/_ufuncs.py` to replace the `vars()[name]` loop patterns with `globals().update()` dict comprehensions that survive bytecode compilation. The original file is restored after the build.

**Layer 3 — Spec Excludes** (`stembler.spec`):
All `torch._numpy` submodules are added to the `excludes` list. Since Layer 1 provides stubs, the real modules aren't needed in the bundle.

Also keeps `TORCHDYNAMO_DISABLE=1` as a secondary signal in the runtime hook.

---

### 2. scipy Import Crash

**Symptom:** App crashes at startup with `NameError` in `scipy/stats/_distn_infrastructure.py`

**Root Cause:** Similar PyInstaller bytecode bug affecting scipy's statistics module. The import chain `scipy.signal` -> `scipy.stats` triggers the crash.

**Solution:** Made scipy import lazy in `stem_processor.py`. Instead of importing at module level, import inside the method that uses it:

```python
# Before (crashes in PyInstaller):
from scipy import signal

# After (works in PyInstaller):
def enhance_audio_quality(self, audio_data):
    from scipy import signal  # Lazy import
    sos = signal.butter(...)
```

---

### 3. Duplicate GUI Spawns on "Separate Stems"

**Symptom:** Clicking "Separate Stems" opens a second copy of the app

**Root Cause:** The original code used subprocess to run demucs:

```python
cmd = [sys.executable, "-m", "demucs.separate", ...]
subprocess.run(cmd)
```

In a PyInstaller bundle, `sys.executable` points to the bundled app itself (`Stembler`), not the Python interpreter. So this literally runs `Stembler -m demucs.separate`, launching another GUI instance.

**Solution:** Call demucs as a Python library instead of subprocess:

```python
from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import save_audio

model = get_model(model_name)
sources = apply_model(model, wav, device=device)
save_audio(source, path, samplerate)
```

---

### 4. ffprobe Not Found / SIGABRT Crash

**Symptom:** Either "ffprobe not found" error, or ffprobe crashes with SIGABRT

**Root Cause:**
- demucs/torchaudio uses ffprobe to read audio files
- Homebrew ffprobe has 30+ dynamic library dependencies that aren't in the bundle
- Even if ffprobe is found, it crashes because its dylib dependencies are missing

**Solution:** Bundle static ffmpeg/ffprobe builds that only depend on system frameworks:

1. Download static builds from https://evermeet.cx/ffmpeg/
2. Place in `packaging/macos/bin/`
3. Add to PyInstaller spec as binaries
4. Set PATH in launcher to include bundled bin directory

```python
# In launcher.py
if getattr(sys, "frozen", False):
    bundle_bin = Path(sys._MEIPASS) / "bin"
    os.environ["PATH"] = str(bundle_bin) + os.pathsep + os.environ.get("PATH", "")
```

---

### 5. DMG App Won't Launch (libpython not found)

**Symptom:** App passes Gatekeeper verification but nothing happens

**Root Cause:** PyInstaller's bootloader looks for `libpython` in `Contents/Frameworks/` when running from a `.app` bundle. If you manually create the `.app` structure (copying from `dist/Stembler/` to `dist/Stembler.app/Contents/MacOS/`), the library paths are wrong.

**Solution:** Use PyInstaller's BUNDLE step (not manual `.app` creation). The BUNDLE step correctly places libraries and sets up paths:

```python
# In stembler.spec
app = BUNDLE(
    coll,
    name='Stembler.app',
    ...
)
```

---

## File Structure

```
packaging/
  macos/
    bin/
      ffmpeg          # Static binary (80MB)
      ffprobe         # Static binary (80MB)
    build.sh          # Main build script
    build_dmg.sh      # DMG creation script
    launcher.py       # PyInstaller entry point
    runtime_hook.py   # Pre-import environment setup
    stembler.spec     # PyInstaller specification
    icon.icns         # macOS app icon
  windows/
    launcher.py
    runtime_hook.py   # Pre-import environment setup (same as macOS)
    stembler.spec
    icon.ico
```

## Debugging Tips

1. **Check logs:** `~/Library/Logs/Stembler/stembler_*.log` contains full tracebacks
2. **Test bundle directly:** Run `dist/Stembler.app/Contents/MacOS/Stembler` from terminal to see stdout/stderr
3. **Compare dev vs bundle:** If it works with `uv run` but not in bundle, it's likely a PyInstaller-specific issue
4. **Search for bytecode bugs:** Patterns like `vars()`, `locals()`, and certain loop constructs often break in PyInstaller
