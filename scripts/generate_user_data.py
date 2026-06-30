"""
Generates enriched synthetic source data for all candidates.
Each source type is realistic in depth: multi-entry experience, education,
varied skill names, messy date/phone formats where the edge case requires it.
C09 ATS stays malformed. C14 resume stays empty. C13 CSV stays duplicated.

Run: python scripts/generate_user_data.py
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources"

CSV_ROWS = [
    dict(candidate_id="C01", full_name="Linus Torvalds", email="linus.t@example.com",
         phone="+1-415-555-0101", current_company="Linux Foundation",
         title="Kernel Maintainer", location="Portland, OR, US",
         years_experience=29, last_updated="2026-05-01"),
    dict(candidate_id="C02", full_name="Dan Abramov", email="dan.a@example.com",
         phone="+1-415-555-0102", current_company="Meta",
         title="Senior Software Engineer", location="San Francisco, CA, US",
         years_experience=11, last_updated="2026-05-01"),
    dict(candidate_id="C03", full_name="Sindre Sorhus", email="sindre.s@example.com",
         phone="+1-415-555-0103", current_company="Independent",
         title="Open Source Maintainer", location="Tromsoe, Troms, NO",
         years_experience=14, last_updated="2026-05-01"),
    dict(candidate_id="C04", full_name="Priya Nair", email="priya.nair@example.com",
         phone="+91-98765-10004", current_company="Razorpay",
         title="Backend Engineer", location="Pune, Maharashtra, IN",
         years_experience=3, last_updated="2026-05-02"),
    dict(candidate_id="C05", full_name="Evan You", email="evan.y@example.com",
         phone="+1-415-555-0105", current_company="VoidZero",
         title="Founder", location="San Francisco, CA, US",
         years_experience=12, last_updated="2026-05-01"),
    dict(candidate_id="C07", full_name="Arjun Mehta", email="arjun.mehta@example.com",
         phone="+91-98765-10007", current_company="Flipkart",
         title="SDE 2", location="Bangalore, Karnataka, IN",
         years_experience=4, last_updated="2026-05-03"),
    dict(candidate_id="C08", full_name="Sara Khan", email="sara.khan@example.com",
         phone="", current_company="Zomato",
         title="Data Engineer", location="Mumbai, Maharashtra, IN",
         years_experience=5, last_updated="2026-05-02"),
    dict(candidate_id="C09", full_name="Rohit Verma", email="rohit.verma@example.com",
         phone="+91-98765-10009", current_company="Swiggy",
         title="SRE", location="Hyderabad, Telangana, IN",
         years_experience=3, last_updated="2026-05-02"),
    dict(candidate_id="C10", full_name="TJ Holowaychuk", email="tj.h@example.com",
         phone="+1-415-555-0110", current_company="Independent",
         title="Open Source Engineer", location="Victoria, BC, CA",
         years_experience=18, last_updated="2026-05-01"),
    dict(candidate_id="C11", full_name="Meera Iyer", email="meera.iyer@example.com",
         phone="098765 10011", current_company="Paytm",
         title="ML Engineer", location="Bangalore, Karnataka, IN",
         years_experience=3, last_updated="2026-05-04"),
    dict(candidate_id="C12", full_name="Kent C. Dodds", email="kent.d@example.com",
         phone="+1-415-555-0112", current_company="Epic Web Dev",
         title="Educator", location="Lehi, UT, US",
         years_experience=10, last_updated="2026-05-01"),
    dict(candidate_id="C13", full_name="Aditya Rao", email="aditya.rao@example.com",
         phone="+91-98765-10013", current_company="PhonePe",
         title="Backend Engineer", location="",
         years_experience=4, last_updated="2026-04-10"),
    dict(candidate_id="C13", full_name="Aditya Rao", email="aditya.rao@example.com",
         phone="+91-98765-99913", current_company="PhonePe",
         title="Backend Engineer", location="",
         years_experience=4, last_updated="2026-05-20"),
    dict(candidate_id="C15", full_name="Tom Preston-Werner", email="tom.pw@example.com",
         phone="+1-415-555-0115", current_company="Chatterbug",
         title="Co-founder", location="San Francisco, CA, US",
         years_experience=20, last_updated="2026-05-01"),
    dict(candidate_id="C16", full_name="Neha Joshi", email="",
         phone="+91-98765-10016", current_company="Ola",
         title="Frontend Engineer", location="Delhi, DL, IN",
         years_experience=4, last_updated="2026-05-05"),
    dict(candidate_id="C17", full_name="Aman Sharma", email="aman.sharma17@example.com",
         phone="+91-98765-10017", current_company="Cred",
         title="Product Engineer", location="Bangalore, Karnataka, IN",
         years_experience=5, last_updated="2026-05-02"),
    dict(candidate_id="C18", full_name="Amann Sharma", email="amann.sharma18@example.com",
         phone="+91-98765-10018", current_company="Groww",
         title="Backend Engineer", location="Mumbai, Maharashtra, IN",
         years_experience=5, last_updated="2026-05-02"),
    dict(candidate_id="C19", full_name="Divya Pillai", email="divya.pillai@example.com",
         phone="+91-98765-10019", current_company="Freshworks",
         title="Software Engineer", location="Chennai, Tamil Nadu, IN",
         years_experience=5, last_updated="2026-05-03"),
    dict(candidate_id="C20", full_name="Paul Irish", email="paul.i@example.com",
         phone="+1-415-555-0120", current_company="Google",
         title="Developer Advocate", location="Mountain View, CA, US",
         years_experience=15, last_updated="2026-05-01"),
]

ATS_RECORDS = [
    dict(
        candidate_id="C01",
        name="Linus Torvalds", email="linus.t@example.com",
        phone="+14155550101", role_title="Kernel Maintainer",
        company="Linux Foundation", location="Portland, OR, US",
        bio="Creator of the Linux kernel and Git version control system.",
        years_experience=29,
        skills=["c", "linux", "git", "c++", "assembly", "make"],
        experience=[
            dict(company="Linux Foundation", title="Kernel Maintainer",
                 start="2005-01", end=None,
                 summary="Leads development and release of the Linux kernel."),
            dict(company="OSDL", title="Fellow",
                 start="2003-06", end="2005-01",
                 summary="Open Source Development Labs research fellow."),
            dict(company="Transmeta", title="Software Engineer",
                 start="1997-01", end="2003-06",
                 summary="VLIW processor architecture and Linux kernel portability."),
        ],
        education=dict(institution="University of Helsinki",
                       degree="B.Sc.", field="Computer Science", end_year="1996"),
        last_updated="2026-05-01",
    ),
    dict(
        candidate_id="C02",
        name="Dan Abramov", email="dan.a@example.com",
        phone="+14155550102", role_title="Staff Software Engineer",
        company="Meta", location="San Francisco, CA, US",
        bio="Author of Redux and co-creator of Create React App.",
        years_experience=11,
        skills=["javascript", "react", "redux", "typescript", "graphql"],
        experience=[
            dict(company="Meta", title="Staff Software Engineer",
                 start="2015-01", end=None,
                 summary="Core React team. Leads open-source React ecosystem work."),
            dict(company="Brain.fm", title="Frontend Engineer",
                 start="2014-06", end="2015-01",
                 summary="Built audio focus product UI."),
        ],
        education=dict(institution="Moscow State Technical University",
                       degree="B.Sc.", field="Computer Science", end_year="2014"),
        last_updated="2026-05-02",
    ),
    dict(
        candidate_id="C04",
        name="Priya Nair", email="priya.nair@example.com",
        phone="+919876510004", role_title="Backend Engineer",
        company="Razorpay", location="Pune, Maharashtra, IN",
        bio="Backend engineer specialising in payment systems and distributed services.",
        years_experience=3,
        skills=["java", "spring", "postgres", "kafka", "docker", "rest"],
        experience=[
            dict(company="Razorpay", title="Backend Engineer",
                 start="2023-01", end=None,
                 summary="Builds and owns payment gateway microservices."),
            dict(company="Infosys", title="Associate Software Engineer",
                 start="2021-07", end="2022-12",
                 summary="Java backend development for banking clients."),
        ],
        education=dict(institution="NIT Trichy",
                       degree="B.Tech", field="Computer Science", end_year="2021"),
        last_updated="2026-05-02",
    ),
    dict(
        candidate_id="C05",
        name="Evan You", email="evan.y@example.com",
        phone="+14155550105", role_title="Founder",
        company="VoidZero", location="San Francisco, CA, US",
        bio="Creator of Vue.js and Vite. Founder of VoidZero.",
        years_experience=12,
        skills=["javascript", "vue", "vite", "rust", "rollup", "esbuild"],
        experience=[
            dict(company="VoidZero", title="Founder & CEO",
                 start="2023-10", end=None,
                 summary="Building the next generation JavaScript toolchain."),
            dict(company="Netlify", title="Open Source Engineer",
                 start="2021-01", end="2023-09",
                 summary="Full time Vue.js and Vite open-source development."),
            dict(company="Meteor Development Group", title="UI Engineer",
                 start="2014-06", end="2016-01",
                 summary="Built Meteor UI layer and contributed to open-source tooling."),
        ],
        education=dict(institution="Parsons School of Design",
                       degree="M.F.A.", field="Design and Technology", end_year="2014"),
        last_updated="2026-05-01",
    ),
    dict(
        candidate_id="C06",
        name="Addy Osmani", email="",
        phone="+14155550106", role_title="Engineering Lead",
        company="Google", location="San Francisco, CA, US",
        bio="Engineering Lead at Google Chrome. Author of Learning JavaScript Design Patterns.",
        years_experience=16,
        skills=["javascript", "performance", "web-vitals", "chrome-devtools", "css"],
        experience=[
            dict(company="Google", title="Engineering Lead",
                 start="2017-01", end=None,
                 summary="Leads Chrome web performance and developer experience initiatives."),
            dict(company="Google", title="Senior Staff Engineer",
                 start="2012-06", end="2017-01",
                 summary="Chrome DevTools and web standards work."),
        ],
        education=dict(institution="University of Ulster",
                       degree="B.Sc.", field="Computer Science", end_year="2008"),
        last_updated="2026-05-01",
    ),
    dict(
        candidate_id="C07",
        name="Arjun Mehta", email="arjun.mehta@example.com",
        phone="+919876510007", role_title="Senior SDE",
        company="Flipkart", location="Bangalore, Karnataka, IN",
        bio="Backend engineer building high-throughput order management systems.",
        years_experience=4,
        skills=["python", "django", "postgresql", "redis", "docker", "rest"],
        experience=[
            dict(company="Flipkart", title="Senior SDE",
                 start="2022-03", end=None,
                 summary="Owns order management service handling 500k orders per day."),
            dict(company="TCS", title="Software Engineer",
                 start="2020-07", end="2022-02",
                 summary="Enterprise Java development for retail client."),
        ],
        education=dict(institution="BITS Pilani",
                       degree="B.E.", field="Computer Science", end_year="2020"),
        last_updated="2026-05-03",
    ),
    dict(
        candidate_id="C08",
        name="Sara Khan", email="sara.khan@example.com",
        phone="+919876510008", role_title="Data Engineer",
        company="Zomato", location="Mumbai, Maharashtra, IN",
        bio="Data engineer building real-time ingestion and analytics pipelines.",
        years_experience=5,
        skills=["python", "spark", "airflow", "kafka", "sql", "dbt"],
        experience=[
            dict(company="Zomato", title="Data Engineer",
                 start="2022-01", end=None,
                 summary="Builds and maintains real-time data pipelines for restaurant analytics."),
            dict(company="Accenture", title="Data Analyst",
                 start="2020-06", end="2021-12",
                 summary="BI reporting and ETL pipeline work for FMCG clients."),
        ],
        education=dict(institution="Symbiosis Institute of Technology",
                       degree="B.Tech", field="Information Technology", end_year="2020"),
        last_updated="2026-05-02",
    ),
    dict(
        candidate_id="C13",
        name="Aditya Rao", email="aditya.rao@example.com",
        phone="+919876599913", role_title="Backend Engineer",
        company="PhonePe", location="",
        bio="Go and Kubernetes engineer working on payment infrastructure.",
        years_experience=4,
        skills=["go", "kubernetes", "grpc", "postgresql", "redis"],
        experience=[
            dict(company="PhonePe", title="Backend Engineer",
                 start="2022-06", end=None,
                 summary="Payment infrastructure services in Go."),
            dict(company="Ola", title="Software Engineer",
                 start="2020-07", end="2022-05",
                 summary="Ride pricing and surge algorithms."),
        ],
        education=dict(institution="VIT Vellore",
                       degree="B.Tech", field="Computer Science", end_year="2020"),
        last_updated="2026-05-20",
    ),
    dict(
        candidate_id="C17",
        name="Aman Sharma", email="aman.sharma17@example.com",
        phone="+919876510017", role_title="Product Engineer",
        company="Cred", location="Bangalore, Karnataka, IN",
        bio="Product-minded engineer building Android and backend features.",
        years_experience=5,
        skills=["kotlin", "android", "java", "firebase", "rest"],
        experience=[
            dict(company="Cred", title="Product Engineer",
                 start="2021-06", end=None,
                 summary="Builds member-facing Android features for the Cred app."),
            dict(company="Myntra", title="Android Engineer",
                 start="2019-07", end="2021-05",
                 summary="Fashion e-commerce Android app features."),
        ],
        education=dict(institution="Delhi Technological University",
                       degree="B.Tech", field="Software Engineering", end_year="2019"),
        last_updated="2026-05-02",
    ),
    dict(
        candidate_id="C18",
        name="Amann Sharma", email="amann.sharma18@example.com",
        phone="+919876510018", role_title="Backend Engineer",
        company="Groww", location="Mumbai, Maharashtra, IN",
        bio="Java backend engineer building fintech trading infrastructure.",
        years_experience=5,
        skills=["java", "kafka", "spring", "mysql", "docker"],
        experience=[
            dict(company="Groww", title="Backend Engineer",
                 start="2021-06", end=None,
                 summary="Trading engine and portfolio service development."),
            dict(company="HDFC Securities", title="Software Engineer",
                 start="2019-07", end="2021-05",
                 summary="Core banking API development."),
        ],
        education=dict(institution="Mumbai University",
                       degree="B.E.", field="Computer Engineering", end_year="2019"),
        last_updated="2026-05-02",
    ),
    dict(
        candidate_id="C19",
        name="Divya Pillai", email="divya.pillai@example.com",
        phone="+919876510019", role_title="Software Engineer II",
        company="Freshworks", location="Chennai, Tamil Nadu, IN",
        bio="Full-stack engineer building CRM product features.",
        years_experience=5,
        skills=["reactjs", "node", "typescript", "postgresql", "graphql"],
        experience=[
            dict(company="Freshworks", title="Software Engineer II",
                 start="2021-06", end=None,
                 summary="Builds CRM pipeline and contact management features."),
            dict(company="HCL Technologies", title="Software Engineer",
                 start="2019-07", end="2021-05",
                 summary="Enterprise Java applications for telecom client."),
        ],
        education=dict(institution="Anna University",
                       degree="B.E.", field="Computer Science", end_year="2019"),
        last_updated="2026-05-03",
    ),
]

RESUMES = {
    "C01": """Linus Torvalds
linus.t@example.com | +1-415-555-0101 | Portland, OR
https://github.com/torvalds

SUMMARY
Creator of the Linux kernel and Git. Focused on systems programming, OS kernel design, and open-source governance.

EXPERIENCE
Linux Foundation — Kernel Maintainer
Jan 2005 - Present
Led development and release cycle of the Linux kernel. Manage contributor review process across thousands of patches per release. Responsible for final merge decisions for all kernel subsystems.

OSDL — Fellow
June 2003 - Jan 2005
Research fellow at Open Source Development Labs focused on enterprise Linux adoption.

Transmeta Corporation — Software Engineer
January 1997 - June 2003
Worked on VLIW processor architecture and ported Linux to Transmeta hardware platforms.

EDUCATION
B.Sc. Computer Science — University of Helsinki, 1996

SKILLS
C, C++, Linux, Git, Assembly, Make, GDB, Bash""",

    "C03": """Sindre Sorhus
sindre.s@example.com | Tromsoe, Norway
https://sindresorhus.com

SUMMARY
Prolific open-source developer. Creator and maintainer of hundreds of npm packages used by millions of developers worldwide.

EXPERIENCE
Independent — Open Source Maintainer
2012 - Present
Maintains 1000+ open-source projects. Focus areas include CLI tooling, Node.js utilities, and developer experience packages.

Bekkely — Developer
2010 - 2012
Full-stack web development for Norwegian clients.

EDUCATION
Norwegian University of Science and Technology, Computer Science, 2010

NOTE: Skills available via GitHub profile only.""",

    "C04": """PRIYA NAIR
priya.nair@example.com | 9876510004 | Pune, India

OBJECTIVE
Backend engineer with 3 years experience in Java and distributed payment systems.

EXPERIENCE
Razorpay, Pune
Backend Engineer
January 2023 to Present
Built and own payment gateway microservices handling 2M transactions per day.
Reduced p99 latency by 40% through async processing redesign.
Tech: Java, Spring Boot, Kafka, PostgreSQL, Docker, Redis

Infosys, Pune
Associate Software Engineer
July 2021 - December 2022
Java backend development for a UK banking client.
Developed REST APIs for account management and transaction history.
Tech: Java, Spring MVC, Oracle DB

EDUCATION
B.Tech Computer Science
National Institute of Technology, Trichy
2017 - 2021, CGPA 8.7/10

SKILLS
Java, Spring Boot, Spring MVC, PostgreSQL, MySQL, Kafka, Docker, REST APIs, Microservices, Redis""",

    "C06": """Addy Osmani
Engineering Lead — Google
San Francisco, CA | https://addyosmani.com | https://github.com/addyosmani

SUMMARY
Engineering Lead on Chrome at Google. Author of Learning JavaScript Design Patterns (O'Reilly). Focused on web performance, developer experience, and open-source tooling.

EXPERIENCE
Google — Engineering Lead, Chrome
2017 to Present
Lead Chrome web performance initiatives including Core Web Vitals and performance tooling. Author of web.dev/vitals standards. Manage a team of 8 engineers.

Google — Senior Staff Software Engineer
June 2012 - 2017
Built and shipped Chrome DevTools features. Authored tooling widely used by frontend developers globally.

EDUCATION
B.Sc. Multimedia Technology and Design — University of Ulster, 2008

SKILLS
JavaScript, Web Performance, Core Web Vitals, Chrome DevTools, CSS, HTML, Workbox, Lighthouse""",

    "C07": """Arjun Mehta
arjun.mehta@example.com
Phone: +91 9876512345
Bangalore, India

SUMMARY
Backend SDE with 4 years of experience building high-throughput distributed systems.

EXPERIENCE
Flipkart — SDE 2
03/2022 - Present
Own order management service handling 500k daily orders. Led migration from monolith to microservices. Reduced service error rate from 0.8% to 0.05%.

TCS — Software Engineer
Jul 2020 to Feb 2022
Enterprise Java development for a UK retail client. Maintained and extended Spring MVC application serving 5M users.

EDUCATION
B.E. Computer Science, BITS Pilani, 2020

SKILLS
Python, Django, REST APIs, PostgreSQL, Redis, Docker, Kafka, Celery""",

    "C09": """Rohit Verma
rohit.verma@example.com | +91-98765-10009
Hyderabad, India

SUMMARY
Site Reliability Engineer with focus on Kubernetes-based infrastructure and observability.

EXPERIENCE
Swiggy — Site Reliability Engineer
2023-06 - Present
Manages Kubernetes clusters serving food delivery platform. Owns observability stack: Prometheus, Grafana, Loki. Reduced MTTR by 60% through alerting overhaul.

Wipro — DevOps Engineer
Aug 2021 to May 2023
CI/CD pipeline implementation and cloud infrastructure management on AWS for BFSI clients.

EDUCATION
B.Tech Information Technology, JNTU Hyderabad, 2021

SKILLS
Kubernetes, Prometheus, Grafana, Go, Terraform, AWS, Docker, Linux, Bash""",

    "C11": """Meera Iyer
meera.iyer@example.com
Mobile: 9876510011
Bangalore, India

PROFILE
ML Engineer with 3 years experience in recommendation systems and NLP pipelines.

EXPERIENCE
Paytm — ML Engineer
February 2023 - Present
Builds recommendation and fraud detection models for Paytm's payment platform.
Developed real-time feature store reducing model inference latency by 35%.

Wipro — Data Scientist
June 2021 - January 2023
Built NLP document classification models for insurance automation clients.

EDUCATION
M.Tech Artificial Intelligence, IISc Bangalore, 2021
B.Tech Electronics, NIT Calicut, 2019

SKILLS
Python, TensorFlow, PyTorch, Scikit-learn, SQL, Spark, Kafka, MLflow, Docker""",

    "C12": """Kent C. Dodds
kent.d@example.com | +1-415-555-0112 | Lehi, UT
https://kentcdodds.com

SUMMARY
Developer educator and open-source author. Creator of Testing Library, Epic React, and Epic Web Dev.

EXPERIENCE
Epic Web Dev — Educator & Founder
2020 - Present
Created and runs Epic React and Epic Web courses used by 100k+ developers.
Full-stack web development curriculum including React, Remix, and databases.

PayPal — Principal Engineer
2016 - 2020
Led frontend architecture for PayPal's checkout and developer experience platforms.
Introduced Testing Library across the organisation.

EDUCATION
B.Sc. Computer Information Technology — Brigham Young University, 2014

SKILLS
ReactJS, TestingLibrary, JavaScript, TypeScript, Remix, Node.js, Jest, CSS""",

    "C14": "",

    "C15": """Tom Preston-Werner
tom.pw@example.com | +1-415-555-0115 | San Francisco, CA
https://tom.preston-werner.com | https://github.com/mojombo

SUMMARY
Co-founder of GitHub and Chatterbug. Open-source contributor and investor focused on developer infrastructure.

EXPERIENCE
Chatterbug — Co-founder
2016 - Present
Built language learning platform using spaced repetition and live tutoring sessions.

GitHub — Co-founder & CEO
2008 - 2014
Co-founded GitHub, growing it from 0 to 10M users and the world's largest code hosting platform. Led product, engineering, and fundraising.

Gravatar — Creator
2003 - 2008
Created Gravatar (globally recognised avatars), later acquired by Automattic.

EDUCATION
B.S. Physics — Harvey Mudd College, 2003

SKILLS
Ruby, Ruby on Rails, Git, Go, Markdown, Liquid templating, JavaScript""",

    "C16": """Neha Joshi
Phone: +91-98765-10016
Delhi, India

SUMMARY
Frontend engineer with 4 years of experience building responsive web applications.

EXPERIENCE
Ola — Frontend Engineer
2022 - Present
Builds driver onboarding and earnings dashboard UIs. Improved page load performance by 30%.

Cognizant — Frontend Developer
2020 - 2022
Built React components for a US insurance client's self-service portal.

EDUCATION
B.Tech Computer Science, Delhi Technological University, 2020

SKILLS
React, CSS, HTML, JavaScript, Redux, Webpack, Figma""",

    "C19": """Divya Pillai
divya.pillai@example.com | Chennai, India

ABOUT
Full-stack software engineer with 5 years in SaaS CRM product engineering.

EXPERIENCE
Freshworks — Software Engineer II
June 2021 - Present
Builds CRM pipeline, contact management, and bulk action features in React.js and Node.js.
Led migration of legacy jQuery UI to React, reducing bundle size by 45%.

HCL Technologies — Software Engineer
Jul 2019 to May 2021
Enterprise Java and REST API development for a US telecom client.

EDUCATION
B.E. Computer Science, Anna University, 2019

SKILLS
React.js, Node.js, TypeScript, PostgreSQL, GraphQL, Jest, Docker""",

    "C20": """Paul Irish
paul.i@example.com | +1-415-555-0120 | Mountain View, CA
https://paulirish.com | https://github.com/paulirish

SUMMARY
Developer Advocate at Google focused on browser performance, DevTools, and web developer experience.

EXPERIENCE
Google — Developer Advocate
2014 - Present
Advocates for web developers. Contributes to Chrome DevTools, Lighthouse, and web performance standards. Creator of HTML5 Boilerplate.

Filament Group — Lead Developer
2009 - 2014
Front-end development and progressive enhancement consulting for major US clients.

EDUCATION
Self-taught. No formal degree.

SKILLS
JavaScript, Chrome DevTools, Lighthouse, HTML, CSS, Web Performance, DevTools protocol""",
}

LINKEDIN_RECORDS = [
    dict(
        candidate_id="C02",
        full_name="Dan Abramov", email="dan.a@example.com",
        headline="Software Engineer II", company="Meta",
        location="San Francisco, CA",
        connections=8400,
        skills=["javascript", "react", "redux", "typescript", "graphql", "open-source"],
        experience=[
            dict(company="Meta", title="Software Engineer II",
                 start="Jan 2015", end=None),
            dict(company="Brain.fm", title="Frontend Engineer",
                 start="Jun 2014", end="Jan 2015"),
        ],
        education=[
            dict(institution="Moscow State Technical University",
                 degree="B.Sc.", field="Computer Science", end_year="2014"),
        ],
        last_updated="2026-04-20",
    ),
    dict(
        candidate_id="C10",
        full_name="TJ Holowaychuk", email="tj.h@example.com",
        headline="Open Source Engineer", company="Independent",
        location="Victoria, BC, Canada",
        connections=5200,
        skills=["go", "node.js", "javascript", "c", "lua", "rust"],
        experience=[
            dict(company="Independent", title="Open Source Engineer",
                 start="April 2014", end=None),
            dict(company="LearnBoost", title="Lead Developer",
                 start="February 2010", end="March 2014"),
        ],
        education=[],
        last_updated="2026-04-15",
    ),
    dict(
        candidate_id="C11",
        full_name="Meera Iyer", email="meera.iyer@example.com",
        headline="Machine Learning Engineer", company="Paytm",
        location="Bangalore, Karnataka, India",
        connections=1800,
        skills=["python", "tensorflow", "pytorch", "nlp", "recommendation systems", "sql"],
        experience=[
            dict(company="Paytm", title="Machine Learning Engineer",
                 start="Feb 2023", end=None),
            dict(company="Wipro", title="Data Scientist",
                 start="Jun 2021", end="Jan 2023"),
        ],
        education=[
            dict(institution="IISc Bangalore",
                 degree="M.Tech", field="Artificial Intelligence", end_year="2021"),
            dict(institution="NIT Calicut",
                 degree="B.Tech", field="Electronics", end_year="2019"),
        ],
        last_updated="2026-04-18",
    ),
    dict(
        candidate_id="C19",
        full_name="Divya Pillai", email="divya.pillai@example.com",
        headline="Software Engineer II", company="Freshworks",
        location="Chennai, Tamil Nadu, India",
        connections=2100,
        skills=["react", "node", "typescript", "graphql", "postgresql", "jest"],
        experience=[
            dict(company="Freshworks", title="Software Engineer II",
                 start="June 2021", end=None),
            dict(company="HCL Technologies", title="Software Engineer",
                 start="July 2019", end="May 2021"),
        ],
        education=[
            dict(institution="Anna University",
                 degree="B.E.", field="Computer Science", end_year="2019"),
        ],
        last_updated="2026-04-22",
    ),
]

RECRUITER_NOTES = {
    "C04": (
        "Spoke with Priya on 14 May. Very strong on backend systems design. "
        "Mentioned she wants to move into a distributed systems architect role in 12-18 months. "
        "Currently notice period 60 days. Salary expectation: 28-32 LPA. Good culture fit."
    ),
    "C12": (
        "Kent on a call 8 May. Not actively looking but open to the right opportunity. "
        "Strong preference for remote-first. Very focused on teaching and DX. "
        "Would consider Staff Engineer or Educator-in-Residence type role."
    ),
    "C20": (
        "Spoke to Paul on call. Strong DX background, very articulate. "
        "Mentioned interest in dev tooling roles. Notes from screening, 2026-05-10."
    ),
}


def write_csv():
    path = SRC / "recruiter_csv" / "candidates.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "full_name", "email", "phone", "current_company", "title",
        "location", "years_experience", "last_updated",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in CSV_ROWS:
            writer.writerow({k: row[k] for k in fields})


def write_ats():
    path = SRC / "ats_json" / "candidates.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [{k: v for k, v in r.items() if k != "candidate_id"} for r in ATS_RECORDS]
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    malformed_path = SRC / "ats_json" / "C09_malformed.json"
    malformed_path.write_text(
        '{"name": "Rohit Verma", "email": "rohit.verma@example.com", '
        '"phone": "+91-98765-10009", "role_title": "SRE", "skills": ["kubernetes", "go"'
    )


def write_resumes():
    (SRC / "resumes").mkdir(parents=True, exist_ok=True)
    for cid, text in RESUMES.items():
        path = SRC / "resumes" / f"{cid}.txt"
        path.write_text(text, encoding="utf-8")


def write_linkedin():
    path = SRC / "linkedin" / "candidates.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [{k: v for k, v in r.items() if k != "candidate_id"} for r in LINKEDIN_RECORDS]
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def write_recruiter_notes():
    (SRC / "recruiter_notes").mkdir(parents=True, exist_ok=True)
    for cid, text in RECRUITER_NOTES.items():
        path = SRC / "recruiter_notes" / f"{cid}.txt"
        path.write_text(text, encoding="utf-8")


def write_candidate_index():
    seen = {}
    for row in CSV_ROWS:
        cid = row["candidate_id"]
        if cid not in seen:
            seen[cid] = {
                "full_name": row["full_name"],
                "email": row["email"] or None,
            }
    additional = [
        ("C06", {"full_name": "Addy Osmani", "email": None}),
        ("C14", {"full_name": None, "email": None}),
    ]
    for cid, info in additional:
        if cid not in seen:
            seen[cid] = info
    path = SRC / "candidate_index.json"
    path.write_text(json.dumps(seen, indent=2, sort_keys=True), encoding="utf-8")


def main():
    write_csv()
    write_ats()
    write_resumes()
    write_linkedin()
    write_recruiter_notes()
    write_candidate_index()
    print("enriched synthetic data written for all candidates")


if __name__ == "__main__":
    main()