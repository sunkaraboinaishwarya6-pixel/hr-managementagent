import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


from servies.ollama_service import ask_qwen

from servies.resume_parser import (
    extract_profile_facts,
    extract_text_from_pdf,
    analyze_resume_with_ai,
    extract_verified_academic_facts
)

from role_matcher import calculate_role_scores

from database import db

from auth import (
    create_user,
    verify_password,
    hash_password,
    login_user
)

from RAG.rag_chat import ask_hr_with_rag


app = FastAPI()


UPLOAD_FOLDER = os.path.join(
    tempfile.gettempdir(),
    "hr-management-agent-uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# RESUME UPLOAD
# =========================================================

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())


    resume_text = extract_text_from_pdf(
        file_path
    )


    ai_analysis = analyze_resume_with_ai(
        resume_text
    )


    role_scores = calculate_role_scores(
        skills=resume_text,
        projects=resume_text,
        experience=resume_text
    )


    lines = ai_analysis.splitlines()

    candidate_name = "Unknown Candidate"
    candidate_email = None


    for line in lines:

        line = line.strip()

        if line.startswith("Name:"):

            candidate_name = (
                line.replace(
                    "Name:",
                    "",
                    1
                ).strip()
            )

        elif line.startswith("Email:"):

            email_value = (
                line.replace(
                    "Email:",
                    "",
                    1
                ).strip()
            )

            if email_value:
                candidate_email = email_value


    academic_facts = (
        extract_verified_academic_facts(
            resume_text
        )
    )


    profile_facts = extract_profile_facts(
        resume_text
    )


    cursor = db.cursor()


    try:

        # =================================================
        # SAVE CANDIDATE
        # =================================================

        cursor.execute(
            """
            INSERT INTO candidates (
                name,
                email
            )
            VALUES (%s, %s)
            """,
            (
                candidate_name,
                candidate_email
            )
        )

        candidate_id = cursor.lastrowid


        # =================================================
        # SAVE RESUME
        # =================================================

        cursor.execute(
            """
            INSERT INTO resumes (
                candidate_id,
                file_name,
                file_path
            )
            VALUES (%s, %s, %s)
            """,
            (
                candidate_id,
                file.filename,
                file_path
            )
        )


        # =================================================
        # SAVE 10TH
        # =================================================

        tenth_percentage = (
            academic_facts["10th"]["percentage"]
        )

        if tenth_percentage is not None:

            cursor.execute(
                """
                INSERT INTO education (
                    candidate_id,
                    qualification,
                    year,
                    percentage
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    candidate_id,
                    "10th",
                    academic_facts["10th"]["year"],
                    float(tenth_percentage)
                )
            )


        # =================================================
        # SAVE 12TH
        # =================================================

        twelfth_percentage = (
            academic_facts["12th"]["percentage"]
        )

        if twelfth_percentage is not None:

            cursor.execute(
                """
                INSERT INTO education (
                    candidate_id,
                    qualification,
                    year,
                    percentage
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    candidate_id,
                    "12th / Intermediate",
                    academic_facts["12th"]["year"],
                    float(twelfth_percentage)
                )
            )


        # =================================================
        # SAVE B.TECH
        # =================================================

        btech_percentage = (
            academic_facts["btech"]["percentage"]
        )

        if btech_percentage is not None:

            cursor.execute(
                """
                INSERT INTO education (
                    candidate_id,
                    qualification,
                    year,
                    percentage
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    candidate_id,
                    "B.Tech / Degree",
                    None,
                    float(btech_percentage)
                )
            )


        # =================================================
        # SAVE CODING / SOCIAL PROFILES
        # =================================================

        for profile_key, profile_data in profile_facts.items():

            platform = profile_data.get("platform")
            profile_url = profile_data.get("url")
            username = profile_data.get("username")

            if platform:

                cursor.execute(
                    """
                    INSERT INTO coding_profiles (
                        candidate_id,
                        platform,
                        profile_url,
                        username
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        candidate_id,
                        platform,
                        profile_url,
                        username
                    )
                )


        # =================================================
        # SAVE ROLE SCORES
        # =================================================

        if isinstance(role_scores, dict):

            for role_name, score in role_scores.items():

                try:

                    numeric_score = float(score)

                    cursor.execute(
                        """
                        INSERT INTO role_scores (
                         candidate_id,
                         role_name,
                         score
)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            candidate_id,
                            role_name,
                            numeric_score
                        )
                    )

                except (ValueError, TypeError):
                    pass


        db.commit()


    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        cursor.close()


    return {

        "message":
            "Resume uploaded, analyzed and saved successfully",

        "candidate_id":
            candidate_id,

        "file_name":
            file.filename,

        "ai_analysis":
            ai_analysis,

        "role_scores":
            role_scores,

        "profile_facts":
            profile_facts
    }


# =========================================================
# INTERVIEW ROUND SAVE
# =========================================================

@app.post("/interview-round")
def save_interview_round(
    candidate_id: int,
    round_number: int,
    round_name: str,
    score: float,
    status: str,
    feedback: str = ""
):

    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO placement_rounds (
                candidate_id,
                round_number,
                round_name,
                score,
                status,
                feedback
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                candidate_id,
                round_number,
                round_name,
                score,
                status,
                feedback
            )
        )

        db.commit()

        round_id = cursor.lastrowid

        return {
            "message": "Interview round saved successfully",
            "round_id": round_id,
            "candidate_id": candidate_id,
            "round_number": round_number,
            "round_name": round_name,
            "score": score,
            "status": status,
            "feedback": feedback
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        cursor.close()


# =========================================================
# GET CANDIDATE INTERVIEW ROUNDS
# =========================================================

@app.get("/candidate/{candidate_id}/rounds")
def get_candidate_rounds(
    candidate_id: int
):

    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                round_id,
                candidate_id,
                round_number,
                round_name,
                score,
                status,
                feedback
            FROM placement_rounds
            WHERE candidate_id = %s
            ORDER BY round_number ASC
            """,
            (candidate_id,)
        )

        rounds = cursor.fetchall()

        return {
            "candidate_id": candidate_id,
            "rounds": rounds
        }

    finally:

        cursor.close()


# =========================================================
# FINAL REPORT
# =========================================================

@app.post("/final-report")
def create_final_report(
    candidate_id: int,
    overall_score: float,
    qualification_status: str,
    strengths: str = "",
    weaknesses: str = "",
    recommendation: str = ""
):

    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO final_reports (
                candidate_id,
                overall_score,
                qualification_status,
                strengths,
                weaknesses,
                recommendation
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                candidate_id,
                overall_score,
                qualification_status,
                strengths,
                weaknesses,
                recommendation
            )
        )

        db.commit()

        report_id = cursor.lastrowid

        return {
            "message": "Final report saved successfully",
            "report_id": report_id,
            "candidate_id": candidate_id,
            "overall_score": overall_score,
            "qualification_status": qualification_status,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": recommendation
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        cursor.close()


# =========================================================
# GET FINAL REPORT
# =========================================================

@app.get("/candidate/{candidate_id}/final-report")
def get_final_report(
    candidate_id: int
):

    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT *
            FROM final_reports
            WHERE candidate_id = %s
            ORDER BY report_id DESC
            LIMIT 1
            """,
            (candidate_id,)
        )

        report = cursor.fetchone()

        return {
            "candidate_id": candidate_id,
            "report": report
        }

    finally:

        cursor.close()



@app.get("/candidate/{candidate_id}/dashboard")
def candidate_dashboard(candidate_id: int):

    cursor = db.cursor(dictionary=True)

    try:

        # Candidate
        cursor.execute(
            """
            SELECT
                candidate_id,
                name,
                email
            FROM candidates
            WHERE candidate_id = %s
            """,
            (candidate_id,)
        )

        candidate = cursor.fetchone()

        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        # Resume
        cursor.execute(
            """
            SELECT
                resume_id,
                file_name,
                file_path
            FROM resumes
            WHERE candidate_id = %s
            ORDER BY resume_id DESC
            LIMIT 1
            """,
            (candidate_id,)
        )

        resume = cursor.fetchone()

        # Interview rounds
        cursor.execute(
            """
            SELECT
                round_id,
                round_number,
                round_name,
                score,
                status,
                feedback
            FROM placement_rounds
            WHERE candidate_id = %s
            ORDER BY round_number ASC
            """,
            (candidate_id,)
        )

        rounds = cursor.fetchall()

        # Final report
        cursor.execute(
            """
            SELECT
                report_id,
                overall_score,
                qualification_status,
                strengths,
                weaknesses,
                recommendation,
                generated_at
            FROM final_reports
            WHERE candidate_id = %s
            ORDER BY report_id DESC
            LIMIT 1
            """,
            (candidate_id,)
        )

        final_report = cursor.fetchone()

        return {
            "candidate": candidate,
            "resume": resume,
            "interview_rounds": rounds,
            "final_report": final_report
        }

    finally:

        cursor.close()

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message":
            "HR Management AI Agent is running!"
    }


# =========================================================
# BASIC QWEN ASK
# =========================================================

@app.get("/ask")
def ask(question: str):

    return StreamingResponse(
        ask_qwen(question),
        media_type="text/plain"
    )


# =========================================================
# SIGNUP
# =========================================================

@app.post("/signup")
def signup(
    name: str,
    email: str,
    password: str,
    role: str = "EMPLOYEE"
):

    return {

        "message":
            create_user(
                name,
                email,
                password,
                role
            )
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login(
    email: str,
    password: str
):

    return login_user(
        email,
        password
    )


# =========================================================
# HR RAG CHAT
# =========================================================

@app.get("/hr-chat")
def hr_chat(question: str):

    answer = ask_hr_with_rag(
        question
    )

    return {

        "question":
            question,

        "answer":
            answer
    }