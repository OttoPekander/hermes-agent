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
