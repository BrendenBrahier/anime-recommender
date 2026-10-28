"""Apply reviewed recommendation gates without rewriting source relationships."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

POLICY = Path(__file__).resolve().parents[1] / 'data/watch_order_decisions.json'


def load_policy(path=POLICY):
    raw = Path(path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def apply_policy(source, policy):
    if policy.get('schema_version') != 1:
        raise ValueError('Unsupported watch-order policy')
    records = deepcopy(source)
    changed = set()
    for group in policy['groups']:
        for change in group['decisions']:
            key = change['anime_id']
            if key in changed:
                raise ValueError('Duplicate watch-order decision: ' + key)
            changed.add(key)
            if key not in records:
                # A partial catalog may not include this reviewed franchise.
                continue
            row = records[key]
            expected = change['expected_source_prerequisites']
            required = change['required_prerequisites']
            optional = change['optional_context']
            if not row.get('verified_relations') or sorted(row.get('prerequisites', [])) != sorted(expected):
                raise ValueError('Watch-order evidence changed; review decision for ' + key)
            if (len(set(required)) != len(required) or len(set(optional)) != len(optional)
                    or set(required) & set(optional) or key in required
                    or not set(expected) <= set(required) | set(optional)
                    or not change.get('rationale') or not change.get('evidence')):
                raise ValueError('Invalid watch-order decision for ' + key)
            for target in set(required) | set(optional):
                if not records.get(target, {}).get('verified_relations'):
                    raise ValueError('Missing watch-order evidence for ' + target)
            row['source_prerequisites'] = list(row['prerequisites'])
            row['prerequisites'] = list(required)
            row['optional_context'] = list(optional)
            row['watch_order_decision'] = group['id']
            row['watch_order_rationale'] = change['rationale']
        for key in group['entry_points']:
            if key in records:
                records[key]['reviewed_entry_point'] = True
    for key, row in records.items():
        if row.get('reviewed_entry_point') and row.get('prerequisites'):
            raise ValueError('Reviewed entry point still has mandatory prerequisites: ' + key)
    return records
