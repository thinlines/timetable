--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: class_enrollments; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.class_enrollments (
    id integer NOT NULL,
    scheduled_class_id integer,
    student_id integer,
    enrollment_status character varying(20) DEFAULT 'enrolled'::character varying
);


ALTER TABLE public.class_enrollments OWNER TO randy;

--
-- Name: class_enrollments_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.class_enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_enrollments_id_seq OWNER TO randy;

--
-- Name: class_enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.class_enrollments_id_seq OWNED BY public.class_enrollments.id;


--
-- Name: class_sections; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.class_sections (
    id integer NOT NULL,
    course_id integer,
    section_name character varying(10),
    max_students integer DEFAULT 24,
    semester character varying(10),
    is_active boolean DEFAULT true
);


ALTER TABLE public.class_sections OWNER TO randy;

--
-- Name: class_sections_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.class_sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_sections_id_seq OWNER TO randy;

--
-- Name: class_sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.class_sections_id_seq OWNED BY public.class_sections.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    department character varying(100),
    periods_per_week integer NOT NULL,
    is_mandatory boolean DEFAULT false,
    is_elective boolean DEFAULT false,
    requires_consecutive_periods boolean DEFAULT false,
    preferred_facility_type character varying(50),
    requires_specific_facility boolean DEFAULT false,
    grade_levels jsonb,
    notes text,
    CONSTRAINT courses_periods_per_week_check CHECK (((periods_per_week >= 1) AND (periods_per_week <= 6)))
);


ALTER TABLE public.courses OWNER TO randy;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO randy;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: facilities; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.facilities (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    facility_type character varying(50),
    capacity integer DEFAULT 24,
    can_split boolean DEFAULT false,
    split_capacity integer,
    notes text
);


ALTER TABLE public.facilities OWNER TO randy;

--
-- Name: facilities_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.facilities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.facilities_id_seq OWNER TO randy;

--
-- Name: facilities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.facilities_id_seq OWNED BY public.facilities.id;


--
-- Name: homerooms; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.homerooms (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    capacity integer DEFAULT 24,
    grade_level integer,
    room_type character varying(20) DEFAULT 'homeroom'::character varying,
    CONSTRAINT homerooms_grade_level_check CHECK ((grade_level = ANY (ARRAY[10, 11, 12])))
);


ALTER TABLE public.homerooms OWNER TO randy;

--
-- Name: homerooms_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.homerooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.homerooms_id_seq OWNER TO randy;

--
-- Name: homerooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.homerooms_id_seq OWNED BY public.homerooms.id;


--
-- Name: scheduled_classes; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.scheduled_classes (
    id integer NOT NULL,
    class_section_id integer,
    teacher_id integer,
    facility_id integer,
    time_period_id integer,
    week_pattern character varying(50) DEFAULT 'all'::character varying,
    is_double_period boolean DEFAULT false,
    linked_period_id integer,
    semester character varying(10),
    notes text
);


ALTER TABLE public.scheduled_classes OWNER TO randy;

--
-- Name: scheduled_classes_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.scheduled_classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scheduled_classes_id_seq OWNER TO randy;

--
-- Name: scheduled_classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.scheduled_classes_id_seq OWNED BY public.scheduled_classes.id;


--
-- Name: scheduling_constraints; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.scheduling_constraints (
    id integer NOT NULL,
    constraint_type character varying(50),
    constraint_value jsonb,
    is_active boolean DEFAULT true,
    description text
);


ALTER TABLE public.scheduling_constraints OWNER TO randy;

--
-- Name: scheduling_constraints_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.scheduling_constraints_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scheduling_constraints_id_seq OWNER TO randy;

--
-- Name: scheduling_constraints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.scheduling_constraints_id_seq OWNED BY public.scheduling_constraints.id;


--
-- Name: semester_config; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.semester_config (
    id integer NOT NULL,
    semester character varying(10) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    weeks_count integer DEFAULT 18,
    is_current boolean DEFAULT false,
    notes text
);


ALTER TABLE public.semester_config OWNER TO randy;

--
-- Name: semester_config_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.semester_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.semester_config_id_seq OWNER TO randy;

--
-- Name: semester_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.semester_config_id_seq OWNED BY public.semester_config.id;


--
-- Name: special_events; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.special_events (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    event_type character varying(50),
    start_date date,
    end_date date,
    time_period_id integer,
    affects_all_classes boolean DEFAULT false,
    affected_grades jsonb,
    description text
);


ALTER TABLE public.special_events OWNER TO randy;

--
-- Name: special_events_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.special_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.special_events_id_seq OWNER TO randy;

--
-- Name: special_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.special_events_id_seq OWNED BY public.special_events.id;


--
-- Name: student_courses; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.student_courses (
    id integer NOT NULL,
    student_id integer,
    course_id integer,
    enrollment_status character varying(20) DEFAULT 'enrolled'::character varying,
    semester character varying(10)
);


ALTER TABLE public.student_courses OWNER TO randy;

--
-- Name: student_courses_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.student_courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_courses_id_seq OWNER TO randy;

--
-- Name: student_courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.student_courses_id_seq OWNED BY public.student_courses.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.students (
    id integer NOT NULL,
    student_id character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    grade_level integer,
    homeroom_id integer,
    enrollment_status character varying(20) DEFAULT 'active'::character varying,
    notes text,
    CONSTRAINT students_grade_level_check CHECK ((grade_level = ANY (ARRAY[10, 11, 12])))
);


ALTER TABLE public.students OWNER TO randy;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO randy;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: study_hour_assignments; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.study_hour_assignments (
    id integer NOT NULL,
    student_id integer,
    time_period_id integer,
    supervisor_teacher_id integer,
    assignment_type character varying(20) DEFAULT 'regular'::character varying,
    semester character varying(10)
);


ALTER TABLE public.study_hour_assignments OWNER TO randy;

--
-- Name: study_hour_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.study_hour_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_hour_assignments_id_seq OWNER TO randy;

--
-- Name: study_hour_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.study_hour_assignments_id_seq OWNED BY public.study_hour_assignments.id;


--
-- Name: teacher_courses; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.teacher_courses (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    course_id integer NOT NULL,
    notes text
);


ALTER TABLE public.teacher_courses OWNER TO randy;

--
-- Name: teacher_courses_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.teacher_courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_courses_id_seq OWNER TO randy;

--
-- Name: teacher_courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.teacher_courses_id_seq OWNED BY public.teacher_courses.id;


--
-- Name: teachers; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.teachers (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    employee_id character varying(50),
    max_periods_per_week integer DEFAULT 24,
    is_international boolean DEFAULT false,
    can_supervise_study_hours boolean DEFAULT true,
    departments jsonb,
    preferred_periods jsonb,
    unavailable_periods jsonb,
    notes text
);


ALTER TABLE public.teachers OWNER TO randy;

--
-- Name: teachers_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.teachers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teachers_id_seq OWNER TO randy;

--
-- Name: teachers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.teachers_id_seq OWNED BY public.teachers.id;


--
-- Name: time_periods; Type: TABLE; Schema: public; Owner: randy
--

CREATE TABLE public.time_periods (
    id integer NOT NULL,
    period_number integer NOT NULL,
    day_of_week integer,
    period_type character varying(20) DEFAULT 'regular'::character varying,
    start_time time without time zone,
    end_time time without time zone,
    is_active boolean DEFAULT true,
    special_notes character varying(200),
    CONSTRAINT time_periods_day_of_week_check CHECK (((day_of_week >= 1) AND (day_of_week <= 5)))
);


ALTER TABLE public.time_periods OWNER TO randy;

--
-- Name: time_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: randy
--

CREATE SEQUENCE public.time_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.time_periods_id_seq OWNER TO randy;

--
-- Name: time_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: randy
--

ALTER SEQUENCE public.time_periods_id_seq OWNED BY public.time_periods.id;


--
-- Name: class_enrollments id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_enrollments ALTER COLUMN id SET DEFAULT nextval('public.class_enrollments_id_seq'::regclass);


--
-- Name: class_sections id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_sections ALTER COLUMN id SET DEFAULT nextval('public.class_sections_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: facilities id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.facilities ALTER COLUMN id SET DEFAULT nextval('public.facilities_id_seq'::regclass);


--
-- Name: homerooms id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.homerooms ALTER COLUMN id SET DEFAULT nextval('public.homerooms_id_seq'::regclass);


--
-- Name: scheduled_classes id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes ALTER COLUMN id SET DEFAULT nextval('public.scheduled_classes_id_seq'::regclass);


--
-- Name: scheduling_constraints id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduling_constraints ALTER COLUMN id SET DEFAULT nextval('public.scheduling_constraints_id_seq'::regclass);


--
-- Name: semester_config id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.semester_config ALTER COLUMN id SET DEFAULT nextval('public.semester_config_id_seq'::regclass);


--
-- Name: special_events id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.special_events ALTER COLUMN id SET DEFAULT nextval('public.special_events_id_seq'::regclass);


--
-- Name: student_courses id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.student_courses ALTER COLUMN id SET DEFAULT nextval('public.student_courses_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: study_hour_assignments id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.study_hour_assignments ALTER COLUMN id SET DEFAULT nextval('public.study_hour_assignments_id_seq'::regclass);


--
-- Name: teacher_courses id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teacher_courses ALTER COLUMN id SET DEFAULT nextval('public.teacher_courses_id_seq'::regclass);


--
-- Name: teachers id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teachers ALTER COLUMN id SET DEFAULT nextval('public.teachers_id_seq'::regclass);


--
-- Name: time_periods id; Type: DEFAULT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.time_periods ALTER COLUMN id SET DEFAULT nextval('public.time_periods_id_seq'::regclass);


--
-- Name: class_enrollments class_enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_enrollments
    ADD CONSTRAINT class_enrollments_pkey PRIMARY KEY (id);


--
-- Name: class_enrollments class_enrollments_scheduled_class_id_student_id_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_enrollments
    ADD CONSTRAINT class_enrollments_scheduled_class_id_student_id_key UNIQUE (scheduled_class_id, student_id);


--
-- Name: class_sections class_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_sections
    ADD CONSTRAINT class_sections_pkey PRIMARY KEY (id);


--
-- Name: courses courses_code_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_code_key UNIQUE (code);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: facilities facilities_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.facilities
    ADD CONSTRAINT facilities_pkey PRIMARY KEY (id);


--
-- Name: homerooms homerooms_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.homerooms
    ADD CONSTRAINT homerooms_pkey PRIMARY KEY (id);


--
-- Name: scheduled_classes scheduled_classes_facility_id_time_period_id_semester_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_facility_id_time_period_id_semester_key UNIQUE (facility_id, time_period_id, semester);


--
-- Name: scheduled_classes scheduled_classes_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_pkey PRIMARY KEY (id);


--
-- Name: scheduled_classes scheduled_classes_teacher_id_time_period_id_semester_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_teacher_id_time_period_id_semester_key UNIQUE (teacher_id, time_period_id, semester);


--
-- Name: scheduling_constraints scheduling_constraints_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduling_constraints
    ADD CONSTRAINT scheduling_constraints_pkey PRIMARY KEY (id);


--
-- Name: semester_config semester_config_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.semester_config
    ADD CONSTRAINT semester_config_pkey PRIMARY KEY (id);


--
-- Name: special_events special_events_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.special_events
    ADD CONSTRAINT special_events_pkey PRIMARY KEY (id);


--
-- Name: student_courses student_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.student_courses
    ADD CONSTRAINT student_courses_pkey PRIMARY KEY (id);


--
-- Name: student_courses student_courses_student_id_course_id_semester_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.student_courses
    ADD CONSTRAINT student_courses_student_id_course_id_semester_key UNIQUE (student_id, course_id, semester);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: students students_student_id_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_student_id_key UNIQUE (student_id);


--
-- Name: study_hour_assignments study_hour_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.study_hour_assignments
    ADD CONSTRAINT study_hour_assignments_pkey PRIMARY KEY (id);


--
-- Name: study_hour_assignments study_hour_assignments_student_id_time_period_id_semester_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.study_hour_assignments
    ADD CONSTRAINT study_hour_assignments_student_id_time_period_id_semester_key UNIQUE (student_id, time_period_id, semester);


--
-- Name: teacher_courses teacher_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT teacher_courses_pkey PRIMARY KEY (id);


--
-- Name: teachers teachers_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_employee_id_key UNIQUE (employee_id);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (id);


--
-- Name: time_periods time_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.time_periods
    ADD CONSTRAINT time_periods_pkey PRIMARY KEY (id);


--
-- Name: idx_class_enrollments_student; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_class_enrollments_student ON public.class_enrollments USING btree (student_id);


--
-- Name: idx_scheduled_classes_facility; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_scheduled_classes_facility ON public.scheduled_classes USING btree (facility_id);


--
-- Name: idx_scheduled_classes_semester; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_scheduled_classes_semester ON public.scheduled_classes USING btree (semester);


--
-- Name: idx_scheduled_classes_teacher; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_scheduled_classes_teacher ON public.scheduled_classes USING btree (teacher_id);


--
-- Name: idx_scheduled_classes_time; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_scheduled_classes_time ON public.scheduled_classes USING btree (time_period_id);


--
-- Name: idx_student_courses_student; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_student_courses_student ON public.student_courses USING btree (student_id);


--
-- Name: idx_students_grade; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_students_grade ON public.students USING btree (grade_level);


--
-- Name: idx_students_homeroom; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_students_homeroom ON public.students USING btree (homeroom_id);


--
-- Name: idx_teacher_courses_course; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_teacher_courses_course ON public.teacher_courses USING btree (course_id);


--
-- Name: idx_teacher_courses_teacher; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_teacher_courses_teacher ON public.teacher_courses USING btree (teacher_id);


--
-- Name: idx_teacher_courses_teacher_course; Type: INDEX; Schema: public; Owner: randy
--

CREATE INDEX idx_teacher_courses_teacher_course ON public.teacher_courses USING btree (teacher_id, course_id);


--
-- Name: class_enrollments class_enrollments_scheduled_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_enrollments
    ADD CONSTRAINT class_enrollments_scheduled_class_id_fkey FOREIGN KEY (scheduled_class_id) REFERENCES public.scheduled_classes(id);


--
-- Name: class_enrollments class_enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_enrollments
    ADD CONSTRAINT class_enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: class_sections class_sections_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.class_sections
    ADD CONSTRAINT class_sections_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: scheduled_classes scheduled_classes_class_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_class_section_id_fkey FOREIGN KEY (class_section_id) REFERENCES public.class_sections(id);


--
-- Name: scheduled_classes scheduled_classes_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id);


--
-- Name: scheduled_classes scheduled_classes_linked_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_linked_period_id_fkey FOREIGN KEY (linked_period_id) REFERENCES public.scheduled_classes(id);


--
-- Name: scheduled_classes scheduled_classes_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id);


--
-- Name: scheduled_classes scheduled_classes_time_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.scheduled_classes
    ADD CONSTRAINT scheduled_classes_time_period_id_fkey FOREIGN KEY (time_period_id) REFERENCES public.time_periods(id);


--
-- Name: special_events special_events_time_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.special_events
    ADD CONSTRAINT special_events_time_period_id_fkey FOREIGN KEY (time_period_id) REFERENCES public.time_periods(id);


--
-- Name: student_courses student_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.student_courses
    ADD CONSTRAINT student_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: student_courses student_courses_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.student_courses
    ADD CONSTRAINT student_courses_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: students students_homeroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_homeroom_id_fkey FOREIGN KEY (homeroom_id) REFERENCES public.homerooms(id);


--
-- Name: study_hour_assignments study_hour_assignments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.study_hour_assignments
    ADD CONSTRAINT study_hour_assignments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: study_hour_assignments study_hour_assignments_supervisor_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.study_hour_assignments
    ADD CONSTRAINT study_hour_assignments_supervisor_teacher_id_fkey FOREIGN KEY (supervisor_teacher_id) REFERENCES public.teachers(id);


--
-- Name: study_hour_assignments study_hour_assignments_time_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.study_hour_assignments
    ADD CONSTRAINT study_hour_assignments_time_period_id_fkey FOREIGN KEY (time_period_id) REFERENCES public.time_periods(id);


--
-- Name: teacher_courses teacher_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT teacher_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: teacher_courses teacher_courses_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: randy
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT teacher_courses_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

