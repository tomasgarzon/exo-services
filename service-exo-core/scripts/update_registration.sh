#  POSTGRES

UPDATE django_content_type SET app_label='registration' WHERE app_label='certification';
ALTER TABLE certification_exocertification RENAME TO registration_exocertification;
UPDATE django_migrations SET app='registration' WHERE app='certification';

