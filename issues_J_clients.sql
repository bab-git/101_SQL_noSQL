SELECT *
	-- prj.name
FROM 101redmine.issues as iss
Join 101redmine.projects as prj on iss.project_id = prj.id
where 
	-- iss.created_on >= "2019-07-01"
	-- and priority_id = 3
    -- iss.id in (54376,52329,52219,53634,52945,52956,52968)
    -- iss.id > 52215 and iss.id < 52230
    prj.name LIKE "Multiprofil%"
    -- Multiprofil GmbH