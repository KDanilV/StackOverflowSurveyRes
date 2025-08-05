CREATE VIEW countrytoplanguages AS 
(WITH lang_in_countries AS
(SELECT m."ResponseId" ind, 
"LanguageHaveWorkedWith" Language, 
"Country" country
FROM main m JOIN public.languagehaveworkedwith l
ON m."ResponseId" = l."ResponseId"),
LanguageCounts AS (
    SELECT 
        Country,
        Language,
        COUNT(*) AS LanguageCount
    FROM lang_in_countries
    GROUP BY Country, Language
),
RankedLanguages AS (
    SELECT 
        Country,
        Language,
        LanguageCount,
		        ROW_NUMBER() OVER (
            PARTITION BY Country 
            ORDER BY LanguageCount DESC, Language ASC) AS RowNum 
    FROM LanguageCounts
)

SELECT 
    Country,
    Language AS MostPopularLanguage,
    LanguageCount AS UsageCount
FROM RankedLanguages
WHERE RowNum = 1 AND Country IS NOT NULL
ORDER BY Country);