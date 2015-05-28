--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: b3c; Tablespace: 
--

CREATE TABLE groups (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.groups OWNER TO b3c;

--
-- Name: principals; Type: TABLE; Schema: public; Owner: b3c; Tablespace: 
--

CREATE TABLE principals (
    id integer NOT NULL
);


ALTER TABLE public.principals OWNER TO b3c;

--
-- Name: principals_id; Type: SEQUENCE; Schema: public; Owner: b3c
--

CREATE SEQUENCE principals_id
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.principals_id OWNER TO b3c;

--
-- Name: role_assignment_id; Type: SEQUENCE; Schema: public; Owner: b3c
--

CREATE SEQUENCE role_assignment_id
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.role_assignment_id OWNER TO b3c;

--
-- Name: role_assignments; Type: TABLE; Schema: public; Owner: b3c; Tablespace: 
--

CREATE TABLE role_assignments (
    id integer NOT NULL,
    principal_id integer,
    name character varying(64)
);


ALTER TABLE public.role_assignments OWNER TO b3c;

--
-- Name: user_auth; Type: TABLE; Schema: public; Owner: b3c; Tablespace: 
--

CREATE TABLE user_auth (
    id integer NOT NULL,
    login character varying,
    name character varying,
    password character varying,
    salt character varying(12),
    enabled boolean,
    email character varying(40)
);


ALTER TABLE public.user_auth OWNER TO b3c;

--
-- Name: user_auth_id_seq; Type: SEQUENCE; Schema: public; Owner: b3c
--

CREATE SEQUENCE user_auth_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.user_auth_id_seq OWNER TO b3c;

--
-- Name: user_auth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: b3c
--

ALTER SEQUENCE user_auth_id_seq OWNED BY user_auth.id;


--
-- Name: user_groups; Type: TABLE; Schema: public; Owner: b3c; Tablespace: 
--

CREATE TABLE user_groups (
    user_id integer,
    group_id integer
);


ALTER TABLE public.user_groups OWNER TO b3c;

--
-- Name: users; Type: TABLE; Schema: public; Owner: b3c; Tablespace: 
--

CREATE TABLE users (
    id integer NOT NULL,
    login character varying,
    name character varying,
    password character varying,
    salt character varying(12),
    enabled boolean,
    email character varying(40),
    portal_skin character varying(20),
    listed integer,
    login_time timestamp without time zone,
    last_login_time timestamp without time zone,
    fullname character varying(40),
    error_log_update double precision,
    home_page character varying(40),
    location character varying(40),
    description text,
    language character varying(20),
    ext_editor integer,
    wysiwyg_editor character varying(10),
    visible_ids integer,
    firstname character varying(30),
    lastname character varying(30),
    join_time timestamp without time zone,
    gender character varying(10),
    city character varying(20),
    date_created timestamp without time zone NOT NULL,
    date_of_birth timestamp without time zone,
    date_updated timestamp without time zone,
    genres character varying(20),
    street character varying(40),
    house_number character varying(8),
    zip_code character varying(5),
    sport character varying(20),
    car character varying(20),
    income character varying(15),
    family_status character varying(15),
    education character varying(25),
    flags integer,
    country character varying(20),
    cell_number character varying(15)
);


ALTER TABLE public.users OWNER TO b3c;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: b3c
--

ALTER TABLE user_auth ALTER COLUMN id SET DEFAULT nextval('user_auth_id_seq'::regclass);


--
-- Name: groups_name_key; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_name_key UNIQUE (name);


--
-- Name: groups_pkey; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: principals_pkey; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY principals
    ADD CONSTRAINT principals_pkey PRIMARY KEY (id);


--
-- Name: role_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY role_assignments
    ADD CONSTRAINT role_assignments_pkey PRIMARY KEY (id);


--
-- Name: user_auth_pkey; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY user_auth
    ADD CONSTRAINT user_auth_pkey PRIMARY KEY (id);


--
-- Name: users_login_key; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users_name_key; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_name_key UNIQUE (name);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: b3c; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: groups_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: b3c
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_id_fkey FOREIGN KEY (id) REFERENCES principals(id);


--
-- Name: role_assignments_principal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: b3c
--

ALTER TABLE ONLY role_assignments
    ADD CONSTRAINT role_assignments_principal_id_fkey FOREIGN KEY (principal_id) REFERENCES principals(id);


--
-- Name: user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: b3c
--

ALTER TABLE ONLY user_groups
    ADD CONSTRAINT user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES groups(id);


--
-- Name: user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: b3c
--

ALTER TABLE ONLY user_groups
    ADD CONSTRAINT user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: users_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: b3c
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_id_fkey FOREIGN KEY (id) REFERENCES principals(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: gscs0001
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM gscs0001;
GRANT ALL ON SCHEMA public TO gscs0001;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

