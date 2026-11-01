"""Live served-profile evidence for an already kernel-bound native s6 launch.

This is an observation on the original identify response, not idle admission,
permission, an activation token, or a new profile/authority store.
"""
from __future__ import annotations

from pathlib import Path

_MAX_PROFILE_BINDINGS = 128


def bind_live_served_profiles(payload: dict, runner) -> dict:
    """Enrich only an existing original launch receipt from native live authorities."""
    original = payload.get('launch_admission')
    if not isinstance(original, dict):
        return payload
    receipt = dict(original, runtime_profile_binding_verified=False)
    receipt.pop('runtime_profile_binding', None)
    payload['launch_admission'] = receipt
    receipt['runtime_profile_binding_status'] = 'unverified'
    try:
        binding = _live_binding(payload, runner, receipt)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        receipt['runtime_profile_binding_status'] = 'unavailable'
        return payload
    if binding is not None:
        receipt.update(runtime_profile_binding_verified=True,
                       runtime_profile_binding_status='observed_live_authorities',
                       runtime_profile_binding=binding)
    return payload


def _signature(authorities):
    return {(id(a), a.instance_id, a.epoch) for a in authorities}


def _live_binding(payload, runner, receipt):
    from gateway.session_authorities import local_bots

    descriptor = runner.session_runtime_descriptor
    registry = runner.session_authorities
    instance = descriptor.get('instance_id')
    if (payload.get('state') != 'ready' or descriptor.get('state') != 'ready'
            or getattr(runner, '_draining', False) or not isinstance(instance, str) or not instance
            or payload.get('instance_id') != instance):
        return None
    before = _signature(registry.serving())
    bots = [b for b in local_bots(runner) if not b.retiring]
    if not bots or len(bots) > _MAX_PROFILE_BINDINGS:
        return None  # No partial set can become verified evidence.
    bindings, launch_matches = _profile_rows(registry, receipt, payload, instance, bots)
    if (launch_matches != 1 or before != _signature(registry.serving())
            or before != _signature([b.authority for b in bots])
            or runner.session_runtime_descriptor is not descriptor
            or descriptor.get('state') != 'ready' or descriptor.get('instance_id') != instance
            or getattr(runner, '_draining', False)):
        return None
    return {'scope': 'observed_served_profiles', 'instance_id': instance,
            'profiles': sorted(bindings, key=lambda b: b['profile'])}


def _profile_rows(registry, receipt, payload, instance, bots):
    from hermes_cli.service_manager_admission import _identity

    bindings = []
    launch_matches = 0
    for bot in bots:
        authority = bot.authority
        if (bot.problem or registry.for_home(bot.home) is not authority
                or authority.instance_id != instance or type(authority.epoch) is not int
                or authority.epoch < 1):
            raise ValueError("authority binding unavailable")
        identity = _identity(bot.home)
        bindings.append({'profile': bot.name, 'home_identity': identity,
                         'authority_epoch': authority.epoch})
        if authority is registry.launch:
            if (bot.name != receipt['launch_profile'] or identity != receipt['home_identity']
                    or bot.home.resolve() != Path(payload['hermes_home']).resolve()
                    or authority.epoch != payload.get('authority_epoch')):
                raise ValueError("authority binding unavailable")
            launch_matches += 1
    return bindings, launch_matches
