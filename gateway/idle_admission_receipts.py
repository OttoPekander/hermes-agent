"""Bounded original native idle-request completion records; never activation grants."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import threading

_REQUEST_ID = re.compile(r'[0-9a-f]{32}')


def request_digest(params):
    encoded = json.dumps(params, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    if len(encoded) > 16384:
        raise ValueError('idle request too large')
    return hashlib.sha256(encoded).hexdigest()


class IdleRequestBook:
    """No eviction/expiry: a remembered ID cannot become a new admission in this run."""
    def __init__(self, instance_reader):
        self.instance_reader = instance_reader
        self.lock = threading.Lock()
        self.requests = {}

    def run(self):
        from hermes_cli.service_manager_admission import _process
        instance = self.instance_reader()
        if not isinstance(instance, str) or not instance or len(instance) > 128:
            raise ValueError('native runtime unavailable')
        return {'process': _process(os.getpid()), 'instance_id': instance}

    def begin(self, params):
        identity = params.get('request_id')
        if 'request_id' not in params:
            return None, None  # Legacy bound callers retain their original contract.
        try:
            if not isinstance(identity, str) or not _REQUEST_ID.fullmatch(identity):
                raise ValueError('invalid request identity')
            digest, run = request_digest(params), self.run()
        except (ValueError, TypeError, OSError):
            return None, {'pausing': False, 'request_refused': True}
        with self.lock:
            original = self.requests.get(identity)
            if original is not None:
                return None, {'pausing': False, 'request_replayed': True}
            if len(self.requests) >= 128:
                return None, {'pausing': False, 'request_capacity_refused': True}
            self.requests[identity] = {'digest': digest, 'run': run, 'complete': False, 'proof': None}
        return identity, None

    def timeout(self, identity):
        if identity is None:
            return None
        with self.lock:
            record = self.requests[identity]
            if record['run'] != self.run():
                return None
            return {'protocol': 1, 'outcome': 'loop_timeout_not_admitted',
                    'request_id': identity, 'request_sha256': record['digest'],
                    'run': copy.deepcopy(record['run'])}

    def complete(self, identity, result):
        if identity is not None:
            with self.lock:
                self.requests[identity]['complete'] = True
                self.requests[identity]['proof'] = copy.deepcopy(result.get('non_admission'))

    def observe(self, params):
        identity, digest = params.get('request_id'), params.get('request_sha256')
        if not isinstance(identity, str) or not isinstance(digest, str):
            return {'status': 'unavailable'}
        with self.lock:
            record = self.requests.get(identity)
            if (record is None or record['digest'] != digest or not record['complete']
                    or record['proof'] is None or record['run'] != self.run()):
                return {'status': 'unavailable'}
            return {'non_admission': copy.deepcopy(record['proof'])}
