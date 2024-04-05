import pygame   # pygame 라이브러리를 임포트합니다.
import os       # 파일 경로 등 시스템과 관련된 기능을 사용하기 위해 os 라이브러리를 임포트합니다.
import math     # 수학적 계산(예: 삼각함수)을 위해 math 라이브러리를 임포트합니다.
import sys      # 시스템과 관련된 기능을 사용하기 위해 sys 라이브러리를 임포트합니다.
import neat     # NEAT(NeuroEvolution of Augmenting Topologies) 알고리즘을 사용하기 위해 neat 라이브러리를 임포트합니다.

SCREEN_WIDTH = 1244     # 화면의 너비를 정의합니다.
SCREEN_HEIGHT = 1016    # 화면의 높이를 정의합니다.
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 게임 화면의 크기를 설정합니다.

TRACK = pygame.image.load(os.path.join("Assets", "track.png"))  # 트랙 이미지를 불러옵니다.


class Car(pygame.sprite.Sprite):  # 자동차를 나타내는 클래스를 정의합니다. pygame의 Sprite 클래스를 상속받습니다.
    def __init__(self):
        super().__init__()                                                          # Sprite 클래스의 생성자를 호출합니다.
        self.original_image = pygame.image.load(os.path.join("Assets", "car.png"))  # 자동차 이미지를 불러옵니다.
        self.image = self.original_image                                            # 현재 이미지를 원본 이미지로 초기화합니다.
        self.rect = self.image.get_rect(center=(490, 820))                          # 이미지의 위치 및 크기 정보를 담는 rect 객체를 초기화합니다.
        self.vel_vector = pygame.math.Vector2(0.8, 0)                               # 자동차의 속도 및 방향을 나타내는 벡터를 초기화합니다.
        self.angle = 0                                                              # 자동차의 현재 각도를 나타냅니다.
        self.rotation_vel = 5                                                       # 자동차가 회전하는 속도를 나타냅니다.
        self.direction = 0                                                          # 자동차의 방향을 나타냅니다. 1은 오른쪽, -1은 왼쪽, 0은 직진입니다.
        self.alive = True                                                           # 자동차의 생존 상태를 나타냅니다.
        self.radars = []                                                            # 레이더(환경 감지 센서) 데이터를 저장할 리스트입니다.

    def update(self):
        self.radars.clear()                         # 레이더 데이터를 초기화합니다.
        self.drive()                                # 자동차를 이동시킵니다.
        self.rotate()                               # 자동차를 회전시킵니다.
        for radar_angle in (-60, -30, 0, 30, 60):   # 다양한 각도로 레이더를 설정합니다.
            self.radar(radar_angle)                 # 레이더를 사용하여 환경을 감지합니다.
        self.collision()                            # 충돌을 체크합니다.
        self.data()                                 # NEAT 알고리즘 입력 데이터를 준비합니다.

    def drive(self):
        self.rect.center += self.vel_vector * 6     # 현재 속도 및 방향에 따라 자동차의 위치를 업데이트합니다.

    def collision(self):
        length = 40                                 # 충돌 감지를 위한 거리를 설정합니다.
        # 충돌 감지 포인트(자동차의 오른쪽 및 왼쪽 앞부분)를 계산합니다.
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

    # 충돌이 발생하면 자동차를 '죽은' 상태로 설정합니다.
        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False

    # 충돌 포인트를 화면에 표시합니다. (디버깅용)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)

    def rotate(self):
        # 방향에 따라 자동차를 회전시키고, 속도 벡터의 방향을 조정합니다.
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        # 자동차 이미지를 현재 각도에 맞게 회전시킵니다.
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):
        # 레이더(환경 감지 센서) 기능을 구현합니다. 레이더는 자동차 앞의 특정 각도에서 장애물까지의 거리를 측정합니다.
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        # 레이더가 장애물(트랙의 경계)을 감지할 때까지, 또는 최대 거리에 도달할 때까지 레이더를 연장합니다.
        while not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 200:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # 레이더 선과 감지된 포인트를 화면에 표시합니다. (디버깅용)
        pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

        # 레이더가 감지한 거리를 계산하고 저장합니다.
        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                            + math.pow(self.rect.center[1] - y, 2)))
        self.radars.append([radar_angle, dist])

    def data(self):
        # NEAT 알고리즘의 입력으로 사용될 데이터를 준비합니다. 여기서는 레이더가 감지한 거리들입니다.
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input
    
def remove(index):
    cars.pop(index)     # 자동차 리스트에서 해당 인덱스의 자동차를 제거합니다.
    ge.pop(index)       # 해당 인덱스의 게놈(genome)을 제거합니다.
    nets.pop(index)     # 해당 인덱스의 신경망을 제거합니다.

def eval_genomes(genomes, config):
    global cars, ge, nets  # 전역 변수로 cars, ge, nets를 사용합니다.

    cars = []       # 자동차 객체를 저장할 리스트입니다.
    ge = []         # 게놈 객체를 저장할 리스트입니다.
    nets = []       # 신경망 객체를 저장할 리스트입니다.

# genomes 리스트에 있는 각 게놈(genome)에 대해 실행합니다.
    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))           # 각 게놈에 대한 자동차 객체를 생성하고 cars 리스트에 추가합니다.
        ge.append(genome)                                       # 게놈 리스트에 게놈을 추가합니다.
        net = neat.nn.FeedForwardNetwork.create(genome, config) # 게놈과 설정을 바탕으로 신경망을 생성합니다.
        nets.append(net)                                        # 신경망 리스트에 신경망을 추가합니다.
        genome.fitness = 0                                      # 각 게놈의 초기 피트니스 점수를 0으로 설정합니다.

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()                               # Pygame을 종료합니다.
                sys.exit()                                  # 프로그램을 종료합니다.

        SCREEN.blit(TRACK, (0, 0))                          # 트랙 이미지를 화면에 그립니다.

        if len(cars) == 0:                                  # 모든 자동차가 '죽었으면' 루프를 종료합니다.
            break

        for i, car in enumerate(cars):
            ge[i].fitness += 1                              # 생존해 있는 각 자동차의 피트니스 점수를 1씩 증가시킵니다.
            if not car.sprite.alive:
                remove(i)                                   # '죽은' 자동차를 제거합니다.

        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())    # 신경망을 사용해 입력 데이터를 바탕으로 출력값을 계산합니다.
            # 출력값에 따라 자동차의 방향을 결정합니다.
            if output[0] > 0.7:
                car.sprite.direction = 1  # 오른쪽으로 회전합니다.
            if output[1] > 0.7:
                car.sprite.direction = -1  # 왼쪽으로 회전합니다.
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0  # 직진합니다.

        # 모든 자동차를 업데이트하고 화면에 그립니다.
        for car in cars:
            car.draw(SCREEN)
            car.update()
        pygame.display.update()  # 화면을 업데이트합니다.

def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet, 
        neat.DefaultStagnation,
        config_path)  # NEAT 설정 파일을 로드합니다.

    pop = neat.Population(config)  # 설정에 따라 NEAT 인구를 생성합니다.

    pop.add_reporter(neat.StdOutReporter(True)) # 진행 상황을 콘솔에 보고합니다.
    stats = neat.StatisticsReporter()           # 통계 정보를 수집합니다.
    pop.add_reporter(stats)                     # 통계 리포터를 추가합니다.

    pop.run(eval_genomes, 50)  
    # NEAT 알고리즘을 실행합니다. 여기서는 eval_genomes 함수를 사용하여 각 세대(genome)의 피트니스를 평가하고, 총 50세대에 걸쳐 진화를 시킵니다.
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)               # 현재 파일의 디렉토리 경로를 가져옵니다.
    config_path = os.path.join(local_dir, 'config.txt') # NEAT 설정 파일의 경로를 구성합니다.
    run(config_path)                                    # 위에서 정의한 run 함수를 호출하여, NEAT 알고리즘을 사용한 학습 프로세스를 시작합니다.