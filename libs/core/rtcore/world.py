"""World reference data for global compatibility [Committee; D-050; NFR-GLO-01].

ISO 3166-1 alpha-2 / alpha-3 codes, English short name, continent (seven, UN geoscheme style) and the ISO 4217 code of the
principal currency, for every country and territory the platform may be asked to model as a jurisdiction cell. The table
answers "is this a real place and what does it use?" — it never answers "may we operate there?" That question is the
dual-key legal record per cell (services/compliance) and stays [Open] until counsel evidences it.

User-assigned ISO codes (AA, QM–QZ, XA–XZ, ZZ) are accepted only as *simulated* jurisdictions and can never carry a
real legal basis. Reference rows are seeded from public ISO/UN lists by the Data Architect; a reviewer verifies them
against the current ISO 3166 and 4217 registers before any cell in that country is proposed for real (H-29).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

CONTINENTS: tuple[str, ...] = ("Africa", "Antarctica", "Asia", "Europe", "North America", "Oceania", "South America")
USER_ASSIGNED = re.compile(r"^(AA|Q[M-Z]|X[A-Z]|ZZ)$")
NO_CURRENCY = "XXX"  # ISO 4217 "no currency" (Antarctica)


@dataclass(frozen=True)
class Country:
    alpha2: str
    alpha3: str
    name: str
    continent: str
    currency: str


_ROWS: tuple[tuple[str, str, str, str, str], ...] = (
    # Africa
    ("DZ", "DZA", "Algeria", "Africa", "DZD"),
    ("AO", "AGO", "Angola", "Africa", "AOA"),
    ("BJ", "BEN", "Benin", "Africa", "XOF"),
    ("BW", "BWA", "Botswana", "Africa", "BWP"),
    ("BF", "BFA", "Burkina Faso", "Africa", "XOF"),
    ("BI", "BDI", "Burundi", "Africa", "BIF"),
    ("CV", "CPV", "Cabo Verde", "Africa", "CVE"),
    ("CM", "CMR", "Cameroon", "Africa", "XAF"),
    ("CF", "CAF", "Central African Republic", "Africa", "XAF"),
    ("TD", "TCD", "Chad", "Africa", "XAF"),
    ("KM", "COM", "Comoros", "Africa", "KMF"),
    ("CG", "COG", "Congo", "Africa", "XAF"),
    ("CD", "COD", "Congo, Democratic Republic of the", "Africa", "CDF"),
    ("CI", "CIV", "Côte d'Ivoire", "Africa", "XOF"),
    ("DJ", "DJI", "Djibouti", "Africa", "DJF"),
    ("EG", "EGY", "Egypt", "Africa", "EGP"),
    ("GQ", "GNQ", "Equatorial Guinea", "Africa", "XAF"),
    ("ER", "ERI", "Eritrea", "Africa", "ERN"),
    ("SZ", "SWZ", "Eswatini", "Africa", "SZL"),
    ("ET", "ETH", "Ethiopia", "Africa", "ETB"),
    ("GA", "GAB", "Gabon", "Africa", "XAF"),
    ("GM", "GMB", "Gambia", "Africa", "GMD"),
    ("GH", "GHA", "Ghana", "Africa", "GHS"),
    ("GN", "GIN", "Guinea", "Africa", "GNF"),
    ("GW", "GNB", "Guinea-Bissau", "Africa", "XOF"),
    ("KE", "KEN", "Kenya", "Africa", "KES"),
    ("LS", "LSO", "Lesotho", "Africa", "LSL"),
    ("LR", "LBR", "Liberia", "Africa", "LRD"),
    ("LY", "LBY", "Libya", "Africa", "LYD"),
    ("MG", "MDG", "Madagascar", "Africa", "MGA"),
    ("MW", "MWI", "Malawi", "Africa", "MWK"),
    ("ML", "MLI", "Mali", "Africa", "XOF"),
    ("MR", "MRT", "Mauritania", "Africa", "MRU"),
    ("MU", "MUS", "Mauritius", "Africa", "MUR"),
    ("YT", "MYT", "Mayotte", "Africa", "EUR"),
    ("MA", "MAR", "Morocco", "Africa", "MAD"),
    ("MZ", "MOZ", "Mozambique", "Africa", "MZN"),
    ("NA", "NAM", "Namibia", "Africa", "NAD"),
    ("NE", "NER", "Niger", "Africa", "XOF"),
    ("NG", "NGA", "Nigeria", "Africa", "NGN"),
    ("RE", "REU", "Réunion", "Africa", "EUR"),
    ("RW", "RWA", "Rwanda", "Africa", "RWF"),
    ("SH", "SHN", "Saint Helena, Ascension and Tristan da Cunha", "Africa", "SHP"),
    ("ST", "STP", "Sao Tome and Principe", "Africa", "STN"),
    ("SN", "SEN", "Senegal", "Africa", "XOF"),
    ("SC", "SYC", "Seychelles", "Africa", "SCR"),
    ("SL", "SLE", "Sierra Leone", "Africa", "SLE"),
    ("SO", "SOM", "Somalia", "Africa", "SOS"),
    ("ZA", "ZAF", "South Africa", "Africa", "ZAR"),
    ("SS", "SSD", "South Sudan", "Africa", "SSP"),
    ("SD", "SDN", "Sudan", "Africa", "SDG"),
    ("TZ", "TZA", "Tanzania, United Republic of", "Africa", "TZS"),
    ("TG", "TGO", "Togo", "Africa", "XOF"),
    ("TN", "TUN", "Tunisia", "Africa", "TND"),
    ("UG", "UGA", "Uganda", "Africa", "UGX"),
    ("EH", "ESH", "Western Sahara", "Africa", "MAD"),
    ("ZM", "ZMB", "Zambia", "Africa", "ZMW"),
    ("ZW", "ZWE", "Zimbabwe", "Africa", "ZWG"),
    ("IO", "IOT", "British Indian Ocean Territory", "Africa", "USD"),
    # Antarctica
    ("AQ", "ATA", "Antarctica", "Antarctica", "XXX"),
    ("BV", "BVT", "Bouvet Island", "Antarctica", "NOK"),
    ("TF", "ATF", "French Southern Territories", "Antarctica", "EUR"),
    ("HM", "HMD", "Heard Island and McDonald Islands", "Antarctica", "AUD"),
    ("GS", "SGS", "South Georgia and the South Sandwich Islands", "Antarctica", "GBP"),
    # Asia
    ("AF", "AFG", "Afghanistan", "Asia", "AFN"),
    ("AM", "ARM", "Armenia", "Asia", "AMD"),
    ("AZ", "AZE", "Azerbaijan", "Asia", "AZN"),
    ("BH", "BHR", "Bahrain", "Asia", "BHD"),
    ("BD", "BGD", "Bangladesh", "Asia", "BDT"),
    ("BT", "BTN", "Bhutan", "Asia", "BTN"),
    ("BN", "BRN", "Brunei Darussalam", "Asia", "BND"),
    ("KH", "KHM", "Cambodia", "Asia", "KHR"),
    ("CN", "CHN", "China", "Asia", "CNY"),
    ("CY", "CYP", "Cyprus", "Asia", "EUR"),
    ("GE", "GEO", "Georgia", "Asia", "GEL"),
    ("HK", "HKG", "Hong Kong", "Asia", "HKD"),
    ("IN", "IND", "India", "Asia", "INR"),
    ("ID", "IDN", "Indonesia", "Asia", "IDR"),
    ("IR", "IRN", "Iran, Islamic Republic of", "Asia", "IRR"),
    ("IQ", "IRQ", "Iraq", "Asia", "IQD"),
    ("IL", "ISR", "Israel", "Asia", "ILS"),
    ("JP", "JPN", "Japan", "Asia", "JPY"),
    ("JO", "JOR", "Jordan", "Asia", "JOD"),
    ("KZ", "KAZ", "Kazakhstan", "Asia", "KZT"),
    ("KP", "PRK", "Korea, Democratic People's Republic of", "Asia", "KPW"),
    ("KR", "KOR", "Korea, Republic of", "Asia", "KRW"),
    ("KW", "KWT", "Kuwait", "Asia", "KWD"),
    ("KG", "KGZ", "Kyrgyzstan", "Asia", "KGS"),
    ("LA", "LAO", "Lao People's Democratic Republic", "Asia", "LAK"),
    ("LB", "LBN", "Lebanon", "Asia", "LBP"),
    ("MO", "MAC", "Macao", "Asia", "MOP"),
    ("MY", "MYS", "Malaysia", "Asia", "MYR"),
    ("MV", "MDV", "Maldives", "Asia", "MVR"),
    ("MN", "MNG", "Mongolia", "Asia", "MNT"),
    ("MM", "MMR", "Myanmar", "Asia", "MMK"),
    ("NP", "NPL", "Nepal", "Asia", "NPR"),
    ("OM", "OMN", "Oman", "Asia", "OMR"),
    ("PK", "PAK", "Pakistan", "Asia", "PKR"),
    ("PS", "PSE", "Palestine, State of", "Asia", "ILS"),
    ("PH", "PHL", "Philippines", "Asia", "PHP"),
    ("QA", "QAT", "Qatar", "Asia", "QAR"),
    ("SA", "SAU", "Saudi Arabia", "Asia", "SAR"),
    ("SG", "SGP", "Singapore", "Asia", "SGD"),
    ("LK", "LKA", "Sri Lanka", "Asia", "LKR"),
    ("SY", "SYR", "Syrian Arab Republic", "Asia", "SYP"),
    ("TW", "TWN", "Taiwan, Province of China", "Asia", "TWD"),
    ("TJ", "TJK", "Tajikistan", "Asia", "TJS"),
    ("TH", "THA", "Thailand", "Asia", "THB"),
    ("TL", "TLS", "Timor-Leste", "Asia", "USD"),
    ("TR", "TUR", "Türkiye", "Asia", "TRY"),
    ("TM", "TKM", "Turkmenistan", "Asia", "TMT"),
    ("AE", "ARE", "United Arab Emirates", "Asia", "AED"),
    ("UZ", "UZB", "Uzbekistan", "Asia", "UZS"),
    ("VN", "VNM", "Viet Nam", "Asia", "VND"),
    ("YE", "YEM", "Yemen", "Asia", "YER"),
    # Europe
    ("AX", "ALA", "Åland Islands", "Europe", "EUR"),
    ("AL", "ALB", "Albania", "Europe", "ALL"),
    ("AD", "AND", "Andorra", "Europe", "EUR"),
    ("AT", "AUT", "Austria", "Europe", "EUR"),
    ("BY", "BLR", "Belarus", "Europe", "BYN"),
    ("BE", "BEL", "Belgium", "Europe", "EUR"),
    ("BA", "BIH", "Bosnia and Herzegovina", "Europe", "BAM"),
    ("BG", "BGR", "Bulgaria", "Europe", "BGN"),
    ("HR", "HRV", "Croatia", "Europe", "EUR"),
    ("CZ", "CZE", "Czechia", "Europe", "CZK"),
    ("DK", "DNK", "Denmark", "Europe", "DKK"),
    ("EE", "EST", "Estonia", "Europe", "EUR"),
    ("FO", "FRO", "Faroe Islands", "Europe", "DKK"),
    ("FI", "FIN", "Finland", "Europe", "EUR"),
    ("FR", "FRA", "France", "Europe", "EUR"),
    ("DE", "DEU", "Germany", "Europe", "EUR"),
    ("GI", "GIB", "Gibraltar", "Europe", "GIP"),
    ("GR", "GRC", "Greece", "Europe", "EUR"),
    ("GG", "GGY", "Guernsey", "Europe", "GBP"),
    ("VA", "VAT", "Holy See", "Europe", "EUR"),
    ("HU", "HUN", "Hungary", "Europe", "HUF"),
    ("IS", "ISL", "Iceland", "Europe", "ISK"),
    ("IE", "IRL", "Ireland", "Europe", "EUR"),
    ("IM", "IMN", "Isle of Man", "Europe", "GBP"),
    ("IT", "ITA", "Italy", "Europe", "EUR"),
    ("JE", "JEY", "Jersey", "Europe", "GBP"),
    ("LV", "LVA", "Latvia", "Europe", "EUR"),
    ("LI", "LIE", "Liechtenstein", "Europe", "CHF"),
    ("LT", "LTU", "Lithuania", "Europe", "EUR"),
    ("LU", "LUX", "Luxembourg", "Europe", "EUR"),
    ("MT", "MLT", "Malta", "Europe", "EUR"),
    ("MD", "MDA", "Moldova, Republic of", "Europe", "MDL"),
    ("MC", "MCO", "Monaco", "Europe", "EUR"),
    ("ME", "MNE", "Montenegro", "Europe", "EUR"),
    ("NL", "NLD", "Netherlands", "Europe", "EUR"),
    ("MK", "MKD", "North Macedonia", "Europe", "MKD"),
    ("NO", "NOR", "Norway", "Europe", "NOK"),
    ("PL", "POL", "Poland", "Europe", "PLN"),
    ("PT", "PRT", "Portugal", "Europe", "EUR"),
    ("RO", "ROU", "Romania", "Europe", "RON"),
    ("RU", "RUS", "Russian Federation", "Europe", "RUB"),
    ("SM", "SMR", "San Marino", "Europe", "EUR"),
    ("RS", "SRB", "Serbia", "Europe", "RSD"),
    ("SK", "SVK", "Slovakia", "Europe", "EUR"),
    ("SI", "SVN", "Slovenia", "Europe", "EUR"),
    ("ES", "ESP", "Spain", "Europe", "EUR"),
    ("SJ", "SJM", "Svalbard and Jan Mayen", "Europe", "NOK"),
    ("SE", "SWE", "Sweden", "Europe", "SEK"),
    ("CH", "CHE", "Switzerland", "Europe", "CHF"),
    ("UA", "UKR", "Ukraine", "Europe", "UAH"),
    ("GB", "GBR", "United Kingdom of Great Britain and Northern Ireland", "Europe", "GBP"),
    ("XK", "XKX", "Kosovo (user-assigned code in wide use)", "Europe", "EUR"),
    # North America (incl. Central America and the Caribbean)
    ("AI", "AIA", "Anguilla", "North America", "XCD"),
    ("AG", "ATG", "Antigua and Barbuda", "North America", "XCD"),
    ("AW", "ABW", "Aruba", "North America", "AWG"),
    ("BS", "BHS", "Bahamas", "North America", "BSD"),
    ("BB", "BRB", "Barbados", "North America", "BBD"),
    ("BZ", "BLZ", "Belize", "North America", "BZD"),
    ("BM", "BMU", "Bermuda", "North America", "BMD"),
    ("BQ", "BES", "Bonaire, Sint Eustatius and Saba", "North America", "USD"),
    ("VG", "VGB", "Virgin Islands (British)", "North America", "USD"),
    ("CA", "CAN", "Canada", "North America", "CAD"),
    ("KY", "CYM", "Cayman Islands", "North America", "KYD"),
    ("CR", "CRI", "Costa Rica", "North America", "CRC"),
    ("CU", "CUB", "Cuba", "North America", "CUP"),
    ("CW", "CUW", "Curaçao", "North America", "ANG"),
    ("DM", "DMA", "Dominica", "North America", "XCD"),
    ("DO", "DOM", "Dominican Republic", "North America", "DOP"),
    ("SV", "SLV", "El Salvador", "North America", "USD"),
    ("GL", "GRL", "Greenland", "North America", "DKK"),
    ("GD", "GRD", "Grenada", "North America", "XCD"),
    ("GP", "GLP", "Guadeloupe", "North America", "EUR"),
    ("GT", "GTM", "Guatemala", "North America", "GTQ"),
    ("HT", "HTI", "Haiti", "North America", "HTG"),
    ("HN", "HND", "Honduras", "North America", "HNL"),
    ("JM", "JAM", "Jamaica", "North America", "JMD"),
    ("MQ", "MTQ", "Martinique", "North America", "EUR"),
    ("MX", "MEX", "Mexico", "North America", "MXN"),
    ("MS", "MSR", "Montserrat", "North America", "XCD"),
    ("NI", "NIC", "Nicaragua", "North America", "NIO"),
    ("PA", "PAN", "Panama", "North America", "PAB"),
    ("PR", "PRI", "Puerto Rico", "North America", "USD"),
    ("BL", "BLM", "Saint Barthélemy", "North America", "EUR"),
    ("KN", "KNA", "Saint Kitts and Nevis", "North America", "XCD"),
    ("LC", "LCA", "Saint Lucia", "North America", "XCD"),
    ("MF", "MAF", "Saint Martin (French part)", "North America", "EUR"),
    ("PM", "SPM", "Saint Pierre and Miquelon", "North America", "EUR"),
    ("VC", "VCT", "Saint Vincent and the Grenadines", "North America", "XCD"),
    ("SX", "SXM", "Sint Maarten (Dutch part)", "North America", "ANG"),
    ("TT", "TTO", "Trinidad and Tobago", "North America", "TTD"),
    ("TC", "TCA", "Turks and Caicos Islands", "North America", "USD"),
    ("US", "USA", "United States of America", "North America", "USD"),
    ("UM", "UMI", "United States Minor Outlying Islands", "North America", "USD"),
    ("VI", "VIR", "Virgin Islands (U.S.)", "North America", "USD"),
    # Oceania
    ("AS", "ASM", "American Samoa", "Oceania", "USD"),
    ("AU", "AUS", "Australia", "Oceania", "AUD"),
    ("CX", "CXR", "Christmas Island", "Oceania", "AUD"),
    ("CC", "CCK", "Cocos (Keeling) Islands", "Oceania", "AUD"),
    ("CK", "COK", "Cook Islands", "Oceania", "NZD"),
    ("FJ", "FJI", "Fiji", "Oceania", "FJD"),
    ("PF", "PYF", "French Polynesia", "Oceania", "XPF"),
    ("GU", "GUM", "Guam", "Oceania", "USD"),
    ("KI", "KIR", "Kiribati", "Oceania", "AUD"),
    ("MH", "MHL", "Marshall Islands", "Oceania", "USD"),
    ("FM", "FSM", "Micronesia, Federated States of", "Oceania", "USD"),
    ("NR", "NRU", "Nauru", "Oceania", "AUD"),
    ("NC", "NCL", "New Caledonia", "Oceania", "XPF"),
    ("NZ", "NZL", "New Zealand", "Oceania", "NZD"),
    ("NU", "NIU", "Niue", "Oceania", "NZD"),
    ("NF", "NFK", "Norfolk Island", "Oceania", "AUD"),
    ("MP", "MNP", "Northern Mariana Islands", "Oceania", "USD"),
    ("PW", "PLW", "Palau", "Oceania", "USD"),
    ("PG", "PNG", "Papua New Guinea", "Oceania", "PGK"),
    ("PN", "PCN", "Pitcairn", "Oceania", "NZD"),
    ("WS", "WSM", "Samoa", "Oceania", "WST"),
    ("SB", "SLB", "Solomon Islands", "Oceania", "SBD"),
    ("TK", "TKL", "Tokelau", "Oceania", "NZD"),
    ("TO", "TON", "Tonga", "Oceania", "TOP"),
    ("TV", "TUV", "Tuvalu", "Oceania", "AUD"),
    ("VU", "VUT", "Vanuatu", "Oceania", "VUV"),
    ("WF", "WLF", "Wallis and Futuna", "Oceania", "XPF"),
    # South America
    ("AR", "ARG", "Argentina", "South America", "ARS"),
    ("BO", "BOL", "Bolivia, Plurinational State of", "South America", "BOB"),
    ("BR", "BRA", "Brazil", "South America", "BRL"),
    ("CL", "CHL", "Chile", "South America", "CLP"),
    ("CO", "COL", "Colombia", "South America", "COP"),
    ("EC", "ECU", "Ecuador", "South America", "USD"),
    ("FK", "FLK", "Falkland Islands (Malvinas)", "South America", "FKP"),
    ("GF", "GUF", "French Guiana", "South America", "EUR"),
    ("GY", "GUY", "Guyana", "South America", "GYD"),
    ("PY", "PRY", "Paraguay", "South America", "PYG"),
    ("PE", "PER", "Peru", "South America", "PEN"),
    ("SR", "SUR", "Suriname", "South America", "SRD"),
    ("UY", "URY", "Uruguay", "South America", "UYU"),
    ("VE", "VEN", "Venezuela, Bolivarian Republic of", "South America", "VES"),
)

COUNTRIES: dict[str, Country] = {r[0]: Country(*r) for r in _ROWS}

# --- ISO 4217 currencies ---------------------------------------------------------------------------------------
# The registry is the set of principal currencies of the country table (every country and territory above, so every
# continent is covered) plus the fund codes the platform is asked to price in. ``XXX`` ("no currency", Antarctica) is
# deliberately *not* a currency: an amount can never be denominated in it. Precious-metal codes (XAU, XAG, XPD, XPT)
# and the remaining fund codes are out of scope until an instrument needs them [Open: F-3 follow-up].
# Minor units are the ISO 4217 exponents; the exception lists below are the only non-2 cases in this set. Seeded from
# the public ISO register by the Data Architect and verified by a reviewer before any real cell uses them (H-29,
# same convention as the country table) [Open: H-29].
_MINOR_UNITS_0 = frozenset({"BIF", "CLP", "DJF", "GNF", "ISK", "JPY", "KMF", "KRW", "PYG", "RWF", "UGX", "VND", "VUV", "XAF", "XOF", "XPF"})
_MINOR_UNITS_3 = frozenset({"BHD", "IQD", "JOD", "KWD", "LYD", "OMR", "TND"})
_MINOR_UNITS_4 = frozenset({"CLF", "UYW"})  # fund codes (Chilean unidad de fomento, Uruguayan unidad previsional)
_EXTRA_CURRENCIES = frozenset(_MINOR_UNITS_4)


def _minor(code: str) -> int:
    if code in _MINOR_UNITS_0:
        return 0
    if code in _MINOR_UNITS_3:
        return 3
    if code in _MINOR_UNITS_4:
        return 4
    return 2


CURRENCIES: dict[str, int] = {
    code: _minor(code) for code in sorted(({c.currency for c in COUNTRIES.values()} - {NO_CURRENCY}) | _EXTRA_CURRENCIES)
}


def is_currency(code: str) -> bool:
    """True only for an exact, upper-case ISO 4217 code in the registry. ``XXX`` and unknown codes are False (fail closed)."""
    return code in CURRENCIES


def currency_minor_units(code: str) -> int:
    """ISO 4217 exponent (number of minor units) for a known code; raises KeyError for anything else."""
    return CURRENCIES[code]


def is_user_assigned(code: str) -> bool:
    """ISO 3166-1 user-assigned codes: valid only as simulated jurisdictions (never a legal basis)."""
    return bool(USER_ASSIGNED.match(code))


def country(code: str) -> Country:
    """Registry row for an alpha-2 code; raises KeyError for unknown codes (user-assigned codes are not in the registry)."""
    return COUNTRIES[code]


def is_valid_country(code: str) -> bool:
    return code in COUNTRIES


def countries_by_continent(continent: str) -> tuple[Country, ...]:
    return tuple(c for c in COUNTRIES.values() if c.continent == continent)


def continents() -> tuple[str, ...]:
    return CONTINENTS
