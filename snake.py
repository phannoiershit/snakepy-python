import pygame
import random
import os, sys
import json
import base64 # Import thư viện Base64
from pathlib import Path

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
pygame.display.set_caption("Snake v1.2")

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

# --- HÀM TẢI CÁC TÙY CHỌN TỐC ĐỘ TỪ TXT (BASE64 ENCODED JSON) ---
def load_speed_options():
    # Danh sách tốc độ MẶC ĐỊNH
    default_speed_options = [
        ("EASY (3)", 3, green),
        ("MEDIUM (5)", 5, yellow),
        ("HARD (7)", 7, red),
        ("VERY HARD (14)", 14, (160,0,0)),
        ("SUPERIOR (25)", 25, (130,0,20)),
        ("INSANITY (60, try to survive)", 60, (153,0,255)),
        ("DIE BRO (???)", 600, (0,0,0)),
    ]
    
    # Thêm tùy chọn Quit vào cuối danh sách tốc độ
    quit_option = ("Quit", None, (220,121,0))
    file_path = resource_path('customspeed.txt')

    if not Path(file_path).exists():
        print("Using default speed options (customspeed.txt not found).")
        return default_speed_options + [quit_option]

    try:
        # 1. Đọc nội dung tệp TXT (chứa chuỗi Base64)
        with open(file_path, 'r', encoding='utf-8') as f:
            base64_data = f.read().strip()
            
        # 2. Giải mã Base64
        try:
            json_bytes = base64.b64decode(base64_data)
        except base64.binascii.Error:
            print("Error: customspeed.txt contains invalid Base64 string. Using default options.")
            return default_speed_options + [quit_option]
            
        # 3. Chuyển Bytes thành chuỗi JSON
        json_string = json_bytes.decode('utf-8')
        
        # 4. Phân tích cú pháp JSON
        custom_data = json.loads(json_string)
                
        if isinstance(custom_data, list):
            processed_options = []
            for item in custom_data:
                try:
                    label = item.get("label", "Unknown")
                    speed = item.get("speed")
                    color_list = item.get("color", [255, 255, 255])
                    
                    if isinstance(speed, int) and len(color_list) == 3:
                        color_tuple = tuple(color_list)
                        processed_options.append((label, speed, color_tuple))
                except Exception as e:
                    print(f"Skipping invalid speed option in decoded JSON: {e}")
                    
            if processed_options:
                print("Loaded custom speed options from customspeed.txt (Base64 decoded).")
                return processed_options + [quit_option]

        print("Decoded JSON is not a valid list of speed options. Using default options.")
        return default_speed_options + [quit_option]
        
    except FileNotFoundError:
        # Trường hợp này đã được kiểm tra ở đầu hàm, nhưng giữ lại phòng ngừa.
        print("Using default speed options (customspeed.txt not found).")
        return default_speed_options + [quit_option]
    except json.JSONDecodeError:
        print("Error: Decoded data is not valid JSON format. Using default options.")
        return default_speed_options + [quit_option]
    except Exception as e:
        print(f"An unexpected error occurred while loading speed options: {e}. Using default options.")
        return default_speed_options + [quit_option]

def is_remote_collision(snake_x, snake_y, food_x, food_y, remote_blocks=4):
    """..."""
    dx = abs(snake_x - food_x)
    dy = abs(snake_y - food_y)

    # Kiểm tra hình vuông 4x4 (phạm vi X và Y đều tối đa là 4 khối)
    return (dx < block_size * remote_blocks) and (dy < block_size * remote_blocks)
def main_menu():
    
    # Tải tùy chọn tốc độ (từ TXT Base64 nếu có, hoặc mặc định)
    speed_options_data = load_speed_options()

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

                        if selected_speed is None: # Xử lý nút Quit
                            pygame.quit()
                            quit()
                        else:
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
    fxs,fys = generate_food_location()
    fxt,fyt = generate_food_location()
    fxf,fyf = generate_food_location()

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
                        game_close = False 
                        game_over = True 
                    if event.key == pygame.K_r:
                        gameLoop(snake_speed)
                        game_close = False 
                        game_over = True 
                       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Logic điều khiển rắn (giữ nguyên)
                if (event.key == pygame.K_LEFT or event.key ==  pygame.K_a) and x1_change == 0:
                    x1_change = -block_size
                    y1_change = 0
                elif (event.key == pygame.K_RIGHT or event.key ==  pygame.K_d) and x1_change == 0:
                    x1_change = block_size
                    y1_change = 0
                elif (event.key == pygame.K_UP or event.key ==  pygame.K_w) and y1_change == 0:
                    y1_change = -block_size
                    x1_change = 0
                elif (event.key == pygame.K_DOWN or event.key ==  pygame.K_s) and y1_change == 0:
                    y1_change = block_size
                    x1_change = 0
                elif event.key == pygame.K_m:
                   main_menu()
                   game_over = True 
                elif event.key == pygame.K_r:
                   gameLoop(snake_speed)
                   game_over = True 
                
        # Cập nhật vị trí và vẽ (giữ nguyên)
        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        screen.fill(black)
        screen.blit(food_img, (food_x, food_y))
        screen.blit(food_img, (fxs, fys))
        screen.blit(food_img, (fxt, fyt))
        screen.blit(food_img, (fxf, fyf))

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
        if is_remote_collision(x1, y1, food_x, food_y, remote_blocks=4):
            # 1. Tạo vị trí thức ăn 1 mới
            food_x, food_y = generate_food_location()
            while [food_x, food_y] in snake_list or ([food_x, food_y] == [fxs, fys]) or ([food_x, food_y] == [fxt, fyt]) or ([food_x, food_y] == [fxf, fyf]):
                food_x, food_y = generate_food_location()
            
            # --- Logic tính điểm/bonus ---
            probability_of_bonus = snake_speed / 100.0
            bonus_length = 1
            
            if random.random() < probability_of_bonus: 
                bonus_length = 2
                points_message_active = True
                points_message_start_time = pygame.time.get_ticks()
                message_position = (food_x, food_y) 
                
            # 2. Cập nhật độ dài rắn
            length_of_snake += bonus_length 

        # KIỂM TRA VA CHẠM VỚI THỨC ĂN 2 (fxs, fys)
        if is_remote_collision(x1, y1, fxs, fys, remote_blocks=4):
            # 1. Tạo vị trí thức ăn 2 mới
            fxs, fys = generate_food_location()
            # 💥 CẬP NHẬT: Kiểm tra cả food_x, fxt, VÀ fxf
            while [fxs, fys] in snake_list or ([fxs, fys] == [food_x, food_y]) or ([fxs, fys] == [fxt, fyt]) or ([fxs, fys] == [fxf, fyf]):
                fxs, fys = generate_food_location()
            
            # --- Logic tính điểm/bonus (Dành riêng cho Thức ăn 2) ---
            probability_of_bonus = snake_speed / 100.0
            bonus_length = 1
            
            if random.random() < probability_of_bonus: 
                bonus_length = 2
                points_message_active = True
                points_message_start_time = pygame.time.get_ticks()
                message_position = (fxs, fys) 
                
            # 2. Cập nhật độ dài rắn
            length_of_snake += bonus_length 
            
        # KIỂM TRA VA CHẠM VỚI THỨC ĂN 3 (fxt, fyt)
        if is_remote_collision(x1, y1, fxt, fyt, remote_blocks=4):
            # 1. Tạo vị trí thức ăn 3 mới
            fxt, fyt = generate_food_location()
            # 💥 CẬP NHẬT: Kiểm tra cả food_x, fxs, VÀ fxf
            while [fxt, fyt] in snake_list or ([fxt, fyt] == [fxs, fys]) or ([fxt, fyt] == [food_x, food_y]) or ([fxt, fyt] == [fxf, fyf]):
                fxt, fyt = generate_food_location()
        
            # --- Logic tính điểm/bonus (Dành riêng cho Thức ăn 3) ---
            probability_of_bonus = snake_speed / 100.0
            bonus_length = 1
            
            if random.random() < probability_of_bonus: 
                bonus_length = 2
                points_message_active = True
                points_message_start_time = pygame.time.get_ticks()
                message_position = (fxt, fyt)
                
            # 2. Cập nhật độ dài rắn
            length_of_snake += bonus_length 

        # 💥 THAY ĐỔI 3: KHỐI LOGIC VA CHẠM THỨC ĂN 4 (MỚI)
        if x1 == fxf and y1 == fyf:
            # 1. Tạo vị trí thức ăn 4 mới
            fxf, fyf = generate_food_location()
            # Đảm bảo thức ăn 4 không trùng với thân rắn hoặc bất kỳ thức ăn nào khác
            while [fxf, fyf] in snake_list or ([fxf, fyf] == [fxs, fys]) or ([fxf, fyf] == [food_x, food_y]) or ([fxf, fyf] == [fxt, fyt]):
                fxf, fyf = generate_food_location()
        
            # --- Logic tính điểm/bonus (Dành riêng cho Thức ăn 4) ---
            probability_of_bonus = snake_speed / 100.0
            bonus_length = 1
            
            if random.random() < probability_of_bonus: 
                bonus_length = 2
                points_message_active = True
                points_message_start_time = pygame.time.get_ticks()
                message_position = (fxf, fyf) # Sử dụng tọa độ thức ăn 4
                
            # 2. Cập nhật độ dài rắn
            length_of_snake += bonus_length 
            
        clock.tick(snake_speed)

try:
    main_menu()
except:
    pass
