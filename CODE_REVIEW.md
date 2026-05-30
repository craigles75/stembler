# Code Review — Music Stem Separator

Scope: full read of `src/music_stem_separator/*`, tests, config, and docs.
Overall: the architecture is clean and modular, with clear single-responsibility
modules and a readable pipeline in `cli.py:process_track`. The main risks are a
broken secondary entry point, a test suite that no longer matches the implementation,
and several robustness/security gaps in the I/O paths.

## Summary by severity

| Sev | Count | Themes |
|-----|-------|--------|
| Critical | 3 | broken entry point, stale/broken tests, ignored Spotify settings |
| High | 4 | hardcoded stems, no subprocess timeout, incomplete cleanup, metadata points at temp files |
| Security | 3 | SSRF/unbounded download, credential handling, temp paths |
| Medium | ~11 | dict-return pattern, dead code, enhancement applied to all stems, docs drift |

---

## Critical

### C1. Broken `stem-separator-ui` entry point
`pyproject.toml:33` declares `stem-separator-ui = "music_stem_separator.gradio_ui:main"`,
but `src/music_stem_separator/gradio_ui.py` does not exist, and `gradio` is not a
dependency. The console script installs but fails at runtime with `ModuleNotFoundError`.
**Fix:** remove the entry point (and any UI claims) or add the `gradio_ui` module + the
`gradio` dependency.

### C2. Test suite is stale and broken against the current implementation
The docs claim "test-driven development with 80%+ coverage", but key tests patch APIs
the code no longer uses, so they error or assert against dead paths:
- `tests/test_separator.py:37,53` patch `music_stem_separator.separator.demucs.api.separate`.
  `separator.py` no longer imports `demucs.api` — it shells out via
  `subprocess.run([... "-m", "demucs.separate" ...])` (`separator.py:81-97`). The patch
  target doesn't exist, so these tests fail at setup.
- `tests/test_spotify_handler.py:79` sets `mock_spotdl.download.return_value = [".../song.mp3"]`
  and never mocks `spotdl.search`. Current code calls `spotdl.search([...])` then
  `song, downloaded_file = spotdl.download(song)` (tuple unpack, `spotify_handler.py:137-142`),
  so the test does not exercise the real path and would not pass as written.
**Fix:** rewrite these tests against the subprocess/search+download reality, then run
`uv run pytest` in CI so drift is caught.

### C3. Spotify `output_format` / `quality` are silently ignored
`SpotifyHandler.__init__` builds `self.settings` with `output_format` and `bitrate`
(`spotify_handler.py:44-48`), but `download_track` constructs a *new*
`downloader_settings` dict containing only `audio_providers` and `filter_results`
(`spotify_handler.py:126-134`). The configured format/quality never reach `Spotdl`.
**Fix:** pass `output_format`/`bitrate` through to `Spotdl`, or drop the unused params.

---

## High

### H1. Hardcoded stem names — wrong for non-4-stem models
`StemSeparator.STEM_NAMES = ["drums","bass","vocals","other"]` and
`get_stem_paths` (`separator.py:119-142`) always expect exactly those four `.wav`
files. `htdemucs_6s` produces 6 stems (adds piano/guitar) and 2-stem models differ, so
files are silently missed. `verify_stems_exist` exists (`separator.py:144`) but is never
called, so `separate_stems` reports success even if Demucs wrote nothing matching.
**Fix:** discover stems by globbing the model output dir, and verify expected files
exist before returning success.

### H2. No timeout on the Demucs subprocess
`subprocess.run(cmd, capture_output=True, text=True)` (`separator.py:97`) has no
`timeout`. A hung/very long job blocks forever, contradicting the stated "<2 min/song"
goal. **Fix:** add a `timeout=` and handle `subprocess.TimeoutExpired`.

### H3. Incomplete temp-file cleanup
`cli.py:236-241` only removes the downloaded *input* file. The working directories
`{output}/temp`, `{output}/temp_stems`, and `{output}/temp_processed` are never cleaned,
so every run leaves behind full-size intermediate WAVs.
**Fix:** clean up all temp dirs in a `finally` block (use `tempfile.TemporaryDirectory`
or explicit `shutil.rmtree`).

### H4. Metadata/report reference temp paths, not final outputs
`organize_stem_files` copies stems into the track's `stems/` dir, but the metadata and
summary are generated from `separation_result["stems"]` (`cli.py:217-228`), which still
points at `temp_processed/temp_stems`. After cleanup those paths would be invalid.
**Fix:** thread `organization_result["organized_files"]` into metadata/report.

---

## Security

### S1. SSRF / unbounded download in `URLDownloader`
`download_file`/`is_audio_url`/`get_file_info` (`url_downloader.py`) issue HEAD/GET to
any user-supplied URL with no host allowlist, no blocking of `localhost`/private/link-local
IPs, and no maximum size — the streamed download writes until the server stops
(`url_downloader.py:149-158`). On a server this is an SSRF vector and a disk-exhaustion
risk. **Fix:** validate/resolve the host and reject private ranges, cap `content-length`
and bytes written, and restrict schemes to http/https.

### S2. Credential handling
Real Spotify credentials live in `.env` (present locally). Good: `.env` is gitignored
and **not** tracked, and `git log` shows it was never committed. Recommend documenting
key rotation and keeping the "never commit `.env`" guarantee in CI (e.g., a secret scan).

### S3. Predictable temp output location
Spotify/URL inputs default to `/tmp/music_stem_separator` with fixed names
(`input_processor.py:223,227`; `url_downloader.py:129-131`). Low risk on a single-user
CLI, but predictable shared-tmp paths invite clobbering on multi-user hosts. Prefer
`tempfile.mkdtemp()`.

---

## Medium / Maintainability

- **M1. Dict-based `{success, error}` returns everywhere** instead of exceptions force
  callers to check every result and discard tracebacks. Consider a small exception
  hierarchy for the pipeline; keep dicts only at the CLI boundary.
- **M2. README "Option 2: `source .env`" is misleading** (`README.md:60-61`). Plain
  `KEY=value` lines aren't exported, so the `uv run` child process won't see them.
  Options 1 (`--env-file`) and 3 (inline) work; fix or drop option 2.
- **M3. No automatic `.env` loading** — docs center on `.env` but nothing calls
  `load_dotenv`. Either add `python-dotenv` + `load_dotenv()` or document only the
  working invocation methods.
- **M4. Dead/untested API surface**: `batch_download`, `get_track_metadata`,
  `get_download_path`, `get_file_size_info`, `validate_output_files`,
  `verify_stems_exist`, `get_available_models`. Remove or wire in + test.
- **M5. Enhancement applied to all stems**: pre-emphasis + 8 kHz high-pass boost
  (`stem_processor.py:180-190`) is applied uniformly, including bass/drums, likely
  degrading low-frequency stems. Make it per-stem or off by default for bass/drums.
- **M6. `enhancement_applied` is not a bool**: `enable_enhancement and processing_results
  and processing_results["success"]` (`cli.py:248-250`) can evaluate to `None`/dict.
  Wrap in `bool(...)`.
- **M7. Duplicated Spotify URL/track-id logic** in `spotify_handler.py` and
  `input_processor.py` (`_is_spotify_url`, `_extract_spotify_track_id`). Centralize.
- **M8. Inconsistent format lists**: `StemProcessor.get_processing_settings` reports a
  different set (`stem_processor.py:365`) than the canonical `SUPPORTED_FORMATS`.
- **M9. Broad `except Exception` + generic `raise Exception(...)`** throughout obscure
  root causes; prefer specific exceptions and let unexpected ones surface.
- **M10. `.DS_Store` not gitignored** (currently untracked noise). Add it.
- **M11. Stale docs**: `CLAUDE.md` says the project is "in early planning/setup phase",
  but it is fully implemented. Update `CLAUDE.md`/`PROJECT_OVERVIEW.md`/`TODO.md`.

---

## What's good
- Clear modular separation (input → separate → process → organize → report).
- Defensive validation in `InputProcessor` and `OutputManager._sanitize_filename`.
- Sensible audio handling: float WAV output, fade in/out, peak normalization, finite-data
  validation (`stem_processor.py`).
- Robust HTTP session with retry/backoff in `URLDownloader`.
- Credentials are correctly kept out of git.

## Recommended priority order
1. C1 entry point, C2 tests (+ run in CI), C3 Spotify settings.
2. H1 dynamic stems, H2 timeout, H3 cleanup, H4 metadata paths.
3. S1 download guards.
4. Medium maintainability items as capacity allows.
