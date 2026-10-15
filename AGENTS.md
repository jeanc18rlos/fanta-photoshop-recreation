# Working on this Fanta design project

This directory is a Fanta *design project*: a Figma-class design stored as
editable source files. **The design is the source of truth.** Editing these
files edits the design. When this project is open in the editor, saving your
edits to the `.fnx` files update the canvas about 300 ms later, and edits made
on the canvas save back to these same files. So working here as a text agent
*is* the design-to-canvas loop — no export step.

If Fanta is running with this project open you also have a more direct route: a
live MCP server that reads and edits the focused canvas. Prefer reading and
editing the actual project source files for building and changing designs.
Use the live canvas tools to inspect progress, check screenshots, and perform
operations that require editor state. Try available tools before claiming
missing access. Read *Driving the open canvas over MCP* below and call
`get_guidelines` before designing.

## Safe FNX edits

Read `fanta.md` for this project’s product, visual direction, layout and acceptance
criteria. Preserve customized specifications. Inspect the live `get_design_system`
tool for existing components, variable collections, modes, values and bindings.
Build semantic foundation variables before components; compose repeated UI from
instances. Variables live in `doc/variables.json`, document mode pins in
`doc/active_modes.json`; preserve their existing ids and value schema.

Use explicit auto-layout sizing/alignment: button labels can hug unwrapped text
inside padded, min-constrained aligned frames; card paragraphs should auto-height
at their assigned width. Do not compensate for container errors with manual
child-coordinate nudges. Verify wrapping and alignment at representative sizes.

FNX is JSX with JSON attribute values. Every object key inside `{{...}}` must
be double quoted, including nested objects: `style={{"size_px": 16, "weight": 400}}`.
Do not use JavaScript object syntax with unquoted keys. Read the existing source
and types before editing. Save only complete documents with balanced tags and
complete JSON values. Build large designs through small, complete frame or
component edits; do not stream a whole large page in one tool response.
Parser diagnostics are repair instructions: correct the candidate and retry,
without force-saving an incomplete draft. Native and ACP file tools validate
managed FNX before saving; external file agents can call `validate_fnx_source`
with a complete candidate before writing it.

## Directory layout

```
fanta.json                       # project manifest (format tag, versions, ids) — do not hand-edit
fnx.d.ts                         # project-local FNX tag and property types for editor tooling
.prettierrc.json                 # FNX-safe Prettier defaults; user-editable
doc/
  metadata.json                  # title + timestamps
  variables.json                 # design variables / tokens and their modes
  active_modes.json              # which mode is active per variable collection
  motion.json                    # animation clips, tracks, and keyframes
  flow_start.json                # prototype start page (or null)
  flows.json                     # named prototype starting points
  presentation.json              # prototype device and surround color
pages/<page-slug>/
  page.json                      # { "id": "n_…", "name": ..., "order": N }
  page.fnx                       # the page's node tree as readable source  <- edit this
  page.ids.json                  # legacy id/order sidecar kept in sync  — do not hand-edit
components/<component-slug>/     # a component without variants
  def.json                       # component definition (id, root, name)  — do not hand-edit
  master.fnx                     # the component master's tree as source    <- edit this
  master.ids.json                # legacy id/order sidecar kept in sync  — do not hand-edit
components/<set-slug>/           # a component WITH variants: one folder
  set.json                       # its axes, values and default variant    — do not hand-edit
  <variant-slug>/                # one per variant, named by its values (primary-hover)
    def.json                     # the variant's definition               — do not hand-edit
    master.fnx                   # the variant master's tree as source      <- edit this
    master.ids.json              # legacy id/order sidecar kept in sync  — do not hand-edit
assets/index.json                # asset sizes and full SHA-256 digests
assets/<family>/<AssetId>.<ext>  # shared binary assets, one folder per family:
                                 #   images/ video/ audio/ models/ svg/ fonts/ other/
previews/  exports/              # generated output — git-ignored, never an input
```

A component with variants (a component set) is ONE folder: never create a
top-level `components/<slug>/` per variant. Variants are made, added, removed
and renamed with the canvas ops (`combine_variants`, `add_variants`,
`remove_variant`, `rename_component`), and the app places their folders.

Directory names under `pages/` and `components/` are human-readable slugs of
the design's name (two pages named the same get `-2`, `-3` suffixes). The
design's *identity* lives in the JSON header and root source element: `page.json`'s
`"id"`, `def.json`'s `id`, and the root element's bare ULID must identify the
same node. Renaming the folder is
not how you rename a page — edit the root element's `name` attribute and the
app re-derives the folder name on the next save.

Pages name the components they instance (`<Instance component="Button">`), so
renaming a component in `def.json` breaks every page that names it and the
whole project stops loading. Rename components, and build or change variant
sets, with the canvas ops below (`rename_component`, `combine_variants`,
`add_variants`, `remove_variant`, `arrange_variants`); the app then rewrites
`def.json`, `set.json` and every page that names the component together.

## The `.fnx` language

A `.fnx` file is the readable, JSX/TSX-style projection of one page or component
subtree. It opens with `// @generated fanta source …` — treat it as generated
source you may edit, not as a file to reformat. Each scene node is one JSX
element:

- The **tag** is the node kind: `Frame` (group/frame), `Vector` (shape),
  `Text`, `Image`, `Video`, `Audio`, `Model3D`, `NodeGraph`, `AiArtifact`,
  `Instance` (a component instance), `Embed`. Two **authoring shorthands**
  also parse: `<Rect width={100} height={50} …/>` and
  `<Ellipse width={64} height={64} …/>` — each is sugar for a `<Vector>` with
  the equivalent generated `path`, and simple shapes print back in the sugar
  form. Give a sugar tag `width`/`height` (required) plus any normal vector
  attributes (`fills`, `strokes`, `corner_radius`, `x`, `y`, …); do not give
  it an explicit `path`.
- **Attributes** are the node's fields, verbatim. String attributes render as
  `name="Header"`; everything else renders inside braces, e.g. `opacity={1.0}`,
  `x={280.0}`, `corner_radius={2.0}`. Nesting is by hierarchy: an element's
  children are its child nodes, in render (z) order.
- **Colors** render through `fnxColor("#RRGGBB")`, or an eight-digit hex when
  not fully opaque (e.g. `fnxColor("#FFFFFF1A")`).
- **Components by name**: `<Instance component="Button" />` references the
  component named "Button" (a bare 26-character id is also always accepted).
  If two components share a name, the id form is required — the app prints
  ids for ambiguous names.
- **Design tokens by path**: variable bindings accept `$Collection/Name`
  paths and a readable map form:
  `bindings={{"fill_color": "$Theme/bg", "text_style": "$Type/Heading"}}`.
  The tokens themselves are defined in `doc/variables.json`.
- A typo in an attribute name, component name, or token path fails with a
  `line:column` error and a suggestion — a `.fnx` that loads has resolved
  every reference.

A short real snippet:

```jsx
<Frame id="00000000000000000000000001" background={{"kind": "solid", "color": fnxColor("#444444")}} blend_mode="normal"
       corner_radius={2.0} name="Header" opacity={1.0} x={-734.0} y={-491.0}>
  <Text id="00000000000000000000000002" align="left" content="Little Lemon" name="Title" opacity={1.0}
        style={{"font_family": "Inter", "size_px": 64.0, "weight": 700, "color": fnxColor("#1E1E1E")}}
        x={275.0} y={146.0} />
</Frame>
```

Common attributes: `name`, `x`/`y` (position, see below), `opacity`,
`blend_mode`, `background`/`fills`/`strokes` (paints, with colors as hex),
`corner_radius`, `clip_size`, `content` and `style` (Text), `path` (Vector),
`auto_layout` (auto-layout frames), `meta` (source metadata like
`figma_type`/`figma_id`). Component instances carry `component` (the master's
id), `overrides` (per-instance changes such as swapped text or colors),
`prop_values`, and `derived`/`local_size` (solver-computed geometry).

### Coordinates

`x`/`y` are the node's translation in pixels relative to its parent (they are
the pure-translation part of the node's transform). Change them to move a node;
change `clip_size` / `local_size` to resize. You may also write `width={…}`
`height={…}`: on load they fold into `clip_size` on a `Frame` and into
`local_size` on every other sized tag, and an explicit `clip_size`/`local_size`
already on the element wins over the sugar. The one exception is `Vector`, whose
`local_size` is the SVG-viewport *clip* rather than the shape's geometry —
`width`/`height` on a `<Vector>` are ignored, so resize a vector by editing its
`path`, or author it as `<Rect>`/`<Ellipse>` sugar where `width`/`height` do
generate the path. If you spell a size as `width`/`height`, an in-place edit of
that element keeps your spelling; a full reprint of the file emits the canonical
field instead.

Leaving the size off entirely is tolerated, not encouraged: a `Text`, media or
`Instance` element with neither `local_size` nor `width`/`height` is backfilled
on read — media from its intrinsic `natural_size`, text from an estimate of its
style and content, anything else with a 200 x 100 placeholder box — instead of
failing the whole design. Expect the next save to write that guess back as a
real `local_size`.

A node with rotation, scale, or skew shows a raw
`transform={[a, b, c, d, tx, ty]}` array instead of `x`/`y` — leave that
verbatim unless you mean to change the matrix.

### Stable node IDs

Every element has a stable bare-ULID `id="…"` in `.fnx`. Keep that ID when changing or
moving an element. To duplicate one, remove `id` from the copy so the editor
assigns and writes a fresh ID; two elements with the same explicit ID fail to
parse. The neighboring `.ids.json` file is a compatibility/order sidecar kept
in sync by the editor. JSON files are editable; preserve identities and validate
their schema and references before saving. Modern FNX with explicit IDs can
recover a missing or damaged identity sidecar without changing those IDs.

## What you can do by editing `.fnx`

Editing the readable source changes the design directly:

- **Rename a layer** — change its `name="…"`.
- **Edit text** — change a `Text` element's `content="…"`, or an instance's
  `text_content` override.
- **Recolor** — change a hex color inside `fills` / `background` / `strokes` /
  Text `style.color`. Colors use the TSX-valid `fnxColor("#RRGGBB")` helper.
- **Move / resize** — change `x` / `y` (and size-related attributes).
- **Reorder** — change an element's position among its siblings.
- **Duplicate / delete** — copy an element, remove `id` from the copy, or
  remove the element. The editor inserts a fresh ID for the copy.

## Guardrails

- Keep the JSX well-formed: balanced tags, valid attribute values. A `.fnx`
  that fails to parse will not load.
- Preserve each existing element's explicit `id` in `.fnx` and identity
  references in JSON. Inspect the current schema before editing sidecars or
  manifest metadata. A JSON file parsing successfully does not prove its
  typed values and references are valid; validate the complete project.
- Assets are shared **by reference**: they live under `assets/<family>/` and are
  named by content id. `assets/index.json` records full SHA-256 digests and
  sizes. Reference assets by id; never paste binary data inline into `.fnx`.
- For **auto-layout** frames (those with an `auto_layout={…}` attribute), the
  app solves child positions from the layout rules — set the auto-layout
  properties and let the solver place children rather than fighting it with
  manual `x`/`y`.
- `previews/` and `exports/` are generated; they are never read back.
- `.fanta-transaction/` is a temporary recovery journal. If a save stops
  midway, opening the project replays it. Leave it for the editor to recover.
- Positioning: `x`/`y` are sugar for a translation-only transform. A node with
  rotation/scale shows a raw `transform={[a,b,c,d,tx,ty]}` instead — writing
  BOTH `x`/`y` and `transform` on one element is an error, not a merge.

## Driving the open canvas over MCP

While the project is open in Fanta, a local MCP server exposes **the design
canvas that is focused right now**. It is on by default; it is turned off with
`"fanta_live_mcp": { "enabled": false }` in settings.

- **Connecting.** In Fanta, run the **Connect External Agent** command (Help
  menu, or the command palette). It copies a ready-to-paste
  `claude mcp add --scope project --transport stdio fanta -- /path/to/Fanta --mcp-stdio`
  command to the clipboard, and shows the equivalent `[mcp_servers.fanta]`
  snippet for the trusted project's `.codex/config.toml`. Use the exact copied
  command so its executable and instance data directory are correct. Codex
  and Claude chats launched inside Fanta receive the bridge automatically.
- **How the transport works.** The server listens on a Unix socket in a private
  temp directory and advertises the path in
  `~/Library/Application Support/Fanta/fanta_live_mcp.json` (the platform data
  directory elsewhere) as `{"socket": "…/mcp.sock", "pid": 1234}`.
  `fanta --mcp-stdio` reads that file and bridges stdio to the socket. The file
  is published atomically after startup and removed on clean shutdown. Anything
  reading it directly must still check that `pid` is alive before trusting
  `socket`, in case the app crashed.

### Canvas tools

**`get_editor_state`** — `{ empty_space?, page? }`, both optional. Returns the
project name and `project_root`, every page (`index`, `name`, root node id,
node count, `source` path, and which one is `active`), `active_page_bounds`,
the `components` (id, name, root, source), the current `selection` ids and
`selection_bounds`, the `viewport`, `total_nodes`, whether the canvas
`is_editable` and is `dirty`, and a short `hints` list. Pass
`empty_space: [width, height]` to also get `empty_space: {page, x, y, width,
height}` — a free top-left for a new frame of that size, to the right of or
below the page's content. Call it first: the page indices and node ids it
returns are what every other tool takes.

**`get_guidelines`** — takes no arguments. Returns Fanta's design guidelines
for agents (coordinates, frames vs groups, auto layout, spacing and type
scales, naming, components, the working method, and when to edit `.fnx`
instead). Read it once per session before designing.

**`batch_get`** — `{ ids?, page?, depth?, include_geometry?, detail? }`. With
`ids`, returns those nodes' editable style (`detail: "style"`, the default) in
the ops' own vocabulary — `bounds`, `fills`, `strokes`, `effects`,
`auto_layout`, `layout_child`, `constraints`, `text`, `bindings` — so a value
you read can be sent back in an op unchanged; `detail: "raw"` returns the
internal record instead. Without them it lists one page's tree in
compact form, where `page` is a page *index* (default: the active page), `depth`
limits how many levels of children come back (default 2; a cut-off node reports
`child_count`), and `include_geometry: true` adds world-space bounding boxes.
Each listed node carries its id, kind and name plus kind-specific facts: a
frame's `size` and `auto_layout` mode, a text's `text` and `font`, a shape's
first solid `fill`, an instance's `component` name. With `detail: "style"` each listed node
also carries its full style.

**`batch_design`** — `{ ops, label? }`. Applies `ops` in order as **one undo
step**, named by `label` (default `"MCP edit"`). If any op fails the whole batch
rolls back and the error names the op that failed; created ids come back in
`created`. Every `x`/`y` is a world coordinate (px, y down) of a node's
top-left corner, and every `id` is an exact node id. Each op is an object
tagged by `"op"`:

- `create_node` — `node_type` (`"frame"`, `"rectangle"`, `"ellipse"` or
  `"text"`), `x`, `y`, `width`, `height` (all required), plus optional `parent`
  (a frame id; omit to place on the active page), `name`, `fill` (`"#RRGGBB"`
  or `"#RRGGBBAA"`; the glyph color for text), `text` and `font_size`.
- `create_image` — `source` (a `data:image/…;base64,…` URI or raw base64 of
  encoded PNG/JPEG/WebP/GIF bytes; `http(s)` URLs are *not* fetched), `x`, `y`,
  plus optional `parent`, `name`, `width`/`height` (give one and the other
  scales to preserve aspect; give neither for the natural pixel size) and `meta`
  (JSON stored in the node's metadata, e.g. generation provenance). The bytes
  become a project asset under `assets/images/` on the next save.
- `create_instance` — `component` (a component id, or its name when unique),
  `x`, `y`, optional `parent` and `name`. The instance takes the master's size.
- `set_props` — `id` plus only the fields you are changing: `name`, `x`, `y`,
  `width`, `height`, `opacity` (0.0–1.0), `fill`, `corner_radius`, `text`,
  `hidden`, `locked`.
- `set_stroke` — `id`, optional `color`, `width` (`0` removes the stroke),
  `align` (`"inside"`, `"center"`, `"outside"`), `sides` (`[top, right, bottom,
  left]` widths, e.g. `[0, 0, 1, 0]` for a bottom border), `dash` (`[on, off]`),
  `cap` (`butt|round|square`) and `join` (`miter|round|bevel`). Creates the
  stroke if absent.
- `set_shadow` — `id`, optional `color`, `x`, `y`, `blur`, `spread`; edits or
  adds the drop shadow. `remove: true` deletes every drop shadow.
- `set_effects` — `id`, `effects`: the whole stack, bottom first. Shadows are
  `{kind: "drop_shadow"|"inner_shadow", color?, x?, y?, blur?, spread?}`; blurs
  are `{kind: "layer_blur"|"background_blur", radius}`. `[]` removes them all.
- `set_fill` — `id`, `paints`, bottom first: `{kind: "solid", color}`,
  `{kind: "linear", from?, to?, stops: [{position, color}]}`,
  `{kind: "radial", center?, radius?, stops}` (points in the node's 0–1 box) or
  `{kind: "image", source, fit?}`. Frames and shapes; text color is
  `set_text_style`.
- `set_constraints` — `id`, optional `horizontal`
  (`left|right|left_right|center|scale`) and `vertical`
  (`top|bottom|top_bottom|center|scale`): how the node follows a resized
  parent outside auto layout.
- `create_shape` — `shape` (`line|polygon|star|path`), `x`, `y`, `width`,
  `height`, optional `points` (polygon sides / star points), `inner_ratio`,
  `path` (SVG `d` in the shape's own box), `fill`, `stroke`, `stroke_width`.
- `set_text_style` — `id` plus optional `font_family`, `font_weight`
  (100–900), `font_size`, `line_height` (multiple of the size),
  `letter_spacing`, `align` (`left|center|right|justify`), `color`.
- `set_auto_layout` — `id`, `direction` (`"horizontal"`, `"vertical"`,
  `"grid"` or `"none"` to turn it off), optional `gap`, `padding` (`[all]`,
  `[vertical, horizontal]` or `[top, right, bottom, left]`), `align_items`
  (`start|center|end|stretch|baseline`) and `justify`
  (`start|center|end|space_between|space_evenly`).
- `set_index` — `id`, `position`: `"front"`, `"back"`, `"forward"`,
  `"backward"` or `{"index": n}` (0 = bottom) among the current siblings.
- `rotate` — `id`, `degrees`: absolute angle about the node's centre.
- `align` — `ids`, `edge` (`left|center_x|right|top|center_y|bottom`): aligns
  two or more nodes to their combined bounds, or one node to its parent frame.
- `distribute` — `ids` (three or more), `axis` (`"horizontal"` or
  `"vertical"`): equal gaps, outer nodes fixed.
- `group` / `frame_selection` — `ids`, optional `name`: wrap the nodes in a new
  group (no clipping) or a new frame sized to their bounds; the new id is in
  `created`. `ungroup` — `id`: dissolves a group/frame and reports the freed
  `children`.
- `duplicate` — `id`, optional `dx`/`dy`: deep-copies the node one slot above
  the original; the copy's id is in `created`.
- `create_component` — `id` of a frame or group: makes it a component master
  in place and reports the `component` id.
- `componentize` — `ids` of look-alike layers: the first becomes the master
  and the others are replaced in place by instances that override whatever
  they changed (text, fills, hidden layers, other properties). Copies must have
  the master's structure. Reports the `component` and the new `instances`.
- `reparent` — `id`, optional `parent` (omit to move to the active page root)
  and optional `index` among the new siblings (0 = bottom; omit to append on
  top). The node keeps its world position.
- `delete` — `id`; removes that node and its whole subtree.
- `select` — `ids`, replacing the editor selection.
- `set_viewport` — optional `center` (`[x, y]`) and `zoom`.

**`get_design_system`** — optional `collection` (exact id or unique name),
`offset`, `limit` (up to 200), `include_bindings`. Inspect existing component
properties, variant sets, collections, modes and typed variable values first.

**`prepare_design_asset`** — `{ kind: "image" | "svg", prompt, preferred_model? }`.
Opens the image or SVG generation composer with that prompt as a draft for the
user to review. It never submits a generation or spends credits; use it when
the user asks for an asset, then place the result once they generate it.

Variables are real undoable ops: `create_variable_collection` (`name`, `modes`),
`add_variable_mode`, `create_variable` (`collection`, `name`, `kind`, primitive
`value`), `set_variable_value` (`variable`, `mode`, `value`), `set_variable_mode`
(`collection`, optional `mode`/`frame`), `bind_variable` / `unbind_variable`
(`id`, `property` such as `{ "prop": "fill_color", "index": 0 }`).
Variable values are hex colors, finite numbers, strings, booleans or TextStyle
objects. Aliases use `{ "alias": "exact variable id or unique name" }`.
Create foundations before components and prefer returned ids.

A component with variants is ONE variant set: a frame named after the
component holding every variant's master, laid out as a grid of their values,
like a Figma component set. Name each master after its values
(`Variant=Primary, State=Hover`), then `combine_variants` them (`ids`, `name`
such as "Button") to get one axis per property. `add_variants` (`set`, `ids`)
grows a set (new axes and values extend it; existing variants take `Default`
on a new axis and are renamed to match), `remove_variant` (`id`) takes one
out, `arrange_variants` (`set`) puts every variant back in the set's frame and
re-grids it, and `rename_component` (`component`, `name`) renames a component
or set. Other component ops: `create_component_property` (`component`, `kind`, optional `name`),
`bind_component_property` (`component`, descendant `id`, `target` field,
optional exposed `property`) and `set_instance_property` (`id`, `property`,
primitive `value`). Variant sets can be instanced by id; Variant property
values select the named member. Inspect the returned property schema.

`set_auto_layout` also accepts primary/counter `*_sizing` (`fixed`/`hug`),
`min_size`/`max_size` ([width,height], null clears an axis), `wrap` and `counter_gap`.
`set_layout_child` accepts `grow`, `align_self`, `absolute`; positive grow fills
the parent’s primary axis. `set_grid_layout` — `id`, `columns` and optional
`rows` (tracks: a px number, `"1fr"`/`"2fr"`, or `"auto"` to hug), `gap`,
`row_gap` — makes the frame a grid; children fill cells row by row, and
`set_layout_child` `column`/`row` (0-based), `column_span`/`row_span`,
`cell_horizontal`/`cell_vertical` (`start|center|end`) pin one, `auto_place`
unpins it. `set_text_style.sizing` is `fixed`, `auto_height` or
`auto_width`. A centered button: horizontal layout, center justify/align_items,
Hug axes, padding [8,16], min_size [128,48], auto-width label. A wrapping card:
vertical Hug height, fixed width, Stretch children and auto-height paragraphs.

Gradients and per-run rich text still require source editing.
For those, read the page's `.fnx`, edit the file with your normal file tools,
and let the canvas reload — that edit is also a reviewable git diff, which a
`batch_design` call is not until the editor saves.

**`get_screenshot`** — `{ page?, node?, max_dimension? }`, all optional. Renders
a PNG of the active page, of another page by index, or of a single node's region,
capped so the longer side is at most `max_dimension` pixels (default 1024). Use
it to check your own work before telling the user it is done.

**`read_fnx_source`** — `{ path?, offset?, limit?, max_bytes? }`. Omit `path`
for the project `root` and the list of its source files; pass a project-relative
path (for example `pages/<page-slug>/page.fnx`) for that file's text, returned
in slices (64 KiB by default) with `total_lines`, `total_bytes`, `truncated` and
a notice naming the next slice's arguments. Paths that escape the project
root are rejected. This tool only reads — write with your own file tools. On a
document that has never been saved it fails with *the document has no on-disk
Fanta project yet; save the canvas once to materialize one*.

**`import_image`** imports a generated image from a local `path`, `url`, or
base64 `source` into the saved project asset library and returns its asset id
and file path. Use those references in source edits. Generated image blocks
returned by MCP tools are imported automatically when possible; an import
failure is shown in chat.

**`list_comments`** reads a page's unresolved comments. **`reply_comment`**
posts an attributed agent reply to an exact comment id; resolve only after
verifying the requested work. Review mode reads designs and replies to
comments without changing scene content. Plan mode is read-only.

**`report_agent_activity`** reports a stable agent id, mage name, action,
page/node/world focus, `source_path` and `workspace` (`canvas`, `variables`,
`code`). Choose a mage name such as Merlyn, Morgana, Cornelius or Severus.
Use the same name throughout the task. The user can follow that agent across
source-file tabs and editor workspaces. Report the actual working location
at every visible milestone. External MCP agents must reuse the same identity
in `batch_design.activity` so each streamed placement stays attributed to
that agent. Set `active: false` when finished.

### Visible progress

Build one component or one coherent screen section at a time. Prefer native
canvas operations, which paint each edit gradually. For source edits, save a
complete, valid milestone before continuing. Show each new component on the
current page or open its own page/file tab, focus it, and place a representative
instance before building the next component. Do not build a hidden component
library before showing the screen. Give delegated agents the same visibility
requirements and the user's reference attachments. Let actual edits drive
cursor positions and highlights; report file/workspace focus when switching.

## Creating animations

Authored animation data lives in `doc/motion.json`, separately from page
nodes. Read the existing JSON library before adding clips, tracks and
keyframes targeting exact node ids. Preserve existing identities and verify
multiple `get_screenshot` samples using `motion_clip` and `playhead_ms`
after saving, then check playback in the Motion workspace when available. `motion/<slug>/` directories
are index stubs; their presence alone does not create playable animations.

The built-in Fanta agent uses the same surface through its native tools
`design_state` (= `get_editor_state` + `batch_get`, with `empty_space`),
`design_edit` (= `batch_design`), `design_screenshot` (= `get_screenshot`) and
`place_generation` (download an image URL and place it as a `create_image`),
`import_project_image` (save an image without creating a layer),
`design_comments`, and `report_agent_activity`.

### When no canvas is open

Every one of these tools fails with *no design canvas is open; open a .fig file
or Fanta project in Fanta first* unless a design canvas is focused in the app.
You can continue editing the actual source files without an open canvas.
For visual verification, open the project in Fanta or report the specific
verification limitation. Do not replace authorized file edits with a
ready-to-paste code block merely because live canvas access is unavailable.

## Saving, reloading, and checkpoints

Native Full Access initializes Git when needed at the verified active Fanta
project root in a trusted local worktree, creates a `codex/fanta-...` task
branch, and saves durable before/after project snapshots under
`refs/fanta/checkpoints/`. The temporary snapshot index preserves user staging
and dirty changes. Save source progress and verify the design; create normal
commits only when requested. External agents should preserve user changes
when creating task branches and checkpoints.

## Saving, reloading, and committing

The two directions have different latencies, and mixing them up is the usual way
to commit a broken tree:

- **You edit a `.fnx`; the canvas follows.** The editor watches this directory
  and reloads roughly **300 ms** after a burst of external writes settles, so a
  multi-file rewrite lands as one reload rather than several. A parse error
  keeps the old canvas and surfaces the `line:column` error instead.
- **The canvas edits; the files follow.** Canvas edits — including everything
  `batch_design` does — are held in the editor's document until it saves, so
  treat the on-disk tree as *behind* the canvas until you have checked. Cmd-S
  saves immediately; the editor may also save on its own about a second after
  the last edit. Never assume either has happened.

`get_editor_state`'s `dirty` field is how you check: while it is `true` the
editor is still holding changes that have not reached disk, and re-reading the
`.fnx` will show you the state *before* those edits.

Saving updates only changed project files and keeps the `.ids.json` sidecars in
sync. After an edit, let the editor save before `git add`. Committing while
`dirty` is `true` can capture source and sidecars from different revisions.

## Finding the node the user means

When the user says "the selected frame" or "this button", call
`get_editor_state` and read `selection` — those are the node ids the canvas has
selected right now, and `batch_get` turns them into names, geometry and parents.
If the app is not running there is no live selection to read: ask the user for
the **layer name** (the `name="…"` attribute) or the page name and find it in
the relevant `page.fnx` / `master.fnx`. Names are not unique, so when several
elements share one, confirm the match by its parent frame, position or
surrounding text before editing.
