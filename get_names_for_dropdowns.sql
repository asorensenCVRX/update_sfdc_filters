SELECT
    A.ROLE,
    B.NAME,
    A.LNAME_REP,
    A.REP_EMAIL
FROM
    (
        SELECT
            *
        FROM
            qryRoster
        WHERE
            STATUS = 'ACTIVE'
            AND ROLE IN('REP')
            AND DOT IS NULL --UNION ALL 
            --SELECT *
            --FROM qryRoster
            --WHERE STATUS = 'ACTIVE' AND ROLE IN('FCE')
            --AND REP_EMAIL IN (
            --Select distinct OPP_OWNER_EMAIL
            --FROM qryOpps a WHERE A.OPP_STATUS = 'OPEN'
            --)
    ) AS A
    LEFT JOIN sfdcUser AS B ON A.REP_EMAIL = B.EMAIL
UNION
SELECT
    DISTINCT 'FCE',
    AM_FOR_CREDIT,
    b.LNAME_REP,
    AM_FOR_CREDIT_EMAIL --A.OPP_OWNER_NAME, a.OPP_OWNER_LNAME, OPP_OWNER_EMAIL
FROM
    qryOpps A
    LEFT JOIN (
        SELECT
            REP_EMAIL,
            LNAME_REP
        FROM
            qryRoster
        WHERE
            STATUS = 'ACTIVE'
            AND ROLE IN('FCE')
    ) b ON A.AM_FOR_CREDIT_EMAIL = B.REP_EMAIL
WHERE
    B.REP_EMAIL IS NOT NULL
    AND OPP_STATUS <> 'cancelled'
ORDER BY
    LNAME_REP