import pygame
import sys
import random
import time
import csv
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (240, 240, 240)
STIMULUS_COLOR = (0, 0, 255)
STIMULUS_ACTIVE_COLOR = (255, 0, 0)
STIMULUS_SIZE = 50
STIMULUS_DISTANCE = 120  # Space between stimuli
SEQUENCE_LENGTH = 10  # Length of the structured sequence
FEEDBACK_DURATION = 500  # Feedback duration in milliseconds

# Default experiment settings
DEFAULT_POSITIONS = 4  # Default number of stimulus positions
DEFAULT_BLOCKS = 8  # Default number of blocks for normal mode
DEFAULT_TRIALS_PER_BLOCK = 60  # Default trials per block for normal mode
TEST_BLOCKS = 2  # Number of blocks for test mode
TEST_TRIALS_PER_BLOCK = 10  # Number of trials per block for test mode

# Maximum number of positions (limited by available keys)
MAX_POSITIONS = 8  # Maximum number of positions allowed
POSITION_KEYS = ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',']  # Keys for each position
KEY_MAPPING = {
    pygame.K_z: 0,
    pygame.K_x: 1,
    pygame.K_c: 2,
    pygame.K_v: 3,
    pygame.K_b: 4,
    pygame.K_n: 5,
    pygame.K_m: 6,
    pygame.K_COMMA: 7
}

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tarefa de Tempo de Reação em Série (SRTT)")

# Font setup
font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 22)

# Create structured sequence (with second-order dependencies)
# This is a 10-item sequence with balanced transitions
DEFAULT_STRUCTURED_SEQUENCE = [0, 2, 1, 0, 3, 1, 2, 3, 0, 1]

class SRTTExperiment:
    def __init__(self):
        self.participant_id = None
        self.results = []
        self.current_block = 0
        self.current_trial = 0
        self.start_time = 0
        self.reaction_time = 0
        self.current_position = 0
        self.correct_responses = 0
        self.is_structured_block = True
        self.running = True
        self.state = "settings"  # Start with settings screen
        self.blocks_data = []
        self.show_stimulus = False
        self.block_sequence = []
        
        # Experiment settings (can be changed in settings screen)
        self.positions = DEFAULT_POSITIONS  # Number of stimulus positions
        self.blocks = DEFAULT_BLOCKS
        self.trials_per_block = DEFAULT_TRIALS_PER_BLOCK
        self.is_test_mode = False
        
        # Generate structured sequence for the selected number of positions
        self.structured_sequence = self.generate_structured_sequence()
    
    def generate_structured_sequence(self):
        """Generate a structured sequence for the current number of positions"""
        if self.positions <= 4:
            # For 4 positions or less, use the default sequence
            return DEFAULT_STRUCTURED_SEQUENCE
        else:
            # For more positions, create a new balanced sequence
            seq = []
            for i in range(SEQUENCE_LENGTH):
                # Avoid consecutive repetitions
                if i > 0:
                    options = list(range(self.positions))
                    if seq:
                        options.remove(seq[-1])  # Don't repeat last position
                    pos = random.choice(options)
                else:
                    pos = random.randint(0, self.positions - 1)
                seq.append(pos)
            return seq
    
    def get_experiment_settings(self):
        """Display settings screen for configuration"""
        pygame.display.set_caption("Configurações do Experimento")
        
        position_slider = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60, 200, 20)
        position_value = self.positions
        
        test_mode_box = pygame.Rect(SCREEN_WIDTH//2 - 10, SCREEN_HEIGHT//2, 20, 20)
        
        slider_active = False
        done = False
        
        while not done and self.running:
            screen.fill(BACKGROUND_COLOR)
            
            # Draw title
            title = font.render("Configurações do Experimento", True, (0, 0, 0))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
            
            # Draw position slider
            slider_text = font.render(f"Número de posições: {position_value}", True, (0, 0, 0))
            screen.blit(slider_text, (SCREEN_WIDTH//2 - slider_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
            
            # Draw slider
            pygame.draw.rect(screen, (200, 200, 200), position_slider)
            pygame.draw.rect(screen, (0, 0, 0), position_slider, 1)
            
            # Draw slider marker
            marker_x = position_slider.x + int((position_value - 2) * position_slider.width / (MAX_POSITIONS - 2))
            marker_rect = pygame.Rect(marker_x - 5, position_slider.y - 5, 10, position_slider.height + 10)
            pygame.draw.rect(screen, (0, 0, 255), marker_rect)
            
            # Draw min/max values
            min_text = small_font.render("2", True, (0, 0, 0))
            screen.blit(min_text, (position_slider.x - min_text.get_width()//2, position_slider.y + 25))
            
            max_text = small_font.render(str(MAX_POSITIONS), True, (0, 0, 0))
            screen.blit(max_text, (position_slider.x + position_slider.width - max_text.get_width()//2, position_slider.y + 25))
            
            # Draw test mode checkbox
            test_mode_text = font.render("Modo de teste (versão reduzida)", True, (0, 0, 0))
            screen.blit(test_mode_text, (SCREEN_WIDTH//2 - test_mode_text.get_width() - 20, SCREEN_HEIGHT//2))
            
            pygame.draw.rect(screen, (200, 200, 200), test_mode_box)
            pygame.draw.rect(screen, (0, 0, 0), test_mode_box, 1)
            
            if self.is_test_mode:
                # Draw check mark
                pygame.draw.line(screen, (0, 0, 0), 
                                (test_mode_box.x + 2, test_mode_box.y + test_mode_box.height//2),
                                (test_mode_box.x + 8, test_mode_box.y + test_mode_box.height - 4), 2)
                pygame.draw.line(screen, (0, 0, 0),
                                (test_mode_box.x + 8, test_mode_box.y + test_mode_box.height - 4),
                                (test_mode_box.x + test_mode_box.width - 2, test_mode_box.y + 4), 2)
            
            # Draw continue button
            continue_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 80, 200, 40)
            pygame.draw.rect(screen, (100, 100, 250), continue_rect)
            pygame.draw.rect(screen, (0, 0, 0), continue_rect, 1)
            
            continue_text = font.render("Continuar", True, (0, 0, 0))
            screen.blit(continue_text, (continue_rect.x + continue_rect.width//2 - continue_text.get_width()//2, 
                                       continue_rect.y + continue_rect.height//2 - continue_text.get_height()//2))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if position_slider.collidepoint(event.pos):
                        slider_active = True
                    elif test_mode_box.collidepoint(event.pos):
                        self.is_test_mode = not self.is_test_mode
                    elif continue_rect.collidepoint(event.pos):
                        # Save settings and continue
                        self.positions = position_value
                        
                        # Update blocks and trials based on test mode
                        if self.is_test_mode:
                            self.blocks = TEST_BLOCKS
                            self.trials_per_block = TEST_TRIALS_PER_BLOCK
                        else:
                            self.blocks = DEFAULT_BLOCKS
                            self.trials_per_block = DEFAULT_TRIALS_PER_BLOCK
                        
                        # Update structured sequence based on new positions
                        self.structured_sequence = self.generate_structured_sequence()
                        
                        done = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    slider_active = False
                
                if event.type == pygame.MOUSEMOTION and slider_active:
                    # Update slider position
                    rel_x = max(0, min(event.pos[0] - position_slider.x, position_slider.width))
                    position_value = int(2 + (rel_x / position_slider.width) * (MAX_POSITIONS - 2))
                    position_value = max(2, min(MAX_POSITIONS, position_value))
        
        # Move to next state
        self.state = "participant_info"
    
    def generate_block_sequence(self):
        """Generate the sequence for the current block"""
        if self.is_structured_block:
            # For structured blocks, repeat the predefined sequence as needed
            repetitions = self.trials_per_block // SEQUENCE_LENGTH
            remainder = self.trials_per_block % SEQUENCE_LENGTH
            sequence = (self.structured_sequence * repetitions) + self.structured_sequence[:remainder]
            
            # Modify the sequence to ensure no immediate repetitions
            for i in range(1, len(sequence)):
                if sequence[i] == sequence[i-1]:
                    # Find a non-repeating value
                    options = list(range(self.positions))
                    options.remove(sequence[i-1])
                    sequence[i] = random.choice(options)
                    
            return sequence
        else:
            # For random blocks, generate a pseudo-random sequence
            random_sequence = []
            last_position = None
            
            for _ in range(self.trials_per_block):
                # Generate new positions ensuring no immediate repetitions
                available_positions = list(range(self.positions))
                if last_position is not None:
                    available_positions.remove(last_position)
                
                new_position = random.choice(available_positions)
                random_sequence.append(new_position)
                last_position = new_position
                
            return random_sequence
    def collect_participant_info(self):
        """Collect participant information using a simple input dialog"""
        pygame.display.set_caption("Enter Participant ID")
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 20, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        done = False
        
        while not done and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            if text:
                                done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
            
            screen.fill(BACKGROUND_COLOR)
            
            # Render instructions
            instructions = font.render('Digite o ID do participante e pressione Enter', True, (0, 0, 0))
            screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, SCREEN_HEIGHT//2 - 60))
            
            # Render input box
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 10))
            pygame.draw.rect(screen, color, input_box, 2)
            
            pygame.display.flip()
        
        self.participant_id = text
        
        # Move to next state
        self.state = "instructions"
        
    def show_instructions(self):
        """Display instructions for the experiment"""
        screen.fill(BACKGROUND_COLOR)
        
        instructions = [
            "Tarefa de Tempo de Reação em Série (SRTT)",
            "",
            "Você verá círculos azuis em várias posições.",
            "Quando um círculo ficar vermelho, pressione a tecla correspondente",
            "o mais rápido e precisamente possível:",
            "",
        ]
        
        for i in range(self.positions):
            instructions.append(f"Posição {i + 1}: tecla '{POSITION_KEYS[i]}'")
        
        instructions += [
            "",
            "Mantenha seus dedos posicionados nas teclas durante todo o experimento.",
            f"O experimento consiste em {self.blocks} blocos de {self.trials_per_block} estímulos cada.",
            "",
            "Pressione ESPAÇO para iniciar o experimento."
        ]
        
        y_pos = SCREEN_HEIGHT // 4
        for line in instructions:
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 30
        
        pygame.display.flip()
        
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_input = False
    
    def show_break(self):
        """Display break screen between blocks"""
        screen.fill(BACKGROUND_COLOR)
        
        break_text = [
            f"Bloco {self.current_block} de {self.blocks} concluído!",
            "",
            "Você pode fazer uma pequena pausa agora.",
            "",
            "Pressione ESPAÇO quando estiver pronto para continuar."
        ]
        
        y_pos = SCREEN_HEIGHT // 3
        for line in break_text:
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 40
        
        pygame.display.flip()
        
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_input = False
    
    def draw_stimuli(self):
        """Draw all stimulus positions and highlight the active one"""
        # Calculate the starting position
        start_x = SCREEN_WIDTH // 2 - ((self.positions - 1) * STIMULUS_DISTANCE) // 2
        
        for i in range(self.positions):
            x = start_x + i * STIMULUS_DISTANCE
            y = SCREEN_HEIGHT // 2
            
            # Draw corresponding key above the circle
            key_text = font.render(POSITION_KEYS[i], True, (0, 0, 0))
            screen.blit(key_text, (x - key_text.get_width()//2, y - STIMULUS_SIZE - 15))
            
            color = STIMULUS_ACTIVE_COLOR if i == self.current_position and self.show_stimulus else STIMULUS_COLOR
            pygame.draw.circle(screen, color, (x, y), STIMULUS_SIZE // 2)
            
            # Draw position number underneath
            position_text = font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(position_text, (x - position_text.get_width()//2, y + STIMULUS_SIZE))
    
    def validate_response(self, key_pressed):
        """Check if the key pressed corresponds to the current position"""
        if key_pressed in KEY_MAPPING and KEY_MAPPING[key_pressed] == self.current_position:
            return True
        return False
    
    def present_trial(self):
        """Present a single trial"""
        self.current_position = self.block_sequence[self.current_trial]
        self.show_stimulus = True
        self.start_time = time.time()
        
        # Reset for next trial
        self.reaction_time = 0
        waiting_for_response = True
        incorrect_attempts = 0
        
        while waiting_for_response and self.running:
            screen.fill(BACKGROUND_COLOR)
            
            # Display block and trial info
            block_info = font.render(f"Bloco: {self.current_block + 1}/{self.blocks}  Trial: {self.current_trial + 1}/{self.trials_per_block}", 
                                     True, (0, 0, 0))
            screen.blit(block_info, (10, 10))
            
            self.draw_stimuli()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                    
                    # Check response keys
                    if event.key in KEY_MAPPING:
                        response_time = (time.time() - self.start_time) * 1000  # Convert to milliseconds
                        correct = self.validate_response(event.key)
                        
                        # Record the reaction time (only record the time for the first attempt)
                        if incorrect_attempts == 0:
                            self.reaction_time = response_time
                        
                        # If correct, end trial and proceed
                        if correct:
                            self.correct_responses += 1
                            
                            # Record trial data
                            self.results.append({
                                "participant_id": self.participant_id,
                                "block": self.current_block + 1,
                                "block_type": "structured" if self.is_structured_block else "random",
                                "trial": self.current_trial + 1,
                                "position": self.current_position + 1,
                                "reaction_time": round(self.reaction_time, 2),
                                "correct": True,
                                "attempts": incorrect_attempts + 1,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            # Show feedback briefly
                            self.show_stimulus = False
                            pygame.display.flip()
                            pygame.time.delay(100)  # Brief delay between trials
                            
                            waiting_for_response = False
                        else:
                            # For incorrect response, keep showing stimulus but record the attempt
                            incorrect_attempts += 1
                            
                            # Flash the stimulus briefly to indicate incorrect response
                            self.show_stimulus = False
                            pygame.display.flip()
                            pygame.time.delay(200)
                            self.show_stimulus = True
                            pygame.display.flip()
            
            # If no response after 5 seconds, count as error but don't move to next trial
            if time.time() - self.start_time > 5.0 and waiting_for_response:
                # Reset timer for next attempt
                self.start_time = time.time()
                
                # Record that we've had a timeout
                incorrect_attempts += 1
                
                # Flash the stimulus to indicate timeout (only if we haven't exceeded max attempts)
                if incorrect_attempts <= 5:  # Limit number of timeouts before moving on
                    self.show_stimulus = False
                    pygame.display.flip()
                    pygame.time.delay(200)
                    self.show_stimulus = True
                    pygame.display.flip()
                else:
                    # After 5 timeouts, move on to next trial
                    self.results.append({
                        "participant_id": self.participant_id,
                        "block": self.current_block + 1,
                        "block_type": "structured" if self.is_structured_block else "random",
                        "trial": self.current_trial + 1,
                        "position": self.current_position + 1,
                        "reaction_time": 5000,  # Set to maximum RT
                        "correct": False,
                        "attempts": incorrect_attempts,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    waiting_for_response = False
    
    def save_results(self):
        """Save results to a CSV file"""
        # Create results directory if it doesn't exist
        if not os.path.exists('results'):
            os.makedirs('results')
        
        # Generate filename with participant ID and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/srtt_participant_{self.participant_id}_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["participant_id", "block", "block_type", "trial", 
                          "position", "reaction_time", "correct", "attempts", "timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                # Ensure all results have the attempts field
                if "attempts" not in result:
                    result["attempts"] = 1
                writer.writerow(result)
                
        print(f"Results saved to {filename}")
        return filename
    
    def show_completion_screen(self, filename):
        """Show experiment completion screen"""
        screen.fill(BACKGROUND_COLOR)
        
        # Calculate accuracy
        accuracy = (self.correct_responses / (self.current_block * self.trials_per_block + self.current_trial)) * 100
        
        completion_text = [
            "Experimento concluído!",
            "",
            f"Precisão geral: {accuracy:.1f}%",
            "",
            f"Os resultados foram salvos em:",
            filename,
            "",
            "Obrigado pela sua participação!",
            "",
            "Pressione ESC para sair."
        ]
        
        y_pos = SCREEN_HEIGHT // 4
        for line in completion_text:
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 40
        
        pygame.display.flip()
        
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting_for_input = False
    
    def calculate_block_statistics(self):
        """Calculate statistics for the current block"""
        if self.current_trial > 0:
            # Filter results for the current block
            block_results = [r for r in self.results if r["block"] == self.current_block + 1]
            
            # Calculate mean RT for correct responses only
            correct_rts = [r["reaction_time"] for r in block_results if r["correct"]]
            mean_rt = sum(correct_rts) / len(correct_rts) if correct_rts else 0
            
            # Calculate accuracy
            accuracy = (sum(1 for r in block_results if r["correct"]) / len(block_results)) * 100
            
            block_type = "structured" if self.is_structured_block else "random"
            
            self.blocks_data.append({
                "block": self.current_block + 1,
                "type": block_type,
                "mean_rt": mean_rt,
                "accuracy": accuracy
            })
    
    def run(self):
        """Run the entire experiment"""
        # Collect experiment settings
        self.get_experiment_settings()
        
        # Collect participant info
        self.collect_participant_info()
        
        # Show instructions
        self.show_instructions()
        
        while self.running and self.current_block < self.blocks:
            # Determine if this is a structured or random block (alternating)
            self.is_structured_block = (self.current_block % 2 == 0)
            
            # Generate block sequence
            self.block_sequence = self.generate_block_sequence()
            
            # Reset for new block
            self.current_trial = 0
            
            # Run trials for current block
            while self.current_trial < self.trials_per_block and self.running:
                # Present trial
                self.present_trial()
                
                # Move to next trial
                self.current_trial += 1
            
            # Calculate and store block statistics
            self.calculate_block_statistics()
            
            # Move to next block
            self.current_block += 1
            
            # Show break between blocks (if not the last block)
            if self.current_block < self.blocks and self.running:
                self.show_break()
        
        if self.running:
            # Save results to file
            filename = self.save_results()
            
            # Show completion screen
            self.show_completion_screen(filename)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    experiment = SRTTExperiment()
    experiment.run()
