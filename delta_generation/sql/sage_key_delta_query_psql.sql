-- total_real_value (yearly)
SELECT sage_sage_source_key,SUM(real_value::numeric) AS total_real_value
FROM (
    SELECT *
    FROM (
        SELECT
            CASE
                WHEN YANNEE_0 IS NOT NULL
                 AND ymois_0  IS NOT NULL
                THEN TO_CHAR(
                        TO_DATE(
                            YANNEE_0::text || LPAD(ymois_0::text, 2, '0') || '01',
                            'YYYYMMDD'
                        ),
                        'YYYY-MM-DD'
                     )
                ELSE NULL
            END AS report_date,

            MAX(
                CASE
                    WHEN COL_0 = '0'
                     AND AMTVAL_0 IS NOT NULL
                     AND STRPOS(AMTVAL_0, '-') > 0
                    THEN SUBSTRING(AMTVAL_0 FROM '^[^-]+')
                END
            ) AS sage_sage_source_key,

            MAX(
                CASE
                    WHEN COL_0 = '0'
                     AND AMTVAL_0 IS NOT NULL
                     AND STRPOS(AMTVAL_0, '-') > 0
                    THEN SUBSTRING(AMTVAL_0 FROM '-([^-]+)')
                END
            ) AS metric_name,

            MAX(CASE WHEN COL_0 = '1' THEN AMTVAL_0 END) AS real_value,

            LIG_0,
            ymois_0
        FROM MOOV.YEXPTDB
        WHERE VERSION_0 = 'YEXPTDB'
          AND IND_0 = '0'
          AND TXSNAM_0 = %s
          AND COL_0 IN ('0', '1')
          AND YANNEE_0 = %s
          AND ymois_0 <= %s
        GROUP BY LIG_0, ymois_0, YANNEE_0
    ) abc
    WHERE sage_sage_source_key = %s
ORDER BY LIG_0, ymois_0) abf
GROUP  BY sage_sage_source_key;
