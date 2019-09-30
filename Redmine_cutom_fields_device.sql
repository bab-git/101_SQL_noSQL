SELECT * FROM 101redmine.custom_values 
where 
-- custom_field_id = 95   -- PC name
-- custom_field_id = 150  -- server or not?
-- custom_field_id = 100  -- standort --> site
-- and value is not null
customized_id = 4229     -- ticket id
-- order by customized_id desc