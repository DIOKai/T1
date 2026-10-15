# Point auditor

Run from the skill directory using Python 3. No network or third-party package is needed.

~~~powershell
python scripts/audit_points.py survey.csv --order PNEZD --header --units m --crs "Project supplied CRS" --vertical-datum "Project benchmark datum" --output survey-qc.json
~~~

P = point ID, N = northing, E = easting, Z = elevation, D = description. Order must contain P/N/E/Z once, with optional D. Declare --header or --no-header. Header labels are recorded as evidence; --order controls interpretation, so the caller must verify they match.

CSV defaults: comma delimiter, UTF-8 with optional BOM. For semicolon CSV add --delimiter ";". The word 'tab' selects a tab delimiter. Use --encoding only with a known source encoding. Decimal fields use a dot; a comma decimal or thousands separator is not inferred.

--units accepts m, mm, ft or us-ft and applies to all three axes. Reported bounds are converted to metres using declared units; this is a unit conversion, not a CRS transform. For mixed-axis units or geographic degrees, use a separate verified parser.

Optional --bounds takes MIN_E MAX_E MIN_N MAX_N MIN_Z MAX_Z in metres.
Optional --max-z-deviation takes a nonnegative distance in metres from the median valid Z; it flags candidates, not proven blunders.

The helper records SHA-256, original point IDs, source line numbers, row and valid-point counts, duplicate IDs, exact duplicate XYZ, same XY/different Z, numeric failures and optional threshold findings. Unknown CRS/vertical datum is a review finding. Empty files and malformed rows block the structural audit. Blank lines are reported.

Status and exit codes:
- 0: clear-limited; no findings in this limited audit.
- 1: blocked or review-required; inspect the JSON findings.
- 2: argument/input/output failure, including an existing output file.

Output creation is exclusive: it never overwrites an existing report or input file. Without --output JSON goes to stdout. A clear-limited result does not prove correct axis order, CRS, field accuracy, coverage, boundary or control tolerance; these remain manual/unperformed checks.
