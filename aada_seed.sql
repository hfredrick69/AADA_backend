--
-- PostgreSQL database dump
--

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.18 (Homebrew)

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

--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: aada_user
--

COPY public.students (id, name, email, fcm_token, square_customer_id, enrollment_status) FROM stdin;
4	Vyncjy Ajpjlk	vyncjy.ajpjlk@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	7WZ85RXPVW6437NFS2SPK6M7P4	Enrolling
5	Eejuwl Roslrm	eejuwl.roslrm@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	HNQCNAH166SK1MG38Y5ZKS8VBR	Enrolling
6	Dtdpfi Bvpbdx	dtdpfi.bvpbdx@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	CHZA57QBK0FXMGPCRRA8XTMQKM	Enrolling
7	Tuxufk Vvjrpj	tuxufk.vvjrpj@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	E2AB2WMM2AY3AC6QWMEAV7NF84	Enrolling
8	Xsduho Jrphzg	xsduho.jrphzg@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	FFCSZ8XPCPBK0T9YWTF4YD32KC	Enrolling
9	Xinjkt Zecdzm	xinjkt.zecdzm@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	YC642E6F1JQ7180BZM5XDS6ND8	Enrolling
10	Iedueo Wrkari	iedueo.wrkari@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	R38PMS9PC85B4ZV01YMPMQY1Y4	Enrolling
11	Dzcpki Cxtnzz	dzcpki.cxtnzz@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	79HN4FH4F1KR5XCS5SSKBY9BM8	Enrolling
12	Flgfxn Pauihw	flgfxn.pauihw@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	GEDW0KX06QTCBN47B4SKK4SK34	Enrolling
13	Aeinsf Wohahu	aeinsf.wohahu@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	CG1B6P0SDTMPEZ0PQTRDC4ETAW	Enrolling
1	Jane Doe	jane@example.com	cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0	\N	Enrolled
\.


--
-- Data for Name: externship_status; Type: TABLE DATA; Schema: public; Owner: aada_user
--

COPY public.externship_status (id, student_id, status) FROM stdin;
\.


--
-- Data for Name: externships; Type: TABLE DATA; Schema: public; Owner: aada_user
--

COPY public.externships (id, student_id, status) FROM stdin;
1	1	Completed
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: herbert
--

COPY public.invoices (id, student_id, due_date, amount_cents, status, square_invoice_id, reminder_sent, late_notice_sent, created_at, updated_at, description) FROM stdin;
4	1	2025-06-15	600	PENDING	\N	f	t	2025-06-28 00:08:22.727851-04	2025-06-28 00:00:00-04	Monthly Tuition Payment
\.


--
-- Data for Name: payment_plans; Type: TABLE DATA; Schema: public; Owner: aada_user
--

COPY public.payment_plans (id, student_id, amount, due_date) FROM stdin;
1	1	500	2025-07-01
3	1	400	2024-06-01
4	1	600	2025-08-01
\.


--
-- Data for Name: payment_reminders; Type: TABLE DATA; Schema: public; Owner: herbert
--

COPY public.payment_reminders (id, student_id, month, year, reminder_sent, overdue_reminder_sent, last_checked) FROM stdin;
\.


--
-- Name: externship_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aada_user
--

SELECT pg_catalog.setval('public.externship_status_id_seq', 1, false);


--
-- Name: externships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aada_user
--

SELECT pg_catalog.setval('public.externships_id_seq', 1, true);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: herbert
--

SELECT pg_catalog.setval('public.invoices_id_seq', 4, true);


--
-- Name: payment_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aada_user
--

SELECT pg_catalog.setval('public.payment_plans_id_seq', 7, true);


--
-- Name: payment_reminders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: herbert
--

SELECT pg_catalog.setval('public.payment_reminders_id_seq', 1, false);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aada_user
--

SELECT pg_catalog.setval('public.students_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

