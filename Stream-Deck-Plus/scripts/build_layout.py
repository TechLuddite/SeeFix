import json
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description="Build Stream Deck Plus pages and SVG icons without modifying your installed configuration.")
parser.add_argument('--serial', required=True, help='Stream Deck Plus serial number')
parser.add_argument('--data-path', type=Path, default=Path.home() / '.var/app/com.core447.StreamController/data', help='Target StreamController data directory; embedded in generated page paths')
parser.add_argument('--stream-page', type=Path, default=ROOT / 'examples/Stream.base.json', help='Existing OBS page or editable example; OBS action settings are preserved')
parser.add_argument('--output', type=Path, default=ROOT / 'build', help='Output directory for generated pages and icons')
args = parser.parse_args()
DATA = args.data_path.expanduser().resolve()
STAGE = args.output.expanduser().resolve()
STREAM_PAGE = args.stream_page.expanduser().resolve()
if STAGE == DATA or DATA in STAGE.parents:
    parser.error('--output must be outside the live StreamController data directory')
try:
    stream = json.loads(STREAM_PAGE.read_text())
except (OSError, json.JSONDecodeError) as error:
    parser.error(f'Cannot read source OBS page: {error}')
expected_keys = {f'{x}x{y}' for y in range(2) for x in range(4)}
expected_dials = {str(index) for index in range(4)}
if not isinstance(stream, dict) or set(stream.get('keys', {})) != expected_keys or set(stream.get('dials', {})) != expected_dials:
    parser.error('Source page must have the documented 8 button positions and 4 dial positions')
for kind in ['keys', 'dials']:
    for name, item in stream[kind].items():
        if not isinstance(item, dict) or not isinstance(item.get('states', {}).get('0'), dict):
            parser.error(f'Source {kind}/{name} needs state 0; see examples/Stream.base.json')
ASSETS = STAGE / 'Assets' / 'StreamDeckIcons'
ASSETS.mkdir(parents=True, exist_ok=True)

# Simple vector symbols designed to remain legible on a 120-pixel button.
symbols = {
 'terminal': '<rect x="22" y="22" width="76" height="65" rx="8"/><path d="m36 40 16 14-16 14m27 0h19"/>',
 'browser': '<circle cx="60" cy="53" r="34"/><ellipse cx="60" cy="53" rx="15" ry="34"/><path d="M26 53h68M32 35h56M32 71h56"/>',
 'files': '<path d="M23 83V29h29l10 12h35v42z"/><path d="M24 47h72"/>',
 'screenshot': '<path d="M25 39V23h16m38 0h16v16m0 28v16H79m-38 0H25V67"/><rect x="37" y="36" width="46" height="34" rx="5"/><circle cx="60" cy="53" r="10"/>',
 'record': '<rect x="22" y="25" width="76" height="54" rx="7"/><path d="M60 79v13m-19 0h38"/><circle cx="60" cy="52" r="13" fill="#f7768e" stroke="none"/>',
 'previous': '<rect x="21" y="24" width="78" height="59" rx="6"/><path d="m59 39-17 15 17 15m-17-15h37"/>',
 'next': '<rect x="21" y="24" width="78" height="59" rx="6"/><path d="m61 39 17 15-17 15m17-15H41"/>',
 'media': '<path d="m29 29 30 25-30 25zm42 0v50m17-50v50"/>',
 'starting': '<circle cx="60" cy="53" r="34"/><path d="m51 35 25 18-25 18z"/>',
 'full': '<rect x="21" y="28" width="58" height="50" rx="7"/><path d="m79 43 21-11v43L79 64"/>',
 'nerve': '<rect x="18" y="25" width="84" height="58" rx="7"/><circle cx="48" cy="44" r="9"/><path d="M31 70c0-20 34-20 34 0m11-33h15m-15 15h15m-15 15h15"/>',
 'screen': '<rect x="18" y="24" width="84" height="55" rx="6"/><path d="M60 79v13m-22 0h44"/>',
 'break': '<path d="M27 40h52v32c0 23-52 23-52 0zm52 4h9c21 0 21 25-9 25M40 18v11m20-11v11"/>',
 'ending-cam': '<rect x="18" y="31" width="55" height="44" rx="6"/><path d="m73 43 15-8v36l-15-8m21-43 10 10m-10 0 10-10"/>',
 'ending-reel': '<rect x="24" y="18" width="72" height="76" rx="5"/><path d="M38 18v76m44-76v76M24 36h14m-14 19h14m-14 19h14m44-38h14m-14 19h14m-14 19h14m-45-37 20 17-20 17z"/>',
 'multi': '<rect x="20" y="20" width="80" height="68" rx="6"/><path d="M60 20v68M20 54h80"/>',
 'volume': '<path d="M22 43h17l21-18v56L39 63H22zm52-7c14 9 14 25 0 34m12-45c23 15 23 42 0 57"/>',
 'workspaces': '<rect x="18" y="24" width="36" height="54" rx="5"/><rect x="66" y="24" width="36" height="54" rx="5"/><path d="M29 88h62m-7-7 7 7-7 7"/>',
}
colors = ['#7aa2f7', '#7dcfff', '#e0af68', '#9ece6a', '#f7768e', '#bb9af7', '#ff9e64', '#2ac3de']
for i, (name, shape) in enumerate(symbols.items()):
    color = '#bb9af7' if name in ['previous', 'next', 'workspaces'] else colors[i % len(colors)]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"><rect width="120" height="120" rx="12" fill="#151922"/><g transform="translate(6 5) scale(.9)" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{shape}</g></svg>'
    (ASSETS / f'{name}.svg').write_text(svg)

def icon(state, name, text):
    state['media'] = {'path': str(DATA / 'Assets' / 'StreamDeckIcons' / f'{name}.svg'), 'size': 1, 'valign': 0, 'halign': 0}
    state['labels'] = {'bottom': {'text': text, 'font-family': 'Liberation Sans', 'font-size': 14, 'color': [238, 242, 255, 255], 'outline_width': 0}}
    state['image-control-action'] = 0
    return state

def hotkey(*codes):
    return {'id': 'com_core447_OSPlugin::Hotkey', 'settings': {'keys': [[c, 1] for c in codes] + [[c, 0] for c in reversed(codes)], 'delay': 0.02}}

def command(cmd):
    return {'id': 'com_core447_OSPlugin::RunCommand', 'settings': {'command': cmd, 'detached': True, 'display_output': False}}

def nav(target):
    return {'id': 'com_core447_DeckPlugin::ChangePage', 'settings': {'selected_page': str(DATA / 'pages' / f'{target}.json'), 'deck_number': args.serial, 'return_timeout': 0}}

events = ['Key Down', 'Key Up', 'Key Short Up', 'Key Hold Start', 'Key Hold Stop', 'Dial Down', 'Dial Up', 'Dial Short Up', 'Dial Hold Start', 'Dial Hold Stop', 'Dial Turn CW', 'Dial Turn CCW', 'Dial Touchscreen Short Press', 'Dial Touchscreen Long Press', 'Touchscreen Drag Left', 'Touchscreen Drag Right']
def assign(action, *targets):
    action['event-assignments'] = {event: ('Key Down' if event in targets else None) for event in events}
    return action

def swipe(target):
    return {'sd-plus': {'states': {'0': {'actions': [assign(nav(target), 'Touchscreen Drag Left', 'Touchscreen Drag Right')]}}}}

names = ['starting', 'full', 'nerve', 'screen', 'break', 'ending-cam', 'ending-reel', 'multi']
labels = ['Starting', 'Full', '+ Nerve', 'Screen Cap', 'Break', 'Ending Cam', 'Ending Reel', 'Multi']
for i, (name, label) in enumerate(zip(names, labels)):
    icon(stream['keys'][f'{i % 4}x{i // 4}']['states']['0'], name, label)
for dial in stream['dials'].values():
    state = dial['states']['0']
    state['image-control-action'] = 0
    state['label-control-actions'] = [0, 0, None]
    for label in state.get('labels', {}).values():
        label.update({'font-family': 'Liberation Sans', 'font-size': 15, 'outline_width': 0, 'color': [238, 242, 255, 255]})
stream['dials']['2']['states']['0']['labels']['top'] = {'text': 'Swipe for shortcuts', 'font-family': 'Liberation Sans', 'font-size': 12, 'color': [238, 242, 255, 255], 'outline_width': 0}
stream['dials']['2']['states']['0']['media'] = {'size': .65, 'valign': 0, 'halign': 0}
stream['touchscreens'] = swipe('Shortcuts')

shortcuts = {'keys': {}, 'dials': {}, 'touchscreens': swipe('Stream')}
buttons = [
 ('terminal', 'Terminal', hotkey(125, 28)),
 ('browser', 'Browser', hotkey(125, 42, 48)),
 ('files', 'Files', hotkey(125, 42, 33)),
 ('screenshot', 'Screenshot', hotkey(99)),
 ('record', 'Record / Stop', command('omarchy screenrecord --fullscreen --with-desktop-audio')),
 ('previous', 'Prev Space', hotkey(125, 42, 15)),
 ('next', 'Next Space', hotkey(125, 15)),
 ('media', 'Play / Pause', hotkey(164)),
]
for i, (name, label, action) in enumerate(buttons):
    shortcuts['keys'][f'{i % 4}x{i // 4}'] = {'states': {'0': icon({'actions': [action]}, name, label)}}

# The second action only polls status; a press always triggers the recorder once.
record_state = shortcuts['keys']['0x1']['states']['0']
status = command("if pgrep -f '^gpu-screen-recorder' >/dev/null; then printf 'STOP REC'; else printf 'Record'; fi")
status['settings'].update({'detached': False, 'display_output': True, 'label_position': 'bottom', 'auto_run': 1})
assign(status)
record_state['actions'].append(status)
record_state['label-control-actions'] = [None, None, 1]
record_state['labels']['bottom']['text'] = None

dials = [
 ('volume', 'Volume', [assign(hotkey(115), 'Dial Turn CW'), assign(hotkey(114), 'Dial Turn CCW'), assign(hotkey(113), 'Dial Down', 'Dial Touchscreen Short Press')]),
 ('media', 'Tracks', [assign(hotkey(163), 'Dial Turn CW'), assign(hotkey(165), 'Dial Turn CCW'), assign(hotkey(164), 'Dial Down', 'Dial Touchscreen Short Press')]),
 ('workspaces', 'Workspaces', [assign(hotkey(125, 15), 'Dial Turn CW'), assign(hotkey(125, 42, 15), 'Dial Turn CCW'), assign(hotkey(125, 29, 15), 'Dial Down', 'Dial Touchscreen Short Press')]),
 ('multi', 'OBS / Swipe', [assign(nav('Stream'), 'Dial Down', 'Dial Touchscreen Short Press')]),
]
for i, (name, label, actions) in enumerate(dials):
    title, line1, line2 = [
        ('Volume', 'TURN level', 'PRESS mute'),
        ('Tracks', 'TURN tracks', 'PRESS play'),
        ('Workspaces', 'TURN space', 'PRESS previous'),
        ('OBS', 'PRESS to return', 'SWIPE for pages'),
    ][i]
    shape = symbols[name]
    color = '#bb9af7' if name == 'workspaces' else colors[i]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><rect width="200" height="100" fill="#151922"/><path d="M199 10v80" stroke="#30384a"/><g transform="translate(4 17) scale(.6)" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{shape}</g><g fill="#eef2ff" font-family="Liberation Sans"><text x="80" y="33" font-size="16" font-weight="bold">{title}</text><g fill="#a9b4cc" font-size="11"><text x="80" y="54">{line1}</text><text x="80" y="73">{line2}</text></g></g></svg>'
    (ASSETS / f'dial-{i}.svg').write_text(svg)
    state = {'actions': actions, 'media': {'path': str(DATA / 'Assets' / 'StreamDeckIcons' / f'dial-{i}.svg'), 'size': 1}, 'image-control-action': 0}
    shortcuts['dials'][str(i)] = {'states': {'0': state}}

(STAGE / 'pages').mkdir(exist_ok=True)
for name, page in [('Stream', stream), ('Shortcuts', shortcuts)]:
    (STAGE / 'pages' / f'{name}.json').write_text(json.dumps(page, indent=2) + '\n')

(STAGE / 'build-info.json').write_text(json.dumps({'model': 'Stream Deck Plus', 'data_path': str(DATA), 'serial': args.serial}, indent=2) + '\n')
print('Built 2 pages and 22 SVG icons in', STAGE)
