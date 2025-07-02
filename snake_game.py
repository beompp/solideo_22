import pygame
import random
import sys


# 파이게임 라이브러리 초기화
pygame.init()

# 색상 정의 (RGB 튜플)
BLACK = (0, 0, 0)       # 배경색
WHITE = (255, 255, 255) # 텍스트 등
RED = (255, 0, 0)       # 음식 색
GREEN = (0, 255, 0)     # 지렁이 색

# 게임 설정값
WINDOW_WIDTH = 800      # 창 가로 크기
WINDOW_HEIGHT = 600     # 창 세로 크기
BLOCK_SIZE = 20         # 지렁이/음식 한 칸 크기
GAME_SPEED = 15         # 프레임 속도 (숫자가 클수록 빠름)

# 화면 및 시계 객체 생성
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # 게임 창 생성
pygame.display.set_caption('지렁이 게임')                       # 창 제목
clock = pygame.time.Clock()                                    # FPS 제어용


# 지렁이(스네이크) 클래스
class Snake:
    def __init__(self):
        # 지렁이 몸통 좌표 리스트 (처음엔 화면 중앙에 1칸)
        self.body = [(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)]
        self.direction = 'RIGHT'      # 현재 이동 방향
        self.change_to = self.direction # 입력받은 다음 방향

    # 방향 전환 처리 (반대 방향으로는 못감)
    def change_direction(self):
        if self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'
        elif self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'

    # 지렁이 이동 (머리 방향으로 한 칸 추가)
    def move(self):
        x, y = self.body[0]
        if self.direction == 'RIGHT':
            x += BLOCK_SIZE
        elif self.direction == 'LEFT':
            x -= BLOCK_SIZE
        elif self.direction == 'UP':
            y -= BLOCK_SIZE
        elif self.direction == 'DOWN':
            y += BLOCK_SIZE
        self.body.insert(0, (x, y)) # 머리를 앞으로 추가

    # 성장(길이 증가) 함수 (move에서 이미 머리가 추가되므로 별도 처리 필요 없음)
    def grow(self):
        pass

    # 벽 또는 자기 몸과 충돌했는지 확인
    def check_collision(self):
        x, y = self.body[0]
        return (
            x < 0 or x >= WINDOW_WIDTH or # 벽 충돌
            y < 0 or y >= WINDOW_HEIGHT or
            (x, y) in self.body[1:]       # 자기 몸 충돌
        )


# 음식 클래스
class Food:
    def __init__(self):
        self.position = self.generate_position() # 음식 위치 생성

    # 음식 위치를 무작위로 생성 (지렁이와 겹칠 수 있음)
    def generate_position(self):
        x = random.randrange(0, WINDOW_WIDTH, BLOCK_SIZE)
        y = random.randrange(0, WINDOW_HEIGHT, BLOCK_SIZE)
        return (x, y)

    # 음식 위치를 새로 생성
    def respawn(self):
        self.position = self.generate_position()


# 메인 게임 루프 함수
def main():
    snake = Snake()      # 지렁이 객체 생성
    food = Food()        # 음식 객체 생성
    game_over = False    # 게임 오버 여부
    score = 0            # 점수

    while True:
        # 이벤트 처리 (키보드, 창 닫기 등)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    snake.change_to = 'RIGHT' # 오른쪽 방향키
                elif event.key == pygame.K_LEFT:
                    snake.change_to = 'LEFT'  # 왼쪽 방향키
                elif event.key == pygame.K_UP:
                    snake.change_to = 'UP'    # 위쪽 방향키
                elif event.key == pygame.K_DOWN:
                    snake.change_to = 'DOWN'  # 아래쪽 방향키
                elif event.key == pygame.K_r and game_over:
                    # 게임 재시작 (R키)
                    snake = Snake()
                    food = Food()
                    game_over = False
                    score = 0

        if not game_over:
            snake.change_direction() # 방향 전환
            snake.move()             # 이동

            # 음식 먹었는지 확인
            if snake.body[0] == food.position:
                score += 1
                food.respawn()       # 음식 새로 생성
            else:
                snake.body.pop()    # 안 먹었으면 꼬리 제거

            # 충돌(벽/몸) 확인
            if snake.check_collision():
                game_over = True

        # 화면 그리기
        screen.fill(BLACK) # 배경
        
        # 지렁이 그리기
        for segment in snake.body:
            pygame.draw.rect(screen, GREEN, (*segment, BLOCK_SIZE, BLOCK_SIZE))
        
        # 음식 그리기
        pygame.draw.rect(screen, RED, (*food.position, BLOCK_SIZE, BLOCK_SIZE))

        # 점수 표시
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        # 게임 오버 메시지
        if game_over:
            game_over_text = font.render('Game Over! Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(game_over_text, text_rect)

        # 화면 업데이트 및 FPS 제어
        pygame.display.flip()
        clock.tick(GAME_SPEED)

# 프로그램 시작점
if __name__ == '__main__':
    main()
