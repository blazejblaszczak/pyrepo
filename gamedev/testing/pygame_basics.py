import pygame, sys, math

# Set up everything Pygame related
pygame.init()

# Clock for setting FPS
clock = pygame.time.Clock()

# Game screen (surface)
screen = pygame.display.set_mode()

# Set the game caption
pygame.display.set_caption("My Special Game")

# Background color
background_color = "white"
circle_x = 50
circle_y = 50

# Start run loop

while True:
  # Listen for all events currently occurring
  for event in pygame.event.get():
    # Check if there is a quit event (triggered by pressing the close button)
    if event.type == pygame.QUIT:
      # Shut down Pygame
      pygame.quit()
      # Exit the system
      sys.exit()

    # Detect when any key was pressed down
    # if event.type == pygame.KEYDOWN:
    #   if event.key == pygame.K_LEFT:
    #     print("Left keydown")
    # Detect when any key was released
    # if event.type == pygame.KEYUP:
    #   print("Keyup")

  # Get list of keys currently being pressed
  keys = pygame.key.get_pressed()
  # Each case returns true if that key is currently being pressed
  if keys[pygame.K_LEFT]:
    circle_x -= 1
  if keys[pygame.K_RIGHT]:
    circle_x += 1
  if keys[pygame.K_UP]:
    circle_y -= 1
  if keys[pygame.K_DOWN]:
    circle_y += 1
  
  # Set the screen color
  screen.fill(background_color)
  # Draw a circle
  pygame.draw.circle(screen, "purple", (circle_x, circle_y), 25)
  # Redraw the entire display
  pygame.display.flip()
  
  # Tick the clock according to the framerate (60)
  clock. Tick(60)
