"""
quiz_game.py - 게임 전체를 관리하는 QuizGame 클래스

역할별로 메서드를 나눴다.
  - 입력 처리 : get_number, get_text
                get_answer, get_yes_no
  - 게임 진행 : show_menu, play_quiz, add_quiz, list_quizzes, show_score, run
                delete_quiz, get_rank_title
  - 저장 로직 : load_state, save_state, reset_to_default
"""

import json
import os
import random
import shutil
from datetime import datetime

from default_quizzes import get_default_quizzes
from quiz import Quiz

# state.json 은 '이 파일이 있는 폴더' = 프로젝트 루트에 저장한다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
# 손상되거나 덮어쓰기 직전의 state.json 을 보관하는 백업 파일
BACKUP_FILE = STATE_FILE + ".bak"
# 손상된 state.json 원본을 따로 남겨두는 파일 (원인 확인용)
CORRUPT_FILE = STATE_FILE + ".corrupt"
LINE = "=" * 44
THIN_LINE = "-" * 44
HINT_PENALTY = 5   # 힌트 1번 볼 때마다 깎이는 점수
HISTORY_SHOW = 5   # 점수 확인 화면에 보여줄 최근 기록 개수


def safe_input(prompt):
    """입력받은 글자에서 깨진 한글(서로게이트 문자)을 정상 글자로 복구한다."""
    text = input(prompt)
    try:
        return text.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    except UnicodeError:
        return text.encode("utf-8", "replace").decode("utf-8")



class QuizGame:
    """게임 전체(메뉴, 퀴즈 목록, 점수, 파일 저장)를 관리하는 클래스"""

    def __init__(self):
        self.quizzes = get_default_quizzes()  # Quiz 객체들의 리스트
        self.best_score = None                # None = 아직 한 번도 안 풀었음
        self.history = []                     # 게임 기록(dict)들의 리스트
        self.load_state()                     # 저장된 파일이 있으면 덮어쓴다

    # ------------------------------------------------------------
    # 입력 처리
    # ------------------------------------------------------------
    def get_number(self, prompt, min_value, max_value):
        """min_value~max_value 사이 정수를 받을 때까지 계속 다시 묻는다."""
        while True:
            text = safe_input(prompt).strip()  # 앞뒤 공백 제거 (" 1 " -> "1")
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
            text = safe_input(prompt).strip()
            if text == "":
                print("⚠️ 빈 칸은 입력할 수 없습니다. 다시 입력하세요.")
                continue
            return text

    def get_yes_no(self, prompt):
        """y 또는 n 을 받을 때까지 묻고, y 면 True 를 돌려준다."""
        while True:
            text = safe_input(prompt).strip().lower()
            if text in ("y", "yes", "ㅛ"):
                return True
            if text in ("n", "no", "ㅜ"):
                return False
            print("⚠️ y 또는 n 으로 입력하세요.")

    def get_answer(self, quiz):
        """정답 번호(1~4)를 받는다. 'h' 를 입력하면 힌트를 보여준다.

        돌려주는 값: (사용자 답 번호, 힌트를 봤는지 True/False)
        """
        hint_used = False
        while True:
            text = safe_input("정답 입력 (1-4, 힌트는 h): ").strip()
            if text.lower() in ("h", "ㅗ"):
                if quiz.hint == "":
                    print("💡 이 문제는 힌트가 없습니다.")
                elif hint_used:
                    print(f"💡 힌트(다시 보기): {quiz.hint}")
                else:
                    hint_used = True
                    print(f"💡 힌트: {quiz.hint}  (-{HINT_PENALTY}점)")
                continue
            if text == "":
                print("⚠️ 입력이 비어 있습니다. 1-4 사이의 숫자를 입력하세요.")
                continue
            try:
                number = int(text)
            except ValueError:
                print("⚠️ 잘못된 입력입니다. 1-4 사이의 숫자(또는 h)를 입력하세요.")
                continue
            if number < 1 or number > 4:
                print("⚠️ 잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                continue
            return number, hint_used

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
        print("3. 퀴즈 목록 (삭제)")
        print("4. 점수 확인 (기록)")
        print("5. 종료")
        print(LINE)

    # ------------------------------------------------------------
    # 1. 퀴즈 풀기
    # ------------------------------------------------------------
    def play_quiz(self):
        """퀴즈를 랜덤 순서로, 원하는 문제 수만큼 출제하고 결과를 보여준다."""
        if len(self.quizzes) == 0:
            print("📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        count = self.get_number(f"몇 문제를 풀까요? (1-{len(self.quizzes)}): ", 1, len(self.quizzes))
        selected = random.sample(self.quizzes, count)  # 섞어서 count 개 뽑기 (중복 없음)
        total = len(selected)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")
        print(f"💡 막히면 h 를 입력해 힌트를 볼 수 있어요. (힌트 1번당 -{HINT_PENALTY}점)")
        print(THIN_LINE)

        correct_count = 0
        hints_used = 0
        for number, quiz in enumerate(selected, start=1):
            quiz.display(number)
            user_answer, hint_used = self.get_answer(quiz)
            if hint_used:
                hints_used += 1
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.correct_text()} 입니다.")
            print(THIN_LINE)

        base_score = round(correct_count / total * 100)
        score = max(0, base_score - hints_used * HINT_PENALTY)  # 0점 밑으로는 안 내려감
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        if hints_used > 0:
            print(f"   (기본 {base_score}점 - 힌트 {hints_used}회 × {HINT_PENALTY}점)")
        print(f"   칭호: {self.get_rank_title(score)}")
        self.update_best_score(score)
        print(LINE)
        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": total,
            "correct": correct_count,
            "hints_used": hints_used,
            "score": score,
        })
        self.save_state()

    def get_rank_title(self, score):
        """점수에 따라 재미있는 경제 칭호를 돌려준다."""
        if score == 100:
            return "🏦 한국은행 총재급"
        elif score >= 80:
            return "📈 증권사 애널리스트급"
        elif score >= 60:
            return "📰 경제신문 애독자"
        elif score >= 40:
            return "🎓 경제원론 수강생"
        else:
            return "🌱 경제 새싹 (다음엔 더 잘할 수 있어요!)"

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
        hint = safe_input("힌트 (없으면 그냥 Enter): ").strip()  # 힌트는 비워도 됨

        self.quizzes.append(Quiz(question, choices, answer, hint))
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
        self.delete_quiz()

    def delete_quiz(self):
        """목록에서 번호를 골라 퀴즈를 삭제하고 파일에 반영한다. 0 이면 그냥 돌아간다."""
        number = self.get_number(f"🗑️ 삭제할 퀴즈 번호 (0 = 메뉴로 돌아가기, 1-{len(self.quizzes)}): ", 0, len(self.quizzes))
        if number == 0:
            return
        target = self.quizzes[number - 1]
        if not self.get_yes_no(f"'{target.question}' 퀴즈를 정말 삭제할까요? (y/n): "):
            print("↩️ 삭제를 취소했습니다.")
            return
        self.quizzes.pop(number - 1)
        self.save_state()
        print(f"🗑️ 삭제했습니다. (남은 퀴즈 {len(self.quizzes)}개)")

    # ------------------------------------------------------------
    # 4. 점수 확인
    # ------------------------------------------------------------
    def update_best_score(self, score):
        """이번 점수가 최고 점수보다 높으면 갱신한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("🎉 새로운 최고 점수입니다!")

    def show_score(self):
        """최고 점수와 최근 게임 기록을 보여준다."""
        if self.best_score is None:
            print("📭 아직 퀴즈를 풀지 않았습니다. 1번 메뉴에서 먼저 풀어 보세요!")
            return
        print(f"🏆 최고 점수: {self.best_score}점")
        if len(self.history) == 0:
            return
        print(f"\n📜 최근 기록 (최대 {HISTORY_SHOW}개, 총 {len(self.history)}판)")
        print(THIN_LINE)
        for record in self.history[-HISTORY_SHOW:]:
            print(f"{record['played_at']} | {record['total']}문제 중 {record['correct']}개 정답"
                  f" | 힌트 {record['hints_used']}회 | {record['score']}점")
        print(THIN_LINE)

    # ------------------------------------------------------------
    # 파일 저장 / 불러오기 (state.json)
    # ------------------------------------------------------------
    def reset_to_default(self):
        """기본 퀴즈 데이터로 되돌린다."""
        self.quizzes = get_default_quizzes()
        self.best_score = None
        self.history = []

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
            history = data.get("history", [])  # 예전 파일에 history 가 없어도 괜찮게
            if not isinstance(history, list):
                raise ValueError("history 는 리스트여야 합니다")
        except (json.JSONDecodeError, ValueError) as error:
            print(f"⚠️ state.json 파일이 손상되었습니다. ({error})")
            try:
                shutil.move(STATE_FILE, CORRUPT_FILE)
                print(f"💾 손상된 파일은 {os.path.basename(CORRUPT_FILE)} 로 따로 보관했습니다.")
            except OSError:
                pass
            print("🔧 기본 퀴즈 데이터로 복구합니다.")
            self.reset_to_default()
            self.save_state()
            return
        except OSError as error:
            print(f"⚠️ 파일을 읽을 수 없습니다. ({error}) 기본 퀴즈로 시작합니다.")
            return

        self.quizzes = quizzes
        self.best_score = best_score
        self.history = history
        score_text = "없음" if best_score is None else f"{best_score}점"
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {score_text})")

    def save_state(self):
        """현재 퀴즈와 최고 점수를 state.json 에 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        try:
            text = json.dumps(data, ensure_ascii=False, indent=2)
            # 1) 기존 파일을 .bak 으로 백업  2) 임시 파일에 먼저 쓰고  3) 한 번에 교체
            #    → 저장 도중 꺼져도 state.json 이 반쯤 쓰인 채로 깨지지 않는다.
            if os.path.exists(STATE_FILE):
                shutil.copyfile(STATE_FILE, BACKUP_FILE)
            temp_file = STATE_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as file:
                file.write(text)
            os.replace(temp_file, STATE_FILE)
        except (OSError, ValueError) as error:
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
