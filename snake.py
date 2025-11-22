import pygame
import random
import os, sys

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath("."), relative)
def hide_exception(exctype, value, traceback):
    pass

sys.excepthook = hide_exception

# Khởi tạo Pygame
pygame.init()
info = pygame.display.Info()
width = info.current_w
height = info.current_h
# Cài đặt màn hình
screen_width = width
screen_height = height
screen = pygame.display.set_mode((screen_width,screen_height),pygame.NOFRAME)
pygame.display.set_caption("Snake v1.0.1")

# Màu sắc
black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
yellow = (255, 255, 0)
sc = white

# Kích thước khối
block_size = 20

# Khởi tạo phông chữ
font = pygame.font.SysFont(None, 50)
point_font = pygame.font.SysFont(None, 55, bold=True)
title_font = pygame.font.SysFont(None, 100, bold=True)


def message(msg, color, x, y):
    mesg = font.render(msg, True, color)
    screen.blit(mesg, [x, y])

# --- HÀM VẼ THÔNG BÁO ĐIỂM ---
def draw_floating_message(screen, msg, position, color, alpha):
    """Vẽ thông báo điểm với độ trong suốt (alpha) nhất định."""
    temp_surface = point_font.render(msg, True, color)
    temp_surface.set_alpha(alpha)
    screen.blit(temp_surface, position)



def main_menu():

    speed_options_data = [
        ("EASY (3)", 3, green),
        ("MEDIUM (5)", 5, yellow),
        ("HARD (7)", 7, red),
        ("VERY HARD (14)", 14, (160,0,0)),
        ("SUPERIOR (25)", 25, (130,0,20)),
        ("INSANITY (60, try to survive)", 60, (153,0,255)),
        ("DIE BRO (???)", 600, (0,0,0)),
        ("Quit",None,(220,121,0))
    ]

    # Danh sách riêng biệt để lưu trữ các Rect (chỉ 1 giá trị)
    speed_rects = []
    
    # Tính toán vị trí menu
    start_y = screen_height / 3 + 50
    spacing = 60
    
    running = True
    while running:
        screen.fill(black)
        
        # Tiêu đề
        title_text = title_font.render("SNAKE GAME", True, green)
        title_rect = title_text.get_rect(center=(screen_width / 2, screen_height / 4 - 65))
        screen.blit(title_text, title_rect)
        
        # Hướng dẫn
        message("Select Speed:", white, screen_width / 2 - 110, start_y - 130)

        # Vòng lặp 1: Vẽ và lưu Rect
        speed_rects.clear() # Đảm bảo danh sách Rect được làm mới mỗi vòng lặp
        for i, (label, speed, color) in enumerate(speed_options_data):
            y_pos = start_y + i * spacing
            text = font.render(label, True, color)
            rect = text.get_rect(center=(screen_width / 2, y_pos - 65))
            screen.blit(text, rect)
            
            # Chỉ lưu đối tượng Rect
            speed_rects.append(rect) 

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Vòng lặp 2: Kiểm tra click. Lặp qua các Rect đã lưu
                for i, rect in enumerate(speed_rects):
                    if rect.collidepoint(mouse_pos):
                        # Lấy tốc độ từ danh sách data ban đầu bằng index 'i'
                        selected_speed = speed_options_data[i][1]

                        gameLoop(selected_speed) # Bắt đầu trò chơi với tốc độ đã chọn
                        return selected_speed

# ------------------------------------


def gameLoop(snake_speed): 
    game_over = False
    game_close = False


    # Vị trí đầu rắn
    x1 = screen_width / 2
    y1 = screen_height / 2

    # Thay đổi tọa độ
    x1_change = 0
    y1_change = 0

    # Danh sách các khối rắn
    snake_list = []
    length_of_snake = 1

    # --- BIẾN TRẠNG THÁI CHO HIỆU ỨNG ---
    points_message_active = False
    points_message_start_time = 0
    message_duration = 1000 # Thời gian hiển thị (ms)
    message_position = (0, 0)
    # ---------------------------------------------
    
    # Vị trí thức ăn
    def generate_food_location():
        food_x = round(random.randrange(0, screen_width - block_size) / block_size) * block_size
        food_y = round(random.randrange(0, screen_height - block_size) / block_size) * block_size
        return food_x, food_y

    food_x, food_y = generate_food_location()

    clock = pygame.time.Clock()

    # --- Tải và xử lý hình ảnh ---
    try:
        # Giả sử các file ảnh 'snake-head.jpg', 'snake-skin.jpg', 'apple.jpg' tồn tại
        snake_head_img = pygame.image.load(resource_path('snake-head.jpg')).convert_alpha()
        snake_head_img = pygame.transform.scale(snake_head_img, (block_size, block_size))

        snake_body_img = pygame.image.load(resource_path('snake-skin.jpg')).convert_alpha()
        snake_body_img = pygame.transform.scale(snake_body_img, (block_size, block_size))

        food_img = pygame.image.load(resource_path('apple.jpg')).convert_alpha()
        food_img = pygame.transform.scale(food_img, (block_size, block_size))

    except pygame.error as e:
        print(f"Cannot load: {e}")
        print("No image.")
        return
    # -----------------------------

    while not game_over:

        while game_close == True:
            screen.fill(black)
            # THAY ĐỔI: Chuyển message thành hàm có tọa độ
            message("You lost! Press Q to Quit, M to Menu or R to Restart", red, screen_width / 7 + 10, screen_height / 2 - 25)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_m:
                        main_menu()
                    if event.key == pygame.K_r:
                        gameLoop(snake_speed)
                       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Logic điều khiển rắn (giữ nguyên)
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = block_size
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = block_size
                    x1_change = 0
                elif event.key == pygame.K_m:
                   main_menu()
                elif event.key == pygame.K_r:
                   gameLoop(snake_speed)
                
        # Cập nhật vị trí và vẽ (giữ nguyên)
        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        screen.fill(black)
        screen.blit(food_img, (food_x, food_y))

        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        for segment in snake_list:
            if segment == snake_head:
                screen.blit(snake_head_img, (segment[0], segment[1]))
            else:
                screen.blit(snake_body_img, (segment[0], segment[1]))

        # Hiển thị điểm số
        score = length_of_snake - 1
        score_text = font.render(f"DPC: {snake_speed}% | Speed: {snake_speed} | Score: {score} | M to Menu | R to Restart", True, sc)
        screen.blit(score_text, [0, 0])
        
        if points_message_active:
            time_elapsed = pygame.time.get_ticks() - points_message_start_time
            
            if time_elapsed < message_duration:
                alpha = 255 - int((time_elapsed / message_duration) * 255)
                y_pos = message_position[1] - (time_elapsed / 20) 
                
                draw_floating_message(
                    screen, 
                    "+2 points!", 
                    (message_position[0], y_pos), 
                    white, 
                    alpha
                )
            else:
                points_message_active = False 
        # ---------------------------------------------

        pygame.display.update()

        if x1 == food_x and y1 == food_y:
            # 1. Tạo vị trí thức ăn mới
            food_x, food_y = generate_food_location()
            while [food_x, food_y] in snake_list:
                food_x, food_y = generate_food_location()
           
            probability_of_bonus = snake_speed / 100.0
            
            # Giá trị cộng thêm khi ăn: +1 hoặc +2 (khi trúng X2)
            bonus_length = 1
            
            if random.random() < probability_of_bonus: 
                # X2 điểm (cộng 2 thay vì 1)
                bonus_length = 2
                
                # Kích hoạt thông báo +2 điểm
                points_message_active = True
                points_message_start_time = pygame.time.get_ticks()
                message_position = (food_x, food_y) 
                
            # 3. Cập nhật độ dài rắn
            length_of_snake += bonus_length 

        clock.tick(snake_speed) # Dùng biến snake_speed để kiểm soát tốc độ

    pygame.quit()
    quit()

try:
    main_menu()
except:
    pass