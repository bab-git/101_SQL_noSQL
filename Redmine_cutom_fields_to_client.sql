SELECT 
-- * 
	iss.id as issue_id,
    prj.name as client,
    cv.value as site        

FROM 101redmine.custom_values as cv
join 101redmine.issues as iss on cv.customized_id = iss.id
join 101redmine.projects as prj on iss.project_id = prj.id
where 
-- cv.custom_field_id = 95   -- PC name
-- cv.custom_field_id = 150  -- server or not?
cv.custom_field_id = 150  -- standort --> site
and cv.value is not null
-- and prj.name not like "Pixformance%"
-- cv.customized_id = 54376     -- ticket id
order by issue_id desc
-- order by client desc