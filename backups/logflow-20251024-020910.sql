--
-- PostgreSQL database dump
--

\restrict gpuVPkNTK74YMHZYU5Fyt80L5P1Gg9xrDN63jV7C5XPz06GOgnqXfFNF3dY0ebN

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alert_rules; Type: TABLE; Schema: public; Owner: logflow
--

CREATE TABLE public.alert_rules (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    query text NOT NULL,
    condition character varying(50) NOT NULL,
    threshold double precision NOT NULL,
    time_window integer NOT NULL,
    services json,
    levels json,
    notification_channel character varying(50) NOT NULL,
    notification_config json,
    is_active boolean DEFAULT true,
    last_triggered timestamp without time zone,
    trigger_count integer DEFAULT 0,
    owner_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.alert_rules OWNER TO logflow;

--
-- Name: alert_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: logflow
--

CREATE SEQUENCE public.alert_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alert_rules_id_seq OWNER TO logflow;

--
-- Name: alert_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: logflow
--

ALTER SEQUENCE public.alert_rules_id_seq OWNED BY public.alert_rules.id;


--
-- Name: system_config; Type: TABLE; Schema: public; Owner: logflow
--

CREATE TABLE public.system_config (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value json NOT NULL,
    description text,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.system_config OWNER TO logflow;

--
-- Name: system_config_id_seq; Type: SEQUENCE; Schema: public; Owner: logflow
--

CREATE SEQUENCE public.system_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_config_id_seq OWNER TO logflow;

--
-- Name: system_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: logflow
--

ALTER SEQUENCE public.system_config_id_seq OWNED BY public.system_config.id;


--
-- Name: triggered_alerts; Type: TABLE; Schema: public; Owner: logflow
--

CREATE TABLE public.triggered_alerts (
    id integer NOT NULL,
    rule_id integer,
    triggered_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    value double precision NOT NULL,
    threshold double precision NOT NULL,
    log_count integer,
    sample_logs json,
    status character varying(20) DEFAULT 'triggered'::character varying,
    acknowledged_at timestamp without time zone,
    acknowledged_by integer,
    resolved_at timestamp without time zone,
    notes text
);


ALTER TABLE public.triggered_alerts OWNER TO logflow;

--
-- Name: triggered_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: logflow
--

CREATE SEQUENCE public.triggered_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.triggered_alerts_id_seq OWNER TO logflow;

--
-- Name: triggered_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: logflow
--

ALTER SEQUENCE public.triggered_alerts_id_seq OWNED BY public.triggered_alerts.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: logflow
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(100),
    is_active boolean DEFAULT true,
    is_admin boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO logflow;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: logflow
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO logflow;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: logflow
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: alert_rules id; Type: DEFAULT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.alert_rules ALTER COLUMN id SET DEFAULT nextval('public.alert_rules_id_seq'::regclass);


--
-- Name: system_config id; Type: DEFAULT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.system_config ALTER COLUMN id SET DEFAULT nextval('public.system_config_id_seq'::regclass);


--
-- Name: triggered_alerts id; Type: DEFAULT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.triggered_alerts ALTER COLUMN id SET DEFAULT nextval('public.triggered_alerts_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alert_rules; Type: TABLE DATA; Schema: public; Owner: logflow
--

COPY public.alert_rules (id, name, description, query, condition, threshold, time_window, services, levels, notification_channel, notification_config, is_active, last_triggered, trigger_count, owner_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: system_config; Type: TABLE DATA; Schema: public; Owner: logflow
--

COPY public.system_config (id, key, value, description, updated_at) FROM stdin;
1	alert_check_interval	{"seconds": 60}	How often to check alert rules (in seconds)	2025-10-23 20:33:34.97865
2	max_alerts_per_rule	{"count": 100}	Maximum number of triggered alerts to keep per rule	2025-10-23 20:33:34.97865
3	log_retention_days	{"days": 30}	How long to keep logs in Elasticsearch	2025-10-23 20:33:34.97865
\.


--
-- Data for Name: triggered_alerts; Type: TABLE DATA; Schema: public; Owner: logflow
--

COPY public.triggered_alerts (id, rule_id, triggered_at, value, threshold, log_count, sample_logs, status, acknowledged_at, acknowledged_by, resolved_at, notes) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: logflow
--

COPY public.users (id, username, email, hashed_password, full_name, is_active, is_admin, created_at, updated_at) FROM stdin;
1	admin	admin@logflow.local	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lk3v8Z8qU8yK	System Administrator	t	t	2025-10-23 20:33:34.977582	2025-10-23 20:33:34.977582
\.


--
-- Name: alert_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: logflow
--

SELECT pg_catalog.setval('public.alert_rules_id_seq', 1, false);


--
-- Name: system_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: logflow
--

SELECT pg_catalog.setval('public.system_config_id_seq', 3, true);


--
-- Name: triggered_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: logflow
--

SELECT pg_catalog.setval('public.triggered_alerts_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: logflow
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alert_rules alert_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.alert_rules
    ADD CONSTRAINT alert_rules_pkey PRIMARY KEY (id);


--
-- Name: system_config system_config_key_key; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_key_key UNIQUE (key);


--
-- Name: system_config system_config_pkey; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_pkey PRIMARY KEY (id);


--
-- Name: triggered_alerts triggered_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.triggered_alerts
    ADD CONSTRAINT triggered_alerts_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: alert_rules alert_rules_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.alert_rules
    ADD CONSTRAINT alert_rules_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: triggered_alerts triggered_alerts_acknowledged_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.triggered_alerts
    ADD CONSTRAINT triggered_alerts_acknowledged_by_fkey FOREIGN KEY (acknowledged_by) REFERENCES public.users(id);


--
-- Name: triggered_alerts triggered_alerts_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: logflow
--

ALTER TABLE ONLY public.triggered_alerts
    ADD CONSTRAINT triggered_alerts_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.alert_rules(id);


--
-- PostgreSQL database dump complete
--

\unrestrict gpuVPkNTK74YMHZYU5Fyt80L5P1Gg9xrDN63jV7C5XPz06GOgnqXfFNF3dY0ebN

