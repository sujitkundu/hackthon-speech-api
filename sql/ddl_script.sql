CREATE TABLE IF NOT EXISTS public.name_pronunciation_details
(
    user_id text COLLATE pg_catalog."default" NOT NULL,
    first_name text COLLATE pg_catalog."default" NOT NULL,
    last_name text COLLATE pg_catalog."default" NOT NULL,
    short_name text COLLATE pg_catalog."default" NOT NULL,
    voice_path text COLLATE pg_catalog."default" NOT NULL,
    custom_voice_path text COLLATE pg_catalog."default",
    created_timestamp timestamp without time zone,
    phonetic text COLLATE pg_catalog."default",
    CONSTRAINT name_pronunciation_details_pkey PRIMARY KEY (user_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.name_pronunciation_details
    OWNER to yugabyte;