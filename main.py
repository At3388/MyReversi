import pygame
from pygame.locals import *
import random
import time
import sys
import pickle
import asyncio

TITLE, SETTINGS, GAME, END=range(4)
TABLE, REI1, REI2=range(3)

class Game:
    fps=60
    grid=60

    epsilon=0.06

    title_text_pos=(225, 30)
    single_button_pos=(250, 250)
    duo_button_pos=(250, 350)

    table_ai_button_pos=(240, 200)
    reinforcement_ai_button_pos=(240, 260)
    reinforcement_ai_2_button_pos=(240, 320)
    
    turn_text_pos=(10, 20)
    turn_number_text_pos=(400, 20)
    time_text_pos=(510, 20)
    pass_button_pos=(280, 560)

    black_text_pos=(225, 250)
    white_text_pos=(330, 250)
    versus_text_pos=(275, 250)

    small_font=20
    big_font=30
    title_font=40

    def __init__(self):
        pygame.init()

        self.screen=pygame.display.set_mode((self.grid*10, self.grid*10))
        pygame.display.set_caption("Reversi")

        self.TIME_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIME_EVENT, 1000)

        self.clock=pygame.time.Clock()

        self.q_table={}

        self.title_text=None
        self.single_button=None
        self.duo_button=None
        self.turn_text=None
        self.turn_number_text=None
        self.time_text=None
        self.pass_button=None
        self.table_ai_button=None
        self.reinforcement_ai_button=None
        self.reinforcement_ai_2_button=None
        self.winner_text=None
        self.black_text=None
        self.white_text=None
        self.versus_text=None
        
        self.board=[[0 for i in range(8)] for j in range(8)]
        self.board[3][3]=-1
        self.board[3][4]=1
        self.board[4][3]=1
        self.board[4][4]=-1
        self.black_turn=True
        self.dist=((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))
        self.putable_bool=[[False for i in range(8)] for j in range(8)]
        self.putable_list=[[[0 for i in range(8)] for j in range(8)] for k in range(8)]

        self.font_small=pygame.font.Font("./M_PLUS_1p/MPLUS1p-Regular.ttf", self.small_font)
        self.font_big=pygame.font.Font("./M_PLUS_1p/MPLUS1p-Regular.ttf", self.big_font)
        self.font_title=pygame.font.Font("./M_PLUS_1p/MPLUS1p-Regular.ttf", self.title_font)

        self.running=True
        self.playing=0
        self.draw_queue=True
        self.second_player=False
        self.ai_type=TABLE
        self.sum=[0, 0]
        self.pass_able=True
        self.b=False
        self.last_pass=0

        self.turn_number=1
        self.time=0

        self.calc_putable()

        asyncio.run(self.main())

    async def main(self) -> None:
        while self.running:
            self.clock.tick(self.fps)
            await asyncio.sleep(0)
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    self.running=False
                    sys.exit()
                elif event.type==self.TIME_EVENT:
                    self.draw_queue=True
                elif event.type==MOUSEBUTTONDOWN:
                    x, y=event.pos
                    self.click(x, y)
                elif event.type==KEYDOWN:
                    if event.key==K_ESCAPE:
                        pygame.quit()
                        self.running=False
                        sys.exit()
                    elif event.key==K_RETURN:
                        self.playing=END
                        self.draw_queue=True

            self.draw()
            if self.b:
                self.playing=END
                self.draw_queue=True

    def draw(self) -> None:
        if self.draw_queue:
            if self.playing==END:
                self.end_draw()
            else:
                self.screen.fill((170, 170, 220))
                if self.playing==TITLE:
                    self.title_draw()
                elif self.playing==SETTINGS:
                    self.settings_draw()
                elif self.playing==GAME:
                    self.game_draw()
            pygame.display.update()
            self.draw_queue=False

    def title_draw(self) -> None:
        self.title_text=self.font_title.render("REVERSI", True, (0, 0, 0))
        self.single_button=self.font_small.render("一人プレイ", True, (0, 0, 0))
        self.duo_button=self.font_small.render("二人プレイ", True, (0, 0, 0))
        
        self.screen.blit(self.title_text, (self.title_text_pos[0], self.title_text_pos[1]))

        pad=self.small_font//2
        
        pygame.draw.rect(self.screen, (255, 255, 255), Rect(self.single_button_pos[0]-pad, self.single_button_pos[1]-pad, self.small_font*6, self.small_font*2), width=0)
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(self.single_button_pos[0]-pad, self.single_button_pos[1]-pad, self.small_font*6, self.small_font*2), width=1)
        self.screen.blit(self.single_button, (self.single_button_pos[0], self.single_button_pos[1]))

        pygame.draw.rect(self.screen, (255, 255, 255), Rect(self.duo_button_pos[0]-pad, self.duo_button_pos[1]-pad, self.small_font*6, self.small_font*2), width=0)
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(self.duo_button_pos[0]-pad, self.duo_button_pos[1]-pad, self.small_font*6, self.small_font*2), width=1)
        self.screen.blit(self.duo_button, (self.duo_button_pos[0], self.duo_button_pos[1]))

    def settings_draw(self) -> None:
        self.table_ai_button=self.font_small.render("評価関数 AI", True, (0, 0, 0))
        self.reinforcement_ai_button=self.font_small.render("強化学習LV1", True, (0, 0, 0))
        self.reinforcement_ai_2_button=self.font_small.render("強化学習LV2", True, (0, 0, 0))

        pad=self.small_font//2

        pygame.draw.rect(self.screen, (255, 255, 255), Rect(self.table_ai_button_pos[0]-pad, self.table_ai_button_pos[1]-pad, self.small_font*7, self.small_font*2), width=0)
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(self.table_ai_button_pos[0]-pad, self.table_ai_button_pos[1]-pad, self.small_font*7, self.small_font*2), width=1)
        self.screen.blit(self.table_ai_button, (self.table_ai_button_pos[0], self.table_ai_button_pos[1]))

        pygame.draw.rect(self.screen, (255, 255, 255), Rect(self.reinforcement_ai_button_pos[0]-pad, self.reinforcement_ai_button_pos[1]-pad, self.small_font*7, self.small_font*2), width=0)
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(self.reinforcement_ai_button_pos[0]-pad, self.reinforcement_ai_button_pos[1]-pad, self.small_font*7, self.small_font*2), width=1)
        self.screen.blit(self.reinforcement_ai_button, (self.reinforcement_ai_button_pos[0], self.reinforcement_ai_button_pos[1]))

        pygame.draw.rect(self.screen, (255, 255, 255), Rect(self.reinforcement_ai_2_button_pos[0]-pad, self.reinforcement_ai_2_button_pos[1]-pad, self.small_font*7, self.small_font*2), width=0)
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(self.reinforcement_ai_2_button_pos[0]-pad, self.reinforcement_ai_2_button_pos[1]-pad, self.small_font*7, self.small_font*2), width=1)
        self.screen.blit(self.reinforcement_ai_2_button, (self.reinforcement_ai_2_button_pos[0], self.reinforcement_ai_2_button_pos[1]))

    def game_draw(self) -> None:
        for i in range(8):
            for j in range(8):
                if self.putable_bool[j][i]:
                    pygame.draw.rect(self.screen, (250, 250, 120), Rect(self.grid*(i+1), self.grid*(j+1), self.grid, self.grid), width=0)
                    
        for i in range(9):
            pygame.draw.line(self.screen, (0, 0, 0), (self.grid, self.grid*(i+1)), (self.grid*9, self.grid*(i+1)))
        for j in range(9):
            pygame.draw.line(self.screen, (0, 0, 0), (self.grid*(j+1), self.grid), (self.grid*(j+1), self.grid*9))

        play_time=time.time()
        play_time-=self.time
        play_time=int(play_time)
        self.time_text=self.font_small.render(f"{play_time//60 :02d}:{play_time%60 :02d}", True, (0, 0, 0))
        self.screen.blit(self.time_text, (self.time_text_pos[0], self.time_text_pos[1]))

        self.turn_number_text=self.font_small.render(f"ターン{self.turn_number}", True, (0, 0, 0))
        self.screen.blit(self.turn_number_text, (self.turn_number_text_pos[0], self.turn_number_text_pos[1]))

        if self.second_player:
            if self.black_turn:
                self.turn_text=self.font_small.render("プレイヤー1(黒)のターンです。", True, (0, 0, 0))
            else:
                self.turn_text=self.font_small.render("プレイヤー2(白)のターンです。", True, (255, 255, 255))
        else:
            if self.black_turn:
                self.turn_text=self.font_small.render("あなたの番です。", True, (0, 0, 0))
            else:
                self.turn_text=self.font_small.render("相手の番です。", True, (0, 0, 0))
        self.screen.blit(self.turn_text, (self.turn_text_pos[0], self.turn_text_pos[1]))

        pad=self.grid//2
        for i in range(8):
            for j in range(8):
                if self.board[j][i]==1:
                    pygame.draw.circle(self.screen, (0, 0, 0), (self.grid*(i+1)+pad, self.grid*(j+1)+pad), 2*self.grid//5, 0)
                elif self.board[j][i]==-1:
                    pygame.draw.circle(self.screen, (255, 255, 255), (self.grid*(i+1)+pad, self.grid*(j+1)+pad), 2*self.grid//5, 0)

        if self.pass_able:
            pad=self.small_font//2
            self.pass_button=self.font_small.render("パス", True, (0, 0, 0), (255, 255, 255))
            
            pygame.draw.rect(self.screen, (255, 255, 255), Rect(self.pass_button_pos[0]-pad, self.pass_button_pos[1]-pad, self.small_font*3, self.small_font*2), width=0)
            pygame.draw.rect(self.screen, (0, 0, 0), Rect(self.pass_button_pos[0]-pad, self.pass_button_pos[1]-pad, self.small_font*3, self.small_font*2), width=1)
            self.screen.blit(self.pass_button, (self.pass_button_pos[0], self.pass_button_pos[1]))

    def end_draw(self) -> None:
        winner_text_pos=[150, 180]
        if self.sum[0]>self.sum[1]:
            if self.second_player:
                self.winner_text=self.font_big.render("プレイヤー1(黒)の勝ち", True, (0, 0, 0), (170, 170, 220))
            else:
                winner_text_pos=[260, 180]
                self.winner_text=self.font_big.render("勝ち", True, (0, 0, 0), (170, 170, 220))
        elif self.sum[0]<self.sum[1]:
            if self.second_player:
                self.winner_text=self.font_big.render("プレイヤー2(白)の勝ち", True, (0, 0, 0), (170, 170, 220))
            else:
                winner_text_pos=[260, 180]
                self.winner_text=self.font_big.render("負け", True, (0, 0, 0), (170, 170, 220))
        else:
            winner_text_pos=[240, 180]
            self.winner_text=self.font_big.render("引き分け", True, (0, 0, 0), (170, 170, 220))
        self.screen.blit(self.winner_text, (winner_text_pos[0], winner_text_pos[1]))

        self.black_text=self.font_big.render(f"{self.sum[0]:02d}", True, (170, 170, 220), (0, 0, 0))
        self.white_text=self.font_big.render(f"{self.sum[1]:02d}", True, (170, 170, 220), (255, 255, 255))
        self.versus_text=self.font_big.render("VS", True, (255, 20, 20))
        self.screen.blit(self.black_text, (self.black_text_pos[0], self.black_text_pos[1]))
        self.screen.blit(self.white_text, (self.white_text_pos[0], self.white_text_pos[1]))
        self.screen.blit(self.versus_text, (self.versus_text_pos[0], self.versus_text_pos[1]))

    def click(self, x:int, y:int) -> None:
        if self.playing==TITLE:
            self.title_click(x, y)
        elif self.playing==SETTINGS:
            self.settings_click(x, y)
        elif self.playing==GAME:
            self.game_click(x, y)

    def title_click(self, x:int, y:int) -> None:
        pad=self.small_font//2        
        if x>=self.single_button_pos[0]-pad and x<=self.single_button_pos[0]+self.small_font*5+pad and y>=self.single_button_pos[1]-pad and y<=self.single_button_pos[1]+self.small_font+pad:
            self.playing=SETTINGS
            self.draw_queue=True
        elif x>=self.duo_button_pos[0]-pad and x<=self.duo_button_pos[0]+self.small_font*5+pad and y>=self.duo_button_pos[1]-pad and y<=self.duo_button_pos[1]+self.small_font+pad:
            self.playing=GAME
            self.time=time.time()
            self.second_player=True
            self.draw_queue=True

    def settings_click(self, x:int, y:int) -> None:
        pad=self.small_font//2
        if x>=self.table_ai_button_pos[0]-pad and x<=self.table_ai_button_pos[0]+self.small_font*6+pad and y>=self.table_ai_button_pos[1]-pad and y<=self.table_ai_button_pos[1]+self.small_font+pad:
            self.playing=GAME
            self.ai_type=TABLE
            self.time=time.time()
            self.draw_queue=True
        else:
            study=0
            file=""
            if x>=self.reinforcement_ai_button_pos[0]-pad and x<=self.reinforcement_ai_button_pos[0]+self.small_font*6+pad and y>=self.reinforcement_ai_button_pos[1]-pad and y<=self.reinforcement_ai_button_pos[1]+self.small_font+pad:
                self.playing=GAME
                self.time=time.time()
                self.ai_type=REI1
                file="q_table1.pkl"
                self.draw_queue=True
            elif x>=self.reinforcement_ai_2_button_pos[0]-pad and x<=self.reinforcement_ai_2_button_pos[0]+self.small_font*6+pad and y>=self.reinforcement_ai_2_button_pos[1]-pad and y<=self.reinforcement_ai_2_button_pos[1]+self.small_font+pad:
                self.playing=GAME
                self.time=time.time()
                self.ai_type=REI2
                file="q_table2.pkl"
                self.draw_queue=True
            with open(file, "rb") as f:
                self.q_table, study=pickle.load(f)

    def game_click(self, x:int, y:int) -> None:
        pad=self.small_font//2
        if x>=self.grid and x<=self.grid*9 and y>=self.grid and y<=self.grid*9:
            x-=self.grid
            y-=self.grid
            if x!=0:
                x//=self.grid
            if y!=0:
                y//=self.grid
            if self.putable_bool[y][x]:
                if self.black_turn:
                    self.board[y][x]=1
                else:
                    self.board[y][x]=-1
                for i in range(8):
                    for j in range(1, self.putable_list[y][x][i]+1):
                        self.board[y+j*self.dist[i][1]][x+j*self.dist[i][0]]=-self.board[y+j*self.dist[i][1]][x+j*self.dist[i][0]]
                self.black_turn=not self.black_turn
                self.draw_queue=True
                self.turn_number+=1
                self.calc_putable()
                self.b, self.sum[0], self.sum[1]=self.end_check()
                    
        elif x>=self.pass_button_pos[0]-pad and x<=self.pass_button_pos[0]+self.small_font*2+pad and y>=self.pass_button_pos[1]-pad and y<=self.pass_button_pos[1]+self.small_font+pad:
            self.black_turn=not self.black_turn
            if self.turn_number==self.last_pass+1:
                self.playing=END
                self.draw_queue=True
            else:
                self.last_pass=self.turn_number
                self.turn_number+=1
                self.draw_queue=True
                self.calc_putable()
                self.b, self.sum[0], self.sum[1]=self.end_check()
            
        if not self.second_player and not self.black_turn:
            self.ai()

    def calc_putable(self):
        self.pass_able=True
        stone=-1
        self.putable_list=[[[0 for i in range(8)]for j in range(8)]for k in range(8)]
        self.putable_bool=[[False for i in range(8)]for j in range(8)]
        if self.black_turn:
            stone=-stone
        for i in range(8):
            for j in range(8):
                if self.board[j][i]==0:
                    for k in range(8):
                        en_count=0
                        for l in range(1, 8):
                            if i+l*self.dist[k][0]<0 or i+l*self.dist[k][0]>=8 or j+l*self.dist[k][1]<0 or j+l*self.dist[k][1]>=8:break
                            if self.board[j+l*self.dist[k][1]][i+l*self.dist[k][0]]==stone:
                                if en_count>0:
                                    self.putable_list[j][i][k]=en_count
                                    self.putable_bool[j][i]=True
                                    self.pass_able=False
                                break
                            elif self.board[j+l*self.dist[k][1]][i+l*self.dist[k][0]]==-stone:
                                en_count+=1
                            else:break

    def end_check(self) -> tuple:
        black=0
        white=0
        k=0
        b=False
        for i in range(8):
            for j in range(8):
                if self.board[j][i]==-1:
                    white+=1
                elif self.board[j][i]==1:
                    black+=1
                else:
                    k+=1
        if black==0 or white==0 or k==0:
            b=True
        return (b, black, white)

    def ai(self) -> None:
        x=0
        y=0
        if self.pass_able:
            self.black_turn=not self.black_turn
            if self.turn_number==self.last_pass+1:
                self.playing=END
                self.draw_queue=True
            else:
                self.last_pass=self.turn_number
                self.turn_number+=1
                self.draw_queue=True
                self.calc_putable()
                self.b, self.sum[0], self.sum[1]=self.end_check()
        else:
            if self.ai_type==TABLE:
                x, y=self.table()
            else:
                x, y=self.reinforcement()
            self.game_click(self.grid*(x+1), self.grid*(y+1))

    def table(self) -> tuple:
        reverse_sum=[[0 for i in range(8)]for j in range(8)]
        value=[[-10000 for i in range(8)]for j in range(8)]
        for i in range(8):
            for j in range(8):
                reverse_sum[j][i]=sum(self.putable_list[j][i])
        func=[
            [100, -20,  10,   5,   5,  10, -20, 100],
            [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
            [ 10,  -2,   1,   1,   1,   1,  -2,  10],
            [  5,  -2,   1,   0,   0,   1,  -2,   5],
            [  5,  -2,   1,   0,   0,   1,  -2,   5],
            [ 10,  -2,   1,   1,   1,   1,  -2,  10],
            [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
            [100, -20,  10,   5,   5,  10, -20, 100]]
        for i in range(8):
            for j in range(8):
                if self.putable_bool[j][i]:
                    if i==1 and self.board[j][i+1]==1 or i==6 and self.board[j][i-1]==1 or j==1 and self.board[j+1][i]==1 or j==6 and self.board[j-1][i]==1:
                        value[j][i]=-20+reverse_sum[j][i]
                    else:
                        value[j][i]=func[j][i]+reverse_sum[j][i]
        x, y=0, 0
        m=-10000
        for i in range(8):
            for j in range(8):
                if m<value[j][i]:
                    m=value[j][i]
                    x=i
                    y=j
        return x, y

    def to_string(self, board:list) -> str:
        return "".join(str(cell if cell!=-1 else 2) for row in board for cell in row)

    def reinforcement(self) -> tuple:
        x=0
        y=0
        a=self.to_string(self.board)
        if random.random()<self.epsilon:
            x, y=self.random()
        else:
            legal_action=[(x, y) for x in range(8) for y in range(8) if self.putable_bool[y][x]]
            q_values=[(action, self.q_table.get((a, action), 0.0)) for action in legal_action]
            max_q=max(q_values, key=lambda x:x[1])[1]
            best_actions=[action for action, q in q_values if q==max_q]
            x, y=random.choice(best_actions)
        return x, y

    def random(self) -> tuple:
        x=0
        y=0
        while 1:
            x=random.randint(0, 7)
            y=random.randint(0, 7)
            if self.putable_bool[y][x]:
                break
        return x, y

if __name__=="__main__":
    g=Game()
