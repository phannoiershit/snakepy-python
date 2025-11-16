import pygame
import random
import os, sys

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath("."), relative)


# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake")

# Màu sắc
black = (0, 0, 0)
red = (255, 0, 0)

# Kích thước khối
block_size = 20

# Tốc độ rắn
snake_speed = 5

# Khởi tạo phông chữ
font = pygame.font.SysFont(None, 50)

def message(msg, color):
    mesg = font.render(msg, True, color)
    screen.blit(mesg, [screen_width / 6, screen_height / 3])

def gameLoop():
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

    # Vị trí thức ăn
    def generate_food_location():
        food_x = round(random.randrange(0, screen_width - block_size) / block_size) * block_size
        food_y = round(random.randrange(0, screen_height - block_size) / block_size) * block_size
        return food_x, food_y

    food_x, food_y = generate_food_location()

    clock = pygame.time.Clock()

    # --- Tải và xử lý hình ảnh ---
    try:
        # Tải hình ảnh rắn (tên bạn đã đặt ở phản hồi trước)
        snake_head_img = pygame.image.load(resource_path('snake-head.jpg')).convert_alpha()
        snake_head_img = pygame.transform.scale(snake_head_img, (block_size, block_size))

        snake_body_img = pygame.image.load(resource_path('snake-skin.jpg')).convert_alpha()
        snake_body_img = pygame.transform.scale(snake_body_img, (block_size, block_size))

        food_img = pygame.image.load(resource_path('apple.jpg')).convert_alpha()
        food_img = pygame.transform.scale(food_img, (block_size, block_size))

    except pygame.error as e:
        print(f"Không thể tải hình ảnh: {e}")
        print("Đảm bảo bạn có 'snake_head.png', 'snake_body.png' và 'apple.jpg' trong cùng thư mục.")
        return
    # -----------------------------

    while not game_over:

        while game_close == True:
            screen.fill(black)
            message("You lost! Press Q to Quit or C to Replay", red)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
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

        # Cập nhật vị trí
        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        screen.fill(black)

        # Vẽ thức ăn bằng hình ảnh quả táo
        screen.blit(food_img, (food_x, food_y))

        # Cập nhật danh sách rắn
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Kiểm tra va chạm với thân
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        # Vẽ rắn
        for segment in snake_list:
            if segment == snake_head:  # Đây là đầu rắn
                screen.blit(snake_head_img, (segment[0], segment[1]))
            else:  # Đây là thân rắn
                screen.blit(snake_body_img, (segment[0], segment[1]))

        # Hiển thị điểm số
        score = length_of_snake - 1
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        screen.blit(score_text, [0, 0])

        pygame.display.update()

        # Kiểm tra ăn thức ăn
        if x1 == food_x and y1 == food_y:
            food_x, food_y = generate_food_location()
            # Đảm bảo thức ăn không xuất hiện trên thân rắn
            while [food_x, food_y] in snake_list:
                food_x, food_y = generate_food_location()
                
            length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()