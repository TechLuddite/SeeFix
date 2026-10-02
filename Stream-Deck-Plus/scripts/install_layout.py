"""Inspect or install generated pages and icons; no app launch or hardware actions."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build', type=Path, default=ROOT / 'build')
parser.add_argument('--data-path', type=Path, default=Path.home() / '.var/app/com.core447.StreamController/data')
parser.add_argument('--apply', action='store_true', help='Write configuration after validation and backup')
parser.add_argument('--replace-pages', action='store_true', help='Allow replacing existing Stream/Shortcuts pages; backups are always created')
args = parser.parse_args()
build = args.build.expanduser().resolve()
data = args.data_path.expanduser().resolve()
if not data.is_dir():
    parser.error('StreamController data directory does not exist; launch/configure the app first')
info = json.loads((build / 'build-info.json').read_text())
if Path(info['data_path']) != data:
    parser.error('Build paths target a different data directory; rebuild with the matching --data-path')
for plugin in ['com_core447_OSPlugin', 'com_core447_DeckPlugin', 'com_core447_OBSPlugin']:
    if not (data / 'plugins' / plugin / 'main.py').is_file():
        parser.error(f'Missing plugin {plugin}; install it in StreamController first')
pages = {}
for name in ['Stream', 'Shortcuts']:
    pages[name] = json.loads((build / 'pages' / f'{name}.json').read_text())
    if (data / 'pages' / f'{name}.json').exists() and not args.replace_pages:
        parser.error(f'{name} page exists; inspect the generated page, then use --replace-pages to replace it with a backup')
icons = build / 'Assets/StreamDeckIcons'
if len(list(icons.glob('*.svg'))) != 22:
    parser.error('Expected all 22 generated icons; rebuild before installing')
for page in pages.values():
    for kind in ['keys', 'dials']:
        for item in page.get(kind, {}).values():
            for state in item.get('states', {}).values():
                image = state.get('media', {}).get('path')
                if image:
                    path = Path(image)
                    if path.parent != data / 'Assets/StreamDeckIcons' or not (icons / path.name).is_file():
                        parser.error(f'Unresolved icon: {image}')
print('Target:', data)
print('Pages: Stream, Shortcuts; icons: 22; OBS action settings are preserved.')
if not args.apply:
    print('Inspection only. Close StreamController before running again with --apply.')
    raise SystemExit(0)
backup = data / 'backups' / ('seefix-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
backup.mkdir(parents=True)
for name in pages:
    current = data / 'pages' / f'{name}.json'
    if current.exists():
        (backup / 'pages').mkdir(exist_ok=True)
        shutil.copy2(current, backup / 'pages' / current.name)
current_icons = data / 'Assets/StreamDeckIcons'
if current_icons.exists():
    shutil.copytree(current_icons, backup / 'Assets/StreamDeckIcons')
shutil.copytree(icons, current_icons, dirs_exist_ok=True)
(data / 'pages').mkdir(exist_ok=True)
for name, page in pages.items():
    target = data / 'pages' / f'{name}.json'
    temporary = target.with_suffix('.json.seefix-tmp')
    temporary.write_text(json.dumps(page, indent=2) + '\n')
    temporary.replace(target)
print('Installed. Backup:', backup)
print('Open StreamController and select a page. No recording or camera capture was started.')
