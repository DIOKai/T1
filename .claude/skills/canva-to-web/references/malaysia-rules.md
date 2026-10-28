# Malaysian rules for an F&B ordering site

Not legal or tax advice. These are the points that change what the site shows or charges; the owner confirms each with their accountant / the official page. Checked 2026-10 from the sources at the bottom; anything not confirmed from an official page is marked.

## SST (service tax on food and drink)
- **Rate:** F&B services are taxed at **6%** (most other taxable services moved to 8%; F&B kept 6%) — PwC 2025/26 tax booklet. Confirm on MySST before turning it on.
- **Who charges it:** only businesses **registered** with Customs. For restaurants/cafés the registration threshold is **RM1.5 million** taxable turnover in 12 months (most sources; one secondary source said RM500k — check MySST).
- **The template enforces it:** `sst_rate` can't be above 0 without `sst_reg_no` (database constraint, `menu_tool.py` error, staff form check). The cart shows the registration number when SST is charged. Charging "SST" without being registered is collecting a tax you're not allowed to collect — don't turn it on "to look official".
- **SST on the service charge:** `sst_on_service_charge` (default on). Whether the service charge is part of the taxable value is for the accountant to confirm (未验证 from an official page).
- **Service charge itself** isn't a tax. The template charges it on dine-in only by default (`service_charge_takeaway: false`); show it before the customer orders (the cart lists it line by line).

## Rounding cash to 5 sen (Bank Negara)
- Since 2008 the **total bill** paid **in cash over the counter** is rounded to the nearest 5 sen: ending 1, 2, 6, 7 down; 3, 4, 8, 9 up. Item prices are not rounded; card, e-wallet, DuitNow and bank transfers pay the exact amount.
- The template keeps `total_sen` exact and stores `cash_total_sen` separately; the customer page shows the cash figure only when it differs (`round_cash_to_5sen`).

## Halal claims
- The Trade Descriptions (Definition of Halal) Order 2011 and (Certification and Marking of Halal) Order 2011: only premises certified by JAKIM / the state religious authority may describe food as halal or show a halal logo. KPDN prosecutes misuse (several 2025 cases with fines; see sources).
- **The template enforces it:** the word "halal" appears only when `halal_cert` has a number and an unexpired `expires` date; `menu_tool.py` errors on halal / 清真 / حلال wording in menu text without a certificate.
- "Pork-free" / "no pork no lard" signs: JAKIM said in 2016 it had no official complaints about them, and the law targets halal claims — but such wording can still mislead Muslim customers. `menu_tool.py` treats it as an error; leave it out unless the owner decides otherwise after advice (then remove the pattern from `HALAL_WORDS`).

## Allergens
- Labelling rules in the Food Regulations 1985 cover **pre-packed** food; listing allergens on a café menu is good practice rather than a clear legal duty (未验证). If shown, they must be right: the sample menu's allergens are examples — the owner checks every item against supplier labels (milk, soy in chocolate/syrups, nuts in toppings, gluten in cookie crumbs).
- The template shows "Contains: …" per item from `allergens` and vegetarian/vegan from `dietary`. It does not merge allergens from chosen options; put an option's allergen on the item if it can contain it.

## Personal data (PDPA 2010, amended 2024)
- Collect only what the order needs: name, phone (required for takeaway), note. The checkout has an unticked consent box linked to `privacy.html`.
- **Notice in Bahasa Melayu and English:** s.7(3) requires the privacy notice in the national language and English. `privacy.html` is an English starting template; add the BM text before going live.
- **Breach notification** (guideline in force 1 June 2025): notify the Personal Data Protection Commissioner within **72 hours** of becoming aware of a breach that meets the harm threshold, and affected people when it is likely to cause significant harm. Thresholds for "significant scale" differ between sources (500 vs 1,000 people) — check the guideline.
- **DPO:** required for "large scale" processing; a single café is probably below the threshold (未验证 — read the DPO guideline).
- **Retention:** `purge_personal_data(days)` blanks names/phones on old orders and keeps amounts for tax records (keep the books as long as the accountant says; 7 years is the usual figure for business records, 未验证 for this case).
- Telegram alerts leave out the phone number (third party).

## DuitNow QR
- The template uses the shop's **static** DuitNow QR (from its bank or e-wallet provider): the customer pays the shown amount and types the order number as reference; staff tap "Mark paid" after seeing it in the bank app. Nothing is confirmed automatically — tell the owner.
- Fees: Bank Negara / PayNet said merchant fees (MDR) for DuitNow QR stay **waived for micro and small businesses** (2023 announcements); medium/large merchants may pay. Check with the bank.
- Dynamic QR with automatic confirmation needs a payment provider (paid) — see `online-payments.md`.

## e-Invoice (MyInvois)
- Being phased in by size. IRBM guideline v4.8 (Aug 2026) raised the exemption to annual turnover below **RM3 million** from 1 Sep 2026 (news reports; conditions on group structure apply). Most small cafés are exempt; the template does not issue e-invoices. Larger shops: their POS/accounting software handles it — ask the accountant.

## Sources
- SST rate/threshold: https://www.pwc.com/my/en/publications/mtb/service-tax.html , https://www.themalaysianinsight.com/s/91767 , MySST: https://mysst.customs.gov.my
- 5-sen rounding: https://www.bnm.gov.my/-/introduction-of-a-rounding-mechanism-for-over-the-counter-payments
- Halal enforcement: https://www.malaymail.com/news/malaysia/2025/01/13/jakim-kpdn-to-act-on-misuse-of-halal-logo-says-religious-affairs-minister/163102 , https://www.malaymail.com/news/malaysia/2016/02/19/jakim-no-official-complaints-on-pork-free-signs/1063663
- PDPA breach notification: https://cms.law/en/sgp/legal-updates/new-guidelines-on-mandatory-breach-notifications-under-malaysia-s-personal-data-protection-act-2010 , https://privacymatters.dlapiper.com/2025/03/malaysia-guidelines-issued-on-data-breach-notification-and-data-protection-officer-appointment/
- PDPA bilingual notice: https://www.deloitte.com/content/dam/assets-zone1/southeast-asia/en/docs/about/2025/sea-my-about-deloitte-notice-and-choice-principle-statement-noexp.pdf
- DuitNow QR fees: https://www.businesstoday.com.my/2023/09/29/bnm-msmes-will-continue-to-enjoy-zero-transaction-fees-for-qr-payment/
- e-Invoice RM3m exemption: https://www.businesstoday.com.my/2026/08/30/irb-says-1-1-million-to-benefit-from-rm3-million-e-invoice-exemption/
