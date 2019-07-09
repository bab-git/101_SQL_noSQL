SELECT 
	iss.id,
	prj.name,
    iss.subject
    -- *
FROM 101redmine.issues as iss
Join 101redmine.projects as prj on iss.project_id = prj.id
where 
	-- iss.created_on >= "2019-07-01"
	-- and priority_id = 3
    iss.id in (52945,52956,52968)