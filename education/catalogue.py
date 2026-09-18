"""
Education Pathway Catalogue (Member 2 - Step 6).
Data-driven catalogue of factual educational progression possibilities across
all education levels (Secondary, Higher Secondary, Diploma, Undergraduate, Postgraduate, Certifications).
Directly connects to standardized career domains and Career Catalogue IDs.
"""

from typing import List, Dict, Any

EDUCATION_PATHWAY_CATALOGUE: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # 1. Higher Secondary / Secondary Pathways
    # --------------------------------------------------------------------------
    {
        "id": "higher-sec-to-engineering-cs",
        "title": "Higher Secondary to Undergraduate Engineering & Computer Science",
        "current_education_level": "Higher Secondary",
        "possible_next_step": "Undergraduate Degree (B.Tech / B.E. / B.Sc in Computer Science / IT)",
        "higher_study_options": [
            "B.Tech / B.E. in Computer Science & Engineering",
            "B.Tech in Artificial Intelligence & Data Science",
            "B.Sc in Computer Science / Information Technology",
            "Integrated Dual Degree (B.Tech + M.Tech)"
        ],
        "specialization_options": [
            "Software Systems & Architecture",
            "Artificial Intelligence & Machine Learning",
            "Data Engineering & Analytics",
            "Cloud Computing & Infrastructure"
        ],
        "related_career_ids": [
            "software-developer",
            "web-developer",
            "cloud-devops-engineer",
            "data-scientist",
            "machine-learning-engineer"
        ],
        "relevant_domains": ["Technology & Software", "Data & AI"],
        "relevant_interests": ["Python", "Web Development", "Artificial Intelligence", "Machine Learning", "Cloud Computing"],
        "useful_skills": ["Mathematics", "Physics", "Introductory Programming", "Logical Reasoning"],
        "explanation": (
            "Students with a science/mathematics background in higher secondary commonly progress to "
            "undergraduate engineering or computer science programs, which establish foundational knowledge "
            "in algorithmic problem-solving and software design."
        ),
        "admission_prerequisites": (
            "Higher secondary certificate (10+2 or equivalent) with Mathematics and Physics; "
            "institutional entrance exams (such as JEE or state entrance tests) frequently apply."
        ),
        "limitations": [
            "Entrance criteria vary significantly across public and private technical institutions.",
            "Strong mathematical foundation is essential for coursework in algorithms and systems."
        ]
    },
    {
        "id": "higher-sec-to-polytechnic-diploma",
        "title": "Higher Secondary / Secondary to Technical Polytechnic Diploma",
        "current_education_level": "Higher Secondary",
        "possible_next_step": "Polytechnic Diploma in Engineering / Applied Technologies",
        "higher_study_options": [
            "Diploma in Computer Engineering",
            "Diploma in Electronics & Communication",
            "Diploma in Mechanical Engineering",
            "Diploma in Civil Engineering"
        ],
        "specialization_options": [
            "Hardware & Networking Technologies",
            "Industrial Automation & Manufacturing",
            "Computer Applications & Maintenance",
            "Construction Technology"
        ],
        "related_career_ids": [
            "systems-network-technician",
            "mechanical-engineer",
            "civil-engineer",
            "electronics-engineer"
        ],
        "relevant_domains": ["Skilled & Technical Trades", "Engineering", "Technology & Software"],
        "relevant_interests": ["Skilled Trades & Networking", "Mechanical Engineering", "Civil Engineering", "Electronics & Electrical"],
        "useful_skills": ["Applied Mathematics", "Technical Diagnostics", "Workshop Practice", "Computer Fundamentals"],
        "explanation": (
            "Polytechnic diplomas offer an applied, hands-on pathway following secondary or higher secondary study, "
            "providing technical training and serving as a bridge to lateral-entry engineering degrees."
        ),
        "admission_prerequisites": (
            "Secondary (10th) or Higher Secondary (10+2) certificate; state polytechnic entrance test or merit ranking."
        ),
        "limitations": [
            "Focus is on applied technical training; subsequent transition to professional degrees typically requires lateral-entry screening."
        ]
    },
    {
        "id": "higher-sec-to-medical-sciences",
        "title": "Higher Secondary to Medical & Allied Health Sciences",
        "current_education_level": "Higher Secondary",
        "possible_next_step": "Undergraduate Medical Degree (MBBS / BDS / B.Sc Nursing / B.Pharm)",
        "higher_study_options": [
            "Bachelor of Medicine and Bachelor of Surgery (MBBS)",
            "Bachelor of Dental Surgery (BDS)",
            "Bachelor of Pharmacy (B.Pharm)",
            "B.Sc in Nursing / Medical Laboratory Technology"
        ],
        "specialization_options": [
            "General Medicine & Surgery",
            "Clinical Pharmacology",
            "Patient Care & Critical Care Nursing",
            "Diagnostic Medical Laboratory Technologies"
        ],
        "related_career_ids": [
            "medical-professional",
            "clinical-researcher"
        ],
        "relevant_domains": ["Healthcare", "Science & Research"],
        "relevant_interests": ["Medicine & Healthcare", "Biology", "Chemistry"],
        "useful_skills": ["Biology", "Chemistry", "Clinical Empathy", "Analytical Laboratory Observation"],
        "explanation": (
            "Higher secondary study in biological and chemical sciences serves as the requisite starting point "
            "for entry into statutory medical qualifications, clinical research tracks, and healthcare disciplines."
        ),
        "admission_prerequisites": (
            "Higher secondary with Biology, Chemistry, and Physics; statutory national eligibility examination (such as NEET)."
        ),
        "limitations": [
            "Admission is subject to strict statutory quotas, national licensure benchmarks, and extensive clinical internships.",
            "Professional practice requires registration with the applicable medical or nursing council."
        ]
    },
    {
        "id": "higher-sec-to-commerce-finance",
        "title": "Higher Secondary to Commerce, Accounting & Business Studies",
        "current_education_level": "Higher Secondary",
        "possible_next_step": "Undergraduate Commerce Degree (B.Com / BBA / Professional Foundation)",
        "higher_study_options": [
            "Bachelor of Commerce (B.Com / B.Com Honours)",
            "Bachelor of Business Administration (BBA / BMS)",
            "Integrated Chartered Accountancy (CA Foundation / CMA)",
            "B.Sc in Economics & Financial Analysis"
        ],
        "specialization_options": [
            "Corporate Accounting & Auditing",
            "Banking, Financial Services & Insurance (BFSI)",
            "Business Management & Marketing",
            "Taxation & Fiscal Law"
        ],
        "related_career_ids": [
            "chartered-accountant",
            "financial-analyst",
            "business-analyst",
            "marketing-manager"
        ],
        "relevant_domains": ["Finance & Commerce", "Business & Management"],
        "relevant_interests": ["Accounting & Finance", "Financial Analysis", "Business Management", "Marketing"],
        "useful_skills": ["Numerical Analysis", "Bookkeeping", "Spreadsheet Modeling", "Business Communication"],
        "explanation": (
            "Students completing commerce or mathematics at the higher secondary level commonly enter "
            "undergraduate commerce and management programs that prepare for statutory accounting or financial analytics."
        ),
        "admission_prerequisites": (
            "Higher secondary certificate in Commerce, Mathematics, or equivalent stream with institutional cutoff criteria."
        ),
        "limitations": [
            "Professional certifications (such as CA, CPA, or CFA) require separate enrollment with governing statutory bodies."
        ]
    },
    {
        "id": "higher-sec-to-design-arts",
        "title": "Higher Secondary to Creative Design & Digital Media Arts",
        "current_education_level": "Higher Secondary",
        "possible_next_step": "Undergraduate Design Degree (B.Des / BFA / B.A. in Visual Arts)",
        "higher_study_options": [
            "Bachelor of Design (B.Des in Product / Communication / UI/UX)",
            "Bachelor of Fine Arts (BFA)",
            "B.Sc in Animation & Multimedia",
            "B.A. in Digital Media & Journalism"
        ],
        "specialization_options": [
            "User Interface & User Experience Design",
            "Digital Visual Communication & Branding",
            "Motion Graphics & Animation",
            "Journalistic & Editorial Content Design"
        ],
        "related_career_ids": [
            "ui-ux-designer",
            "technical-writer-journalist",
            "marketing-manager"
        ],
        "relevant_domains": ["Design & Creative", "Media & Communication"],
        "relevant_interests": ["Graphic Design", "Writing & Journalism", "Web Development"],
        "useful_skills": ["Visual Composition", "Design Empathy", "Creative Storytelling", "Prototyping Basics"],
        "explanation": (
            "Creative aptitude demonstrated in higher secondary can lead to undergraduate design and media programs, "
            "where students build practical portfolios alongside theoretical design training."
        ),
        "admission_prerequisites": (
            "Higher secondary completion in any discipline; creative aptitude tests (UCEED, NID DAT, or institutional tests) and portfolio review."
        ),
        "limitations": [
            "A portfolio of creative work is universally emphasized alongside academic qualification."
        ]
    },
    {
        "id": "higher-sec-to-law-integrated",
        "title": "Higher Secondary to Integrated 5-Year Legal Education",
        "current_education_level": "Higher Secondary",
        "possible_next_step": "Integrated Law Degree (BA LL.B / BBA LL.B / B.Com LL.B)",
        "higher_study_options": [
            "5-Year Integrated Bachelor of Arts & Bachelor of Laws (BA LL.B)",
            "5-Year Integrated Bachelor of Business Administration & Laws (BBA LL.B)",
            "B.Com LL.B Integrated Program"
        ],
        "specialization_options": [
            "Constitutional & Administrative Law",
            "Corporate & Commercial Law",
            "Intellectual Property & Technology Law",
            "Criminal Litigation & Advocacy"
        ],
        "related_career_ids": [
            "legal-counsel",
            "civil-services-administrator"
        ],
        "relevant_domains": ["Law", "Government & Public Service"],
        "relevant_interests": ["Law & Legal Studies", "Government & Civil Services", "Writing & Journalism"],
        "useful_skills": ["Critical Reasoning", "Reading Comprehension", "Legal Research Basics", "Oral Argumentation"],
        "explanation": (
            "Integrated five-year law programs allow higher secondary graduates to combine undergraduate humanities "
            "or commerce studies directly with professional legal education and bar council qualification tracks."
        ),
        "admission_prerequisites": (
            "Higher secondary completion in any stream; competitive law entrance examinations (e.g. CLAT, AILET, or LSAT)."
        ),
        "limitations": [
            "Advocacy practice requires passing the All India Bar Examination (AIBE) or jurisdictional bar council license."
        ]
    },

    # --------------------------------------------------------------------------
    # 2. Diploma / Polytechnic Pathways
    # --------------------------------------------------------------------------
    {
        "id": "diploma-to-btech-lateral",
        "title": "Polytechnic Diploma to Lateral-Entry Undergraduate Engineering",
        "current_education_level": "Diploma",
        "possible_next_step": "Undergraduate Degree via Lateral Entry (Direct 2nd Year B.Tech / B.E.)",
        "higher_study_options": [
            "B.Tech in Computer Science & Engineering (Lateral Entry)",
            "B.Tech in Mechanical / Automation Engineering",
            "B.Tech in Civil Infrastructure Engineering",
            "B.Tech in Electrical & Electronics Engineering"
        ],
        "specialization_options": [
            "Applied Software Systems",
            "Computer Integrated Manufacturing",
            "Structural Analysis & Project Engineering",
            "Power Systems & Embedded Automation"
        ],
        "related_career_ids": [
            "software-developer",
            "mechanical-engineer",
            "civil-engineer",
            "electronics-engineer",
            "systems-network-technician"
        ],
        "relevant_domains": ["Engineering", "Technology & Software", "Skilled & Technical Trades"],
        "relevant_interests": ["Mechanical Engineering", "Civil Engineering", "Electronics & Electrical", "Python", "Skilled Trades & Networking"],
        "useful_skills": ["Engineering Graphics / CAD", "Workshop Practice", "Applied Mathematics", "Programming Fundamentals"],
        "explanation": (
            "Students holding a 3-year polytechnic engineering diploma can leverage lateral entry routes to join "
            "the second year of an undergraduate B.Tech program, completing a professional engineering degree in 3 years."
        ),
        "admission_prerequisites": (
            "State polytechnic diploma in relevant technical discipline with qualifying percentage; lateral entrance test (e.g. ECET)."
        ),
        "limitations": [
            "Lateral entry seats in universities are subject to strict institutional percentages and subject-stream alignment."
        ]
    },
    {
        "id": "diploma-to-advanced-certifications",
        "title": "Diploma to Advanced Technical Certifications & Specializations",
        "current_education_level": "Diploma",
        "possible_next_step": "Advanced Specialist Diploma / Industry Professional Credentials",
        "higher_study_options": [
            "Post-Diploma in Industrial Automation",
            "Professional Cloud Infrastructure Certifications (AWS / Azure / GCP)",
            "Advanced Cisco Networking Credentials (CCNA / CCNP)",
            "Post-Diploma in CAD/CAM Design & Tool Engineering"
        ],
        "specialization_options": [
            "Enterprise Network Administration",
            "SCADA & Programmable Logic Controllers (PLC)",
            "Precision Tooling & CNC Operations",
            "Cloud Infrastructure Support"
        ],
        "related_career_ids": [
            "systems-network-technician",
            "cloud-devops-engineer",
            "mechanical-engineer",
            "electronics-engineer"
        ],
        "relevant_domains": ["Skilled & Technical Trades", "Technology & Software", "Engineering"],
        "relevant_interests": ["Skilled Trades & Networking", "Electronics & Electrical", "Cloud Computing"],
        "useful_skills": ["Network Troubleshooting", "Hardware Diagnostics", "Linux Fundamentals", "Electrical Circuit Analysis"],
        "explanation": (
            "For diploma graduates aiming for immediate technical specialization, advanced vendor and technical "
            "certifications provide industry-recognized credentials without the multi-year duration of full degree programs."
        ),
        "admission_prerequisites": (
            "Polytechnic diploma or equivalent technical certificate; vendor certification exam registration."
        ),
        "limitations": [
            "Vendor certifications require periodic recertification to maintain active professional credentialing."
        ]
    },

    # --------------------------------------------------------------------------
    # 3. Undergraduate Pathways
    # --------------------------------------------------------------------------
    {
        "id": "undergrad-cs-to-mtech-ms",
        "title": "Undergraduate Engineering to Postgraduate M.Tech / M.S. in Computing",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Postgraduate Degree (M.Tech / M.S. in Computer Science, AI, or Data Science)",
        "higher_study_options": [
            "M.Tech in Computer Science & Engineering",
            "M.Tech in Artificial Intelligence & Machine Learning",
            "Master of Science (M.S.) by Research in Computer Systems",
            "Integrated Ph.D. in Computational Sciences"
        ],
        "specialization_options": [
            "Deep Learning & Natural Language Processing",
            "Distributed Systems & Cloud Architecture",
            "Cybersecurity & Cryptography",
            "Autonomous Robotics & Computer Vision"
        ],
        "related_career_ids": [
            "data-scientist",
            "machine-learning-engineer",
            "software-developer",
            "cloud-devops-engineer",
            "cybersecurity-analyst"
        ],
        "relevant_domains": ["Technology & Software", "Data & AI", "Cybersecurity", "Science & Research"],
        "relevant_interests": ["Python", "Artificial Intelligence", "Machine Learning", "Data Science", "Cloud Computing", "Cybersecurity"],
        "useful_skills": ["Data Structures", "Algorithms", "Linear Algebra", "Python / C++", "Operating Systems"],
        "explanation": (
            "Undergraduate engineering graduates in CS, IT, or quantitative sciences frequently pursue postgraduate "
            "master's degrees to build specialized research capabilities in machine learning, distributed systems, or cyber defense."
        ),
        "admission_prerequisites": (
            "B.Tech/B.E. or equivalent in relevant branch; national aptitude test (such as GATE in India or GRE/TOEFL for international study)."
        ),
        "limitations": [
            "Admission is highly competitive; published research or demonstrated software projects strongly complement test scores."
        ]
    },
    {
        "id": "undergrad-to-mba-management",
        "title": "Undergraduate to Master of Business Administration (MBA / PGDM)",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Postgraduate Degree in Management (MBA / PGDM / Master in Management)",
        "higher_study_options": [
            "Master of Business Administration (MBA in Tech Management / Strategy)",
            "Post Graduate Diploma in Management (PGDM)",
            "MBA in Business Analytics & Data Governance",
            "Master in Finance & Corporate Strategy"
        ],
        "specialization_options": [
            "Technology & Operations Management",
            "Business Analytics & Strategic Planning",
            "Product Management & Digital Transformation",
            "Corporate Finance & Strategic Marketing"
        ],
        "related_career_ids": [
            "business-analyst",
            "marketing-manager",
            "financial-analyst",
            "civil-services-administrator"
        ],
        "relevant_domains": ["Business & Management", "Finance & Commerce", "Technology & Software"],
        "relevant_interests": ["Business Management", "Finance", "Marketing", "Data Science"],
        "useful_skills": ["Data Interpretation", "Stakeholder Communication", "Strategic Planning", "Presentation Skills"],
        "explanation": (
            "Graduates across diverse undergraduate disciplines (engineering, commerce, sciences, or humanities) "
            "regularly transition to postgraduate management to take on cross-functional leadership and business operations roles."
        ),
        "admission_prerequisites": (
            "Undergraduate degree in any discipline with minimum qualifying aggregate; competitive management exam (CAT, GMAT, XAT, MAT)."
        ),
        "limitations": [
            "Leading business schools often prioritize candidates with 1–3 years of prior professional work experience alongside test scores."
        ]
    },
    {
        "id": "undergrad-engineering-to-mtech-core",
        "title": "Undergraduate to Postgraduate Core Engineering Specialization",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Postgraduate Core Engineering Degree (M.Tech / M.E. in Specialized Engineering)",
        "higher_study_options": [
            "M.Tech in Industrial Automation & Robotics",
            "M.Tech in Structural & Geotechnical Engineering",
            "M.Tech in VLSI & Embedded Systems Design",
            "M.Tech in Renewable Energy Systems"
        ],
        "specialization_options": [
            "Finite Element Analysis & CAD Simulation",
            "Earthquake Engineering & Urban Infrastructure",
            "Semiconductor Device Modeling & Microelectronics",
            "Thermal Systems & Fluid Dynamics"
        ],
        "related_career_ids": [
            "mechanical-engineer",
            "civil-engineer",
            "electronics-engineer"
        ],
        "relevant_domains": ["Engineering", "Science & Research"],
        "relevant_interests": ["Mechanical Engineering", "Civil Engineering", "Electronics & Electrical", "Robotics"],
        "useful_skills": ["Thermodynamics", "Structural Mechanics", "MATLAB / Simulation Tools", "Circuit Design"],
        "explanation": (
            "Core undergraduate engineers (mechanical, civil, electrical) pursue targeted M.Tech degrees to develop "
            "advanced simulation, structural modeling, or microelectronics competencies demanded in heavy engineering and R&D."
        ),
        "admission_prerequisites": (
            "B.Tech/B.E. in matching engineering discipline; GATE or institutional qualifying exams."
        ),
        "limitations": [
            "Coursework is highly rigorous and mathematically demanding; specific discipline prerequisites apply."
        ]
    },
    {
        "id": "undergrad-commerce-to-mcom-cfa",
        "title": "Undergraduate Commerce to Postgraduate Finance & Professional Charter",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Postgraduate Degree / Global Professional Financial Credentials",
        "higher_study_options": [
            "Master of Commerce (M.Com in Accounting & Taxation)",
            "Chartered Financial Analyst (CFA Program - Levels I to III)",
            "Master of Science (M.Sc) in Quantitative Finance",
            "Certified Public Accountant (CPA) / ACCA Professional Papers"
        ],
        "specialization_options": [
            "Equity Research & Investment Valuation",
            "Risk Management & Quantitative Asset Allocation",
            "Corporate Statutory Auditing & Taxation",
            "Treasury Operations & Financial Engineering"
        ],
        "related_career_ids": [
            "chartered-accountant",
            "financial-analyst",
            "business-analyst"
        ],
        "relevant_domains": ["Finance & Commerce", "Business & Management"],
        "relevant_interests": ["Accounting & Finance", "Financial Analysis", "Business Management"],
        "useful_skills": ["Financial Modeling", "Valuation Methods", "Auditing Frameworks", "Advanced Excel"],
        "explanation": (
            "Commerce, economics, and mathematics graduates commonly advance their qualifications via international "
            "financial charters (CFA, ACCA) or postgraduate finance degrees, enhancing eligibility for investment banking and auditing."
        ),
        "admission_prerequisites": (
            "Bachelor's degree in Commerce, Economics, or Quantitative Sciences; direct registration with certifying institute."
        ),
        "limitations": [
            "Professional charters (such as CFA) involve multiple self-directed examination levels and verified professional work experience requirements."
        ]
    },
    {
        "id": "undergrad-science-to-msc-research",
        "title": "Undergraduate Science to Postgraduate Sciences & Research Preparation",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Postgraduate Science Degree (M.Sc / Integrated Ph.D. in Physical/Life Sciences)",
        "higher_study_options": [
            "Master of Science (M.Sc in Physics / Chemistry / Life Sciences)",
            "Integrated Ph.D. in Interdisciplinary Sciences",
            "M.Sc in Biotechnology & Bioinformatics",
            "M.Sc in Applied Mathematics & Statistics"
        ],
        "specialization_options": [
            "Quantum Mechanics & Condensed Matter Physics",
            "Molecular Biology & Genetic Engineering",
            "Analytical Chemistry & Material Synthesis",
            "Computational Statistics & Stochastic Modeling"
        ],
        "related_career_ids": [
            "research-scientist",
            "clinical-researcher",
            "educator-teacher",
            "data-scientist"
        ],
        "relevant_domains": ["Science & Research", "Healthcare", "Education & Teaching"],
        "relevant_interests": ["Physics", "Chemistry", "Biology", "Mathematics", "Medicine & Healthcare"],
        "useful_skills": ["Laboratory Synthesis", "Scientific Method", "Statistical Hypothesis Testing", "Technical Writing"],
        "explanation": (
            "B.Sc graduates in pure or applied sciences progress to master's degrees (M.Sc) to develop specialized "
            "laboratory and theoretical capabilities, providing the foundation for scientific careers and doctoral research."
        ),
        "admission_prerequisites": (
            "B.Sc degree in relevant discipline; competitive national exams (IIT-JAM, CUET-PG, or university tests)."
        ),
        "limitations": [
            "Career trajectories in scientific research generally necessitate subsequent doctoral (Ph.D.) progression."
        ]
    },
    {
        "id": "undergrad-to-law-llb",
        "title": "Undergraduate Degree to 3-Year Professional Law Degree (LL.B)",
        "current_education_level": "Undergraduate",
        "possible_next_step": "3-Year Bachelor of Laws (LL.B)",
        "higher_study_options": [
            "3-Year Professional LL.B",
            "Postgraduate Diploma in Cyber Law / IPR",
            "Master of Laws (LL.M following LL.B)"
        ],
        "specialization_options": [
            "Corporate Litigation & Mergers",
            "Intellectual Property & Cyber Jurisprudence",
            "Constitutional Law & Civil Liberties",
            "Commercial Arbitration & Dispute Resolution"
        ],
        "related_career_ids": [
            "legal-counsel",
            "civil-services-administrator"
        ],
        "relevant_domains": ["Law", "Government & Public Service"],
        "relevant_interests": ["Law & Legal Studies", "Government & Civil Services", "Writing & Journalism"],
        "useful_skills": ["Statutory Interpretation", "Case Law Analysis", "Legal Drafting", "Argumentation"],
        "explanation": (
            "Graduates holding an undergraduate degree in any academic stream (arts, science, engineering, or commerce) "
            "can enter a 3-year professional LL.B program to qualify as a legal advocate."
        ),
        "admission_prerequisites": (
            "Graduation in any discipline with minimum required marks; university or state law entrance examination."
        ),
        "limitations": [
            "Court practice requires passing the Bar Council licensing examination in the jurisdiction of intended practice."
        ]
    },
    {
        "id": "undergrad-to-bed-teaching",
        "title": "Undergraduate Degree to Professional Teacher Education (B.Ed)",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Bachelor of Education (B.Ed)",
        "higher_study_options": [
            "2-Year Bachelor of Education (B.Ed in Secondary Pedagogy)",
            "Master of Education (M.Ed following B.Ed)",
            "Postgraduate Certificate in Higher Education Teaching"
        ],
        "specialization_options": [
            "Secondary Science & Mathematics Pedagogy",
            "Language & Literature Instruction",
            "Social Sciences & Humanities Pedagogy",
            "Educational Technology & Curriculum Design"
        ],
        "related_career_ids": [
            "educator-teacher",
            "technical-writer-journalist"
        ],
        "relevant_domains": ["Education & Teaching", "Media & Communication"],
        "relevant_interests": ["Teaching & Education", "Mathematics", "Physics", "Writing & Journalism"],
        "useful_skills": ["Pedagogic Communication", "Curriculum Planning", "Student Mentoring", "Formative Assessment"],
        "explanation": (
            "Undergraduate graduates in disciplinary majors (mathematics, science, literature, history) complete a B.Ed "
            "to acquire pedagogical training, instructional methodology, and statutory eligibility for secondary teaching positions."
        ),
        "admission_prerequisites": (
            "Bachelor's degree in target teaching subject; state or national education entrance examination (e.g. B.Ed CET)."
        ),
        "limitations": [
            "Public school employment typically mandates passing national or state Teacher Eligibility Tests (TET / CTET)."
        ]
    },
    {
        "id": "undergrad-to-specialized-certifications",
        "title": "Undergraduate to Professional Technology Certifications & Bootcamps",
        "current_education_level": "Undergraduate",
        "possible_next_step": "Advanced Professional Certifications / Specialized Industry Programs",
        "higher_study_options": [
            "Professional Cloud Architect Certifications (AWS / Azure / GCP)",
            "Certified Kubernetes Administrator (CKA)",
            "Offensive Security Certified Professional (OSCP)",
            "Postgraduate Executive Certificate in Data Engineering"
        ],
        "specialization_options": [
            "Cloud Infrastructure & Containerization",
            "Penetration Testing & Defensive Security",
            "Big Data Pipeline Engineering",
            "Production Machine Learning Operations (MLOps)"
        ],
        "related_career_ids": [
            "cloud-devops-engineer",
            "cybersecurity-analyst",
            "machine-learning-engineer",
            "software-developer"
        ],
        "relevant_domains": ["Technology & Software", "Cybersecurity", "Data & AI"],
        "relevant_interests": ["Cloud Computing", "Cybersecurity", "DevOps", "Python"],
        "useful_skills": ["Linux / Unix", "Docker / Containers", "Networking Protocols", "Python Scripting"],
        "explanation": (
            "Technical graduates seeking specialized industry positioning frequently pursue rigorous hands-on "
            "certifications (Kubernetes, AWS Architect, OSCP) to validate practical engineering capabilities."
        ),
        "admission_prerequisites": (
            "Undergraduate degree in technical discipline or equivalent programming proficiency; vendor exam registration."
        ),
        "limitations": [
            "Industry credentials complement, but do not replace, formal academic accreditation in regulated sectors."
        ]
    },

    # --------------------------------------------------------------------------
    # 4. Postgraduate Pathways
    # --------------------------------------------------------------------------
    {
        "id": "postgrad-to-phd-research",
        "title": "Postgraduate Degree to Doctoral Research (Ph.D. / Fellowship)",
        "current_education_level": "Postgraduate",
        "possible_next_step": "Doctor of Philosophy (Ph.D.) / Postdoctoral Fellowships",
        "higher_study_options": [
            "Ph.D. in Computer Science & Artificial Intelligence",
            "Ph.D. in Physical / Chemical / Biological Sciences",
            "Ph.D. in Engineering & Applied Mechanics",
            "Ph.D. in Economics, Management, or Social Sciences"
        ],
        "specialization_options": [
            "Autonomous Machine Learning Theory",
            "Advanced Nanomaterials & Semiconductor Physics",
            "Bioinformatics & Computational Genomics",
            "Econometric Modeling & Quantitative Policy"
        ],
        "related_career_ids": [
            "research-scientist",
            "educator-teacher",
            "data-scientist",
            "clinical-researcher"
        ],
        "relevant_domains": ["Science & Research", "Education & Teaching", "Data & AI", "Healthcare"],
        "relevant_interests": ["Artificial Intelligence", "Physics", "Chemistry", "Biology", "Mathematics"],
        "useful_skills": ["Literature Review", "Experimental Design", "Peer-Reviewed Scientific Writing", "Statistical Rigor"],
        "explanation": (
            "Postgraduate holders (M.Tech, M.Sc, M.A., or M.S.) conduct original independent research leading to "
            "a doctoral dissertation (Ph.D.), qualifying for university professorships, research lab directorships, and principal scientist roles."
        ),
        "admission_prerequisites": (
            "Master's degree with high academic aggregate; national research fellowship examination (e.g. CSIR-UGC NET JRF, GATE, or institutional research entrance)."
        ),
        "limitations": [
            "Doctoral programs typically span 3 to 5 years of full-time research, requiring independent scholarly commitment and publication output."
        ]
    },
    {
        "id": "postgrad-to-executive-credentials",
        "title": "Postgraduate to Executive Fellowships & Leadership Specializations",
        "current_education_level": "Postgraduate",
        "possible_next_step": "Executive Fellowship / Advanced Post-Master's Credentials",
        "higher_study_options": [
            "Executive Leadership Fellowships",
            "Post-Doctoral Industry Research Fellowships",
            "Chief Technology Officer / Senior Executive Modular Programs"
        ],
        "specialization_options": [
            "Enterprise Technology Governance",
            "Global Supply Chain Leadership",
            "Strategic Healthcare Administration",
            "Venture Creation & Tech Commercialization"
        ],
        "related_career_ids": [
            "software-developer",
            "business-analyst",
            "chartered-accountant",
            "research-scientist"
        ],
        "relevant_domains": ["Business & Management", "Technology & Software", "Finance & Commerce"],
        "relevant_interests": ["Business Management", "Finance", "Cloud Computing"],
        "useful_skills": ["Executive Decision Making", "Organizational Strategy", "Budget Governance", "Cross-Functional Leadership"],
        "explanation": (
            "Mid-career professionals and postgraduate degree holders leverage advanced executive programs and "
            "specialist fellowships to transition from technical management into corporate leadership and strategic governance."
        ),
        "admission_prerequisites": (
            "Postgraduate degree plus substantive professional work experience; executive admissions review."
        ),
        "limitations": [
            "Executive programs prioritize industry track record and corporate sponsorship over academic test scores."
        ]
    }
]

# Indexes for rapid O(1) lookup
PATHWAY_BY_ID: Dict[str, Dict[str, Any]] = {p["id"]: p for p in EDUCATION_PATHWAY_CATALOGUE}

PATHWAYS_BY_LEVEL: Dict[str, List[Dict[str, Any]]] = {}
for p in EDUCATION_PATHWAY_CATALOGUE:
    level = p["current_education_level"].strip().lower()
    PATHWAYS_BY_LEVEL.setdefault(level, []).append(p)
