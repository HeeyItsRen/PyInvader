import pygame, sys
import obstacle
from player import Player
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

class Game:
        def __init__(self):
            #Player Setup
            player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
            self.player = pygame.sprite.GroupSingle(player_sprite)
            
            #Health Setup
            self.lives = 3
            self.live_surface = pygame.image.load('../graphics/player.png').convert_alpha()
            self.live_x_start_pos = screen_width - (self.live_surface.get_size()[0] * 2 + 20)
            
            #Score Setup
            self.score = 0
            self.font = pygame.font.Font('../font/Pixeled.ttf', 20)
            
            
            #Obstacle Setup
            self.shape = obstacle.shape
            self.block_size = 6
            self.blocks = pygame.sprite.Group()
            self.obstacle_amount = 4
            self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
            self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)
            
            #Enemy Setup
            self.aliens = pygame.sprite.Group()
            self.alien_lasers = pygame.sprite.Group()
            self.alien_setup(rows = 6, cols = 8)
            self.alien_direction = 1
            
            #Extra Setup
            self.extra = pygame.sprite.GroupSingle()
            self.extra_spawn_time = randint(40, 80)
            
            #Audio Setup
            #BGM
            music = pygame.mixer.Sound('../audio/music.wav')
            music.set_volume(0.01)
            music.play(loops = -1)
            
            #Lasers
            self.laser_sound = pygame.mixer.Sound('../audio/laser.wav')
            self.laser_sound.set_volume(0.05)
            
            #Explosion
            self.explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
            self.explosion_sound.set_volume(0.05)
            
        def create_obstacle(self, x_start, y_start, offset_x):
            for row_index, row in enumerate(self.shape): #Enumerate returns an int on the index we are on
                for col_index, col in enumerate(row):
                    if col == 'x':
                        x = x_start + col_index * self.block_size + offset_x #col_index * self.block_size IMPORTANT
                        y = y_start + row_index * self.block_size
                        block = obstacle.Block(self.block_size, (241, 79, 80), x, y)
                        self.blocks.add(block)
                        
        def create_multiple_obstacles(self, *offset, x_start, y_start): #unpacking operator
            for offset_x in offset:
                self.create_obstacle(x_start, y_start, offset_x)
        
        def alien_setup(self, rows, cols, x_distance = 60, y_distance = 48, x_offset = 70, y_offset = 100):
            for row_index, row in enumerate(range(rows)): #Enumerate returns an int on the index we are on
                for col_index, col in enumerate(range(cols)):
                    x = col_index * x_distance + x_offset
                    y = row_index * y_distance + y_offset
                    
                    if row_index == 0:
                        alien_sprite = Alien('yellow', x, y)
                    elif 1 <= row_index <= 2:
                        alien_sprite = Alien('green', x, y)
                    else:
                        alien_sprite = Alien('red', x, y)
                    self.aliens.add(alien_sprite)
        
        def alien_position_checker(self):
            all_aliens = self.aliens.sprites()
            for alien in all_aliens:
                if alien.rect.right >= screen_width:
                    self.alien_direction = -1
                    self.alien_move_down(2)
                if alien.rect.left <= 0:
                    self.alien_direction = 1
                    self.alien_move_down(2)
            
        def alien_move_down(self, distance):
            if self.aliens:
                for alien in self.aliens.sprites():
                    alien.rect.y += distance
                    
        def alien_shoot(self):
            if self.aliens.sprites():
                random_alien = choice(self.aliens.sprites())
                laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
                self.alien_lasers.add(laser_sprite)
                self.laser_sound.play()

        def extra_alien_timer(self):
            self.extra_spawn_time -= 1
            if self.extra_spawn_time <= 0:
                self.extra.add(Extra(choice(['right', 'left']), screen_width))
                self.extra_spawn_time = randint(400, 800)
         
        def collision_checks (self):
            
            #Player lasers
            if self.player.sprite.lasers:
                for laser in self.player.sprite.lasers:
                    #Obstacle Collisions
                    if pygame.sprite.spritecollide(laser, self.blocks, True):
                        laser.kill()
                        
                    #Enemy Collisions
                    aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                    if aliens_hit:
                        for alien in aliens_hit:
                            self.score += alien.value
                        laser.kill()
                        self.explosion_sound.play()
                        
                        
                    #Extra Collisions
                    if pygame.sprite.spritecollide(laser, self.extra, True):
                        self.score += 500
                        laser.kill()
                        self.explosion_sound.play()
                        
            #Enemy Lasers
            if self.alien_lasers:
                for laser in self.alien_lasers:
                    #Obstacle Collisions
                    if pygame.sprite.spritecollide(laser, self.blocks, True):
                        laser.kill()
                    if pygame.sprite.spritecollide(laser, self.player, False):
                        laser.kill()
                        self.explosion_sound.play()
                        self.lives -= 1
                        if self.lives <= 0:
                            pygame.quit()
                            sys.exit()
            
            #Enemy
            if self.aliens:
                for alien in self.aliens:
                    pygame.sprite.spritecollide(alien, self.blocks, True)
                    if pygame.sprite.spritecollide(alien, self.player, False):
                        pygame.quit()
                        sys.exit() 
        
        def display_lives(self):
            for lives in range(self.lives - 1): #Shows 2, 1, or 0 lives
                x = self.live_x_start_pos + (lives * (self.live_surface.get_size()[0] + 10))
                screen.blit(self.live_surface, (x, 8))
                
        def display_score(self):
            score_surface = self.font.render(f'Score: {self.score}', False, 'White')
            score_rect = score_surface.get_rect(topleft = (10, -10))
            screen.blit(score_surface, score_rect)   
        
        def victory(self):
            if not self.aliens.sprites():
                victory_surface = self.font.render(f'Victory!!', False, 'White')
                victory_rect = victory_surface.get_rect(center = (screen_width / 2, screen_height / 2))
                screen.blit(victory_surface, victory_rect)
        
        def run(self):    
            self.player.update()
            self.aliens.update(self.alien_direction)
            self.alien_lasers.update()
            self.extra.update()
            
            self.alien_position_checker()
            self.extra_alien_timer()
            self.collision_checks()
            
            self.player.sprite.lasers.draw(screen)
            self.alien_lasers.draw(screen)
            self.player.draw(screen)
            self.blocks.draw(screen)
            self.aliens.draw(screen)
            self.extra.draw(screen)
            
            self.display_lives()
            self.display_score()
            self.victory()
        
class CRT:
    def __init__(self):
        self.tv = pygame.image.load('../graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screen_width, screen_height))
    
    def create_crt_lines(self):
        line_height = 3
        line_amount = int(screen_height / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv, 'Black', (0, y_pos), (screen_width, y_pos), 1)
        
    def draw(self):
        self.tv.set_alpha(randint(75, 90))
        self.create_crt_lines()
        screen.blit(self.tv, (0, 0))
    
if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    pygame.display.set_caption('PyInvader')
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()
    
    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
            
            
        screen.fill((30, 30, 30))
        game.run()
        crt.draw()
        
        pygame.display.flip()
        clock.tick(60)