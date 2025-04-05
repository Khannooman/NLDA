class FastAPIConstants:
    TITLE = 'NLDA | Server'
    DESCRIPTION = """
### Project Description: NLDA (Natural Language Data Analysis)

#### Overview
**NLDA** is a server-side backend project designed to facilitate advanced data analysis using natural language.

#### Technology Stack
- **Programming Language:** Python
- **Framework:** FastAPI

#### Team Members
- **Developer:** Khursheed, Nooman
- **Manager:** Williams

This project is for non-tech users who want to analyze their buisness using natural language. The project is designed to be user-friendly and easy to use.
    """
    SUMMARY = "Project Summary"
    VERSION = "1.0.0"
    T_N_C = "http://nlda.com/terms-and-conditions"
    CONTACT = {
        "name": "Nooman Khan",
        "url": "https://nlda-project.com",
        "email": "khannooman8586@gmail.com",
    }
    LICENSE_INFO = {
        "name": "PicksieAI",
        "url": "http://nlda-project.com/license",
    }

    OPENAPI_TAGS_METADATA = [
        {
            "name": "API Testings",
            "description": "Provides a route to run tests at deployment time."
        },
        {
            "name": "Health",
            "description": "Check health of the server"
        },
        {
            "name": "Chat",
            "description": "Conversational chatbot with RAG"
        },
    ]