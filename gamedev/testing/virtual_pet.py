import pygame


class Pet:
  def __init__(self, x, y, health, max_health, happiness, max_happiness):
    # Set up basic fields
    self.x = x
    self.y = y
    # Health = radius
    self.health = health
    self.max_health = max_health
    # Happiness = green value of colour
    self.happiness = happiness
    self.max_happiness = max_happiness
    self.colour = pygame.Color(0, happiness, 0)

  # Return the x and y positions (center of circle) as a 2D vector
  def get_pos(self):
    return pygame.Vector2(self.x, self.y)
  # Return a rectangle surrounding the circle where the x and y positions are center - radius and the width and height are radius * 2
  def get_rect(self):
    return pygame.Rect(self.x - self.health, self.y - self.health, self.health * 2, self.health * 2)
  # Increase/decrease the x and/or y positions
  def move(self, x_amount, y_amount):
    self.x += x_amount
    self.y += y_amount
  # Update health and happiness by consuming item
  def consume_item(self, item):
    self.update_health(item.health)
    self.update_happiness(item.happiness)
  # Update health (radius) and make sure it doesn't exceed max or min
  def update_health(self, d_h):
    self.health += d_h
    if self.health > self.max_health:
      self.health = self.max_health
    elif self.health < 0:
      self.health = 0
  # Update happiness (green colour) and make sure it doesn't exceed max or min
  def update_happiness(self, d_h):
    self.happiness += d_h
    if self.happiness > self.max_happiness:
      self.happiness = self.max_happiness
    elif self.happiness < 0:
      self.happiness = 0
    self.colour = pygame.Color(0, self.happiness, 0)
  def check_if_dead(self):
    return self.health <= 0 or self.happiness <= 0


class Item:
  def __init__(self, x, y, health, happiness, image_name):
    # Set up basic fields
    self.x = x
    self.y = y
    self.health = health
    self.happiness = happiness
    # Load and store the image based on the filepath
    self.image = pygame.image.load(image_name)
    # Shift the image rect so that the x and y are at the center rather than top left
    rect = self.image.get_rect()
    self.image_rect = pygame.Rect(x - rect.width / 2, y - rect.height / 2, rect.width, rect.height)


class Game:
  def __init__(self):
    # Display variables
    self.width = 500
    self.height = 500
    self.background_colour = "white"
    self.buttons_bar_height = 100
    self.buttons_bar_colour = "orange"
    # Pygame specific variables
    self.screen = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption("Pygame Pet")
    self.clock_tick = 60
    self.clock = pygame.time.Clock()
    # Item variables
    self.image_names = ["apple.png", "icecream.png", "toy.png"]
    self.item_mode_index = 0
    self.item = None
    # Button variables
    self.apple_button = Item(self.width / 4, self.buttons_bar_height / 2, 0, 0, self.image_names[0])
    self.ice_cream_button = Item(self.width / 2, self.buttons_bar_height / 2, 0, 0, self.image_names[1])
    self.toy_button = Item(self.width * (3 / 4), self.buttons_bar_height / 2, 0, 0, self.image_names[2])
    # Pet variables
    self.pet = Pet(self.width / 2, self.height / 2, 50, 100, 180, 255)
    self.speed = 2
    self.d_x = 0
    self.d_y = 0
    self.decay_rate = -1
    self.current_tick = 0
    self.size_update_rate = self.clock_tick / 3
    self.colour_update_rate = self.clock_tick / 10
  # Select an item or place an item if appropriate area is clicked
  def handle_mouse_click(self):
    pos = pygame.mouse.get_pos()
    # Check for button press
    if self.apple_button.image_rect.collidepoint(pos):
      self.item_mode_index = 0
    elif self.ice_cream_button.image_rect.collidepoint(pos):
      self.item_mode_index = 1
    elif self.toy_button.image_rect.collidepoint(pos):
      self.item_mode_index = 2
    # Do nothing if user clicks button bar outside of buttons
    elif pos[1] < self.buttons_bar_height:
      return
    # Create an item at the mouse position
    else:
      self.create_item(pos)
      
  # Spawn an item at the position
  def create_item(self, pos):
    # Get current image name
    image_name = self.image_names[self.item_mode_index]
    # Create an item at the position
    if self.item_mode_index == 0:
      self.item = Item(pos[0], pos[1], 20, 0, image_name)
    elif self.item_mode_index == 1:
      self.item = Item(pos[0], pos[1], -10, 60, image_name)
    elif self.item_mode_index == 2:
      self.item = Item(pos[0], pos[1], 0, 40, image_name)
    # Start moving the pet
    self.set_speed()
  # Set the magnitude and direction of pet movement
  def set_speed(self):
    # Get differences in x and y positions of pet and item
    d_x = abs(self.pet.x - self.item.x)
    d_y = abs(self.pet.y - self.item.y)
    # Check whether x difference is greater than y difference
    if d_x >= d_y:
      self.d_x = self.speed
      # Slow down the y movement
      self.d_y = self.speed * (d_y / d_x)
    else:
      # Slow down the x movement
      self.d_x = self.speed * (d_x / d_y)
      self.d_y = self.speed
    # Set x speed to negative if item is further left than pet
    if self.pet.x > self.item.x:
      self.d_x = -self.d_x
    # Set y speed to negative if item is further up than pet
    if self.pet.y > self.item.y:
      self.d_y = -self.d_y
  # Check for collisions between pet and item
  def handle_item_collision(self):
    # If item exists and item.rect and pet.rect overlap, collision occurred
    if self.item != None and self.item.image_rect.colliderect(self.pet.get_rect()):
      # Consume then delete item
      self.pet.consume_item(self.item)
      self.item = None
      # Stop pet movement by setting speeds to 0
      self.d_x = 0
      self.d_y = 0
  
  
  # Update pet position, health, and happiness
  def update_pet(self):
    # Position
    self.pet.move(self.d_x, self.d_y)
    # Update health and happiness
    self.current_tick += 1
    # Decay the health 3x per second
    if self.current_tick % self.size_update_rate == 0:
      self.pet.update_health(self.decay_rate)
    # Decay the happiness 10x per second
    if self.current_tick % self.colour_update_rate == 0:
      self.pet.update_happiness(self.decay_rate)
    # Reset current tick to prevent it becoming too large
    if self.current_tick == 60:
      self.current_tick = 0
  
  
  # Draw the screen, bar, buttons, item, pet
  def draw_everything(self):
    # Screen
    self.screen.fill(self.background_colour)
    # Item
    if self.item != None:
      self.screen.blit(self.item.image, self.item.image_rect)
    # Pet
    pygame.draw.circle(self.screen, self.pet.colour, self.pet.get_pos(), self.pet.health)
    # Buttons bar
    pygame.draw.rect(self.screen, self.buttons_bar_colour, pygame.Rect(0, 0, self.width, self.buttons_bar_height))
    # Buttons
    self.screen.blit(self.apple_button.image, self.apple_button.image_rect)
    self.screen.blit(self.ice_cream_button.image, self.ice_cream_button.image_rect)
    self.screen.blit(self.toy_button.image, self.toy_button.image_rect)
    # Update
    pygame.display.update()
  
  # Run the game loop
  def run(self):
    while True:
      # Handle incoming events
      for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT:
          pygame.quit()
          return
        elif event.type == pygame.MOUSEBUTTONDOWN:
          self.handle_mouse_click()
      # Detect pet-item collision
      self.handle_item_collision()
      # Check if pet is dead and game over
      if self.pet.check_if_dead():
        pygame.quit()
        return
      # Update
      self.update_pet()
      
      # Draw
      self.draw_everything()
      
      # Tick clock
      self.clock.tick(self.clock_tick)
      
# Initialize Pygame and start running game
pygame.init()
game = Game()
game.run()
