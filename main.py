"""
main.py - 💰 경제 상식 퀴즈 게임 (실행 시작점)

실행: python3 main.py

실제 게임 로직은 quiz_game.py 의 QuizGame 클래스에 있고,
퀴즈 한 문제는 quiz.py 의 Quiz 클래스가 표현한다.
"""

from quiz_game import QuizGame


def main():
    """게임 객체를 만들고 실행한다."""
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
