# Harmonization Keys

## Time Keys
- `year`: four-digit year as string (e.g., "2013")
- Coverage in Eurostat energy file: 2013–2024 (missing allowed)

## Geography Keys
- `geo`: ISO-like country code in Eurostat file (e.g., AT, DE, FR)
- Mapping to NUTS1 (if needed): use standard Eurostat NUTS correspondences

### Notes
- For country-level sources, `geo` is sufficient.
- For subnational integration later (NUTS1/2/3), add keys:
  - `nuts_level`: {1,2,3}
  - `nuts_code`: official NUTS code
- Maintain stable code lists and refer to the Eurostat NUTS reference for vintage alignment.
