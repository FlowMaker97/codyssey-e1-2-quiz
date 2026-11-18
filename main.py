"""
main.py - 💰 경제 상식 퀴즈 게임

실행: python3 main.py
"""

from default_quizzes import get_default_quizzes
from quiz import Quiz

LINE = "=" * 44
THIN_LINE = "-" * 44


class QuizGame:
    """게임 전체(메뉴, 퀴즈 목록, 점수)를 관리하는 클래스"""

    def __init__(self):
        self.quizzes = get_default_quizzes()  # Quiz 객체들의 리스트

    # ------------------------------------------------------------
    # 입력 처리
    # ------------------------------------------------------------
    def get_number(self, prompt, min_value, max_value):
        """min_value~max_value 사이 정수를 받을 때까지 계속 다시 묻는다."""
        while True:
            text = input(prompt).strip()  # 앞뒤 공백 제거 (" 1 " -> "1")
            if text == "":
                print("⚠️ 입력이 비어 있습니다. 숫자를 입력하세요.")
                continue
            try:
                number = int(text)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            if number < min_value or number > max_value:
                print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            return number

    def get_text(self, prompt):
        """빈 칸이 아닌 글자를 받을 때까지 계속 다시 묻는다."""
        while True:
            text = input(prompt).strip()
            if text == "":
                print("⚠️ 빈 칸은 입력할 수 없습니다. 다시 입력하세요.")
                continue
            return text

    # ------------------------------------------------------------
    # 메뉴
    # ------------------------------------------------------------
    def show_menu(self):
        """메인 메뉴를 출력한다."""
        print()
        print(LINE)
        print("        💰 경제 상식 퀴즈 게임 💰")
        print(LINE)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print(LINE)

    def coming_soon(self):
        """아직 만들지 않은 메뉴를 골랐을 때 안내한다."""
        print("🚧 아직 준비 중인 기능입니다.")

    # ------------------------------------------------------------
    # 1. 퀴즈 풀기
    # ------------------------------------------------------------
    def play_quiz(self):
        """등록된 퀴즈를 순서대로 출제하고 결과를 보여준다."""
        if len(self.quizzes) == 0:
            print("📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        total = len(self.quizzes)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")
        print(THIN_LINE)

        correct_count = 0
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            user_answer = self.get_number("정답 입력 (1-4): ", 1, 4)
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.correct_text()} 입니다.")
            print(THIN_LINE)

        score = round(correct_count / total * 100)
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        print(LINE)

    # ------------------------------------------------------------
    # 2. 퀴즈 추가
    # ------------------------------------------------------------
    def add_quiz(self):
        """사용자에게 문제/선택지 4개/정답을 입력받아 새 퀴즈를 등록한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = self.get_text("문제를 입력하세요: ")
        choices = []
        for index in range(1, 5):
            choices.append(self.get_text(f"선택지 {index}: "))
        answer = self.get_number("정답 번호 (1-4): ", 1, 4)

        self.quizzes.append(Quiz(question, choices, answer))
        print("✅ 퀴즈가 추가되었습니다!")

    # ------------------------------------------------------------
    # 3. 퀴즈 목록
    # ------------------------------------------------------------
    def list_quizzes(self):
        """등록된 퀴즈의 문제만 번호와 함께 보여준다."""
        if len(self.quizzes) == 0:
            print("📭 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print(THIN_LINE)

    # ------------------------------------------------------------
    # 게임 실행 (메인 루프)
    # ------------------------------------------------------------
    def run(self):
        """메뉴를 보여주고, 선택한 기능을 실행하는 것을 '종료'를 고를 때까지 반복한다."""
        try:
            while True:
                self.show_menu()
                choice = self.get_number("선택: ", 1, 5)
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.coming_soon()
                else:  # choice == 5
                    print("👋 게임을 종료합니다. 다음에 또 만나요!")
                    break
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C(KeyboardInterrupt) 또는 입력 끝(EOFError) -> 튕기지 않고 정리 후 종료
            print("\n\n⚠️ 입력이 중단되었습니다.")
            print("👋 안전하게 종료합니다.")


if __name__ == "__main__":
    game = QuizGame()
    game.run()
