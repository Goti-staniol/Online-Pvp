import os
import platform

from typing import Literal, List
from textwrap import dedent

from pygame import *

from core.server import Host, Client
from core.models import Player, Bullet, Enemy, PlayerScore


init()

FPS = 30
win_size = (700, 500)
bullet_size = (40, 20)
enemy_size = (50, 50)

clock = time.Clock()
host = Host()
client = Client()
user_type: Literal['host', 'client']
h_port = str(host.port)
c_port = str(client.port)
bullets: List[Bullet] = []
enemies: List[Enemy] = []
enemy_to_remove = []
data = {}


def run_game(status: bool = True) -> None:
    global user_type
    
    while status:
        print('1. Создать игру\n2. Присойденится')
        try:
            user_num = int(input('Выбирите желаемую функцию: '))
            if user_num == 1:
                user_type = 'host'
                print(dedent(f'''
                    Айпи для подключения: {Host.get_machine_ip()}
                    Порт: {host.port}
                    
                    Ожидаем других игроков...
                '''))
                host.run()
            elif user_num == 2:
                user_type = 'client'
                user_ip = input('Введи айпи: ')
                user_port = int(input('Введи порт: '))
                client.connect(user_ip, user_port)
            else:
                raise ValueError('Integer expected.')
        except ValueError:
            system = platform.system()
            if system == 'Windows':
                os.system('cls')
            else:
                os.system('clear')
                
            continue
        break

    window = display.set_mode(win_size)
    display.set_caption('Online Pvp')
    
    player_one = Player(
        (150, 150),
        (60, 60),
        'image/player.png'
    )
    
    player_two = Player(
        (300, 150),
        (60, 60),
        'image/player.png'
    )

    player_one_score = PlayerScore(
        'Игрок 1. Score: 0',
        (5, 440),
        20
    )

    player_two_score = PlayerScore(
        'Игрок 2. Score: 0',
        (5, 470),
        20
    )
    
    while status:
        window.blit(
            source=transform.scale(image.load('image/bg.png'), win_size), 
            dest=(0, 0)
        )

        player_one_score.draw(window)
        player_two_score.draw(window)

        keys = key.get_pressed()
        
        if user_type == 'host':
            player_one.move(keys)
            player_one.create_enemy()

            data[host.port] = player_one.data
            host.send(data)
            client_data = host.get_data(5345)

            player_two.rect.x = client_data[h_port]['x']
            player_two.rect.y = client_data[h_port]['y']
            
            player_two.draw(window)
            player_one.draw(window)

            player_one_bullets: dict = player_one.data['bullets']
            player_two_bullets: dict = client_data[h_port]['bullets']
            all_bullets: dict = player_one_bullets | player_two_bullets

            for enemy_id in player_one.data['enemies'].keys():
                enemy_position = player_one.data['enemies'][enemy_id]
                enemy = Enemy(
                    position=(enemy_position['x'], enemy_position['y']),
                    size=enemy_size,
                    img='image/player.png'
                )
                enemies.append(enemy)
                enemy_to_remove.append(enemy_id)

            for bullet_id in all_bullets.keys():
                x, y = all_bullets[bullet_id]['x'], all_bullets[bullet_id]['y']
                role: Literal['host', 'client'] = (
                    'host' if bullet_id in player_one.data['bullets']
                    else 'client'
                )
                bullet = Bullet(
                    position=(x, y),
                    size=bullet_size,
                    img='image/bullet.png',
                    role=role,
                    speed=3
                )
                bullets.append(bullet)
                    
                if bullet_id in player_one.data['bullets']:
                    del player_one.data['bullets'][bullet_id]

            for enemy_id in enemy_to_remove:
                if enemy_id in player_one.data['enemies']:
                    del player_one.data['enemies'][enemy_id]

        if user_type == 'client':
            player_two.move(keys)
            
            data[client.port] = player_two.data
            client.send(data)
            host_data = client.get_data(5345)
            
            player_one.rect.x = host_data[c_port]['x']
            player_one.rect.y = host_data[c_port]['y']
            
            player_one.draw(window)
            player_two.draw(window)

            player_one_bullets: dict = host_data[c_port]['bullets']
            player_two_bullets: dict = player_two.data['bullets']
            all_bullets: dict = player_one_bullets | player_two_bullets

            for enemy_id in host_data[c_port]['enemies'].keys():
                enemy_coordinates = host_data[c_port]['enemies'][enemy_id]
                enemy = Enemy(
                    position=(enemy_coordinates['x'], enemy_coordinates['y']),
                    size=enemy_size,
                    img='image/player.png'
                )
                enemies.append(enemy)

            for bullet_id in all_bullets.keys():
                x, y = all_bullets[bullet_id]['x'], all_bullets[bullet_id]['y']
                role: Literal['host', 'client'] = (
                    'client' if bullet_id in player_two.data['bullets']
                    else 'host'
                )
                bullet = Bullet(
                    position=(x, y),
                    size=bullet_size,
                    img='image/bullet.png',
                    role=role,
                    speed=3
                )
                bullets.append(bullet)
                    
                if bullet_id in player_two.data['bullets']:
                    del player_two.data['bullets'][bullet_id]

        for enemy in enemies:
            enemy.move()
            enemy.draw(window)

        for bullet in bullets:
            bullet.move()
            bullet.draw(window)

            player_role = bullet.check_rect_collision(enemies, bullets)
            if player_role == 'host':
                player_one.score += 1
                player_one_score.update_score(player_one.score)
            elif player_role == 'client':
                player_two.score += 1
                player_two_score.update_score(player_two.score)

        for e in event.get():
            if e.type == QUIT:
                status = False
        
        display.update()
        clock.tick(FPS)