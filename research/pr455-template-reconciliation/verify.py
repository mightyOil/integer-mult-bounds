#!/usr/bin/env python3
"""Source-bound PR455 hash reconciliation. Apache-2.0; substantial OpenAI assistance.

The retained predecessor is executed unchanged with assertions enabled. This
harness uses explicit checks so its own contracts survive Python -O.
"""
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tarfile
import io

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREFIX = 'research/e8-whole-pool-portfolio/'
ORIGINAL_HEAD = 'f76fc4e36030d4e00b4cbb83b1dbc661a0974c4e'
ORIGINAL_TEMPLATE = '02d4d0031a173664f8adc5bccf0244f8ce349307eac09c0d48a3c8948a7f5b17'
REVIEW_TEMPLATE = '62d1e17fe80b82691e7cef2b03974a826b513da6af5689eb4c0aac1b38355971'
LOCAL_PAYLOAD = 'e1b483423ec93c47c80d21a01d92591f3856d1ec68da231372ec2bc29f7e8fd8'
LOCAL_CONTAINER = '4208096ba6a9b358f4c8687c514da29f15c5245169719b313a9a409d028b537f'
PHASE_LF = 'f34c3da0599c99dfd5111d104a3f6645746d50e268994160fc80eca3f53158cf'
PHASE_CRLF = '79c0098466a2fb80002826b14142dbdc1d60ceb45045107ac2c8755e7d3ae358'
PAYLOAD_TEMPLATE = '0b9538eb416a7bf0360d9d3f8f8b25224269200884536f2ae085af2234288e26'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def pin_bytes(data, row):
    require(sha(data) == row['sha256'], 'source SHA256 mismatch: ' + row['path'])
    obj = b'blob ' + str(len(data)).encode() + b'\0' + data
    require(hashlib.sha1(obj).hexdigest() == row['git_blob'], 'source Git blob mismatch: ' + row['path'])


def prepare_sources(destination):
    sources = read(PACKAGE / 'SOURCES.json')
    archive = sources['archival_inputs']
    require(archive['head'] == ORIGINAL_HEAD and archive['prefix'] == PREFIX, 'wrong historical source')
    for row in sources['files']:
        value = git('show', sources['base_commit'] + ':' + row['path'])
        pin_bytes(value, row)
        if row['usage'] == 'input':
            require((ROOT / row['path']).read_bytes() == value, 'live source drift: ' + row['path'])
    raw_archive = (PACKAGE / archive['archive']).read_bytes()
    require(sha(raw_archive) == archive['archive_sha256'], 'archival source container changed')
    archive_tar = tarfile.open(fileobj=io.BytesIO(raw_archive), mode='r:gz')
    members = archive_tar.getmembers()
    expected_names = {r['path'] for r in archive['files']}
    require(len(members) == len(expected_names) and {m.name for m in members} == expected_names,
            'archival source inventory differs')
    require(all(m.isfile() for m in members), 'non-file archived input')
    paths = []
    for row in archive['files']:
        relative = Path(row['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe source path')
        require(row['path'] not in paths, 'duplicate archived source')
        paths.append(row['path'])
        value = archive_tar.extractfile(row['path']).read()
        pin_bytes(value, row)
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    manifest = read(destination / 'MANIFEST.json')
    for name in paths:
        if name != 'MANIFEST.json':
            require(sha((destination / name).read_bytes()) == manifest[name], 'author manifest mismatch: ' + name)
    require(read(destination / 'EXPECTED.json')['complex_template_sha256'] == ORIGINAL_TEMPLATE,
            'author expected template changed')
    return len(paths)


def check_local_payload(fresh, fixture):
    require(sha(fixture) == LOCAL_CONTAINER, 'historical-compatible container changed')
    require(fixture[:9] == bytes.fromhex('1f8b08000000000002') and fixture[9] == 10,
            'historical-compatible gzip header changed')
    payload = gzip.decompress(fixture)
    require(sha(payload) == LOCAL_PAYLOAD, 'fixture payload changed')
    require(gzip.decompress(fresh) == payload, 'fresh literal local programs changed')


def phase_adapter(fresh):
    # Accept platform text translation, but neither discard JSON fields nor
    # normalize arbitrary whitespace. The complete exact LF bytes are pinned.
    normalized = fresh.replace(b'\r\n', b'\n')
    require(b'\r' not in normalized and sha(normalized) == PHASE_LF, 'fresh complete phase payload changed')
    adapted = normalized.replace(b'\n', b'\r\n')
    require(sha(adapted) == PHASE_CRLF and json.loads(adapted) == json.loads(fresh),
            'phase adapter changed a JSON value')
    return adapted


def payload_template(template, local_bytes, phase_bytes):
    require(template['source_local_programs_sha256'] == sha(local_bytes), 'unbound local container')
    require(template['exact_data_phase_recipe_sha256'] == sha(phase_bytes), 'unbound phase bytes')
    local = gzip.decompress(local_bytes)
    phase = phase_bytes.replace(b'\r\n', b'\n')
    require(sha(local) == LOCAL_PAYLOAD and sha(phase) == PHASE_LF, 'unproved normalization preimage')
    require(template['local_programs'] == json.loads(local), 'embedded literal programs changed')
    result = copy.deepcopy(template)
    result['source_local_programs_sha256'] = sha(local)
    result['exact_data_phase_recipe_sha256'] = sha(phase)
    return sha(canonical(result))


def reject(action, label):
    try:
        action()
    except (ValueError, KeyError, IndexError, OSError, EOFError):
        return label
    raise ValueError('vacuous negative control: ' + label)


def controls(template, fixture, phase, source_row, source_value):
    rejected = []
    # Neither half of the explanation is sufficient on its own. This is the
    # known macOS review container, obtained solely by its OS byte, not deflate.
    mac = bytearray(fixture)
    mac[9] = 255
    lf = phase.replace(b'\r\n', b'\n')
    hashes = {}
    for name, local, ph in [('review', bytes(mac), lf), ('header_only', fixture, lf),
                            ('newline_only', bytes(mac), phase), ('both', fixture, phase)]:
        changed = copy.deepcopy(template)
        changed['source_local_programs_sha256'] = sha(local)
        changed['exact_data_phase_recipe_sha256'] = sha(ph)
        hashes[name] = sha(canonical(changed))
        require(payload_template(changed, local, ph) == PAYLOAD_TEMPLATE, 'payload quotient changed')
    require(hashes['review'] == REVIEW_TEMPLATE and hashes['both'] == ORIGINAL_TEMPLATE,
            'historical endpoints not reconciled')
    require(hashes['header_only'] != ORIGINAL_TEMPLATE and hashes['newline_only'] != ORIGINAL_TEMPLATE,
            'single-adapter control is vacuous')
    bad = json.loads(gzip.decompress(fixture))
    bad['forward'].pop()
    rejected.append(reject(lambda: check_local_payload(gzip.compress(canonical(bad), mtime=0), fixture),
                           'omitted fresh local instruction'))
    rejected.append(reject(lambda: check_local_payload(fixture, fixture + b'x'), 'changed fixture bytes'))
    ph = json.loads(phase)
    ph['recipes'][0]['terminal_Y_translation'] ^= 1
    rejected.append(reject(lambda: phase_adapter(json.dumps(ph, indent=2).encode()), 'changed phase translation'))
    for name, mutate in [
        ('changed owner', lambda t: t['calls'][0]['owners'][240].__setitem__(0, 0)),
        ('omitted literal instruction', lambda t: t['local_programs']['forward'].pop()),
        ('omitted final correction', lambda t: t['execution_schedule'].pop()),
        ('changed paid idle rank', lambda t: t['idle_children'][0].__setitem__('rank', 999)),
        ('forged generated-file binding', lambda t: t.__setitem__('source_local_programs_sha256', '0' * 64)),
    ]:
        changed = copy.deepcopy(template)
        mutate(changed)
        def check(changed=changed):
            require(payload_template(changed, fixture, phase) == PAYLOAD_TEMPLATE, 'complete template payload changed')
        rejected.append(reject(check, name))
    rejected.append(reject(lambda: pin_bytes(source_value + b' ', source_row), 'source byte change'))
    forged = dict(source_row, git_blob='0' * 40)
    rejected.append(reject(lambda: pin_bytes(source_value, forged), 'wrong source object'))
    return hashes, rejected


def execute(work):
    source = work / 'source'
    source_count = prepare_sources(source)
    state = work / 'split-centres'
    state.mkdir()
    for path in (source / 'inputs/complex').iterdir():
        (state / path.name).write_bytes(path.read_bytes())
    out = work / 'complex'
    out.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONPATH=str(source / 'vendor/complex'))
    env.pop('PYTHONOPTIMIZE', None)
    command_names = []
    def run(name, script, *args):
        command_names.append(name)
        with (work / (name + '.log')).open('wb') as log:
            subprocess.run([sys.executable, '-B', str(source / script), *map(str, args)],
                           cwd=work, env=env, check=True, timeout=180, stdout=log, stderr=subprocess.STDOUT)
    run('local-programs', 'vendor/complex/complex_emit.py')
    checks = read(state / 'LOCAL-CHECKS.json')
    require(checks == read(source / 'inputs/complex/LOCAL-CHECKS.json'), 'complete local checks differ')
    run('data-phases', 'vendor/complex/complex_phases.py', state / 'CANONICAL-WORD.json.gz', out / 'DATA-PHASES.json')
    fixture = (PACKAGE / 'historical-compatible-local-programs.json.gz').read_bytes()
    check_local_payload((state / 'LOCAL-PROGRAMS.json.gz').read_bytes(), fixture)
    phase = phase_adapter((out / 'DATA-PHASES.json').read_bytes())
    (state / 'LOCAL-PROGRAMS.json.gz').write_bytes(fixture)
    (out / 'DATA-PHASES.json').write_bytes(phase)
    run('whole-complex', 'code/complex_whole_emit.py', state, out, source / 'inputs/complex-selection.json')
    run('independent-routing', 'code/complex_whole_audit.py', out, state, source / 'inputs/complex-selection.json')
    template = json.loads(gzip.decompress((out / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    actual = sha(canonical(template))
    require(actual == ORIGINAL_TEMPLATE, 'original author expected digest not reproduced')
    require(payload_template(template, fixture, phase) == PAYLOAD_TEMPLATE, 'complete canonical payload mismatch')
    audit = read(out / 'AUDIT.json')
    inherited = audit['mutations_rejected']
    require(len(inherited) == 10 and set(inherited.values()) == {'REJECTED'}, 'incomplete original mutation coverage')
    historical = json.loads(gzip.decompress((ROOT / 'research/community-reconciliation-fourth100-audit/regenerated/pr455-outputs/serialization/complex/AUDIT.json.gz').read_bytes()))
    require(set(audit) == set(historical), 'routing receipt schema differs')
    differences = [k for k in audit if audit[k] != historical[k]]
    require(differences == ['template_sha256', 'source_bindings'], 'scientific routing results differ')
    require(set(audit['source_bindings']) == set(historical['source_bindings']), 'binding schema differs')
    nested = [k for k in audit['source_bindings'] if audit['source_bindings'][k] != historical['source_bindings'][k]]
    require(nested == ['phase_sha256'], 'nonserialization routing source changed')
    sources = read(PACKAGE / 'SOURCES.json')['archival_inputs']['files']
    row = next(r for r in sources if r['path'] == 'code/complex_whole_emit.py')
    hashes, rejected = controls(template, fixture, phase, row, (source / row['path']).read_bytes())
    receipt = dict(status='PASS_PR455_TEMPLATE_RECONCILIATION', archived_files=source_count,
                   unchanged_source_commands=command_names, original_template_sha256=actual,
                   payload_template_sha256=PAYLOAD_TEMPLATE, serializer_combinations=hashes,
                   fresh_local_columns_per_orientation=800, local_events_per_orientation=24857,
                   phase_polynomial_evaluations=read(out / 'DATA-PHASES.json')['exact_phase_polynomial_evaluations'],
                   calls=audit['calls'], whole_residuals=audit['whole_residuals'],
                   occupied_axis_cells=audit['occupied_axis_cells'], profile=audit['profile'],
                   rank_mass=audit['rank_mass'], inherited_mutations_rejected=sorted(inherited),
                   new_controls_rejected=rejected,
                   historical_audit_changed_top_level_keys=differences,
                   historical_audit_changed_binding_keys=nested)
    require(receipt == read(PACKAGE / 'EXPECTED.json'), 'reconciliation receipt changed')
    (work / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('PASS_PR455_TEMPLATE_RECONCILIATION original_hash=' + actual +
          ' calls=88 whole_residuals=49280 inherited_controls=10 new_controls=' + str(len(rejected)))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, help='new directory for review logs and outputs; otherwise use temporary storage')
    args = parser.parse_args()
    if args.work:
        work = args.work.resolve()
        work.mkdir(parents=True, exist_ok=False)
        execute(work)
    else:
        with tempfile.TemporaryDirectory(prefix='pr455-reconciliation-') as directory:
            execute(Path(directory))


if __name__ == '__main__':
    main()
