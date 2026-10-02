-- Update parent_id in financial_metrics_data table
UPDATE financial_metrics_data fmd_child
SET parent_id = (
    SELECT fmd_parent.id
    FROM financial_metrics_data fmd_parent
    WHERE fmd_parent.financial_type_id = (
        -- Get financial_type_id linked to either the metric or submetric
        SELECT fm.financial_type_id
        FROM financial_metric fm
        WHERE fm.id = COALESCE(
            -- If submetric exists, get its financial_metric_id
            (SELECT fsm.financial_metric_id FROM financial_submetric fsm WHERE fsm.id = fmd_child.financial_submetric_id),
            -- Else, use financial_metric_id directly
            fmd_child.financial_metric_id
        )
    )
    -- Ensure we are not assigning self as parent
    AND fmd_parent.id != fmd_child.id
    -- If multiple records exist, pick the latest one
    ORDER BY fmd_parent.date DESC
    LIMIT 1
)
WHERE fmd_child.parent_id IS NULL;  -- Update only if parent_id is NULL

-- Update parent_id in financial_annual_data table
UPDATE financial_annual_data fmd_child
SET parent_id = (
    SELECT fmd_parent.id
    FROM financial_annual_data fmd_parent
    WHERE fmd_parent.financial_type_id = (
        -- Get financial_type_id linked to either the metric or submetric
        SELECT fm.financial_type_id
        FROM financial_metric fm
        WHERE fm.id = COALESCE(
            -- If submetric exists, get its financial_metric_id
            (SELECT fsm.financial_metric_id FROM financial_submetric fsm WHERE fsm.id = fmd_child.financial_submetric_id),
            -- Else, use financial_metric_id directly
            fmd_child.financial_metric_id
        )
    )
    -- Ensure we are not assigning self as parent
    AND fmd_parent.id != fmd_child.id
    -- If multiple records exist, pick the latest one
    ORDER BY fmd_parent.date DESC
    LIMIT 1
)
WHERE fmd_child.parent_id IS NULL;  -- Update only if parent_id is NULL


-- Update parent_id in financial_cumulative_data table
UPDATE financial_cumulative_data fmd_child
SET parent_id = (
    SELECT fmd_parent.id
    FROM financial_cumulative_data fmd_parent
    WHERE fmd_parent.financial_type_id = (
        -- Get financial_type_id linked to either the metric or submetric
        SELECT fm.financial_type_id
        FROM financial_metric fm
        WHERE fm.id = COALESCE(
            -- If submetric exists, get its financial_metric_id
            (SELECT fsm.financial_metric_id FROM financial_submetric fsm WHERE fsm.id = fmd_child.financial_submetric_id),
            -- Else, use financial_metric_id directly
            fmd_child.financial_metric_id
        )
    )
    -- Ensure we are not assigning self as parent
    AND fmd_parent.id != fmd_child.id
    -- If multiple records exist, pick the latest one
    ORDER BY fmd_parent.date DESC
    LIMIT 1
)
WHERE fmd_child.parent_id IS NULL;  -- Update only if parent_id is NULL
