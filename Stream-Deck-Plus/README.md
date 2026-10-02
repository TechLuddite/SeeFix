# Stream Deck Plus

A reusable StreamController setup for Elgato Stream Deck Plus on Omarchy/Hyprland:
distinct scene icons, repaired OBS audio meters, and a swipe-accessible shortcuts
page. It was developed and verified on a physical device, with separate design,
functionality, and usability reviews.

## Included

- `scripts/build_layout.py`: generates two page files and 22 vector icons using
  Python's standard library; never edits the installed app.
- `scripts/install_layout.py`: validates the build, backs up existing pages/icons,
  and installs only with `--apply`.
- `scripts/patch_obs_meter.py`: identifies the exact OBS cached-frame defect and
  applies the fix only with `--apply`, saving the original source.
- `assets/icons/`: finished SVG icons, including four 200×100 dial panels.
- `examples/`: an editable base OBS layout and final JSON templates. Placeholder
  paths/serials are documentation, not directly importable profiles.
- `patches/obs-meter-redraw.patch`: the minimal source change.
- [METHOD.md](METHOD.md): diagnosis, action mappings, rendering details, and checks.
- [VALIDATION.md](VALIDATION.md): what was verified and its limits.
- `provenance.json`: tested device/software and upstream plugin revisions.

No camera images, screenshots, recordings, credentials, raw logs, or upstream
plugin source trees are included. The screenshot shortcut itself remains available.

## Layout

Swipe either direction across the touch strip to move between `Stream` and
`Shortcuts`. Original OBS scene and dial action settings remain configured.

| Shortcuts | Left | Second | Third | Right |
|---|---|---|---|---|
| Top row | Terminal | Browser | Files | Screenshot |
| Bottom row | Record/Stop | Previous workspace | Next workspace | Play/Pause |

| Dial | Turn | Press or tap its strip area |
|---|---|---|
| Volume | Raise/lower desktop volume | Mute/unmute |
| Tracks | Next/previous track | Play/pause |
| Workspaces | Next/previous workspace | Former workspace |
| OBS | — | Return to Stream |

The record button uses `omarchy screenrecord --fullscreen --with-desktop-audio`.
It records the focused monitor and desktop output, excludes the microphone, and
stops on the next press. A separate polling action supplies `Record`/`STOP REC`
label text. Normal recordings use Omarchy's configured Videos directory.

## Build and install

Requires Python 3, StreamController, the OS/Deck/OBS plugins, Liberation Sans,
working virtual-keyboard access, and the Omarchy commands/bindings described in
[METHOD.md](METHOD.md). OBS actions also need its websocket connection.

Install the official plugins through StreamController first. References:
[OS](https://github.com/StreamController/OSPlugin),
[Deck](https://github.com/StreamController/DeckPlugin),
[tested OBS fork](https://github.com/oparada1988/OBSPlugin).
They are referenced here rather than redistributed. Their upstream licenses apply
to their source and modifications; no overall project license has been selected.

From this directory, build a preview using the serial shown by StreamController:

```bash
python3 scripts/build_layout.py --serial YOUR_SERIAL
```

The bundled base is the demonstrated eight-scene OBS layout. Edit its scene/input
names first. To preserve the actual OBS settings of the same layout, supply your
existing page:

```bash
python3 scripts/build_layout.py --serial YOUR_SERIAL \
  --stream-page "$HOME/.var/app/com.core447.StreamController/data/pages/Stream.json"
```

The demonstrated positions are Starting, Full, Full with Nerve, Screen Cap, Break,
Ending Cam, Ending Reel, and Multi. Adapt the generator's icon/caption mapping if
your scene order differs; action settings are copied, but these captions are fixed.
The four OBS dials are Mic/Aux, Desktop Audio, stream toggle, and record toggle.

Inspect `build/pages/` and `build/Assets/StreamDeckIcons/`. Close StreamController
before installation so it does not overwrite the edited page files.

The default `build/` directory is ignored by Git: generated profiles contain your
local data path, device serial, and copied OBS settings. Keep any custom `--output`
directory and private source profiles outside the repository.

```bash
python3 scripts/install_layout.py --replace-pages
python3 scripts/install_layout.py --replace-pages --apply
python3 scripts/patch_obs_meter.py
python3 scripts/patch_obs_meter.py --apply
```

Reopen StreamController and select `Stream` or `Shortcuts`. The scripts do not
change your default page, restart the app, access a camera, or start a recording.
Use the same `--data-path` with the builder, installer, and patcher if your app uses
a custom data directory. A matching or already-fixed OBS implementation is
required; different source is left for inspection.

## Recovery and updates

Page/icon backups are under the selected data directory's `backups/seefix-*`.
With StreamController closed, restore saved pages and icons from the backup; if
the install added a new page, remove it separately when reverting. The OBS source
backup is beside `InputDial.py`; restore it with the app closed if needed.

After an OBS plugin update, rerun the patcher in inspection mode. An update can
replace a local plugin edit, or may already contain an upstream fix.
