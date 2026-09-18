"""
Career Pathway Catalogue (Member 2).
Data-driven catalogue of standard career pathways across 14 standardized domains.
Includes typical educational routes, requisite skills, career progressions, and related interests.
"""

CAREER_CATALOGUE = [
    # 1. Technology & Software
    {
        "id": "software-developer",
        "name": "Software Developer",
        "domain": "Technology & Software",
        "related_domains": ["Data & AI", "Engineering"],
        "description": "Designs, writes, tests, and maintains application software, system services, and backend platforms.",
        "related_interests": ["Python", "Java", "C++", "Web Development", "Full Stack Development", "Cloud Computing", "DevOps"],
        "important_skills": ["Programming", "Data Structures", "Algorithms", "Git & GitHub", "Database Management", "Problem Solving"],
        "typical_education": [
            "Bachelor's degree in Computer Science, Information Technology, or related engineering discipline",
            "Polytechnic diploma in computer engineering with practical software development portfolio",
            "Alternative technical certification tracks combined with demonstrated programming experience"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate", "Diploma"],
        "progression": [
            "Junior / Associate Software Engineer",
            "Software Developer",
            "Senior Software Engineer / Technical Lead",
            "Staff Engineer / Solutions Architect / Engineering Manager"
        ]
    },
    {
        "id": "web-developer",
        "name": "Web Developer (Frontend / Full Stack)",
        "domain": "Technology & Software",
        "related_domains": ["Design & Creative"],
        "description": "Builds responsive client-facing interfaces, web applications, and integrated application programming interfaces (APIs).",
        "related_interests": ["Web Development", "Full Stack Development", "JavaScript", "Graphic Design", "Python"],
        "important_skills": ["HTML/CSS", "JavaScript/TypeScript", "React/Vue/Frontend Frameworks", "REST APIs", "UI Empathy"],
        "typical_education": [
            "Degree or diploma in Computer Science, Web Technologies, or related area",
            "Relevant practical training, coding bootcamps, or self-directed project portfolio"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate", "Higher Secondary"],
        "progression": [
            "Junior Web Developer",
            "Full Stack / Frontend Developer",
            "Lead Web Architect",
            "Head of Digital Engineering / VP of Technology"
        ]
    },
    {
        "id": "cloud-devops-engineer",
        "name": "Cloud & DevOps Engineer",
        "domain": "Technology & Software",
        "related_domains": ["Cybersecurity", "Engineering"],
        "description": "Automates deployment pipelines, manages cloud infrastructure, and ensures system scalability and uptime.",
        "related_interests": ["Cloud Computing", "DevOps", "Python", "Skilled Trades & Networking"],
        "important_skills": ["Linux", "Docker & Kubernetes", "CI/CD Automation", "Cloud Platforms (AWS/GCP/Azure)", "Networking", "Infrastructure as Code"],
        "typical_education": [
            "Degree in Computer Science, Information Systems, or Engineering",
            "Diploma in networking/computer hardware with industry cloud certifications"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate", "Diploma"],
        "progression": [
            "Associate Cloud Engineer",
            "DevOps / SRE Engineer",
            "Senior Cloud Architect",
            "Director of Infrastructure / Chief Technology Officer"
        ]
    },

    # 2. Data & AI
    {
        "id": "data-scientist",
        "name": "Data Scientist",
        "domain": "Data & AI",
        "related_domains": ["Science & Research", "Technology & Software"],
        "description": "Extracts insights from complex datasets using advanced statistical modeling, predictive algorithms, and machine learning.",
        "related_interests": ["Data Science", "Machine Learning", "Python", "Artificial Intelligence", "Mathematics"],
        "typical_education": [
            "Bachelor's or Master's degree in Computer Science, Data Science, Statistics, Mathematics, or Quantitative Sciences",
            "Postgraduate coursework in machine learning, linear algebra, and data pipelines"
        ],
        "important_skills": ["Python / R", "SQL", "Statistical Modeling", "Machine Learning Algorithms", "Data Visualization", "Feature Engineering"],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Junior Data Analyst / Associate Scientist",
            "Data Scientist",
            "Senior Data Scientist / Research Lead",
            "Principal Scientist / Chief Data Officer"
        ]
    },
    {
        "id": "machine-learning-engineer",
        "name": "Machine Learning & AI Engineer",
        "domain": "Data & AI",
        "related_domains": ["Technology & Software", "Engineering"],
        "description": "Designs, deploys, and optimizes scalable machine learning architectures and autonomous deep learning systems.",
        "related_interests": ["Artificial Intelligence", "Machine Learning", "Python", "Data Science", "Robotics"],
        "important_skills": ["Deep Learning Frameworks (PyTorch/TensorFlow)", "Python", "Model Deployment & MLOps", "Data Structures", "Linear Algebra"],
        "typical_education": [
            "Degree in Computer Science, Artificial Intelligence, Computational Engineering, or allied field",
            "Master's or specialized graduate certification often advantageous for advanced research roles"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Associate AI / ML Developer",
            "Machine Learning Engineer",
            "Senior ML Engineer / AI Architect",
            "Head of AI Research & Engineering"
        ]
    },
    {
        "id": "data-analyst",
        "name": "Data Analyst",
        "domain": "Data & AI",
        "related_domains": ["Business & Management", "Finance & Commerce"],
        "description": "Interprets operational metrics, prepares analytical dashboards, and translates data trends into business intelligence.",
        "related_interests": ["Data Science", "Finance", "Business Management", "Accounting"],
        "important_skills": ["SQL", "Excel / Spreadsheets", "BI Tools (PowerBI / Tableau)", "Data Wrangling", "Analytical Communication"],
        "typical_education": [
            "Degree or diploma in Business, Computer Science, Economics, Mathematics, or Commerce",
            "Certified training in database querying and business intelligence tools"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate"],
        "progression": [
            "Junior Data Analyst",
            "Senior Business Intelligence Analyst",
            "Analytics Manager",
            "Director of Business Intelligence"
        ]
    },

    # 3. Cybersecurity
    {
        "id": "cybersecurity-analyst",
        "name": "Cybersecurity Analyst",
        "domain": "Cybersecurity",
        "related_domains": ["Technology & Software", "Government & Public Service"],
        "description": "Monitors enterprise networks, detects vulnerabilities, assesses cyber threats, and implements defense countermeasures.",
        "related_interests": ["Cybersecurity", "Python", "Skilled Trades & Networking"],
        "important_skills": ["Network Protocols", "Threat Analysis", "SIEM Tools", "Vulnerability Scanning", "Incident Response"],
        "typical_education": [
            "Degree in Cybersecurity, Computer Science, Information Assurance, or Computer Engineering",
            "Technical diploma with industry credentials such as CompTIA Security+, CEH, or equivalent"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate"],
        "progression": [
            "Security Operations Center (SOC) Analyst",
            "Information Security Specialist",
            "Senior Security Engineer / Penetration Tester",
            "Chief Information Security Officer (CISO)"
        ]
    },

    # 4. Engineering
    {
        "id": "mechanical-engineer",
        "name": "Mechanical Engineer",
        "domain": "Engineering",
        "related_domains": ["Science & Research"],
        "description": "Develops, tests, and manufactures physical machinery, thermal mechanisms, mechanical equipment, and automotive systems.",
        "related_interests": ["Mechanical Engineering", "Physics", "Robotics"],
        "important_skills": ["CAD Design (AutoCAD/SolidWorks)", "Thermodynamics", "Materials Science", "Fluid Mechanics", "Prototyping"],
        "typical_education": [
            "Bachelor of Technology / Bachelor of Engineering in Mechanical Engineering",
            "Diploma in Mechanical Engineering providing foundational or lateral entry"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate"],
        "progression": [
            "Graduate Engineer Trainee",
            "Mechanical Design Engineer",
            "Senior Systems Engineer / Project Lead",
            "Chief Mechanical Engineer / Plant Director"
        ]
    },
    {
        "id": "civil-engineer",
        "name": "Civil Engineer",
        "domain": "Engineering",
        "related_domains": ["Government & Public Service"],
        "description": "Plans, designs, and oversees construction of physical infrastructure including bridges, transit systems, and commercial buildings.",
        "related_interests": ["Civil Engineering", "Physics", "Government & Civil Services"],
        "important_skills": ["Structural Analysis", "AutoCAD / Civil 3D", "Geotechnical Surveying", "Project Estimation", "Site Management"],
        "typical_education": [
            "Degree in Civil Engineering or Structural Engineering",
            "Diploma in Civil Engineering or Construction Technology"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate"],
        "progression": [
            "Site Engineer / Assistant Civil Engineer",
            "Project Engineer / Structural Consultant",
            "Senior Project Manager",
            "Chief Infrastructure Director"
        ]
    },
    {
        "id": "electronics-engineer",
        "name": "Electronics & Embedded Systems Engineer",
        "domain": "Engineering",
        "related_domains": ["Technology & Software"],
        "description": "Designs circuit boards, microcontrollers, semiconductor architectures, and embedded electronic systems.",
        "related_interests": ["Electronics & Electrical", "Robotics", "C++", "Physics"],
        "important_skills": ["Circuit Simulation", "PCB Layout", "Microcontrollers (ARM/ESP32)", "Embedded C/C++", "Signal Processing"],
        "typical_education": [
            "Degree in Electronics & Communication, Electrical Engineering, or Embedded Systems",
            "Diploma in Electronics or Electrical Engineering"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate"],
        "progression": [
            "Embedded Systems Engineer Trainee",
            "Hardware / Firmware Engineer",
            "Lead VLSI / Electronics Architect",
            "Director of Hardware Engineering"
        ]
    },

    # 5. Healthcare
    {
        "id": "medical-professional",
        "name": "Medical Doctor / Healthcare Professional",
        "domain": "Healthcare",
        "related_domains": ["Science & Research"],
        "description": "Diagnoses, treats, and manages patient illnesses, prescribes therapies, and oversees clinical care pathways.",
        "related_interests": ["Medicine", "Biology", "Chemistry"],
        "important_skills": ["Clinical Diagnosis", "Patient Care", "Medical Knowledge", "Empathy & Communication", "Surgical Precision"],
        "typical_education": [
            "MBBS / MD / equivalent medical degree accredited by relevant national medical regulatory councils",
            "Mandatory clinical internship, residency, and statutory state/national medical licensing"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Medical Intern / Junior Resident",
            "General Physician / Resident Specialist",
            "Consultant Physician / Specialized Surgeon",
            "Medical Director / Department Head"
        ]
    },
    {
        "id": "clinical-researcher",
        "name": "Biomedical & Clinical Researcher",
        "domain": "Healthcare",
        "related_domains": ["Science & Research", "Data & AI"],
        "description": "Conducts laboratory investigations, clinical drug trials, genetic assays, and biological studies to advance medical therapeutics.",
        "related_interests": ["Biology", "Chemistry", "Medicine", "Data Science"],
        "important_skills": ["Laboratory Assays", "Experimental Design", "Data Analysis", "Good Clinical Practice (GCP)", "Scientific Writing"],
        "typical_education": [
            "Bachelor's or Master's degree in Biotechnology, Biochemistry, Microbiology, or Biomedical Sciences",
            "Doctoral degree (PhD) frequently required for independent research lead roles"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Research Assistant / Laboratory Analyst",
            "Clinical Research Associate",
            "Senior Scientist / Clinical Trial Manager",
            "Principal Research Investigator"
        ]
    },

    # 6. Business & Management
    {
        "id": "business-analyst",
        "name": "Business Analyst & Operations Specialist",
        "domain": "Business & Management",
        "related_domains": ["Finance & Commerce", "Technology & Software"],
        "description": "Evaluates enterprise processes, identifies operational efficiencies, and liaises between business units and technical teams.",
        "related_interests": ["Business Management", "Finance", "Data Science", "Marketing"],
        "important_skills": ["Requirements Gathering", "Process Mapping", "Data Interpretation", "Stakeholder Presentation", "Agile Methodologies"],
        "typical_education": [
            "Degree in Business Administration, Commerce, Information Systems, or Engineering",
            "Postgraduate MBA or business analysis credentials advantageous"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate", "Diploma"],
        "progression": [
            "Associate Business Analyst",
            "Senior Business Consultant",
            "Operations Manager",
            "Chief Operating Officer (COO) / Strategy Director"
        ]
    },
    {
        "id": "marketing-manager",
        "name": "Digital Marketing & Growth Strategist",
        "domain": "Business & Management",
        "related_domains": ["Media & Communication", "Design & Creative"],
        "description": "Plans market outreach, optimizes customer acquisition channels, orchestrates brand campaigns, and analyzes consumer analytics.",
        "related_interests": ["Marketing", "Writing & Journalism", "Graphic Design", "Business Management"],
        "important_skills": ["SEO / SEM", "Content Strategy", "Social Media Analytics", "Campaign Performance Analysis", "Creative Storytelling"],
        "typical_education": [
            "Degree in Marketing, Communications, Business Administration, or related field",
            "Certifications in digital analytics and platform marketing"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate", "Diploma"],
        "progression": [
            "Marketing Coordinator",
            "Digital Marketing Manager",
            "Director of Growth & Marketing",
            "Chief Marketing Officer (CMO)"
        ]
    },

    # 7. Finance & Commerce
    {
        "id": "chartered-accountant",
        "name": "Accountant & Financial Auditor",
        "domain": "Finance & Commerce",
        "related_domains": ["Business & Management", "Law"],
        "description": "Prepares financial statements, conducts statutory audits, assesses tax liabilities, and ensures corporate fiscal regulatory compliance.",
        "related_interests": ["Accounting", "Finance", "Law & Legal Studies"],
        "important_skills": ["Financial Reporting", "Tax Compliance", "Auditing", "Accounting Software (Tally/SAP)", "Numerical Accuracy"],
        "typical_education": [
            "Professional qualification (such as CA, CPA, CMA, or ACCA)",
            "Bachelor's degree in Commerce, Accounting, or Finance combined with statutory articleship/internship"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Audit Trainee / Assistant Accountant",
            "Senior Accountant / Internal Auditor",
            "Finance Manager / Partner",
            "Chief Financial Officer (CFO)"
        ]
    },
    {
        "id": "financial-analyst",
        "name": "Financial Analyst & Investment Specialist",
        "domain": "Finance & Commerce",
        "related_domains": ["Business & Management", "Data & AI"],
        "description": "Assesses economic trends, builds financial valuation models, reviews portfolio performance, and advises on capital allocation.",
        "related_interests": ["Finance", "Accounting", "Business Management", "Data Science"],
        "important_skills": ["Financial Modeling", "Valuation", "Excel / Financial Spreadsheets", "Macroeconomic Analysis", "Risk Assessment"],
        "typical_education": [
            "Degree in Finance, Economics, Commerce, Mathematics, or Engineering",
            "Chartered Financial Analyst (CFA) or Master's in Finance frequently pursued"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Junior Financial Analyst",
            "Equity / Investment Analyst",
            "Portfolio Manager / Investment Banker",
            "Chief Investment Officer (CIO)"
        ]
    },

    # 8. Education & Teaching
    {
        "id": "educator-teacher",
        "name": "Teacher & Educational Specialist",
        "domain": "Education & Teaching",
        "related_domains": ["Science & Research", "Media & Communication"],
        "description": "Delivers curriculum instruction, mentors learners across academic disciplines, and designs pedagogic assessment materials.",
        "related_interests": ["Teaching & Education", "Physics", "Chemistry", "Biology", "Mathematics"],
        "important_skills": ["Pedagogy", "Curriculum Planning", "Classroom Communication", "Student Mentorship", "Assessment Design"],
        "typical_education": [
            "Bachelor's or Master's degree in target academic subject plus professional education qualification (such as B.Ed / D.Ed)",
            "Applicable national or state teacher eligibility certifications (e.g. TET/NET) where mandated"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Secondary / Primary Teacher",
            "Senior Subject Head / Academic Coordinator",
            "Vice Principal / Principal",
            "Educational Administrator / Policy Advisor"
        ]
    },

    # 9. Law
    {
        "id": "legal-counsel",
        "name": "Lawyer & Legal Advocate",
        "domain": "Law",
        "related_domains": ["Government & Public Service", "Business & Management"],
        "description": "Provides legal counsel, drafts contracts, represents clients in judicial forums, and advises organizations on statutory compliance.",
        "related_interests": ["Law & Legal Studies", "Government & Civil Services", "Writing & Journalism"],
        "important_skills": ["Legal Research", "Contract Drafting", "Statutory Interpretation", "Argumentation & Advocacy", "Negotiation"],
        "typical_education": [
            "Undergraduate law degree (LL.B, 3-year or 5-year integrated BA/BBA LL.B)",
            "Enrollment and bar license examination with the applicable Bar Council"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Associate Advocate / Legal Associate",
            "Senior Legal Counsel / Litigator",
            "Partner at Law Firm / General Counsel",
            "Senior Advocate / Judicial Officer"
        ]
    },

    # 10. Design & Creative
    {
        "id": "ui-ux-designer",
        "name": "UI/UX & Digital Product Designer",
        "domain": "Design & Creative",
        "related_domains": ["Technology & Software"],
        "description": "Conducts user research, designs wireframes and high-fidelity prototypes, and shapes intuitive digital product user experiences.",
        "related_interests": ["Graphic Design", "Web Development", "Marketing"],
        "important_skills": ["Figma / Design Tools", "Wireframing", "User Research", "Interaction Design", "Usability Testing"],
        "typical_education": [
            "Degree or diploma in Design (B.Des / M.Des), Fine Arts, Human-Computer Interaction, or Architecture",
            "Practical digital portfolio demonstrating user-centric design workflows"
        ],
        "education_levels_supported": ["Undergraduate", "Diploma", "Postgraduate"],
        "progression": [
            "Junior UI/UX Designer",
            "Product Designer",
            "Lead Experience Designer",
            "Head of Design / VP of User Experience"
        ]
    },

    # 11. Government & Public Service
    {
        "id": "civil-services-administrator",
        "name": "Civil Services & Public Administrator",
        "domain": "Government & Public Service",
        "related_domains": ["Law", "Business & Management"],
        "description": "Executes government administrative policies, oversees civic resources, and manages public regulatory and developmental machinery.",
        "related_interests": ["Government & Civil Services", "Law & Legal Studies", "Teaching & Education"],
        "important_skills": ["Public Administration", "Policy Analysis", "Constitutional Knowledge", "Crisis Management", "Public Communication"],
        "typical_education": [
            "Recognized graduation degree in any discipline",
            "Competitive selection through national/state civil service examinations (e.g. UPSC, State PSCs)"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate"],
        "progression": [
            "Sub-Divisional / Assistant Administrator",
            "District Administrative Officer / Joint Secretary",
            "Principal Secretary / Department Head",
            "Chief Secretary / Cabinet Secretary"
        ]
    },

    # 12. Media & Communication
    {
        "id": "technical-writer-journalist",
        "name": "Technical Writer & Communications Specialist",
        "domain": "Media & Communication",
        "related_domains": ["Technology & Software", "Design & Creative"],
        "description": "Creates technical documentation, developer guides, investigative articles, and corporate communication assets.",
        "related_interests": ["Writing & Journalism", "Marketing", "Web Development"],
        "important_skills": ["Technical Writing", "Editing", "Information Architecture", "Content Management", "Research"],
        "typical_education": [
            "Degree in English, Journalism, Mass Communication, Computer Science, or Humanities",
            "Demonstrated portfolio of published technical articles or documentation"
        ],
        "education_levels_supported": ["Undergraduate", "Postgraduate", "Diploma"],
        "progression": [
            "Junior Technical Writer / Reporter",
            "Senior Communications Specialist",
            "Documentation Manager / Editorial Lead",
            "Director of Corporate Communications"
        ]
    },

    # 13. Science & Research
    {
        "id": "research-scientist",
        "name": "Research Scientist (Physical & Chemical Sciences)",
        "domain": "Science & Research",
        "related_domains": ["Engineering", "Healthcare"],
        "description": "Conducts scientific investigations, formulates hypotheses, publishes peer-reviewed research, and develops new materials or technologies.",
        "related_interests": ["Physics", "Chemistry", "Mathematics", "Data Science"],
        "important_skills": ["Empirical Research", "Mathematical Modeling", "Instrumentation", "Statistical Analysis", "Scientific Publishing"],
        "typical_education": [
            "Postgraduate degree (M.Sc / M.Tech) followed by Doctorate (Ph.D.) in scientific or quantitative discipline",
            "Postdoctoral research fellowship commonly required for senior institutional roles"
        ],
        "education_levels_supported": ["Postgraduate"],
        "progression": [
            "Junior Research Fellow (JRF)",
            "Senior Research Fellow (SRF)",
            "Scientist / Assistant Professor",
            "Principal Scientist / Lab Director"
        ]
    },

    # 14. Skilled & Technical Trades
    {
        "id": "systems-network-technician",
        "name": "Hardware & Network Infrastructure Technician",
        "domain": "Skilled & Technical Trades",
        "related_domains": ["Technology & Software", "Cybersecurity"],
        "description": "Installs, configures, and repairs physical IT hardware, network switches, cabling infrastructure, and server appliances.",
        "related_interests": ["Skilled Trades & Networking", "Electronics & Electrical"],
        "important_skills": ["Hardware Diagnostics", "Network Cabling", "Router/Switch Configuration", "OS Installation", "Component Troubleshooting"],
        "typical_education": [
            "Diploma or ITI certificate in Computer Hardware, Electronics, or Networking",
            "Industry vendor certifications (Cisco CCNA, CompTIA A+/Network+)"
        ],
        "education_levels_supported": ["Diploma", "Higher Secondary", "Secondary"],
        "progression": [
            "Junior Bench / Field Technician",
            "Systems Administrator / Network Technician",
            "Infrastructure Lead",
            "Data Center Operations Manager"
        ]
    }
]

# Quick index by ID and domain
CATALOGUE_BY_ID = {c["id"]: c for c in CAREER_CATALOGUE}
CATALOGUE_BY_DOMAIN = {}
for c in CAREER_CATALOGUE:
    CATALOGUE_BY_DOMAIN.setdefault(c["domain"], []).append(c)
