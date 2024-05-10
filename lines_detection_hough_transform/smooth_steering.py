import cv2
import numpy as np

# 이전 프레임의 조향각 값을 저장할 배열
prev_steering_angles = []

# 부드러운 조향각을 계산하는 함수
def smooth_steering_angle(steering_angle, window_size=10):
    global prev_steering_angles
    
    # 현재 조향각 값을 배열에 추가
    prev_steering_angles.append(steering_angle)
    
    # 배열의 길이가 윈도우 크기를 초과하면 가장 오래된 값을 제거
    if len(prev_steering_angles) > window_size:
        prev_steering_angles.pop(0)
    
    # 배열의 모든 값의 평균을 계산하여 부드러운 조향각 반환
    smooth_angle = np.mean(prev_steering_angles)
    return smooth_angle

def calculate_steering_angle(frame, lines):
    if lines is None:
        return 0, frame.shape[1] // 2, 0, 0  # 차선이 검출되지 않았다면 조향각을 0으로 설정하고 화면 중앙을 반환
    
    height, width = frame.shape[:2]
    left_line, right_line = [], []
    
    for line in lines:
        for x1, y1, x2, y2 in line:
            parameters = np.polyfit((x1, x2), (y1, y2), 1)  # 직선의 파라미터 추정
            slope = parameters[0]
            intercept = parameters[1]
            if slope < -0.5:  # 왼쪽 차선
                left_line.append((slope, intercept, x1, x2))
            elif slope > 0.5:  # 오른쪽 차선
                right_line.append((slope, intercept, x1, x2))

    if not left_line or not right_line:
        return 0, width // 2, 0, 0  # 한 쪽 차선만 검출된 경우

    # 각 차선의 중앙 위치 계산
    left_line_center = np.mean([line[2] + (line[3] - line[2]) / 2 for line in left_line], axis=0)
    right_line_center = np.mean([line[2] + (line[3] - line[2]) / 2 for line in right_line], axis=0)

    line_center_x = int((left_line_center + right_line_center) / 2)
    center_offset = width / 2 - line_center_x
    steering_angle = center_offset / width * 90  # 최대 +-45도 각도로 조정
    
    # 좌측 라인과 우측 라인 각각에 대한 직선과의 거리 계산
    left_line_distance = width / 2 - left_line_center
    right_line_distance = right_line_center - width / 2

    return steering_angle, line_center_x, left_line_distance, right_line_distance

def display_heading_line(frame, steering_angle, line_center_x, left_line_distance, right_line_distance):
    height, width, _ = frame.shape

    # 조향각 값 표시
    cv2.putText(frame, f"Steering Angle: {steering_angle:.2f} degrees", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # 직선 표시
    cv2.line(frame, (line_center_x, 0), (line_center_x, height), (0, 0, 255), 2)

    # 좌측 라인과 직선 사이의 거리 및 우측 라인과 직선 사이의 거리 표시
    cv2.putText(frame, f"Left Line Distance: {left_line_distance:.2f} pixels", (width - 400, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Right Line Distance: {right_line_distance:.2f} pixels", (width - 400, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # 화면에 조향선 그리기
    x1 = line_center_x
    y1 = height
    x2 = int(x1 - height / 2 * np.tan(np.radians(steering_angle)))
    y2 = int(height / 2)
    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
    return frame

# 비디오 파일 열기
video = cv2.VideoCapture("road_car2_view.mp4")

while True:
    ret, frame = video.read()
    if not ret:
        break

    height, width = frame.shape[:2]
    roi = frame[int(height * 0.6):height, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, maxLineGap=50)

    steering_angle, line_center_x, left_line_distance, right_line_distance = calculate_steering_angle(frame, lines)
    smooth_angle = smooth_steering_angle(steering_angle)
    
    frame_with_heading = display_heading_line(frame, smooth_angle, line_center_x, left_line_distance, right_line_distance)

    cv2.imshow('Frame with Heading', frame_with_heading)
    cv2.imshow("edges", edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
