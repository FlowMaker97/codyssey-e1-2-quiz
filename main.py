"""
main.py - 💰 경제 상식 퀴즈 게임

실행: python3 main.py
"""
import json
import os

from default_quizzes import get_default_quizzes
from quiz import Quiz

# state.json 은 '이 파일(main.py)이 있는 폴더' = 프로젝트 루트에 저장한다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
LINE = "=" * 44
THIN_LINE = "-" * 44


class QuizGame:
    """게임 전체(메뉴, 퀴즈 목록, 점수)를 관리하는 클래스"""

    def __init__(self):
        self.quizzes = get_default_quizzes()  # Quiz 객체들의 리스트
        self.best_score = None  # None = 아직 한 번도 안 풀었음
        self.load_state()  # 저장된 파일이 있으면 덮어쓴다

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
        self.update_best_score(score)
        print(LINE)
        self.save_state()

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
        self.save_state()
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
    # 4. 점수 확인
    # ------------------------------------------------------------
    def update_best_score(self, score):
        """이번 점수가 최고 점수보다 높으면 갱신한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("🎉 새로운 최고 점수입니다!")

    def show_score(self):
        """최고 점수를 보여준다."""
        if self.best_score is None:
            print("📭 아직 퀴즈를 풀지 않았습니다. 1번 메뉴에서 먼저 풀어 보세요!")
            return
        print(f"🏆 최고 점수: {self.best_score}점")

    # ------------------------------------------------------------
    # 파일 저장 / 불러오기 (state.json)
    # ------------------------------------------------------------
    def load_state(self):
        """state.json 을 읽어서 퀴즈와 최고 점수를 복원한다."""
        if not os.path.exists(STATE_FILE):
            print("📂 저장된 파일이 없어 기본 퀴즈로 시작합니다.")
            return

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
                raise ValueError("quizzes 항목이 없거나 리스트가 아닙니다")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            best_score = data.get("best_score")
            if best_score is not None and (isinstance(best_score, bool) or not isinstance(best_score, int)):
                raise ValueError("best_score 는 정수 또는 null 이어야 합니다")
        except (json.JSONDecodeError, ValueError) as error:
            print(f"⚠️ state.json 파일이 손상되었습니다. ({error})")
            print("🔧 기본 퀴즈 데이터로 복구합니다.")
            self.quizzes = get_default_quizzes()
            self.best_score = None
            self.save_state()
            return
        except OSError as error:
            print(f"⚠️ 파일을 읽을 수 없습니다. ({error}) 기본 퀴즈로 시작합니다.")
            return

        self.quizzes = quizzes
        self.best_score = best_score
        score_text = "없음" if best_score is None else f"{best_score}점"
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {score_text})")

    def save_state(self):
        """현재 퀴즈와 최고 점수를 state.json 에 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except OSError as error:
            print(f"⚠️ 파일 저장 중 오류가 발생했습니다. ({error})")

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
                    self.show_score()
                else:  # choice == 5
                    self.save_state()
                    print("👋 게임을 종료합니다. 다음에 또 만나요!")
                    break
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C(KeyboardInterrupt) 또는 입력 끝(EOFError) -> 튕기지 않고 정리 후 종료
            print("\n\n⚠️ 입력이 중단되었습니다.")
            self.save_state()
            print("💾 지금까지의 데이터를 저장했습니다.")
            print("👋 안전하게 종료합니다.")


if __name__ == "__main__":
    game = QuizGame()
    game.run()
