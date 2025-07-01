import pygame
import asyncio
import platform
from collections import deque
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PipeMaster: Pipeline Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Font
font = pygame.font.SysFont('Arial', 20)

# Pipeline configuration
stages = []
instructions = []
cycle = 0
max_cycles = 20
pipeline_width = 1  # Single instruction per cycle for simplicity
running = False

# Gantt chart settings
gantt_start_y = 100
gantt_row_height = 40
gantt_col_width = 50
gantt_start_x = 100

def setup():
    global stages, instructions, cycle, running
    # Default configuration
    stages = ["IF", "ID", "EX", "MEM", "WB"]  # Default 5-stage pipeline
    instructions = []
    cycle = 0
    running = False
    screen.fill(WHITE)

def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_gantt_chart():
    # Draw cycle headers
    for c in range(max_cycles):
        draw_text(f"C{c}", gantt_start_x + c * gantt_col_width, gantt_start_y - 30)
    
    # Draw stage labels and instruction progress
    for i, inst in enumerate(instructions):
        y = gantt_start_y + i * gantt_row_height
        draw_text(f"Inst {i}: {inst['name']}", 10, y + 10)
        for c in range(max_cycles):
            stage = inst['progress'].get(c, None)
            if stage and stage in stages:
                x = gantt_start_x + c * gantt_col_width
                pygame.draw.rect(screen, BLUE, (x, y, gantt_col_width - 2, gantt_row_height - 2))
                draw_text(stage, x + 10, y + 10, WHITE)

def draw_pipeline_config():
    draw_text("Pipeline Stages: " + ", ".join(stages), 10, 20)
    draw_text(f"Cycle: {cycle}", 10, 50)
    draw_text("Instructions:", 10, 80)
    for i, inst in enumerate(instructions):
        draw_text(f"Inst {i}: {inst['name']}", 20, 100 + i * 20)

def simulate_cycle():
    global cycle
    if cycle >= max_cycles:
        return False
    for inst in instructions:
        if cycle >= inst['start_cycle']:
            current_stage_idx = cycle - inst['start_cycle']
            if current_stage_idx < len(stages):
                inst['progress'][cycle] = stages[current_stage_idx]
    cycle += 1
    return True

async def main():
    global running, stages, instructions
    setup()
    clock = pygame.time.Clock()
    input_mode = "stages"  # Can be 'stages' or 'instructions'
    input_text = ""
    
    while True:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_mode == "stages" and input_text:
                        stages = [s.strip().upper() for s in input_text.split(",")]
                        input_text = ""
                        input_mode = "instructions"
                    elif input_mode == "instructions" and input_text:
                        instructions.append({
                            'name': input_text.strip().upper(),
                            'start_cycle': len(instructions),
                            'progress': {}
                        })
                        input_text = ""
                    elif input_mode == "instructions" and not input_text:
                        input_mode = "run"
                        running = True
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isprintable():
                    input_text += event.unicode
                elif event.key == pygame.K_ESCAPE:
                    setup()  # Reset simulation
                    input_mode = "stages"
                    input_text = ""
        
        # Draw UI
        draw_pipeline_config()
        draw_gantt_chart()
        
        # Draw input prompt
        if input_mode == "stages":
            draw_text("Enter stages (comma-separated, e.g., IF,ID,EX,MEM,WB):", 10, HEIGHT - 40)
        elif input_mode == "instructions":
            draw_text("Enter instruction (e.g., ADD R1, R2, R3) or ENTER to run:", 10, HEIGHT - 40)
        elif input_mode == "run":
            draw_text("Simulation running... Press ESC to reset", 10, HEIGHT - 40)
        
        draw_text(input_text, 10, HEIGHT - 20, RED)
        
        # Run simulation step
        if running and input_mode == "run":
            if not simulate_cycle():
                running = False
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
