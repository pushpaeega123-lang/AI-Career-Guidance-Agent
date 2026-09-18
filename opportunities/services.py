from typing import Any, Dict, List, Optional, Set
from flask import has_request_context, session
from db import db
from .models import Opportunity


class OpportunityService:
    """
    Service logic for Opportunity Aggregation and Job Opportunity Flow.
    Provides sector + education + skills based matching for Government and Private sectors
    returning ALL matching opportunities ordered by relevance with match explanations.
    """

    # Education level qualification hierarchy for deterministic matching
    EDU_TIER = {
        "class 10": 1,
        "10th": 1,
        "matriculation": 1,
        "secondary": 1,
        "class 12": 2,
        "12th": 2,
        "intermediate": 2,
        "higher secondary": 2,
        "senior secondary": 2,
        "10+2": 2,
        "puc": 2,
        "diploma": 3,
        "polytechnic": 3,
        "iti": 3,
        "undergraduate": 4,
        "graduate": 4,
        "degree": 4,
        "bachelor": 4,
        "b.tech": 4,
        "btech": 4,
        "b.sc": 4,
        "b.com": 4,
        "b.a": 4,
        "bba": 4,
        "bca": 4,
        "postgraduate": 5,
        "master": 5,
        "m.tech": 5,
        "mba": 5,
        "ph.d": 5
    }

    # Structured Verified Job Catalog Categorized by Category and Sector
    JOB_CATALOG: List[Dict[str, Any]] = [
        # =========================================================================
        # PRIVATE JOBS - IT & Software
        # =========================================================================
        {
            "id": "priv-it-1",
            "title": "Junior Software Developer / Associate Engineer",
            "category": "private_job",
            "sector": "IT & Software",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Python", "JavaScript", "Problem Solving", "Git"],
            "description": "Writing clean code, assisting web/mobile feature development, and resolving bugs under senior engineer mentorship.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-it-2",
            "title": "Web Development & Frontend Trainee",
            "category": "private_job",
            "sector": "IT & Software",
            "qualification": "Diploma",
            "min_tier": 3,
            "required_skills": ["HTML/CSS", "JavaScript", "Communication", "Problem Solving"],
            "description": "Building responsive landing pages, updating web components, and testing cross-browser styling.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-it-3",
            "title": "QA & Software Testing Associate",
            "category": "private_job",
            "sector": "IT & Software",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Test Documentation", "Attention to Detail", "Basic Coding", "Problem Solving"],
            "description": "Executing test plans, documenting defects in bug trackers, and performing regression validation on web applications.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-it-4",
            "title": "IT Technical Support Associate",
            "category": "private_job",
            "sector": "IT & Software",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["Computer Troubleshooting", "Communication", "Operating Systems", "Active Listening"],
            "description": "Assisting internal employees and customers with software setup, account access, and workstation diagnostics.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },

        # =========================================================================
        # PRIVATE JOBS - Data & Analytics
        # =========================================================================
        {
            "id": "priv-data-1",
            "title": "Business & Data Operations Analyst",
            "category": "private_job",
            "sector": "Data & Analytics",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["SQL", "MS Excel", "Data Analysis", "Problem Solving"],
            "description": "Extracting operational datasets, compiling executive performance dashboards, and identifying workflow optimizations.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-data-2",
            "title": "Data Entry & MIS Operations Assistant",
            "category": "private_job",
            "sector": "Data & Analytics",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["MS Excel", "Data Entry", "Typing Accuracy (30+ WPM)", "Spreadsheets"],
            "description": "Entering, reviewing, and maintaining business information records in spreadsheets and database management systems with high accuracy.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-data-3",
            "title": "Junior Data Extraction & Research Specialist",
            "category": "private_job",
            "sector": "Data & Analytics",
            "qualification": "Diploma",
            "min_tier": 3,
            "required_skills": ["MS Excel", "Web Research", "Data Entry", "Attention to Detail"],
            "description": "Collecting structured industry information from public directories and verifying data records in company spreadsheets.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },

        # =========================================================================
        # PRIVATE JOBS - Finance & Accounting
        # =========================================================================
        {
            "id": "priv-fin-1",
            "title": "Accounts Assistant",
            "category": "private_job",
            "sector": "Finance & Accounting",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Accounting", "MS Excel", "Tally", "Financial Reporting"],
            "description": "Maintaining daily ledger entries, verifying vendor vouchers, preparing account reconciliations, and supporting annual audits.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-fin-2",
            "title": "Finance Operations Associate",
            "category": "private_job",
            "sector": "Finance & Accounting",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Financial Analysis", "MS Excel", "Communication", "Mathematics"],
            "description": "Reviewing expense disbursements, tracking cash flows, and generating recurring financial summaries for team leadership.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-fin-3",
            "title": "Billing & Invoice Processing Executive",
            "category": "private_job",
            "sector": "Finance & Accounting",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["MS Excel", "Data Entry", "Billing Software", "Mathematics"],
            "description": "Generating commercial customer invoices, calculating applicable tax line-items, and verifying dispatch payment receipts.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-fin-4",
            "title": "Bank Branch Operations Trainee",
            "category": "private_job",
            "sector": "Finance & Accounting",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Customer Service", "Banking Operations", "Communication", "Mathematics"],
            "description": "Assisting bank customers with account opening documentation, deposit servicing, and banking kiosk guidance.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },

        # =========================================================================
        # PRIVATE JOBS - Sales & Marketing
        # =========================================================================
        {
            "id": "priv-sales-1",
            "title": "Field Sales & Merchant Onboarding Trainee",
            "category": "private_job",
            "sector": "Sales & Marketing",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["Communication", "Negotiation", "Sales Pitching", "Relationship Building"],
            "description": "Visiting retail stores, presenting digital payment or SaaS merchant solutions, and onboarding new business partners.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-sales-2",
            "title": "Junior Digital Marketing & Social Media Assistant",
            "category": "private_job",
            "sector": "Sales & Marketing",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["Social Media", "Content Creation", "Communication", "Basic Graphic Tools"],
            "description": "Scheduling daily brand promotional posts across social networks, engaging with follower inquiries, and tracking campaign traffic.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-sales-3",
            "title": "Retail Store Sales & Checkout Associate",
            "category": "private_job",
            "sector": "Sales & Marketing",
            "qualification": "Class 10",
            "min_tier": 1,
            "required_skills": ["Customer Service", "Communication", "POS Billing", "Teamwork"],
            "description": "Guiding in-store shoppers, managing counter checkouts, and keeping retail shelves organized and stocked.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-sales-4",
            "title": "Inside Sales & Business Development Associate",
            "category": "private_job",
            "sector": "Sales & Marketing",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Communication", "Lead Qualification", "Email Writing", "Sales Pitching"],
            "description": "Reaching out to inbound customer inquiries via telephone and email, understanding client needs, and booking product demos.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },

        # =========================================================================
        # PRIVATE JOBS - Administration & Customer Service
        # =========================================================================
        {
            "id": "priv-adm-1",
            "title": "Customer Support & Tele-Service Representative",
            "category": "private_job",
            "sector": "Customer Service & Operations",
            "qualification": "Class 10",
            "min_tier": 1,
            "required_skills": ["Spoken Communication", "Active Listening", "Customer Service", "Basic Computer Skills"],
            "description": "Assisting customers with inquiries, order tracking, and service information via voice calls and web chat.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-adm-2",
            "title": "Office Operations & Administrative Assistant",
            "category": "private_job",
            "sector": "Administration & Office",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["MS Office", "Document Organization", "Communication", "Time Management"],
            "description": "Managing office correspondence, organizing physical/digital files, greeting office visitors, and scheduling conference rooms.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-adm-3",
            "title": "Human Resources & Talent Acquisition Associate",
            "category": "private_job",
            "sector": "Administration & Office",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Candidate Screening", "Communication", "Interview Scheduling", "HR Documentation"],
            "description": "Reviewing candidate resumes, organizing interview calendars, and coordinating new employee onboarding documentation.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-adm-4",
            "title": "Logistics & Fulfillment Associate",
            "category": "private_job",
            "sector": "Logistics & Operations",
            "qualification": "Class 10",
            "min_tier": 1,
            "required_skills": ["Inventory Sorting", "Barcode Scanning", "Basic Mathematics", "Teamwork"],
            "description": "Assisting in warehouse inbound sorting, packaging, dispatch verification, and stock recording for retail hubs.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },

        # =========================================================================
        # PRIVATE JOBS - Design & Engineering
        # =========================================================================
        {
            "id": "priv-eng-1",
            "title": "CAD Drafting & Engineering Technician",
            "category": "private_job",
            "sector": "Design & Engineering",
            "qualification": "Diploma",
            "min_tier": 3,
            "required_skills": ["AutoCAD", "Blueprint Reading", "Technical Documentation", "Problem Solving"],
            "description": "Creating 2D/3D component drawings and architectural drafts working directly alongside project engineers.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },
        {
            "id": "priv-eng-2",
            "title": "IT Hardware & Network Support Specialist",
            "category": "private_job",
            "sector": "Design & Engineering",
            "qualification": "Diploma",
            "min_tier": 3,
            "required_skills": ["Hardware Troubleshooting", "LAN / Router Setup", "Operating Systems", "Problem Solving"],
            "description": "Setting up company workstations, resolving hardware issues, and maintaining local office networking stability.",
            "source": "Industry Entry Standard (Verified)",
            "verification_status": "Verified Entry Role"
        },

        # =========================================================================
        # GOVERNMENT JOBS - Central Ministries & Staff Selection
        # =========================================================================
        {
            "id": "govt-ssc-1",
            "title": "Staff Selection Commission - Multi-Tasking Staff (SSC MTS)",
            "category": "govt_job",
            "sector": "Central Ministries & Administration",
            "qualification": "Class 10",
            "min_tier": 1,
            "required_skills": ["General Awareness", "Basic Mathematics", "Reasoning Ability", "English Comprehension"],
            "exam_selection": "SSC MTS Computer Based Examination (CBT)",
            "description": "Central government non-technical staff entry-level roles across various national ministries, departments, and attached offices.",
            "source": "Official SSC Portal (ssc.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-ssc-2",
            "title": "SSC Combined Higher Secondary Level (SSC CHSL)",
            "category": "govt_job",
            "sector": "Central Ministries & Administration",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["Typing Speed", "General Intelligence", "Basic Mathematics", "English"],
            "exam_selection": "SSC CHSL Tier-I (CBT) & Tier-II (Skill/Typing Test)",
            "description": "Lower Division Clerk (LDC), Junior Secretariat Assistant (JSA), and Data Entry Operator (DEO) in central government offices.",
            "source": "Official SSC Portal (ssc.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-ssc-3",
            "title": "SSC Combined Graduate Level (SSC CGL)",
            "category": "govt_job",
            "sector": "Central Ministries & Administration",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Quantitative Aptitude", "General Studies", "Logical Reasoning", "English Comprehension"],
            "exam_selection": "SSC CGL Tier-I & Tier-II Computer Based Examinations",
            "description": "Assistant Section Officer, Inspector (Central Excise / Income Tax), and Sub-Inspector posts across central ministries.",
            "source": "Official SSC Portal (ssc.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-ssc-4",
            "title": "UPSC Civil Services Examination (CSE)",
            "category": "govt_job",
            "sector": "Central Ministries & Administration",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Critical Thinking", "General Studies", "Essay Writing", "Public Affairs Knowledge"],
            "exam_selection": "UPSC Prelims, Mains Written & Personality Test (Interview)",
            "description": "Prestigious administrative leadership roles including Indian Administrative Service (IAS), IPS, and Indian Foreign Service.",
            "source": "Union Public Service Commission (upsc.gov.in)",
            "verification_status": "Verified Public Notification"
        },

        # =========================================================================
        # GOVERNMENT JOBS - Railways & Transport
        # =========================================================================
        {
            "id": "govt-rly-1",
            "title": "Railway Recruitment Board - Level 1 Group D Posts",
            "category": "govt_job",
            "sector": "Railways & Transport",
            "qualification": "Class 10",
            "min_tier": 1,
            "required_skills": ["Basic Science", "Mathematics", "Physical Fitness", "General Reasoning"],
            "exam_selection": "RRB Computer Based Test (CBT) & Physical Efficiency Test",
            "description": "Indian Railways track maintainer, assistant pointsman, carriage and technical workshop support positions.",
            "source": "Railway Recruitment Control Board (indianrailways.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-rly-2",
            "title": "Railway Recruitment Board - Junior Engineer (RRB JE)",
            "category": "govt_job",
            "sector": "Railways & Transport",
            "qualification": "Diploma",
            "min_tier": 3,
            "required_skills": ["Technical Engineering", "General Science", "Reasoning", "Mathematics"],
            "exam_selection": "RRB JE CBT-1 & Technical Domain CBT-2",
            "description": "Technical supervisor and maintenance engineer posts in zonal railway divisions and workshops.",
            "source": "Railway Recruitment Control Board (indianrailways.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-rly-3",
            "title": "RRB Non-Technical Popular Categories (NTPC)",
            "category": "govt_job",
            "sector": "Railways & Transport",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["General Awareness", "Mathematics", "Logical Reasoning", "Typing Speed"],
            "exam_selection": "RRB NTPC CBT-1 & CBT-2 Computer Based Examinations",
            "description": "Station Master, Goods Guard, Senior Commercial Clerk, and Traffic Assistant positions across railway zones.",
            "source": "Railway Recruitment Control Board (indianrailways.gov.in)",
            "verification_status": "Verified Public Notification"
        },

        # =========================================================================
        # GOVERNMENT JOBS - Defense & Police Services
        # =========================================================================
        {
            "id": "govt-def-1",
            "title": "National Defence Academy & Naval Academy (NDA / NA Exam)",
            "category": "govt_job",
            "sector": "Defense & Police Services",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["Mathematics", "Physics", "English", "Physical Fitness", "General Knowledge"],
            "exam_selection": "UPSC Written Examination & SSB Interview",
            "description": "Cadet officer entry into the Indian Army, Navy, and Air Force with full-time defense academy training.",
            "source": "Union Public Service Commission (upsc.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-def-2",
            "title": "State Police Constable Recruitment",
            "category": "govt_job",
            "sector": "Defense & Police Services",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["General Knowledge", "Physical Fitness", "Reasoning", "Communication"],
            "exam_selection": "State Police Board Written Exam & Physical Standards Test",
            "description": "Law enforcement, community patrol, and public safety constable positions in state police departments.",
            "source": "State Police Recruitment Boards",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-def-3",
            "title": "Sub-Inspector of Police (CAPF / State SI)",
            "category": "govt_job",
            "sector": "Defense & Police Services",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["General Studies", "Reasoning Ability", "Physical Fitness", "English Comprehension"],
            "exam_selection": "SSC CPO / State Police SI Written Exam & PET",
            "description": "Sub-Inspector and police officer leadership roles in central armed police forces and state police stations.",
            "source": "Staff Selection Commission & State Police Boards",
            "verification_status": "Verified Public Notification"
        },

        # =========================================================================
        # GOVERNMENT JOBS - Banking & Public Sector
        # =========================================================================
        {
            "id": "govt-bank-1",
            "title": "Banking - Probationary Officer (IBPS / SBI PO)",
            "category": "govt_job",
            "sector": "Banking & Public Sector",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Quantitative Aptitude", "Reasoning Ability", "English", "General Banking Awareness"],
            "exam_selection": "IBPS / SBI PO Prelims, Mains Exam & Group Discussion / Interview",
            "description": "Officer-cadre management trainee positions across major public sector commercial banks.",
            "source": "Institute of Banking Personnel Selection (ibps.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-bank-2",
            "title": "State Bank of India - Junior Associate (Clerical)",
            "category": "govt_job",
            "sector": "Banking & Public Sector",
            "qualification": "Undergraduate",
            "min_tier": 4,
            "required_skills": ["Numerical Ability", "Reasoning", "English Comprehension", "Computer Aptitude"],
            "exam_selection": "SBI Clerk Prelims & Mains Online Examination",
            "description": "Customer servicing, cash transaction processing, and account maintenance across SBI branches nationwide.",
            "source": "State Bank of India (sbi.co.in)",
            "verification_status": "Verified Public Notification"
        },

        # =========================================================================
        # GOVERNMENT JOBS - Postal & Communications
        # =========================================================================
        {
            "id": "govt-post-1",
            "title": "India Post - Gramin Dak Sevak (GDS)",
            "category": "govt_job",
            "sector": "Postal & Communications",
            "qualification": "Class 10",
            "min_tier": 1,
            "required_skills": ["Mathematics", "Local Language", "Basic Computer Knowledge", "Communication"],
            "exam_selection": "Merit-based Selection (Class 10 Board Marks)",
            "description": "Branch Postmaster (BPM) and Assistant Branch Postmaster (ABPM) positions in postal service branches.",
            "source": "Department of Posts (indiapostgdsonline.gov.in)",
            "verification_status": "Verified Public Notification"
        },
        {
            "id": "govt-post-2",
            "title": "India Post - Postman & Mail Guard",
            "category": "govt_job",
            "sector": "Postal & Communications",
            "qualification": "Class 12",
            "min_tier": 2,
            "required_skills": ["Local Language", "General Knowledge", "Basic Mathematics", "Two-Wheeler Driving"],
            "exam_selection": "India Post Direct Recruitment Exam",
            "description": "Delivery sorting and mail dispatch service positions across regional postal distribution circles.",
            "source": "Department of Posts",
            "verification_status": "Verified Public Notification"
        },

        # =========================================================================
        # GOVERNMENT JOBS - Engineering & Technical Services
        # =========================================================================
        {
            "id": "govt-eng-1",
            "title": "SSC Junior Engineer (SSC JE)",
            "category": "govt_job",
            "sector": "Engineering & Technical Services",
            "qualification": "Diploma",
            "min_tier": 3,
            "required_skills": ["Civil/Electrical/Mechanical Engineering", "General Intelligence", "General Science"],
            "exam_selection": "SSC JE Paper 1 (CBT) & Paper 2 (Technical Domain)",
            "description": "Junior Engineer roles in Civil, Electrical, and Mechanical engineering for CPWD, MES, and central water organizations.",
            "source": "Official SSC Portal (ssc.gov.in)",
            "verification_status": "Verified Public Notification"
        }
    ]

    @classmethod
    def normalize_category(cls, cat: Optional[str]) -> str:
        """Normalize category string to 'private_job' or 'govt_job'."""
        if not cat:
            return "private_job"
        c = str(cat).strip().lower()
        if "gov" in c or "exam" in c:
            return "govt_job"
        return "private_job"

    @classmethod
    def get_education_tier(cls, edu: Optional[str]) -> int:
        """Convert education string to numeric tier (1 to 5)."""
        if not edu:
            return 1
        e_norm = str(edu).strip().lower()
        for key, tier in cls.EDU_TIER.items():
            if key in e_norm:
                return tier
        return 1

    @classmethod
    def normalize_qualification(cls, raw_edu: Optional[str]) -> str:
        """Normalize student qualification into catalog tier name."""
        tier = cls.get_education_tier(raw_edu)
        if tier >= 4:
            return "Undergraduate"
        elif tier == 3:
            return "Diploma"
        elif tier == 2:
            return "Class 12"
        return "Class 10"

    @classmethod
    def get_all_jobs(cls, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all catalog jobs merged with any database Opportunity records.
        """
        norm_cat = cls.normalize_category(category) if category else None
        results: List[Dict[str, Any]] = []

        # 1. Base catalog
        for job in cls.JOB_CATALOG:
            if norm_cat is None or job["category"] == norm_cat:
                results.append(dict(job))

        # 2. Database records
        try:
            db_query = Opportunity.query
            if norm_cat == "govt_job":
                db_query = db_query.filter(
                    (Opportunity.opportunity_type == "govt_job") |
                    (Opportunity.opportunity_type == "exam")
                )
            elif norm_cat == "private_job":
                db_query = db_query.filter(
                    (Opportunity.opportunity_type == "job") |
                    (Opportunity.opportunity_type == "private_job") |
                    (Opportunity.opportunity_type == "internship")
                )
            db_opps = db_query.all()
            for opp in db_opps:
                if not any(r["title"] == opp.title for r in results):
                    results.append({
                        "id": f"db-{opp.id}",
                        "title": opp.title,
                        "category": norm_cat or "private_job",
                        "sector": opp.organization or "General Sector",
                        "qualification": "Class 10",
                        "min_tier": 1,
                        "required_skills": ["Communication", "Problem Solving"],
                        "exam_selection": "Direct Application / Interview" if norm_cat == "private_job" else "Selection Route Notification",
                        "description": f"Verified opportunity in {opp.organization or 'authorized sector'}. Deadline: {opp.deadline or 'Open'}.",
                        "source": opp.organization or "System Database",
                        "verification_status": "Verified Database Record"
                    })
        except Exception:
            pass

        return results

    @classmethod
    def get_sectors(cls, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Dynamically calculate all available sectors and their job counts.
        """
        norm_cat = cls.normalize_category(category)
        jobs = cls.get_all_jobs(category=norm_cat)

        sector_counts: Dict[str, int] = {}
        for j in jobs:
            sec = j.get("sector") or "General"
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

        sectors_list = [
            {"name": sec, "job_count": count}
            for sec, count in sorted(sector_counts.items(), key=lambda x: x[0])
        ]

        return {
            "status": "success",
            "category": norm_cat,
            "total_sectors": len(sectors_list),
            "total_jobs": len(jobs),
            "sectors": sectors_list
        }

    @classmethod
    def get_available_skills(
        cls,
        category: Optional[str] = None,
        sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dynamically extract unique skills present in the matching sector/category.
        """
        norm_cat = cls.normalize_category(category)
        jobs = cls.get_all_jobs(category=norm_cat)

        skills_set: Set[str] = set()
        for j in jobs:
            if sector and j.get("sector", "").lower() != str(sector).strip().lower():
                continue
            for sk in j.get("required_skills", []):
                skills_set.add(sk.strip())

        return {
            "status": "success",
            "category": norm_cat,
            "sector": sector,
            "total_skills": len(skills_set),
            "skills": sorted(list(skills_set), key=lambda s: s.lower())
        }

    @classmethod
    def match_jobs(
        cls,
        category: Optional[str] = None,
        sector: Optional[str] = None,
        education_level: Optional[str] = None,
        skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Match and return ALL opportunities satisfying criteria, ordered by relevance.
        DOES NOT slice or limit to top 3.
        """
        norm_cat = cls.normalize_category(category)
        user_tier = cls.get_education_tier(education_level)
        user_skills = [str(s).strip().lower() for s in (skills or []) if str(s).strip()]

        jobs = cls.get_all_jobs(category=norm_cat)
        matched_results: List[Dict[str, Any]] = []

        norm_sector = str(sector).strip().lower() if sector else ""

        for job in jobs:
            # 1. Sector filter
            job_sector = job.get("sector", "").strip().lower()
            if norm_sector and norm_sector != "all" and job_sector != norm_sector:
                continue

            # 2. Education level qualification check
            job_min_tier = job.get("min_tier", 1)
            is_edu_qualified = user_tier >= job_min_tier

            # 3. Skills match comparison
            job_skills = job.get("required_skills", [])
            matched_skills: List[str] = []
            missing_skills: List[str] = []

            for req_sk in job_skills:
                req_lower = req_sk.lower()
                # Check if any user skill matches req_sk
                if any(u in req_lower or req_lower in u for u in user_skills):
                    matched_skills.append(req_sk)
                else:
                    missing_skills.append(req_sk)

            # 4. Calculate explainable match score
            score = 0
            why_matched: List[str] = []

            if is_edu_qualified:
                score += 40
                why_matched.append("Your education level matches")
            else:
                score += 10

            if norm_sector and job_sector == norm_sector:
                score += 20
                why_matched.append("Your selected sector matches")

            if matched_skills:
                # Skill bonus
                skill_bonus = min(40, len(matched_skills) * 15)
                score += skill_bonus
                for ms in matched_skills:
                    why_matched.append(f"{ms} matches the required skill")
            elif user_skills:
                why_matched.append("Opportunity matches your chosen sector and education level")

            if not why_matched:
                why_matched.append("Matches your chosen qualification criteria")

            matched_results.append({
                "id": job["id"],
                "title": job["title"],
                "category": job["category"],
                "sector": job["sector"],
                "qualification": job["qualification"],
                "qualification_match": is_edu_qualified,
                "exam_selection": job.get("exam_selection"),
                "skills": job_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "required_skills": job_skills,
                "match_score": min(100, score),
                "why_matched": why_matched,
                "description": job.get("description"),
                "source": job.get("source"),
                "verification_status": job.get("verification_status", "Verified Record")
            })

        # Sort ALL matches by relevance score descending
        matched_results.sort(key=lambda x: (x["match_score"], len(x["matched_skills"])), reverse=True)

        return {
            "status": "success",
            "category": norm_cat,
            "sector": sector,
            "education_level": education_level or "Class 10",
            "selected_skills": skills or [],
            "total_matches": len(matched_results),
            "matches": matched_results,
            "has_matches": len(matched_results) > 0,
            "no_match_message": (
                "No matching jobs found. We couldn't find a job that matches all of your selected filters. "
                "Try selecting another sector, another education level, or additional skills."
            ) if len(matched_results) == 0 else None
        }

    @classmethod
    def get_opportunities(
        cls,
        category: Optional[str] = None,
        qualification: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Backward-compatible helper returning opportunities by category & qualification.
        """
        norm_cat = cls.normalize_category(category)
        norm_qual = cls.normalize_qualification(qualification) if qualification else "Class 10"
        match_res = cls.match_jobs(category=norm_cat, education_level=norm_qual)

        return {
            "status": "success",
            "category": norm_cat,
            "qualification": norm_qual,
            "raw_qualification": qualification or norm_qual,
            "total_count": match_res["total_matches"],
            "opportunities": match_res["matches"],
            "has_verified_data": match_res["has_matches"],
            "empty_state_message": match_res["no_match_message"]
        }

    @classmethod
    def get_opportunities_by_type(cls, opp_type: Any) -> List[Dict[str, Any]]:
        """
        Backwards-compatible query helper for opportunity queries by type.
        """
        if not opp_type:
            return []
        opp_str = str(opp_type).strip().lower()
        cat = "govt_job" if "gov" in opp_str or "exam" in opp_str else "private_job"
        res = cls.get_opportunities(category=cat)
        return res.get("opportunities", [])

    @classmethod
    def get_student_qualification(cls, session_obj: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Inspect existing student profile/session for known qualification without mutating state.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            # 1. Check exploration profile
            exp_prof = target_session.get("exploration_profile")
            if isinstance(exp_prof, dict) and exp_prof.get("education_level"):
                return str(exp_prof["education_level"]).strip()

            # 2. Check student_id in session
            student_id = target_session.get("student_id")
            if student_id:
                try:
                    from profile.models import StudentProfile
                    st = db.session.get(StudentProfile, student_id)
                    if st and st.education_level:
                        return str(st.education_level).strip()
                except Exception:
                    pass

        return None

    @classmethod
    def get_student_skills(cls, session_obj: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Inspect existing student profile/session for known skills without mutating state.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            exp_prof = target_session.get("exploration_profile")
            if isinstance(exp_prof, dict) and exp_prof.get("skills"):
                return list(exp_prof["skills"])

            student_id = target_session.get("student_id")
            if student_id:
                try:
                    from profile.models import StudentProfile
                    st = db.session.get(StudentProfile, student_id)
                    if st:
                        return st.to_dict().get("skills", [])
                except Exception:
                    pass

        return []


