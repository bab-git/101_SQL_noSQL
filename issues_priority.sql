SELECT 
	priority_id,
    COUNT(*)
FROM 
	101redmine.issues
-- where 
where 
	created_on >= "2019-06-01"
    -- between "2014-06-01" and "2014-07-01"
-- 	priority_id = 2
    -- project_id = 4
-- LIMIT 100
group by
	priority_idcd 