import os
import pygame

from .player import Player
from .platform import Platform
from .hazard import Hazard


WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Difficulty
        self.gravity = 0.6
        self.difficulty = "Medium"
        self.replaying = False

        # Player
        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)

        # Platforms
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]

        # Hazard
        self.hazards = [
            Hazard(240, ground_y - 14, 100)
        ]

        # Goal
        self.goal_x = 740

        # Score
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

        # Sound files
        sound_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "sounds"
        )

        self.jump_sound = None
        self.goal_sound = None
        self.death_sound = None

        # Initialize sounds
        try:
            pygame.mixer.init()

            self.jump_sound = pygame.mixer.Sound(
                os.path.join(sound_path, "jump.wav")
            )

            self.goal_sound = pygame.mixer.Sound(
                os.path.join(sound_path, "goal.wav")
            )

            self.death_sound = pygame.mixer.Sound(
                os.path.join(sound_path, "death.wav")
            )

        except pygame.error:
            print("Audio unavailable. Continuing without sound.")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # Game Over controls
            if self.game_over:

                if event.key == pygame.K_e:
                    self.difficulty = "Easy"
                    self.gravity = 0.4
                    self.player.jump_strength = -10
                    self.replaying = True

                elif event.key == pygame.K_m:
                    self.difficulty = "Medium"
                    self.gravity = 0.6
                    self.player.jump_strength = -12
                    self.replaying = True

                elif event.key == pygame.K_h:
                    self.difficulty = "Hard"
                    self.gravity = 0.8
                    self.player.jump_strength = -14
                    self.replaying = True

                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(
                        pygame.event.Event(pygame.QUIT)
                    )

            # Jump controls
            elif event.key in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_w
            ):
                if self.player.on_ground:
                    self.player.jump()

                    if self.jump_sound:
                        self.jump_sound.play()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        self.player.vx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        # Handle replay after Game Over
        if self.game_over:

            if self.replaying:
                self.player.x = self.start_x
                self.player.y = self.start_y
                self.player.vx = 0
                self.player.vy = 0
                self.player.on_ground = False

                self.score = 0
                self.game_over = False
                self.replaying = False

            else:
                return

        # Store previous vertical position
        previous_y = self.player.y

        # Apply gravity
        self.player.vy += self.gravity

        # Move horizontally
        self.player.x = max(
            0,
            self.player.x + self.player.vx
        )

        # Move vertically
        self.player.y += self.player.vy
        self.player.on_ground = False

        # Improved platform collision detection
        for platform in self.platforms:

            horizontal_overlap = (
                self.player.x + self.player.width > platform.x
                and self.player.x < platform.x + platform.width
            )

            previous_bottom = (
                previous_y + self.player.height
            )

            current_bottom = (
                self.player.y + self.player.height
            )

            crossed_platform = (
                previous_bottom <= platform.y
                and current_bottom >= platform.y
            )

            if (
                horizontal_overlap
                and crossed_platform
                and self.player.vy >= 0
            ):
                self.player.y = (
                    platform.y - self.player.height
                )

                self.player.vy = 0
                self.player.on_ground = True
                break

        # Hazard collision
        for hazard in self.hazards:

            if self.player.rect().colliderect(
                hazard.rect()
            ):
                self.game_over = True

                if self.death_sound:
                    self.death_sound.play()

                return

        # Falling below screen
        if self.player.y > self.height:
            self.game_over = True

            if self.death_sound:
                self.death_sound.play()

            return

        # Goal
        if self.player.x >= self.goal_x:
            self.score += 1

            if self.goal_sound:
                self.goal_sound.play()

            self.player.x = self.start_x
            self.player.y = self.start_y
            self.player.vy = 0

    def render(self, screen):
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(
                screen,
                BROWN,
                platform.rect()
            )

        # Draw hazards
        for hazard in self.hazards:
            pygame.draw.rect(
                screen,
                RED,
                hazard.rect()
            )

        # Draw goal
        goal_rect = pygame.Rect(
            self.goal_x,
            0,
            6,
            self.height
        )

        pygame.draw.rect(
            screen,
            GREEN,
            goal_rect
        )

        # Draw player
        pygame.draw.rect(
            screen,
            WHITE,
            self.player.rect()
        )

        # Draw score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        # Game Over screen
        if self.game_over:

            game_over_text = self.font.render(
                "GAME OVER",
                True,
                WHITE
            )

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            restart_text = self.font.render(
                "E: Easy   M: Medium   H: Hard   ESC: Exit",
                True,
                WHITE
            )

            screen.blit(
                game_over_text,
                (
                    self.width // 2
                    - game_over_text.get_width() // 2,
                    self.height // 2 - 60
                )
            )

            screen.blit(
                final_score_text,
                (
                    self.width // 2
                    - final_score_text.get_width() // 2,
                    self.height // 2
                )
            )

            screen.blit(
                restart_text,
                (
                    self.width // 2
                    - restart_text.get_width() // 2,
                    self.height // 2 + 50
                )
            )