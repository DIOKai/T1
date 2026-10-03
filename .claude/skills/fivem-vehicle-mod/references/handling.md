# handling.meta

Structure: `<CHandlingDataMgr><HandlingData><Item type="CHandlingData">…</Item></HandlingData></CHandlingDataMgr>`. Each car has one `<Item>` whose `<handlingName>` equals its vehicles.meta `handlingId`. Full real example: LividDS/lds-lorevehicles `data/sunrise1/handling.meta`.

Sources: field meanings and conversions come from the gtamods Handling.meta page (read via search snippets — the site is blocked here) and eddlm/Handling-Tools (measured in game; community). FiveM loader behaviour is from FiveM source code. Treat the "typical" numbers as starting points, not rules.

## How FiveM loads it
- Each handling.meta pushes its entries onto a per-`handlingName` stack; the **last loaded wins**, and the previous entry returns when that resource stops (HandlingDataManager.cpp). Two resources with the same handlingName silently override each other.
- If `handlingId` isn't found, the car uses **Adder** handling and the client logs `Couldn't find handling for hash %08x - returning ADDER instead!` (CrashFixes.cpp). "My car drives like an Adder" = this.
- Restart the resource (and respawn the car) after editing; live edits with vehicleDebug are client-side only.

## Fields

### Mass, aero, engine
| Field | Meaning | Typical |
|---|---|---|
| `fMass` | kg; mostly governs collisions with other entities (eddlm) | real car's weight |
| `fInitialDragCoeff` | drag multiplier; drag ≈ (speed × coeff × 0.0001)² g (eddlm) | ~0–20 |
| `fPercentSubmerged` | % of height submerged before floating | 85 road cars |
| `vecCentreOfMassOffset` | x/y/z metres; lower z = more stable | small values |
| `vecInertiaMultiplier` | rotational inertia x/y/z | default ~1.0 |
| `fDriveBiasFront` | 0.0 RWD, 1.0 FWD, between = AWD | AWD ~0.2–0.5 |
| `nInitialDriveGears` | stock gears (a transmission upgrade adds one — eddlm) | real car's gear count |
| `fInitialDriveForce` | engine power as target acceleration (g), scaled by gear | 0.2–0.5 |
| `fDriveInertia` | rev response; 1/value ≈ seconds idle→redline (eddlm) | ~1.0 |
| `fClutchChangeRateScaleUpShift` / `DownShift` | 1/value ≈ shift time | copy a similar vanilla car |
| `fInitialDriveMaxFlatVel` | redline speed in top gear, not guaranteed to be reached. ×0.82 ≈ mph, ×1.32 ≈ km/h (inverse: km/h × 0.75) | |

### Brakes and steering
| Field | Meaning | Typical |
|---|---|---|
| `fBrakeForce` | deceleration (g) per wheel | 0.4–1.0 |
| `fBrakeBiasFront` | 0 rear only, 1 front only, 0.5 equal | 0.55–0.7 (eddlm) |
| `fHandBrakeForce` | rear axle only | |
| `fSteeringLock` | inner-wheel lock (degrees) | 35–45 cars |

### Traction
| Field | Meaning | Typical |
|---|---|---|
| `fTractionCurveMax` / `fTractionCurveMin` | peak / sliding grip (g) | 1.8–2.8 |
| `fTractionCurveLateral` | slip angle (deg) at peak grip | 22.5 default, ~18 sports, ≤24 (eddlm) |
| `fTractionSpringDeltaMax` | height above ground where traction is lost | |
| `fLowSpeedTractionLossMult` | burnout at launch; lower = less wheelspin | |
| `fCamberStiffnesss` | drift behaviour — **three s's** is the game's spelling | |
| `fTractionBiasFront` | traction split; 0.0 or 1.0 = no traction on one axle | copy a similar vanilla car |
| `fTractionLossMult` | grip loss off-road; 1.0 normal | |

### Suspension and roll
`fSuspensionForce`, `fSuspensionCompDamp`, `fSuspensionReboundDamp`, `fSuspensionUpperLimit` / `fSuspensionLowerLimit` (metres, e.g. 0.12 / -0.16), `fSuspensionRaise`, `fSuspensionBiasFront`, `fAntiRollBarForce` (more = less roll), `fAntiRollBarBiasFront`, `fRollCentreHeightFront` / `Rear` (recommended about -0.15 to 0.15).

### Damage, value, flags
- `fCollisionDamageMult`, `fWeaponDamageMult`, `fDeformationDamageMult` (1 default, 0.5 half), `fEngineDamageMult`, `fPetrolTankVolume`, `fOilVolume`, `fSeatOffsetDistX/Y/Z`.
- The money field is **`nMonetaryValue`** (integer), not `fMonetaryValue`.
- `strModelFlags`, `strHandlingFlags`, `strDamageFlags`: hex strings, rightmost digit = first flag; `strAdvancedFlags` lives in `CCarHandlingData`. Copy from a similar vanilla car unless you know the flag bits.
- `AIHandling`: e.g. `AVERAGE`, `SPORTS_CAR`.

### SubHandlingData
Usually three slots: one `<Item type="CCarHandlingData">` and two `<Item type="NULL" />` for cars. Bikes use `CBikeHandlingData`, aircraft `CFlyingHandlingData`, boats `CBoatHandlingData`, trailers `CTrailerHandlingData`. Copy the block from a vanilla vehicle of the same type.

## Tuning workflow
1. Start from a similar vanilla car's handling (muto-atlas `/vehicle <vanilla>` gives its handlingId) or a preset (`fivem-handling show <preset>`; apply only with `-o` to a one-car file).
2. Set the obvious ones from the real car: `fMass`, `fDriveBiasFront`, `nInitialDriveGears`, top speed via `fInitialDriveMaxFlatVel` (km/h × 0.75).
3. On a dev server, tune in vehicleDebug: power (`fInitialDriveForce`), grip (`fTractionCurveMax/Min`, `Lateral`), brakes, suspension, centre of mass for roll-overs.
4. "Copy Handling", paste over the fields in the file, restart the resource, re-test with a fresh spawn.
5. Keep cars in the same class comparable (same server = shared economy and racing) — compare against 2–3 vanilla cars in that class.
