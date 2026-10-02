-- Update last_year_total for 2025
UPDATE cashflow_data curr
SET last_year_total = COALESCE(prev.current_year_total, 0)
FROM cashflow_data prev
WHERE curr.entity_id = prev.entity_id
  AND curr.entity_type = prev.entity_type
  AND curr.year = prev.year + 1
and curr.year = 2025 ;


-- Update current_year_total for 2025
UPDATE cashflow_data
SET current_year_total =
    COALESCE(jan, 0) +
    COALESCE(feb, 0) +
    COALESCE(mar, 0) +
    COALESCE(apr, 0) +
    COALESCE(may, 0) +
    COALESCE(jun, 0) +
    COALESCE(jul, 0) +
    COALESCE(aug, 0) +
    COALESCE(sep, 0) +
    COALESCE(oct, 0) +
    COALESCE(nov, 0) +
    COALESCE(dec, 0)
where year=2025;


UPDATE cashflow_data
SET
    current_year_total = COALESCE(current_year_total, 0.0) / 1000000.0,
    jan = COALESCE(jan, 0.0) / 1000000.0,
    feb = COALESCE(feb, 0.0) / 1000000.0,
    mar = COALESCE(mar, 0.0) / 1000000.0,
    apr = COALESCE(apr, 0.0) / 1000000.0,
    may = COALESCE(may, 0.0) / 1000000.0,
    jun = COALESCE(jun, 0.0) / 1000000.0,
    jul = COALESCE(jul, 0.0) / 1000000.0,
    aug = COALESCE(aug, 0.0) / 1000000.0,
    sep = COALESCE(sep, 0.0) / 1000000.0,
    oct = COALESCE(oct, 0.0) / 1000000.0,
    nov = COALESCE(nov, 0.0) / 1000000.0,
    dec = COALESCE(dec, 0.0) / 1000000.0
WHERE year = 2025;
