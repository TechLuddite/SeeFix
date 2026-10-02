"""Inspect/apply the OBS InputDial cached-frame repair, with a source backup."""
import argparse
from datetime import datetime
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data-path', type=Path, default=Path.home() / '.var/app/com.core447.StreamController/data')
parser.add_argument('--source', type=Path, help='Explicit InputDial.py path, overriding --data-path')
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
source = (args.source or args.data_path / 'plugins/com_core447_OBSPlugin/actions/InputDial/InputDial.py').expanduser().resolve()
if not source.is_file():
    parser.error(f'InputDial.py not found: {source}')
old = '        if getattr(self, "_last_state", None) == state:\n            return None\n'
new = '        input_state = self.get_state()\n        rendered_image = getattr(input_state, "image" if is_dial else "key_image", None)\n        if getattr(self, "_last_state", None) == state and rendered_image is not None:\n            return None\n'
text = source.read_text()
if new in text:
    print('Already fixed:', source)
    raise SystemExit(0)
if text.count(old) != 1:
    parser.error('Implementation differs from the reviewed version; inspect before applying this patch')
fixed = text.replace(old, new, 1)
compile(fixed, str(source), 'exec')
if not args.apply:
    print('Matching cached-frame defect found. Close StreamController, then rerun with --apply.')
    raise SystemExit(0)
backup = source.with_name(source.name + '.seefix-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.bak')
shutil.copy2(source, backup)
source.write_text(fixed)
print('Patched:', source)
print('Source backup:', backup)
