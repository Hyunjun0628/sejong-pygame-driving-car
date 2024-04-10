import pygame
import os
import math
import sys
from collections import deque

# 화면 크기 정의
screen_width = 1500
screen_height = 800

# 자동차 클래스
class Car:
    def __init__(self):
        # 자동차의 이미지를 로드하고 크기를 조정
        self.surface = pygame.image.load(os.path.join("C:\\Users\\junzz\\OneDrive\\Desktop\\과제1\\Assets", "car1.png"))
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface  # 회전된 이미지를 저장할 변수
        self.pos = [1300, 600]  # 자동차의 초기위치
        self.angle = 90  # 초기 각도
        self.speed = 0.01  # 초기 속도
        self.center = [self.pos[0] + 50, self.pos[1] + 50]  # 자동차 중심의 좌표
        self.radars = []  # 레이더를 저장할 리스트
        self.is_alive = True  # 생존 여부
        self.radar_left90 = deque([100, 100]) #선입 선출 자료구조를 위해 큐로 레이더 값 저장.
        self.radar_left45 = deque([100, 100])
        self.radar_center = deque([100, 100])
        self.radar_right45 = deque([100, 100])
        self.radar_right90 = deque([100, 100])

    # 자동차를 그림
    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)

    # 레이더를 그리는 메서드
    def draw_radar(self, screen):
        for radar in self.radars:
            start_pos, end_pos = radar
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), end_pos, 5)

    # 레이더 길이 표시
    def draw_radar_length(self, screen):
        font = pygame.font.Font(None, 40)  # None으로 지정하여 기본 폰트를 사용하고, 크기를 40으로 설정
        for radar in self.radars:
            start_pos, end_pos = radar
            length = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)  # 레이더 길이 계산
            text = font.render(str(int(length)), True, (255,0,0))  # 길이를 문자열로 변환하여 텍스트 생성
            screen.blit(text, (end_pos[0] + 5, end_pos[1] + 5))  # 화면에 길이 표시 , 숫자의 위치

    # 이미지를 회전시키는 함수
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    # 레이더 업데이트
    def update_radar(self, map):
        self.radars.clear()
        for degree in range(-90, 120, 45):
            start_pos = self.center
            # 레이더의 끝점 초기화
            end_pos = self.center
            len = 0
            # 벽면에 닿을 때까지 거리를 계산
            while not map.get_at((int(end_pos[0]), int(end_pos[1]))) == (0, 0, 0, 255) and len < 2000:
                len += 1
                end_pos = [
                    int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len),
                    int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
                ]
            length = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)  # 레이더 길이 계산
            self.radars.append((start_pos, end_pos))
            if degree == -90: #시작할 때 기준 -y축 방향(우측)
                self.radar_right90.append(length)
                self.radar_right90.popleft()

            elif degree == -45: #시작할 때 기준 y = -x 방향(대각 우측)
                self.radar_right45.append(length)
                self.radar_right45.popleft()

            elif degree == 0: #시작할 때 기준 +x축 방향(정면)
                self.radar_center.append(length)
                self.radar_center.popleft()

            elif degree == 45: #시작할 때 기준 y = x 방향(대각 좌측)
                self.radar_left45.append(length)
                self.radar_left45.popleft()

            elif degree == 90: #시작할 때 기준 +y축 방향(좌측)
                self.radar_left90.append(length)
                self.radar_left90.popleft()

    #차량 제어 알고리즘
    def control(self):
        
        #전방 거리 기준 속도 가감속
        if self.radar_center[1] > 250 or self.radar_center[0] > 200:
            self.speed += 0.1
        elif self.radar_center[1] < 250:
            while self.speed > 10:
                self.speed -= 0.1
        elif self.radar_center[1] < 50:
            while self.speed > 10:
                self.speed -= 0.1
        
        #한 레이더에서 측정한 값을 서로 비교하여 큰 차이를 보이는 레이더 판별 방식
        #각 코너를 최단거리로 이동하기에 수월할 듯.
        if abs(self.radar_left45[0] - self.radar_left45[1]) > 30:
            while abs(self.radar_left45[0] - self.radar_left45[1]) < -5:
                self.angle += 10
        
        if abs(self.radar_right45[0] - self.radar_right45[1]) > 30:
            while abs(self.radar_right45[0] - self.radar_right45[1]) < -5:
                self.angle -= 10

        #if abs(self.radar_left90[0] - self.radar_left90[1]) > 30:
        #     while abs(self.radar_left90[0] - self.radar_left90[1]) < 5:
        #         self.angle += 10
        
        #if abs(self.radar_right90[0] - self.radar_right90[1]) > 30:
        #     while abs(self.radar_right90[0] - self.radar_right90[1]) < 5:
        #         self.angl -= 10

        #대각선의 레이더 값들이 늘어날 때 기준
        if abs(self.radar_left45[1] - self.radar_right45[1]) > 50:
            if self.radar_left45[1] > self.radar_right45[1]:
                self.angle += 10
            else:
                self.angle -= 10

        # 급커브 인지
        if abs(self.radar_left90[1] - self.radar_right90[1]) > 20:
            if self.radar_left90[1] > self.radar_right90[1]:
                self.angle += 5
            else:
                self.angle -= 5

        #끝에 도달시 유턴
        if self.radar_center[1] < 100 and self.radar_center[0] < 100:
           if self.radar_left45[1] < 160 and self.radar_right45[1] < 160 and self.radar_left45[0] < 160 and self.radar_right45[0] < 160:
               self.speed = 3
               if self.angle > 200:
                   while self.angle > 90:
                       self.angle -= 40
               if self.angle < -80:
                   while self.angle < 90:
                       self.angle += 40




    # 자동차 업데이트
    def update(self, map):
        #self.angle += 1
        Car.control(self)

        # 자동차의 새로운 위치 계산
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        # 자동차의 중심 좌표 업데이트
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        # 회전된 이미지 업데이트
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        # 레이더 업데이트
        self.update_radar(map)

# 메인 함수
def main():
    # 파이    # 게임 초기화
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    map = pygame.image.load(os.path.join("C:\\Users\\junzz\\OneDrive\\Desktop\\과제1\\Assets", "task1_map.png"))

    # 자동차 객체 생성
    car = Car()

    # 메인 루프
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 게임 객체 업데이트
        car.update(map)

        # 화면 그리기
        screen.blit(map, (0, 0))
        car.draw(screen)
        car.draw_radar(screen)
        car.draw_radar_length(screen)

        # 화면 업데이트
        pygame.display.flip()
        clock.tick(100)

    # 게임 종료
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
