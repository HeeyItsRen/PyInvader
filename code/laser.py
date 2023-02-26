import pygame

class Laser(pygame.sprite.Sprite):
    def __init__(self, position, speed, constraint):
        super().__init__()
        self.image = pygame.Surface((4, 20)) 
        self.image.fill('White')
        self.rect = self.image.get_rect(center = position)
        self.speed = speed
        self.height_y = constraint
        
    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y + 50:
            self.kill()
        
    def update(self):
        self.rect.y += self.speed
        self.destroy()
        