# Benchmark: managing the Darkest Theme page

How quickly Fanta's live MCP server handles the Adobe Spectrum kit, and in particular its **Darkest Theme** page, where every component used in the Photoshop screen lives.

Raw results: [results.json](results.json). Script: [../tools/bench.py](../tools/bench.py).

## Setup

- Apple M3 Max, 36 GB memory, macOS 27.
- Fanta **debug build** (`target/debug/fanta`), with the project open and the live MCP server on.
- Client: `tools/fanta.py`, newline-delimited JSON-RPC over Fanta's Unix socket. Times are wall-clock round trips measured in the client, so they include the socket and JSON encoding.
- Each operation ran 3 or 5 times (see `runs`). The table reports the median, with min and max.

## Scale

| | |
| --- | --- |
| Darkest Theme page | **8,470 nodes** |
| Whole document | **74,076 nodes**, 24 pages |
| Components | **9,012** |
| Darkest page `page.fnx` | 6,764,511 bytes: 1,281 `Frame`, 773 `Text`, 649 `Instance`, 377 `Vector`, 312 `Rect`, 16 `Ellipse` |
| Darkest page tree walked (instances not expanded) | 4,449 nodes |
| Component masters found on the Darkest page | 1,042 |

The page listing counts 8,470 nodes, including the content of component masters. The walk stops at component masters and instances, so it visits 4,449.

## Results

| Operation | What it does | Median | Min | Max |
| --- | --- | --- | --- | --- |
| `get_editor_state` | Summary of the whole 74,076-node document | 26.7 ms | 15.9 ms | 129.9 ms |
| `batch_get` page 8, depth 1 | List the Darkest page's top level | 0.3 ms | 0.3 ms | 0.9 ms |
| `batch_get` page 8, depth 3 | List three levels of the Darkest page | 10.7 ms | 8.8 ms | 11.7 ms |
| Tree walk | Breadth-first `batch_get` of 150 ids per call over the Darkest page, matching component roots: 4,449 nodes, 1,042 masters, 34 calls | **95.1 ms** | 92.3 ms | 98.7 ms |
| `get_design_system`, all pages | Page through all 9,012 components, 200 at a time | 193.8 ms | 192.2 ms | 195.9 ms |
| `get_screenshot` page 8, 1024 px | Render all 8,470 nodes | 594.6 ms | 556.3 ms | 713.1 ms |
| `get_screenshot` page 8, 2048 px | Render all 8,470 nodes | 553.2 ms | 550.5 ms | 563.3 ms |
| `get_screenshot` Photoshop page, 1920 px | Render the 150-node screen | 859.5 ms | 826.5 ms | 987.8 ms |
| `validate_fnx_source` | Validate the Photoshop page source | 12.4 s | 11.5 s | 94.6 s |

## Reading the numbers

- **Reads are fast at this scale.** Finding every Darkest Theme master took under 100 ms, and summarizing the whole 74k-node document takes about 27 ms.
- **Rendering is under a second.** The 1920 px Photoshop screen takes longer than the full Darkest page at 2048 px. Its full-resolution artwork image is the likely reason.
- **Validation is the bottleneck.** Validating one page re-materializes the whole project to check that the page resolves against all 9,012 components. One of five runs took 94.6 s, probably while the app was busy reloading.
- **Debug build.** All numbers come from an unoptimized build, so a release build should be faster across the board.

## Reproduce

With this project open in Fanta and its live MCP server enabled:

```bash
python3 tools/bench.py
```

It overwrites `benchmark/results.json`.
