# Reading a plan into numbers

Sources are listed at the end. "Rule of thumb" marks values that are common practice, not a code requirement.

## 1. Scale, most trusted first

1. **Dimension strings** (`12'-6"`, `3600`, `3.6`): measure the pixels between the two extension-line ends, divide by the stated length → px per metre. Take two or more in X and two or more in Y. If X and Y differ by more than ~2 %, the image was stretched (common on listing sites): rescale one axis before anything else.
2. **Scale bar**: same method. A printed "1:100" only holds on the original vector PDF at original size — a screenshot breaks it.
3. **Room-size labels** ("Bedroom 11'2" × 10'6""): usually wall-face to wall-face (interior clear size), not centre lines. Rule of thumb; check against a dimension string if there is one.
4. **Standard parts** (when there are no numbers at all): measure 3–5 doors and take the median; the door swing arc's radius equals the leaf width. Report the result as an estimate (±5–10 %).
   - USA: the IRC requires at least one egress door with ≥ 32 in clear width and ≥ 78 in clear height; that needs a 36 in door. Interior doors have no minimum; 28–32 in are common (rule of thumb).
   - UK: the most common internal door is 1981 × 762 mm; metric series 2040 × 526–926 mm (retailer guides).
   - Malaysia: the UBBL door-width and ceiling-height numbers were not verified from the by-law text — ask the user or the drawings, don't quote a number as law.
5. **Ceiling height**: plans rarely show it. Section/elevation → listing text ("9 ft ceilings") → photos (door ≈ 2.03 m against the ceiling) → default (US 8 ft = 2.44 m, newer houses 9 ft — rule of thumb) and tell the user it is a default.

## 2. Units
Store metres only. Parse `12'-6"`, `12' 6"`, `12.5'`, `3600` (mm), `3.6` (m); keep the original string in `scale.samples[].label` so it can be checked. 1 ft = 0.3048 m, 1 in = 0.0254 m, 1 m² = 10.7639 ft².

## 3. Wall thickness and where dimensions are measured
- US wood frame: exterior dimensions usually go to the outside face of studs; interior partitions to their centre lines. Masonry is dimensioned to faces. This is convention, not a single standard — read the drawing's notes.
- Typical thicknesses (rule of thumb): 2×4 stud + two 1/2 in boards ≈ 0.115 m; exterior 2×6 + cladding 0.17–0.2 m; brick walls in Malaysia/Asia often ~0.23 m outside, ~0.115 m inside (not verified). The repo's Bonsai skills default to 0.2 m exterior and 0.1 m interior.
- Measure the drawn line thickness (thick = exterior), round to the nearest common value, and set `thickness_source` to `measured` or `default`.
- Pick `justify` so the dimensions you read land on the right face: if the plan dimensions the outside face, draw the exterior path on that face and justify the wall inwards.

## 4. When dimensions are missing
- Only a total area: scale the outline by `k = sqrt(listing_area / measured_area)`.
- Some rooms dimensioned: scale from those, convert the rest by pixels, and list which were measured and which derived.
- Photos only: doors, standard tiles (300/600 mm or 12/24 in), kitchen counters (~0.9 m high, ~0.6 m deep) give rough sizes (rule of thumb). Confirm key sizes with the user.
- AI reference images: style reference only; they have no trustworthy dimensions.

## 5. Checking against the listing area
ANSI Z765 (used for US single-family homes) measures to the exterior finished surface, counts finished above-grade area only, excludes garages, unfinished basements and porches, and does not apply to condos/co-ops. Scan services such as iGUIDE include interior walls. Listing-site areas often come from public records and may be wrong for remodelled homes. So treat the listing area as a rough check: room floors summed are normally a few percent below it; more than ~15 % off means a missed room or a wrong scale.

## Sources
- IRC R311.2 summary: https://buildingcodetrainer.com/front-door-size-residential-egress/ (secondary; the ICC page could not be fetched)
- UK door sizes: https://www.howarth-timber.co.uk/help-advice/uk-door-sizes
- Malaysian room minima (UBBL by-law 42 via PAM): https://pam.org.my/images/resources/bureau/Category_C_-_Building_Control-2025.pdf
- Dimensioning conventions: https://forums.augi.com/archive/index.php/t-59740.html , https://community.graphisoft.com/t5/Documentation/Dimension-to-CENTER-of-walls/td-p/113255
- ANSI Z765 summaries: https://www.mckissock.com/blog/appraisal/appraisal-career/freddie-mac-announces-adoption-of-ansi-measurement-standard/ , https://www.opendoor.com/articles/how-to-measure-square-footage
- iGUIDE method: https://help.youriguide.com/support-center/floorplans-and-measurements/information/iguide-method-of-measurement
