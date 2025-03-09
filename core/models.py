import time as tm

from random import randint
from uuid import uuid4
from typing import Tuple, Literal
from abc import abstractmethod

from pygame import *


class Text:
    def __init__(
        self,
        text: str,
        position: Tuple[int, int],
        size: int,
        txt_color: Tuple[int, int, int] = (255, 255, 255),
        txt_font: str = None
    ) -> None:
        self.font = font.SysFont(txt_font, size)
        self.color = txt_color
        self.source_text = text
        self.text = self.font.render(text,  True, self.color)
        self.rect = self.text.get_rect()
        self.rect.x, self.rect.y = position

    def update_text(self, text: str):
        self.text = self.font.render(text, True, self.color)

    def draw(self, window: Surface) -> None:
        window.blit(self.text, (self.rect.x, self.rect.y))


class PlayerScore(Text):
    def update_score(self, score: str | int):
        new_text = self.source_text[:-1]
        super().update_text(new_text + str(score))


class Sprite(sprite.Sprite):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        img: str,
        speed: int = 5
    ) -> None:
        super().__init__()
        self.image = transform.scale(
            surface=image.load(img),
            size=size
        )
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.speed = speed

    @abstractmethod
    def move(self, *args, **kwargs) -> None:
        pass

    def draw(self, window: Surface) -> None:
        window.blit(source=self.image, dest=(self.rect.x, self.rect.y))


class Bullet(Sprite):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        img: str,
        role: Literal['host', 'client'],
        speed: int = 1
    ) -> None:
        super().__init__(position, size, img, speed)
        self.role = role
    
    def move(self) -> None:
        self.rect.y -= self.speed

    def check_rect_collision(
        self,
        enemies: list,
        bullets: list
    ) -> Literal['host', 'client'] | None:
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                bullets.remove(self)
                enemies.remove(enemy)

                return self.role


class Player(Sprite):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        img: str,
        speed: int = 5
    ) -> None:
        super().__init__(position, size, img, speed)
        self._count = 0
        self.score = 0
        self._bullets = {}
        self._enemies = {}
        self._spawn_time = tm.time()
        self.data = {
            'x': self.rect.x,
            'y': self.rect.y,
            'bullets': self._bullets,
            'enemies': self._enemies,
            'score': 0
        }
    
    def move(self, keys: key.ScancodeWrapper) -> None:
        if keys[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
            self.data['y'] = self.rect.y
        if keys[K_s] and self.rect.y < 450:
            self.rect.y += self.speed
            self.data['y'] = self.rect.y
        
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
            self.data['x'] = self.rect.x
        if keys[K_d] and self.rect.x < 645:
            self.rect.x += self.speed
            self.data['x'] = self.rect.x

        if keys[K_SPACE]:
            current_time = tm.time()

            if current_time - self._spawn_time >= 0.3:
                bullet_id = str(uuid4())
                self._bullets[bullet_id] = {
                    'x': self.rect.x,
                    'y': self.rect.y + 10
                }
                self._spawn_time = current_time

    def create_enemy(self) -> None:
        self._count += 1

        if self._count >= 20:
            x, y = randint(50, 620), randint(0, 30)
            enemy_id = str(uuid4())
            self._enemies[enemy_id] = {
                'x': x,
                'y': y
            }
            self._count = 0

    def draw(self, window: Surface) -> None:
        window.blit(source=self.image, dest=(self.rect.x, self.rect.y))


class Enemy(Sprite):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        img: str,
        speed: int = 2
    ):
        super().__init__(position, size, img, speed)

    def move(self) -> None:
        self.rect.y += self.speed