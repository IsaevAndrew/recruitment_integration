import uuid


def generate_session_token() -> str:
    return str(uuid.uuid4())


def calculate_score(
    correct_count: int,
    total_questions: int
) -> float:
    if total_questions == 0:
        return 0.0
    return (correct_count / total_questions) * 100.0
