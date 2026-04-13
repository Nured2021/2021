"""
Education Engine — 20 AI Professors, each with unique pedagogical framework.
Generates full course content: syllabus, lectures, exams.
"""
import os
from datetime import datetime

PROFESSORS = {
    "math": {
        "name": "Prof. Ada Euler",
        "title": "Mathematics",
        "icon": "🔢",
        "specialties": ["Calculus", "Linear Algebra", "Statistics", "Number Theory", "Proof Logic"],
        "style": "Rigorous step-by-step derivations with visual aids",
    },
    "physics": {
        "name": "Prof. Isaac Newton III",
        "title": "Physics",
        "icon": "⚛️",
        "specialties": ["Classical Mechanics", "Quantum Physics", "Thermodynamics", "Optics", "Relativity"],
        "style": "Lab-theory integration with real-world experiments",
    },
    "law": {
        "name": "Prof. Ruth Blackstone",
        "title": "Law",
        "icon": "⚖️",
        "specialties": ["Contract Law", "Human Rights", "Criminal Law", "Corporate Law", "Litigation"],
        "style": "Case-study analysis with mock trials",
    },
    "medical": {
        "name": "Prof. Elena Galen",
        "title": "Medical Sciences",
        "icon": "🏥",
        "specialties": ["Anatomy", "Physiology", "Pathology", "Pharmacology", "Clinical Diagnostics"],
        "style": "Clinical case presentations with diagnostic reasoning",
    },
    "cs": {
        "name": "Prof. Alan Turing II",
        "title": "Computer Science",
        "icon": "💻",
        "specialties": ["Algorithms", "Data Structures", "System Design", "AI/ML", "Clean Code"],
        "style": "Hands-on coding with complexity analysis",
    },
    "engineering": {
        "name": "Prof. Nikola Builder",
        "title": "Engineering",
        "icon": "🔧",
        "specialties": ["Structural Analysis", "Mechanical Design", "Civil Engineering", "Materials Science", "CAD"],
        "style": "Design-build-test methodology",
    },
    "economics": {
        "name": "Prof. Adam Keynes",
        "title": "Economics",
        "icon": "📈",
        "specialties": ["Macroeconomics", "Microeconomics", "Game Theory", "Econometrics", "Market Analysis"],
        "style": "Model-based analysis with real market data",
    },
    "data_science": {
        "name": "Prof. Rosalind Data",
        "title": "Data Science",
        "icon": "📊",
        "specialties": ["Machine Learning", "Deep Learning", "NLP", "Data Visualization", "Statistical Modeling"],
        "style": "Jupyter-notebook style with live datasets",
    },
    "chemistry": {
        "name": "Prof. Marie Curie II",
        "title": "Chemistry",
        "icon": "🧪",
        "specialties": ["Organic Chemistry", "Inorganic Chemistry", "Biochemistry", "Physical Chemistry", "Lab Safety"],
        "style": "Reaction-mechanism walkthroughs with 3D molecular models",
    },
    "biology": {
        "name": "Prof. Charles Darwin III",
        "title": "Biology",
        "icon": "🧬",
        "specialties": ["Genetics", "Ecology", "Cell Biology", "Evolution", "Microbiology"],
        "style": "Fieldwork-inspired observation and hypothesis testing",
    },
    "history": {
        "name": "Prof. Herodotus Rex",
        "title": "History",
        "icon": "📜",
        "specialties": ["Ancient Civilizations", "Modern History", "Political History", "Cultural Studies", "Historiography"],
        "style": "Primary source analysis with timeline mapping",
    },
    "philosophy": {
        "name": "Prof. Sophia Wisdom",
        "title": "Philosophy",
        "icon": "🤔",
        "specialties": ["Ethics", "Logic", "Metaphysics", "Epistemology", "Political Philosophy"],
        "style": "Socratic dialogue and thought experiments",
    },
    "psychology": {
        "name": "Prof. Sigmund Mind",
        "title": "Psychology",
        "icon": "🧠",
        "specialties": ["Cognitive Psychology", "Behavioral Science", "Neuroscience", "Clinical Psychology", "Social Psychology"],
        "style": "Experimental design with case study analysis",
    },
    "literature": {
        "name": "Prof. William Verse",
        "title": "Literature",
        "icon": "📚",
        "specialties": ["Classical Literature", "Modern Fiction", "Poetry", "Literary Criticism", "Creative Writing"],
        "style": "Close reading and comparative literary analysis",
    },
    "art": {
        "name": "Prof. Leonardo Canvas",
        "title": "Art & Design",
        "icon": "🎨",
        "specialties": ["Art History", "Design Principles", "Color Theory", "Digital Art", "Architecture"],
        "style": "Visual analysis with portfolio-based learning",
    },
    "music": {
        "name": "Prof. Ludwig Harmony",
        "title": "Music",
        "icon": "🎵",
        "specialties": ["Music Theory", "Composition", "Music History", "Performance", "Audio Production"],
        "style": "Score analysis with listening exercises",
    },
    "business": {
        "name": "Prof. Warren Strategy",
        "title": "Business Administration",
        "icon": "💼",
        "specialties": ["Management", "Marketing", "Finance", "Entrepreneurship", "Strategy"],
        "style": "Harvard case method with real company analysis",
    },
    "political_science": {
        "name": "Prof. Aristotle Polis",
        "title": "Political Science",
        "icon": "🏛️",
        "specialties": ["Comparative Politics", "International Relations", "Public Policy", "Democracy Studies", "Governance"],
        "style": "Comparative analysis with current affairs integration",
    },
    "sociology": {
        "name": "Prof. Emile Society",
        "title": "Sociology",
        "icon": "👥",
        "specialties": ["Social Theory", "Research Methods", "Cultural Studies", "Inequality", "Urban Sociology"],
        "style": "Ethnographic approach with survey methodology",
    },
    "environmental_science": {
        "name": "Prof. Gaia Green",
        "title": "Environmental Science",
        "icon": "🌍",
        "specialties": ["Climate Science", "Ecology", "Sustainability", "Conservation", "Environmental Policy"],
        "style": "Field-data driven with sustainability impact assessment",
    },
}


def get_all_professors() -> list:
    result = []
    for key, prof in PROFESSORS.items():
        result.append({
            "id": key,
            "name": prof["name"],
            "title": prof["title"],
            "icon": prof["icon"],
            "specialties": prof["specialties"],
            "style": prof["style"],
        })
    return result


def generate_course(professor_id: str, topic: str) -> dict:
    prof = PROFESSORS.get(professor_id, PROFESSORS["cs"])
    now = datetime.now().strftime("%B %d, %Y")

    weeks = []
    week_topics = [
        f"Introduction to {topic}",
        f"Foundations & Core Concepts of {topic}",
        f"Theoretical Framework",
        f"Analytical Methods & Techniques",
        f"Case Studies & Applications",
        f"Advanced Concepts I",
        f"Advanced Concepts II",
        f"Midterm Review & Assessment",
        f"Research Methodologies in {prof['title']}",
        f"Contemporary Issues & Debates",
        f"Practical Applications",
        f"Integration & Synthesis",
        f"Project Development",
        f"Peer Review & Refinement",
        f"Final Assessment & Course Summary",
    ]

    for i, wt in enumerate(week_topics, 1):
        weeks.append({
            "week": i,
            "topic": wt,
            "objectives": [
                f"Understand key principles of {wt.lower()}",
                f"Apply {prof['title'].lower()} methodology to analyze problems",
                f"Demonstrate competency through practical exercises",
            ],
            "readings": f"Chapter {i} of '{prof['title']}: A Comprehensive Guide'",
        })

    lecture = {
        "title": f"Lecture: {topic}",
        "professor": prof["name"],
        "content": (
            f"Welcome to this lecture on {topic}, delivered by {prof['name']}, "
            f"your {prof['title']} professor.\n\n"
            f"## Overview\n"
            f"In this module, we will explore the fundamental aspects of {topic} "
            f"through the lens of {prof['title']}. Our approach follows the "
            f"pedagogical style of: {prof['style']}.\n\n"
            f"## Core Concepts\n"
            f"The study of {topic} within {prof['title']} encompasses several key areas:\n\n"
        ) + "\n".join(f"- **{s}**: A critical component that forms the foundation of understanding."
                      for s in prof["specialties"]) + (
            f"\n\n## Methodology\n"
            f"We employ {prof['style']} to ensure deep comprehension. "
            f"Each concept is reinforced through practical exercises and real-world applications.\n\n"
            f"## Key Takeaways\n"
            f"1. {topic} is a multifaceted subject requiring interdisciplinary thinking.\n"
            f"2. Practical application solidifies theoretical understanding.\n"
            f"3. Critical analysis is essential for mastery.\n"
            f"4. Continuous practice leads to expertise.\n"
        ),
    }

    exam = {
        "title": f"Examination: {topic}",
        "professor": prof["name"],
        "duration": "3 hours",
        "sections": [
            {
                "type": "Multiple Choice",
                "count": 20,
                "points_each": 2,
                "questions": [
                    {"q": f"Which of the following best describes the primary function of {topic}?",
                     "options": ["A) Theoretical framework", "B) Practical application", "C) Both A and B", "D) Neither"],
                     "answer": "C"},
                    {"q": f"In {prof['title']}, the methodology of {prof['style']} is best used for:",
                     "options": ["A) Basic analysis", "B) Complex problem solving", "C) Data collection", "D) All of the above"],
                     "answer": "D"},
                    {"q": f"The most significant contribution of {topic} to {prof['title']} is:",
                     "options": ["A) Theoretical advancement", "B) Practical tools", "C) Interdisciplinary bridges", "D) Research methodology"],
                     "answer": "C"},
                ],
            },
            {
                "type": "Short Answer",
                "count": 5,
                "points_each": 10,
                "questions": [
                    f"Explain the relationship between {topic} and {prof['specialties'][0]}.",
                    f"Describe three key methodologies used in studying {topic}.",
                    f"Compare and contrast two approaches to analyzing {topic}.",
                ],
            },
            {
                "type": "Essay",
                "count": 2,
                "points_each": 25,
                "questions": [
                    f"Critically evaluate the impact of {topic} on modern {prof['title']}. Support your arguments with specific examples and theoretical frameworks. (Minimum 500 words)",
                    f"Propose a research design to investigate an open question in {topic}. Include methodology, expected outcomes, and potential limitations. (Minimum 500 words)",
                ],
            },
        ],
    }

    return {
        "professor": prof,
        "topic": topic,
        "date": now,
        "syllabus": {"weeks": weeks, "total_weeks": 15},
        "lecture": lecture,
        "exam": exam,
    }
