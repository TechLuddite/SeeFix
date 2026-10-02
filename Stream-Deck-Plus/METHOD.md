# Method

## Inspect before changing

Identify the device and running app, then read the existing page JSON and app
source. This case used Stream Deck Plus (USB `0fd9:0084`), StreamController
`1.5.0-beta.15`, eight 120×120 button images, and an 800×100 touch strip divided
into four 200×100 dial panels. Consult `provenance.json` for plugin versions.

Preserve the existing OBS action objects and back up pages/settings before editing.
Read the installed Omarchy binding files rather than guessing which shortcuts are
active. Camera stills helped confirm the hardware result during the session; they
are excluded from this project.

## Empty icons: action drawing permission

The original page had OBS actions and labels, but omitted `image-control-action`.
In the tested app, `ActionCore.has_image_control()` compares that index with the
action index; a missing value did not give action 0 permission to draw.

Set `"image-control-action": 0` on the relevant state. For distinct scene icons,
provide `media.path` pointing to an SVG. Explicit custom media takes precedence
over plugin icons. Leave OBS audio dials without custom `media.path`, allowing
their plugin to draw changing meters. Use page-owned font/label styles separately.

Use an installed normal text font (Liberation Sans here), high-contrast symbols,
14px key captions, and a dedicated 200×100 composition for dial instructions.
Related previous/next workspace controls share the same purple accent.

## Blank OBS meters: cached frame with no current image

The meter could render before StreamController recreated its input state. Its
`_last_state` cache still matched the current mute/volume values, so it skipped
redrawing although the current state no longer contained an image.

The fix checks both conditions before skipping a frame:

```python
input_state = self.get_state()
rendered_image = getattr(input_state, "image" if is_dial else "key_image", None)
if getattr(self, "_last_state", None) == state and rendered_image is not None:
    return None
```

This keeps the usual unchanged-frame optimization while repairing missing frames.
`ControllerDialState.image` and `ControllerKeyState.key_image` were verified in
the installed app. The patch targets the user-owned OBS plugin, not packaged
StreamController or Omarchy source.

## Shortcut events and navigation

OSPlugin Hotkey uses Linux evdev keycodes. Emit key-down events in order and
release in reverse order, with a short delay. The demonstrated bindings were:

| Action | Combination / evdev codes |
|---|---|
| Terminal | Super+Enter / 125, 28 |
| Browser | Super+Shift+B / 125, 42, 48 |
| Files | Super+Shift+F / 125, 42, 33 |
| Screenshot | Print / 99 |
| Next workspace | Super+Tab / 125, 15 |
| Previous workspace | Super+Shift+Tab / 125, 42, 15 |
| Former workspace | Super+Ctrl+Tab / 125, 29, 15 |
| Play/pause | KEY_PLAYPAUSE / 164 |
| Next/previous track | KEY_NEXTSONG / 163; KEY_PREVIOUSSONG / 165 |
| Volume up/down/mute | 115 / 114 / 113 |

Virtual-keyboard permissions were tested by creating and closing an evdev UInput
device without sending keys. Follow the OS plugin's current setup instructions if
that fails on another machine. Desktop bindings and permissions are separate from
whether the deck can draw an icon.

Map each dial action's chosen input event to `Key Down`, and explicitly disable its
other events. This avoids rotating a dial also triggering another action's default
handlers. Dial presses and short touch-strip taps can share a function.

The `touchscreens.sd-plus` state uses DeckPlugin ChangePage. Both
`Touchscreen Drag Left` and `Touchscreen Drag Right` map to the action's `Key Down`
event. Each page points to the other using its actual JSON path and device serial.
The fourth Shortcuts dial additionally returns to Stream on press/tap.

## Recording and status

Omarchy's tested recorder initializes desktop and microphone audio to false.
`--with-desktop-audio` selects `default_output`; excluding
`--with-microphone-audio` keeps `default_input` out of the recorder arguments.
`--fullscreen` captures the focused monitor. An existing recorder causes the same
command to stop/finalize instead of starting another.

The recording button has two RunCommand actions: a detached toggle command, and a
one-second status poll. The latter captures output synchronously and has every
input event disabled, so it cannot toggle recording when pressed. Its command is:

```sh
if pgrep -f '^gpu-screen-recorder' >/dev/null; then
  printf 'STOP REC'
else
  printf 'Record'
fi
```

Set `label-control-actions` to `[null, null, 1]` and page bottom label `text` to
`null`. A non-null page label overrides the polling action's text even if the
action has label permission. Keep font/color styling in the page.

## Verification and review

Check actual page switching, virtual-keyboard access, and rendered hardware
separately. Test recording only when no unrelated recording is active: start,
inspect actual recorder arguments for `-a default_output` without `default_input`,
then stop cleanly and use ffprobe to check finalized video and audio streams.

Use camera verification for missing icons, clipping, and dial rendering; do not
infer tiny label text from a blurred photo. In this session, design, action, and
usability reviewers checked repeated revisions. Their reviews caught the cached
meter defect and the recording label override. Behavior and review limitations
are recorded in [VALIDATION.md](VALIDATION.md).

For app reloads, close and restart as separate operations. The tested
`--close-running` path sometimes exited on a D-Bus NoReply after successfully
closing the old instance, so it did not reliably launch a replacement.
