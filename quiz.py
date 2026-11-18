"""
quiz.py - 퀴즈 '한 문제'를 표현하는 Quiz 클래스
"""


class Quiz:
    """퀴즈 한 문제 = 문제 + 선택지 4개 + 정답 번호(1~4) + 힌트(선택)"""

    def __init__(self, question, choices, answer, hint=""):
        # self.○○ 에 저장한 값은 이 객체(문제 하나)가 계속 들고 다니는 '속성'이다.
        self.question = question  # str  : 문제 내용
        self.choices = choices    # list : 선택지 4개 (str)
        self.answer = answer      # int  : 정답 번호 1~4
        self.hint = hint          # str  : 힌트 (없으면 빈 문자열)

    def display(self, number):
        """문제와 선택지를 화면에 출력한다."""
        print(f"\n[문제 {number}]")
        print(self.question)
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")

    def is_correct(self, user_answer):
        """사용자가 고른 번호가 정답이면 True, 아니면 False 를 돌려준다."""
        return user_answer == self.answer

    def correct_text(self):
        """'2번 (하락)' 처럼 정답을 사람이 읽기 좋은 글자로 돌려준다."""
        return f"{self.answer}번 ({self.choices[self.answer - 1]})"

    def to_dict(self):
        """JSON 으로 저장할 수 있게 dict 로 바꾼다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """state.json 에서 읽은 dict 를 검사한 뒤 Quiz 객체로 만든다.

        형식이 이상하면 ValueError 를 일으켜서, 불러오는 쪽(QuizGame)이
        '파일이 손상됐다'고 판단할 수 있게 한다.
        """
        if not isinstance(data, dict):
            raise ValueError("퀴즈 항목이 dict 형식이 아닙니다")
        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        hint = data.get("hint", "")

        if not isinstance(question, str) or question.strip() == "":
            raise ValueError("question 이 비어 있거나 글자가 아닙니다")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("choices 는 4개짜리 리스트여야 합니다")
        for choice in choices:
            if not isinstance(choice, str):
                raise ValueError("선택지는 모두 글자(str)여야 합니다")
        if isinstance(answer, bool) or not isinstance(answer, int) or not 1 <= answer <= 4:
            raise ValueError("answer 는 1~4 사이 정수여야 합니다")
        if not isinstance(hint, str):
            hint = ""
        return cls(question, choices, answer, hint)
