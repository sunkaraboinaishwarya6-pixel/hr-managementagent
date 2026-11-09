def calculate_role_scores(skills, projects, experience):
    """
    Evidence-based role scoring.
    Scores are based only on information found in the resume.
    """

    text = " ".join([
        str(skills),
        str(projects),
        str(experience)
    ]).lower()

    scores = {
        "Data Science": 0,
        "Full Stack Developer": 0,
        "Data Analyst": 0,
        "Machine Learning": 0
    }

    # Data Science
    if "python" in text:
        scores["Data Science"] += 20
    if "data science" in text:
        scores["Data Science"] += 25
    if "sql" in text or "mysql" in text or "postgresql" in text:
        scores["Data Science"] += 15
    if "jupyter" in text or "google colab" in text:
        scores["Data Science"] += 10

    # Full Stack
    if "react" in text:
        scores["Full Stack Developer"] += 25
    if "supabase" in text:
        scores["Full Stack Developer"] += 15
    if "postgresql" in text or "mysql" in text:
        scores["Full Stack Developer"] += 10
    if "web" in text:
        scores["Full Stack Developer"] += 15

    # Data Analyst
    if "sql" in text or "mysql" in text or "postgresql" in text:
        scores["Data Analyst"] += 20
    if "python" in text:
        scores["Data Analyst"] += 15
    if "power bi" in text:
        scores["Data Analyst"] += 25
    if "excel" in text:
        scores["Data Analyst"] += 15

    # Machine Learning
    if "tensorflow" in text:
        scores["Machine Learning"] += 25
    if "opencv" in text:
        scores["Machine Learning"] += 15
    if "mediapipe" in text:
        scores["Machine Learning"] += 15
    if "machine learning" in text or "deep learning" in text:
        scores["Machine Learning"] += 25

    return scores