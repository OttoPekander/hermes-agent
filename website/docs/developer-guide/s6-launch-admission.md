# Opt-in s6 launch admission prerequisite

The native `S6ServiceManager.register_profile_gateway` API accepts
`launch_admission=True` only with `start_now=False`. Existing registration and launch defaults
are unchanged. The existing native s6 child sentinel now classifies a launch as
supervised even when enrollment is missing/invalid; this is refusal-only ownership
information, never positive enrollment proof. A new slot is built hidden and persistently
down, with an enrollment describing its exact directory identity, native launcher
hash, profile home identity and expected runtime UID. Registration does not alter
an existing slot or adopt a preexisting launcher.

The renderer invokes native admission after its normal UID-drop branch. Admission
requires the exact enrollment and launcher, the actual current child PID reported
by s6, and the same live parent supervisor PID/start/boot identity, executable and
slot working directory. It then execs the ordinary gateway **without `--replace`**;
enrollment gives no authority to displace another gateway.

The original answering gateway's existing local `identify` response can carry
`launch_admission`. It is recomputed from that answering process and the native
enrollment, not accepted from a caller or ambient declaration. It names the launch
profile; the launch-only builder keeps `runtime_profile_binding_verified` false.
The runtime's original `identify` handler may enrich that receipt from its existing
live `SessionAuthorities` registry and canonical `local_bots` names. Only a ready,
non-draining original runtime with an exact matching launch authority can report
`runtime_profile_binding_verified: true`. Its bounded `runtime_profile_binding`
names `scope: observed_served_profiles`, the original runtime instance and each
served profile's canonical name, directory device/inode and native authority epoch.
The registry is read before/after projection; missing/changed/ambiguous/retiring or
unavailable authority stays unverified. More than128profiles yields no positive
partial projection. Saved `served_profiles` status, caller labels and the
supervisor sentinel cannot establish this binding. `behavior_accepted` stays false.
Legacy, missing, invalid or inaccessible enrollment yields no positive receipt.
A verified receipt classifies this launch as supervised `s6`, preserving refusal
by consumers that support manual owners only. This is a live observation, not atomic idle admission or a permission to stop,
replace or activate an owner. It cannot be replayed as a grant; consumers still
need the original current run, applicable profile scope, cancellation and native
idle/holdoff fencing. The set may change after this observation.

This is a cooperative same-UID operator contract, not isolation against malicious
code running as that UID. It is Linux-only and fails closed when proc identity or
s6 status cannot be read. In particular, a root supervisor whose proc executable
or working directory is unreadable after the UID drop remains unsupported; do not
widen privileges to make admission pass. Qualification of that root-to-user path,
startup/successor fencing, atomic idle drain, durable hold/recovery integration and
independently installed recovery is still required before activation. Existing
idle-drain contribution144790 is separate and must not be duplicated or treated as
a maintained runtime pin before canonical merge/release qualification.

`scripts/e2e_s6_launch_admission.py` exercises private real s6 registration and the
actual gateway control boundary. Use a compatible existing Hermes interpreter,
a fresh private short fixture path, and no owner credentials. It uses installed
`S6_KEEP_ENV=1` to keep its cleared environment rather than importing the host
container environment. The foreground competitor explicitly uses the documented
`--no-supervise` route, never the container's global service redirect. It requests
no model turns and does not establish user-facing activation or production proof.

`scripts/e2e_s6_served_profile.py` exercises one native default multiplexer serving
an eligible named profile. A new standalone named gateway is refused by current
native policy and is not a workaround; the journey does not use `--force` or a
standalone compatibility shim. Markerless homes are not profiles and must not gain
bindings. Its preflight proves private service/log/socket targets, cleared
environment and `S6_KEEP_ENV=1` before any supervisor is started. A same-UID Linux
open-directory alias may keep a socket path short while resolving all files into
the private fixture. No shared `/run/service` lifecycle operation or logger target
is allowed. This supports the served-profile prerequisite only; root-to-user,
new-owner fencing, method activation and production remain separate gates.

`scripts/e2e_s6_dynamic_authority.py` uses the same private fixture and native
control socket to unserve and re-serve its named profile, then stop and start only
its enrolled private slot. It checks that removal excludes the old authority,
re-serving preserves the home identity while advancing its epoch, and a successor
under the same supervisor/enrollment has a different launch/runtime and newer
profile epochs. Each lifecycle operation is issued once; pending replies are
reconciled by observation instead of replay. No model turn is requested.

These comparisons qualify observation freshness, not enforcement of a stale-token
refusal: there is no activation token in this contract. A saved receipt cannot
substitute for the current answering runtime. Retiring live writers, an observed
draining window, overflow, atomic idle admission, root-to-user enrollment and
shared activation remain separate qualification gates. The journey does not
manufacture those states or duplicate the native idle-admission contribution.

## Bound idle consumer prerequisite

The local integration carries the existing native `pause-if-idle` implementation
from upstream PR144790 (`62e405383bf7de73f9adbeec2e2613bd94501587`). It is an
unmerged dependency, not an installed runtime pin. The ordinary updater's
`pause-if-idle` contract remains unchanged.

An original runtime advertising `launch_binding_idle_protocol: 1` also exposes
`pause-if-idle-bound`. Its parameters are `expected_binding` (the exact original
`identify.launch_admission` object) and optional update `target`. The handler
recomputes the original kernel enrollment and complete live served-authority set
on the gateway loop, compares every JSON field/type, then calls the existing
native idle decision in that same loop step, with no await in between. Missing,
unavailable or different evidence returns `pausing: false`, `binding_refused:
true`, protocol1 and a fixed `binding_status` of `unavailable` or `mismatch`.
Matching evidence reports `binding_status: matched`; only the native idle decision
can report `pausing: true`. A matched but busy/stopping response is not acceptance.
A timeout/unknown response is not permission to replay or publish method bytes.

This is a cooperative same-UID freshness precondition, not authentication, a token
grant or an independent supervisor hold. Callers must use the bound verb and
verify its protocol/result; they must never fall back to the legacy updater or
`pause-for-update` when binding is required. It does not install an Arwen recovery
adapter, permit shared activation, or clear the held original effect journal.

`scripts/e2e_s6_bound_idle.py` drives genuine missing/partial/wrong-profile,
removed/re-served-authority and successor refusals through the original private
native control boundary. Every refusal must leave the same current runtime ready
with the same complete binding. It deliberately requests no matching pause or
model turn. Matching admission, busy-work/draining/retiring/overflow, installed
independent recovery and full activation remain separate qualification gates.
