"""
create_sample_resumes.py
Generates diverse, realistic candidate resumes in .txt, .docx, and .pdf formats.
"""

import os
import docx
from docx.shared import Pt, Inches, RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

SAMPLES = [
    {
        "filename": "Aarav_Sharma_AI_ML_Engineer",
        "name": "Aarav Sharma",
        "email": "aarav.sharma@gmail.com",
        "phone": "+91 98765 43210",
        "linkedin": "https://linkedin.com/in/aarav-sharma-ml",
        "github": "https://github.com/aarav-sharma",
        "location": "Bangalore, India",
        "education": "B.Tech in Computer Science and Engineering, IIT Kharagpur (2018 - 2022)",
        "summary": "Innovative AI/ML Engineer with 3.5 years of experience architecting end-to-end Machine Learning pipelines, NLP systems, and predictive models. Proven expertise in PyTorch, TensorFlow, scikit-learn, and deploying containerized microservices using Docker and FastAPI on AWS.",
        "experience": [
            "Senior Machine Learning Engineer | DataCore Systems (2022 - Present)<br/>• Designed and productionized transformer-based NLP models reducing customer ticket routing time by 42%.<br/>• Built end-to-end predictive modeling workflows using scikit-learn, Pandas, and PyTorch.<br/>• Containerized AI services with Docker and deployed scalable REST APIs using FastAPI and Kubernetes.<br/>• Collaborated with DevOps teams to integrate automated model retraining CI/CD pipelines.",
            "Junior Data Scientist | CogniTech Analytics (2021 - 2022)<br/>• Developed deep learning image classification models with TensorFlow and OpenCV.<br/>• Cleaned and preprocessed large-scale datasets using NumPy, Pandas, and SQL.<br/>• Performed statistical A/B testing and model evaluation using precision, recall, and ROC-AUC."
        ],
        "skills": "Python, Machine Learning, Deep Learning, NLP, PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, FastAPI, Docker, Kubernetes, AWS, SQL, Git, Linux",
        "projects": [
            "Resume Screening & Parser: Built an automated recruitment parser using TF-IDF and Spacy entity recognition.",
            "Customer Churn Prediction: Implemented XGBoost and Random Forest models achieving 89% accuracy."
        ]
    },
    {
        "filename": "Priya_Patel_FullStack_Developer",
        "name": "Priya Patel",
        "email": "priya.patel.dev@gmail.com",
        "phone": "+91 98112 34567",
        "linkedin": "https://linkedin.com/in/priyapatel-dev",
        "github": "https://github.com/priyapatel-code",
        "location": "Pune, India",
        "education": "B.Tech in Information Technology, Pune University (2019 - 2023)",
        "summary": "Dynamic Full Stack Software Engineer with 2.5 years of experience developing responsive web applications and scalable backends. Skilled in Python (Django, Flask), React.js, TypeScript, PostgreSQL, and REST API design.",
        "experience": [
            "Full Stack Web Developer | CloudMinds Tech (2023 - Present)<br/>• Engineered responsive single-page applications using React.js, Redux, and Tailwind CSS.<br/>• Architected RESTful backend APIs utilizing Python and Django REST Framework with PostgreSQL.<br/>• Integrated authentication with JWT and managed CI/CD deployment via GitHub Actions and Docker.<br/>• Improved database query performance by 35% through indexing and query optimization.",
            "Web Developer Intern | TechSphere Solutions (2022 - 2023)<br/>• Built reusable frontend components using React and JavaScript.<br/>• Developed CRUD microservices with Flask and SQLite."
        ],
        "skills": "Python, JavaScript, TypeScript, React, React.js, Django, Flask, PostgreSQL, MySQL, REST API, HTML5, CSS3, Tailwind CSS, Git, Docker",
        "projects": [
            "E-Commerce SaaS Platform: Developed a multi-tenant store with React frontend and Django backend.",
            "Team Collaboration Board: Kanban-style task manager built with WebSockets and Redux."
        ]
    },
    {
        "filename": "Rohan_Verma_Data_Analyst",
        "name": "Rohan Verma",
        "email": "rohan.verma.analytics@outlook.com",
        "phone": "+91 97654 32198",
        "linkedin": "https://linkedin.com/in/rohan-verma-data",
        "github": "https://github.com/rohan-analytics",
        "location": "Mumbai, India",
        "education": "B.S. in Statistics and Data Science, Mumbai University (2020 - 2023)",
        "summary": "Detail-oriented Data Analyst with 2 years of experience turning complex datasets into strategic business intelligence dashboards. Proficient in SQL, Tableau, Power BI, Python, Pandas, and Excel data modeling.",
        "experience": [
            "Business Data Analyst | FinMetrics Global (2023 - Present)<br/>• Created 20+ executive dashboards in Tableau and Power BI tracking revenue KPIs and user retention.<br/>• Formulated complex SQL queries (CTEs, Window Functions, Joins) on Snowflake and PostgreSQL.<br/>• Automated weekly reporting pipelines using Python (Pandas, NumPy, OpenPyXL), saving 12 manual hours/week.<br/>• Conducted root-cause data audits to maintain 99.8% data integrity across ETL pipelines.",
            "Data Analyst Trainee | InsightHub Analytics (2022 - 2023)<br/>• Executed exploratory data analysis and customer segmentation using Python and Matplotlib.<br/>• Built financial modeling spreadsheets with advanced Excel formulas and macros."
        ],
        "skills": "Python, SQL, Tableau, Power BI, Pandas, NumPy, Excel, Data Analysis, Data Visualization, Matplotlib, Seaborn, ETL, Statistics",
        "projects": [
            "E-Commerce Sales Performance Dashboard: Interactive Tableau dashboard analyzing $5M in omnichannel sales.",
            "Healthcare Patient Flow Forecasting: Time-series analysis model predicting hospital bed occupancy."
        ]
    },
    {
        "filename": "Neha_Gupta_Junior_Python_Dev",
        "name": "Neha Gupta",
        "email": "neha.gupta.cs@gmail.com",
        "phone": "+91 91234 56780",
        "linkedin": "https://linkedin.com/in/neha-gupta-dev",
        "github": "https://github.com/nehagupta-py",
        "location": "Delhi, India",
        "education": "BCA (Bachelor of Computer Applications), Delhi University (2021 - 2024)",
        "summary": "Aspiring Junior Software Developer with hands-on academic and internship experience in Python, Flask, HTML, CSS, and relational databases. Eager to contribute to high-impact software engineering teams.",
        "experience": [
            "Software Intern | AlphaByte Labs (2023 - 2024)<br/>• Assisted in developing internal automation scripts using Python and Beautiful Soup.<br/>• Created simple REST API endpoints with Flask and SQLite database.<br/>• Collaborated on frontend bug fixes using HTML5, CSS3, and JavaScript."
        ],
        "skills": "Python, Flask, SQLite, HTML5, CSS3, JavaScript, Git, Problem Solving, Communication",
        "projects": [
            "Student Attendance Management: Desktop and web utility using Python, Tkinter, and SQLite.",
            "Weather Forecast App: Responsive web app fetching OpenWeatherMap REST API."
        ]
    },
    {
        "filename": "Vikram_Malhotra_DevOps_Cloud",
        "name": "Vikram Malhotra",
        "email": "vikram.malhotra.ops@gmail.com",
        "phone": "+91 99887 76655",
        "linkedin": "https://linkedin.com/in/vikram-devops",
        "github": "https://github.com/v-malhotra-ops",
        "location": "Hyderabad, India",
        "education": "B.Tech in Computer Engineering, JNTU Hyderabad (2017 - 2021)",
        "summary": "Accomplished DevOps and Cloud Infrastructure Engineer with 4 years of experience orchestrating AWS cloud architecture, Kubernetes clusters, Docker microservices, and automated CI/CD pipelines.",
        "experience": [
            "DevOps Infrastructure Engineer | CloudScale Networks (2021 - Present)<br/>• Provisioned and managed AWS infrastructure (VPC, EC2, EKS, RDS, S3) using Terraform Infrastructure as Code.<br/>• Deployed production Kubernetes (k8s) clusters and configured Helm charts for microservices.<br/>• Automated continuous integration and deployment pipelines using Jenkins, GitHub Actions, and Docker.<br/>• Implemented centralized logging and alerting with Prometheus, Grafana, and ELK stack.",
            "Linux Systems Administrator | Nexa Hostings (2020 - 2021)<br/>• Managed fleet of 150+ Ubuntu and CentOS servers, configuring Nginx, SSL certificates, and firewall rules.<br/>• Wrote automated maintenance scripts in Bash and Python."
        ],
        "skills": "AWS, Docker, Kubernetes, CI/CD, Terraform, Jenkins, Linux, Ubuntu, Nginx, Python, Bash, Git, Prometheus, Grafana",
        "projects": [
            "Zero-Downtime EKS Deployment: Automated blue-green deployment pipeline for high-traffic financial app.",
            "Disaster Recovery Infrastructure: Automated Terraform modules for multi-region AWS failover."
        ]
    },
    {
        "filename": "Ananya_Deshmukh_Frontend_Developer",
        "name": "Ananya Deshmukh",
        "email": "ananya.deshmukh.ui@gmail.com",
        "phone": "+91 94567 89012",
        "linkedin": "https://linkedin.com/in/ananya-deshmukh-ui",
        "github": "https://github.com/ananya-ui",
        "location": "Chennai, India",
        "education": "B.E. in Computer Science, Anna University (2020 - 2024)",
        "summary": "Creative Frontend Developer with 1.5 years of experience specializing in React.js, Tailwind CSS, Next.js, and interactive user experiences. Passionate about responsive design and web accessibility.",
        "experience": [
            "Frontend Engineer | PixelCraft Studio (2023 - Present)<br/>• Built responsive web user interfaces using React, Next.js, and Tailwind CSS.<br/>• Translated Figma designs into high-performance accessible HTML and CSS layouts.<br/>• Managed state using Redux Toolkit and integrated REST APIs.",
            "UI/UX Design Intern | CreativeWave (2022 - 2023)<br/>• Designed interactive wireframes and prototypes in Figma.<br/>• Implemented client-side form validations and animations using JavaScript."
        ],
        "skills": "React, React.js, Next.js, JavaScript, TypeScript, HTML5, CSS3, Tailwind CSS, Bootstrap, Redux, Git, Figma",
        "projects": [
            "Interactive Travel Booking UI: Next.js landing page with Tailwind CSS and Framer Motion animations.",
            "Design System Component Library: Reusable React component library with Storybook documentation."
        ]
    }
]

def generate_sample_files(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        'DocName',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'DocContact',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )

    for item in SAMPLES:
        # 1. Plain Text Resume (.txt)
        txt_path = os.path.join(output_dir, f"{item['filename']}.txt")
        clean_exp = [e.replace('<br/>', '\n') for e in item['experience']]
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{item['name']}\n")
            f.write(f"Email: {item['email']} | Phone: {item['phone']} | Location: {item['location']}\n")
            f.write(f"LinkedIn: {item['linkedin']} | GitHub: {item['github']}\n\n")
            f.write("PROFESSIONAL SUMMARY\n")
            f.write(f"{item['summary']}\n\n")
            f.write("EDUCATION\n")
            f.write(f"{item['education']}\n\n")
            f.write("TECHNICAL SKILLS\n")
            f.write(f"{item['skills']}\n\n")
            f.write("PROFESSIONAL EXPERIENCE\n")
            for exp in clean_exp:
                f.write(f"{exp}\n\n")
            f.write("KEY PROJECTS\n")
            for proj in item['projects']:
                f.write(f"• {proj}\n")

        # 2. Word Document Resume (.docx)
        docx_path = os.path.join(output_dir, f"{item['filename']}.docx")
        doc = docx.Document()
        title_p = doc.add_paragraph()
        run = title_p.add_run(item['name'])
        run.bold = True
        run.font.size = Pt(20)
        run.font.color.rgb = RGBColor(30, 58, 138)

        contact_p = doc.add_paragraph()
        contact_p.add_run(f"Email: {item['email']}  |  Phone: {item['phone']}  |  Location: {item['location']}\n")
        contact_p.add_run(f"LinkedIn: {item['linkedin']}  |  GitHub: {item['github']}")

        doc.add_heading("Professional Summary", level=2)
        doc.add_paragraph(item['summary'])

        doc.add_heading("Education", level=2)
        doc.add_paragraph(item['education'])

        doc.add_heading("Technical Skills", level=2)
        doc.add_paragraph(item['skills'])

        doc.add_heading("Professional Experience", level=2)
        for exp in clean_exp:
            doc.add_paragraph(exp)

        doc.add_heading("Key Projects", level=2)
        for proj in item['projects']:
            doc.add_paragraph(f"• {proj}")

        doc.save(docx_path)

        # 3. PDF Document Resume (.pdf)
        pdf_path = os.path.join(output_dir, f"{item['filename']}.pdf")
        doc_pdf = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=40, leftMargin=40,
            topMargin=40, bottomMargin=40
        )
        story = []
        story.append(Paragraph(item['name'], name_style))
        story.append(Paragraph(f"Email: {item['email']} | Phone: {item['phone']} | {item['location']}<br/>LinkedIn: {item['linkedin']} | GitHub: {item['github']}", contact_style))
        story.append(Spacer(1, 4))

        story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", section_style))
        story.append(Paragraph(item['summary'], body_style))

        story.append(Paragraph("<b>EDUCATION</b>", section_style))
        story.append(Paragraph(item['education'], body_style))

        story.append(Paragraph("<b>TECHNICAL SKILLS</b>", section_style))
        story.append(Paragraph(item['skills'], body_style))

        story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", section_style))
        for exp in item['experience']:
            story.append(Paragraph(exp, body_style))

        story.append(Paragraph("<b>KEY PROJECTS</b>", section_style))
        for proj in item['projects']:
            story.append(Paragraph(f"• {proj}", body_style))

        doc_pdf.build(story)

    print(f"Generated {len(SAMPLES)} sample resumes in TXT, DOCX, and PDF formats in {output_dir}")

if __name__ == "__main__":
    target = os.path.join(os.path.dirname(__file__), "sample_resumes")
    generate_sample_files(target)
