# pygame 활용 radar 거리 감지를 이용한 단순 제어 차량 코드입니다
# 구동시 map.png 및 car.png 필요
# pygame 활용시, angle의 값을 정수로만 넣어주어도, 내부적으로 radian값으로 변환해주기때문에, 과정이 생략가능

import pygame
import os
import math
import sys
import time

# 화면 크기를 정의합니다.
screen_width = 1500
screen_height = 800

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0

    def calculate(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.previous_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

# Car 클래스에 PIDController를 추가합니다.

# 자동차 클래스입니다.
class Car:
    def __init__(self):
        # 자동차 이미지를 로드하고 크기를 조정합니다.
        self.surface = pygame.image.load(os.path.join("C:\\Users\\junzz\\OneDrive\\Desktop\\과제1\\Assets", "car1.png"))
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface  # 회전된 이미지를 저장할 변수입니다.
        self.pos = [1400, 500]  # 자동차의 초기 위치를 설정합니다.
        self.angle = 0  # 초기 각도를 설정합니다.
        self.speed = 0.01  # 초기 속도를 설정합니다.
        self.center = [self.pos[0] + 50, self.pos[1] + 50]  # 자동차 중심의 좌표를 계산합니다.
        self.radars = []  # 레이더 데이터를 저장할 리스트입니다.
        self.is_alive = True  # 자동차의 생존 여부를 나타냅니다.
        self.radar_len = [0, 0, 0, 0, 0]  # 레이더가 측정한 거리값을 저장할 리스트입니다.
        self.pid_controller = PIDController(kp=0.003, ki=0, kd=0)  # PID 계수는 실험을 통해 조절해야 합니다.
        self.last_hit_time = 0

    # 자동차를 화면에 그립니다.
    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)

    # 레이더를 화면에 그립니다.
    def draw_radar(self, screen):
        for radar in self.radars:
            start_pos, end_pos = radar
            pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 1)
            pygame.draw.circle(screen, (255, 0, 0), end_pos, 5)

    # 레이더 길이를 화면에 표시합니다.
    def draw_radar_length(self, screen):
        font = pygame.font.Font(None, 20)  # 폰트를 설정합니다.
        for radar in self.radars:
            start_pos, end_pos = radar
            # 레이더 길이를 계산합니다.
            length = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)
            # 길이를 문자열로 변환하여 텍스트 객체를 생성합니다.
            text = font.render(str(int(length)), True, (255, 0, 0))
            # 화면에 길이를 표시합니다.
            screen.blit(text, (end_pos[0] + 5, end_pos[1] + 5))

    # 이미지를 중심을 기준으로 회전시킵니다.
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    # 레이더를 업데이트합니다. 환경을 스캔하고 거리 데이터를 수집합니다.
    def update_radar(self, map):
        self.radars.clear()
        # 주변을 45도 간격으로 스캔합니다.
        for degree in range(-90, 120, 45):
            start_pos = self.center
            end_pos = self.center
            len = 0
            # 벽면에 닿을 때까지 거리를 증가시키면서 스캔합니다.
            while not map.get_at((int(end_pos[0]), int(end_pos[1]))) == (0, 0, 0, 255) and len < 2000:
                len += 1
                end_pos = [
                    int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len),
                    int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
                ]
            # 레이더 길이를 계산하고 저장합니다.
            length = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)
            self.radars.append((start_pos, end_pos))
            # 각도에 따라 적절한 리스트 인덱스에 거리값을 저장합니다.
            if degree == -90:
                self.radar_len[0] = length
            elif degree == -45:
                self.radar_len[1] = length
            elif degree == 0:
                self.radar_len[2] = length
            elif degree == 45:
                self.radar_len[3] = length
            elif degree == 90:
                self.radar_len[4] = length

    # 차량의 주행 제어 알고리즘을 구현합니다. 여기서는 속도 조절과 방향 조절을 합니다.
                
    
    def control(self):
        # 전방 레이더 거리에 따라 속도를 조절합니다.
        if self.radar_len[2] > 200:
            self.speed += 0.01
        elif self.radar_len[2] < 100:
            while self.speed > 15:
                self.speed -= 0.1
        elif self.radar_len[2] < 50:
            while self.speed > 0.05:
                self.speed -= 0.1
        
        # 차량이 도로의 중앙을 유지하도록 방향을 조절합니다.
        steering_angle = 0  # 조향각을 초기화합니다.
        if abs(self.radar_len[1] - self.radar_len[3]) > 20:
            if self.radar_len[1] > self.radar_len[3]:
                steering_angle -= 10  # 왼쪽으로 회전하는 경우
            else:
                steering_angle += 10  # 오른쪽으로 회전하는 경우

        # 급커브를 인지하여 방향을 조절합니다.
        if abs(self.radar_len[0] - self.radar_len[4]) > 50:
            if self.radar_len[0] > self.radar_len[4]:
                steering_angle -= 5  # 왼쪽으로 회전하는 경우
            else:
                steering_angle += 5  # 오른쪽으로 회전하는 경우

        # 도로의 중앙을 유지하도록 조향각을 제한합니다.
        max_steering_angle = 30  # 최대 조향각을 설정합니다.
        steering_angle = max(-max_steering_angle, min(steering_angle, max_steering_angle))

        # 각도를 조절합니다.
        self.angle += steering_angle
        
        # 도로의 중앙을 유지하도록 조향각을 계산합니다.
        # 중앙선을 유지하는 것을 목표로 설정합니다.
        setpoint = 0  # 중앙선에 위치하고 있다고 가정합니다.
        # measured_value는 왼쪽 레이더와 오른쪽 레이더 간의 거리 차이로, 중앙에서의 이탈 정도를 나타냅니다.
        measured_value = self.radar_len[1] - self.radar_len[3] 
        # PID 제어기로부터 조향각을 계산합니다.
        control_value = self.pid_controller.calculate(setpoint, measured_value)
        # 계산된 조향각으로 차량의 각도를 조정합니다.
        self.angle += control_value * 5

        if self.radar_len[2] < 50:  # 예를 들어, 전방 레이더 거리가 20 미만일 때 벽에 부딪혔다고 판단
            self.angle += 180  # 180도 회전
            if self.angle > 360:
                self.angle -= 360
            self.speed = 0.01  # 속도를 초기화 (또는 조정)


    # 자동차의 상태를 업데이트합니다. 위치, 각도 등을 업데이트합니다.
    def update(self, map):
        # control 함수를 호출하여 자동차를 제어합니다.
        self.control()
        # 자동차의 새로운 위치를 계산합니다.
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        # 자동차의 중심 좌표를 업데이트합니다.
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        # 회전된 이미지를 업데이트합니다.
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        # 레이더를 업데이트합니다.
        self.update_radar(map)

# 메인 함수입니다. 게임을 초기화하고 메인 루프를 실행합니다.
def main():
    # pygame을 초기화합니다.
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    # 맵 이미지를 로드합니다.
    map = pygame.image.load(os.path.join("C:\\Users\\junzz\\OneDrive\\Desktop\\과제1\\Assets", "task1_map.png"))

    # 자동차 객체를 생성합니다.
    car = Car()

    # 메인 루프를 실행합니다.
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 자동차를 업데이트합니다.
        car.update(map)

        # 화면에 객체들을 그립니다.
        screen.blit(map, (0, 0))
        car.draw(screen)
        car.draw_radar(screen)
        car.draw_radar_length(screen)

        # 화면을 업데이트합니다.
        pygame.display.flip()
        clock.tick(50)

    # 게임을 종료합니다.
    pygame.quit()
    sys.exit()

# 이 스크립트가 메인으로 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()



#다이나믹스를 알고리즘을 고려해야한다.
#delay의 존재를 고려면 시스템이 발산할 수 있다.
#무조건 빨리 가는 것이 좋은 알고리즘은 아닐 수 있다.
#Faze margin? -> 

#20 - 50 hz 정도가 Tu 주기가 될 수 있다/\. Tu = 0.1초 
#Tu를 구하는 방법: 1. /2.
#Rinux는 Realtime os가 아니다. thread 형식으로 처리가됨. 주기적으로 conrtol해도, 갑자기 일어날 수 있음
# delta t가 변하기때문에, 우리가 원하는 Tu를 구할 수 없다.
#이 떄, real time os를 구하는 Rinux 프로그램을 찾아서 구해야한다. 
#주행 control에는 os가 크게 의미가 없기때문에, 어떻게 돌아가느냐?에 대한 답... -> 개발시, interupt 혹은 timer를 사용하여 10초마다 한번씩 interupt가 걸리게끔 진행하게 개발
# 우리가 쓸 하드웨어는 os가 적용되어 있음. -> 이 때, 많이 쓰는 방법은 main 파일에 printf 혹은 시리얼 포트로 얼만큼 출력되냐에 따라 츨정후, delta t를 찾는다. 
#delta t(통신포트)를 찾는다. urat 혹은 serial로 넘겨준다. 이 때, 출력되는 정도로 delta t를 설정후, i gain과 D gain을 설정해준다. 
#I Gain은 0.01 
#slow in fast out 가속으로 시간


#과제 1 - 안정적으로 준비하기. - > 가속도에 limit을 부여해서 빠르게 가지 않도록/ 함수대신 look up table에 대한 제약.
# turn에 대한 delay를 주는 알고리즘을 넣어주어야 회전이 덜 빠르게 진행될 수 있다. 

#과제 2 - 대비 준비

