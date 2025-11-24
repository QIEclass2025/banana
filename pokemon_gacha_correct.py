import tkinter as tk
from tkinter import ttk, messagebox
import requests
import random
import threading
from PIL import Image, ImageTk
import io


class PokemonBattleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("포켓몬 랜덤 배틀 (종족값 대결)")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # --- 스타일 설정 ---
        self.font_default = ("Malgun Gothic", 10)
        self.font_bold = ("Malgun Gothic", 12, "bold")
        self.font_result = ("Malgun Gothic", 16, "bold")

        # --- UI 구성 ---
        self.top_frame = tk.Frame(root, pady=10)
        self.top_frame.pack()

        self.lbl_title = tk.Label(self.top_frame, text="포켓몬 종족값 배틀!", font=("Malgun Gothic", 20, "bold"))
        self.lbl_title.pack()

        self.btn_battle = tk.Button(self.top_frame, text="배틀 시작 (뽑기)", font=self.font_bold, bg="#FFCC00",
                                    command=self.start_battle_thread, width=20, height=2)
        self.btn_battle.pack(pady=10)

        # 배틀 존 (플레이어 vs 컴퓨터)
        self.battle_frame = tk.Frame(root)
        self.battle_frame.pack(expand=True, fill="both", padx=20)

        # 플레이어 영역
        self.frame_player = self.create_card_frame(self.battle_frame, "나의 포켓몬", "blue")
        self.frame_player.pack(side=tk.LEFT, expand=True, fill="both", padx=5)

        # VS 텍스트
        self.lbl_vs = tk.Label(self.battle_frame, text="VS", font=("Impact", 30), fg="red")
        self.lbl_vs.pack(side=tk.LEFT, padx=10)

        # 컴퓨터 영역
        self.frame_cpu = self.create_card_frame(self.battle_frame, "상대 포켓몬", "red")
        self.frame_cpu.pack(side=tk.RIGHT, expand=True, fill="both", padx=5)

        # 결과 표시창
        self.lbl_final_result = tk.Label(root, text="", font=self.font_result, pady=20)
        self.lbl_final_result.pack()

        # 데이터 캐싱용 (이미지 참조 유지)
        self.current_images = []

    def create_card_frame(self, parent, title, color):
        frame = tk.LabelFrame(parent, text=title, font=self.font_bold, fg=color, bg="white", bd=3)

        lbl_img = tk.Label(frame, text="?", bg="#f0f0f0", width=20, height=10)
        lbl_img.pack(pady=10, fill="x")

        lbl_name = tk.Label(frame, text="-", font=self.font_bold, bg="white")
        lbl_name.pack()

        lbl_rarity = tk.Label(frame, text="", font=self.font_default, fg="gray", bg="white")
        lbl_rarity.pack()

        lbl_stats = tk.Label(frame, text="전투력(Total): 0", font=("Malgun Gothic", 14, "bold"), fg="black", bg="white")
        lbl_stats.pack(pady=10)

        # 위젯들을 딕셔너리로 저장해둠 (나중에 접근하기 위해)
        frame.widgets = {
            "img": lbl_img,
            "name": lbl_name,
            "rarity": lbl_rarity,
            "stats": lbl_stats
        }
        return frame

    def start_battle_thread(self):
        self.btn_battle.config(state=tk.DISABLED, text="배틀 진행 중...")
        self.lbl_final_result.config(text="데이터를 불러오는 중입니다...", fg="black")

        # 스레드 시작
        threading.Thread(target=self.run_battle_logic, daemon=True).start()

    def get_random_pokemon_data(self):
        """API에서 랜덤 포켓몬 1마리의 정보를 가져옴"""
        try:
            # 1~1025번 (현재까지의 도감 번호) 중 랜덤 선택 -> 메가진화 등 복잡한 폼 제외하고 기본 폼만 조회
            p_id = random.randint(1, 1025)

            # 1. 기본 정보 조회
            url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{p_id}"
            res_p = requests.get(url_pokemon)
            res_p.raise_for_status()
            data_p = res_p.json()

            # 2. 종족값(Stats) 합산
            stats = data_p['stats']
            total_stats = sum([s['base_stat'] for s in stats])

            # 3. 이미지 (공식 일러스트 사용 -> 퀄리티 UP)
            img_url = data_p['sprites']['other']['official-artwork']['front_default']
            if not img_url:
                img_url = data_p['sprites']['front_default']  # 없으면 기본 도트

            # 4. 종(Species) 정보 조회 (한글 이름, 전설 여부 등)
            url_species = data_p['species']['url']
            res_s = requests.get(url_species)
            res_s.raise_for_status()
            data_s = res_s.json()

            # 한글 이름 찾기
            korean_name = data_p['name']
            for name_info in data_s['names']:
                if name_info['language']['name'] == 'ko':
                    korean_name = name_info['name']
                    break

            # 희귀도 판별 (API 데이터 기반)
            rarity = "일반"
            if data_s['is_mythical']:
                rarity = "환상"
            elif data_s['is_legendary']:
                rarity = "전설"

            return {
                "name": korean_name,
                "stats": total_stats,
                "rarity": rarity,
                "img_url": img_url
            }

        except Exception as e:
            print(f"Error fetching pokemon: {e}")
            return None

    def download_image(self, url):
        if not url: return None
        try:
            res = requests.get(url)
            img_data = res.content
            image = Image.open(io.BytesIO(img_data))
            image = image.resize((180, 180), Image.Resampling.LANCZOS)  # Pillow로 리사이징
            return ImageTk.PhotoImage(image)
        except:
            return None

    def run_battle_logic(self):
        # 두 마리 포켓몬 데이터 가져오기
        player_data = self.get_random_pokemon_data()
        cpu_data = self.get_random_pokemon_data()

        if not player_data or not cpu_data:
            self.root.after(0, self.show_error)
            return

        # 이미지 다운로드
        player_img = self.download_image(player_data['img_url'])
        cpu_img = self.download_image(cpu_data['img_url'])

        # UI 업데이트 요청
        self.root.after(0, lambda: self.update_ui(player_data, player_img, cpu_data, cpu_img))

    def update_ui(self, p_data, p_img, c_data, c_img):
        self.current_images = [p_img, c_img]  # 가비지 컬렉션 방지

        # 플레이어 업데이트
        p_widgets = self.frame_player.widgets
        p_widgets['img'].config(image=p_img, text="")
        p_widgets['name'].config(text=p_data['name'])
        p_widgets['rarity'].config(text=f"[{p_data['rarity']}]", fg="purple" if p_data['rarity'] != "일반" else "gray")
        p_widgets['stats'].config(text=f"전투력: {p_data['stats']}")

        # 컴퓨터 업데이트
        c_widgets = self.frame_cpu.widgets
        c_widgets['img'].config(image=c_img, text="")
        c_widgets['name'].config(text=c_data['name'])
        c_widgets['rarity'].config(text=f"[{c_data['rarity']}]", fg="purple" if c_data['rarity'] != "일반" else "gray")
        c_widgets['stats'].config(text=f"전투력: {c_data['stats']}")

        # 승패 판정
        if p_data['stats'] > c_data['stats']:
            result_text = "🎉 플레이어 승리! 🎉"
            result_color = "blue"
        elif p_data['stats'] < c_data['stats']:
            result_text = "💀 패배했습니다... 💀"
            result_color = "red"
        else:
            result_text = "무승부!"
            result_color = "green"

        self.lbl_final_result.config(text=result_text, fg=result_color)
        self.btn_battle.config(state=tk.NORMAL, text="다시 배틀하기")

    def show_error(self):
        messagebox.showerror("오류", "데이터를 가져오는데 실패했습니다.\n인터넷 연결을 확인하세요.")
        self.btn_battle.config(state=tk.NORMAL, text="배틀 시작")


if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonBattleGame(root)
    root.mainloop()