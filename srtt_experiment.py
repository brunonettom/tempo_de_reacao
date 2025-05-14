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

# Default experiment settings (modifiable)
DEFAULT_POSITIONS = 4  # Default number of stimulus positions
DEFAULT_BLOCKS = 8  # Default number of blocks
DEFAULT_TRIALS_PER_BLOCK = 60  # Default trials per block

# Position keys - usando teclas numéricas do teclado principal
POSITION_KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']  # Teclas numéricas
KEY_MAPPING = {
    pygame.K_1: 0,
    pygame.K_2: 1, 
    pygame.K_3: 2,
    pygame.K_4: 3,
    pygame.K_5: 4,
    pygame.K_6: 5,
    pygame.K_7: 6,
    pygame.K_8: 7,
    pygame.K_9: 8,
    pygame.K_0: 9
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
        self.total_responses = 0  # Adicionado para rastrear o total de respostas
        self.correct_timestamps = []  # Adicionado para rastrear os timestamps dos acertos
        self.is_structured_block = True
        self.running = True
        self.state = "participant_info"  # Start with participant info screen
        self.blocks_data = []
        self.block_sequence = []
        
        # Experiment settings (can be changed in settings screen)
        self.positions = DEFAULT_POSITIONS
        self.blocks = DEFAULT_BLOCKS
        self.trials_per_block = DEFAULT_TRIALS_PER_BLOCK
        
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
        
        # Text input boxes for numerical values
        position_box = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 - 160, 80, 30)
        blocks_box = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 - 100, 80, 30)
        trials_box = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 - 40, 80, 30)
        
        position_value = str(self.positions)
        blocks_value = str(self.blocks)
        trials_value = str(self.trials_per_block)
        
        active_box = None
        done = False
        
        while not done and self.running:
            screen.fill(BACKGROUND_COLOR)
            
            # Draw title
            title = font.render("Configurações do Experimento", True, (0, 0, 0))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
            
            # Draw position input
            position_text = font.render("Número de posições:", True, (0, 0, 0))
            screen.blit(position_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 150))
            
            pygame.draw.rect(screen, (255, 255, 255), position_box)
            pygame.draw.rect(screen, (0, 0, 0) if active_box == position_box else (200, 200, 200), position_box, 2)
            position_surface = font.render(position_value, True, (0, 0, 0))
            screen.blit(position_surface, (position_box.x + 5, position_box.y + 5))
            
            # Draw blocks input
            blocks_text = font.render("Número de blocos:", True, (0, 0, 0))
            screen.blit(blocks_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 90))
            
            pygame.draw.rect(screen, (255, 255, 255), blocks_box)
            pygame.draw.rect(screen, (0, 0, 0) if active_box == blocks_box else (200, 200, 200), blocks_box, 2)
            blocks_surface = font.render(blocks_value, True, (0, 0, 0))
            screen.blit(blocks_surface, (blocks_box.x + 5, blocks_box.y + 5))
            
            # Draw trials input
            trials_text = font.render("Estímulos por bloco:", True, (0, 0, 0))
            screen.blit(trials_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 30))
            
            pygame.draw.rect(screen, (255, 255, 255), trials_box)
            pygame.draw.rect(screen, (0, 0, 0) if active_box == trials_box else (200, 200, 200), trials_box, 2)
            trials_surface = font.render(trials_value, True, (0, 0, 0))
            screen.blit(trials_surface, (trials_box.x + 5, trials_box.y + 5))
            
            # Draw continue button
            continue_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40, 200, 40)
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
                    if position_box.collidepoint(event.pos):
                        active_box = position_box
                    elif blocks_box.collidepoint(event.pos):
                        active_box = blocks_box
                    elif trials_box.collidepoint(event.pos):
                        active_box = trials_box
                    elif continue_rect.collidepoint(event.pos):
                        # Save settings and continue
                        try:
                            self.positions = max(1, int(position_value))
                            self.blocks = max(1, int(blocks_value))
                            self.trials_per_block = max(1, int(trials_value))
                            done = True
                        except ValueError:
                            # If conversion fails, use default values
                            position_value = str(DEFAULT_POSITIONS)
                            blocks_value = str(DEFAULT_BLOCKS)
                            trials_value = str(DEFAULT_TRIALS_PER_BLOCK)
                    else:
                        active_box = None
                
                if event.type == pygame.KEYDOWN:
                    if active_box:
                        if event.key == pygame.K_RETURN:
                            # Save settings and continue
                            try:
                                self.positions = max(1, int(position_value))
                                self.blocks = max(1, int(blocks_value))
                                self.trials_per_block = max(1, int(trials_value))
                                done = True
                            except ValueError:
                                # If conversion fails, use default values
                                position_value = str(DEFAULT_POSITIONS)
                                blocks_value = str(DEFAULT_BLOCKS)
                                trials_value = str(DEFAULT_TRIALS_PER_BLOCK)
                        elif event.key == pygame.K_BACKSPACE:
                            if active_box == position_box:
                                position_value = position_value[:-1]
                            elif active_box == blocks_box:
                                blocks_value = blocks_value[:-1]
                            elif active_box == trials_box:
                                trials_value = trials_value[:-1]
                        elif event.unicode.isdigit():  # Only allow digits
                            if active_box == position_box:
                                position_value += event.unicode
                            elif active_box == blocks_box:
                                blocks_value += event.unicode
                            elif active_box == trials_box:
                                trials_value += event.unicode

    def generate_block_sequence(self):
        """Generate the sequence for the current block"""
        if self.is_structured_block:
            # For structured blocks, repeat the predefined sequence as needed
            structured_sequence = self.generate_structured_sequence()
            repetitions = self.trials_per_block // SEQUENCE_LENGTH
            remainder = self.trials_per_block % SEQUENCE_LENGTH
            sequence = (structured_sequence * repetitions) + structured_sequence[:remainder]
            
            # Modify the sequence to ensure no immediate repetitions
            for i in range(1, len(sequence)):
                if sequence[i] == sequence[i-1]:
                    # Find a non-repeating value
                    options = list(range(self.positions))
                    options.remove(sequence[i-1])
                    if options:  # Make sure we have options
                        sequence[i] = random.choice(options)
                    
            return sequence
        else:
            # For random blocks, generate a pseudo-random sequence
            random_sequence = []
            last_position = None
            
            for _ in range(self.trials_per_block):
                # Generate new positions ensuring no immediate repetitions
                available_positions = list(range(self.positions))
                if last_position is not None and last_position in available_positions:
                    available_positions.remove(last_position)
                
                if available_positions:  # Make sure we have options
                    new_position = random.choice(available_positions)
                    random_sequence.append(new_position)
                    last_position = new_position
                else:
                    # Fallback if we somehow have only one position available
                    random_sequence.append(random.randint(0, self.positions-1))
                
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
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
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
        
        # Move to settings screen
        self.get_experiment_settings()
    
    def show_instructions(self):
        """Display instructions for the experiment"""
        screen.fill(BACKGROUND_COLOR)
        
        instructions = [
            "Tarefa de Tempo de Reação em Série (SRTT)",
            "",
            f"Você verá círculos azuis em {self.positions} posições.",
            "Quando um círculo ficar vermelho, pressione a tecla numérica correspondente",
            "o mais rápido e precisamente possível:",
            "",
        ]
        
        # Add key mapping instructions based on selected positions
        for i in range(self.positions):
            if i == 0:
                instructions.append(f"Posição {i + 1} (esquerda): tecla '{POSITION_KEYS[i]}'")
            elif i == self.positions - 1:
                instructions.append(f"Posição {i + 1} (direita): tecla '{POSITION_KEYS[i]}'")
            else:
                instructions.append(f"Posição {i + 1}: tecla '{POSITION_KEYS[i]}'")
        
        instructions += [
            "",
            "Mantenha seus dedos posicionados nas teclas numéricas durante todo o experimento.",
            f"O experimento consiste em {self.blocks} blocos de {self.trials_per_block} estímulos cada.",
            "",
            "Pressione ESPAÇO para iniciar o experimento."
        ]
        
        # Começar o texto muito mais acima na tela e com margens adequadas
        margin = 40  # Margem horizontal para evitar corte nas bordas
        y_pos = 20  # Começar praticamente no topo
        
        # Calcula largura máxima do texto para posicionamento centralizado
        max_width = 0
        for line in instructions:
            text_surface = font.render(line, True, (0, 0, 0))
            max_width = max(max_width, text_surface.get_width())
        
        # Garante que o texto não exceda as margens laterais
        available_width = SCREEN_WIDTH - (2 * margin)
        
        for line in instructions:
            text = font.render(line, True, (0, 0, 0))
            # Centraliza o texto mas garantindo margens mínimas
            x_pos = max(margin, SCREEN_WIDTH//2 - text.get_width()//2)
            screen.blit(text, (x_pos, y_pos))
            y_pos += 26  # Distância entre linhas reduzida para caber mais texto
        
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
        
        # Começar o texto mais acima na tela e com margens adequadas
        margin = 40  # Margem horizontal para evitar corte nas bordas
        y_pos = 20  # Começar praticamente no topo
        
        for line in break_text:
            text = font.render(line, True, (0, 0, 0))
            # Centraliza o texto mas garantindo margens mínimas
            x_pos = max(margin, SCREEN_WIDTH//2 - text.get_width()//2)
            screen.blit(text, (x_pos, y_pos))
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
            
            # Determinar cor do círculo - SEMPRE vermelho para a posição atual
            if i == self.current_position:
                color = STIMULUS_ACTIVE_COLOR  # Vermelho para a posição atual
            else:
                color = STIMULUS_COLOR  # Azul para as outras posições
            
            # Desenhar o círculo
            pygame.draw.circle(screen, color, (x, y), STIMULUS_SIZE // 2)
            
            # Desenhar número da posição embaixo do círculo
            position_text = font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(position_text, (x - position_text.get_width()//2, y + STIMULUS_SIZE))
    
    def validate_response(self, key_pressed):
        """Check if the key pressed corresponds to the current position"""
        if key_pressed in KEY_MAPPING and KEY_MAPPING[key_pressed] < self.positions and KEY_MAPPING[key_pressed] == self.current_position:
            return True
        return False
    
    def present_trial(self):
        """Present a single trial"""
        self.current_position = self.block_sequence[self.current_trial]
        # Remover uso da variável show_stimulus que estava causando problemas
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
            
            # Desenhar círculos (um será vermelho)
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
                    
                    # Check response keys - agora usando teclas numéricas
                    if event.key in KEY_MAPPING:
                        response_time = (time.time() - self.start_time) * 1000  # Convert to milliseconds
                        correct = self.validate_response(event.key)
                        
                        # Record the reaction time (only record the time for the first attempt)
                        if incorrect_attempts == 0:
                            self.reaction_time = response_time
                        
                        # Incrementar total de respostas
                        self.total_responses += 1
                        
                        # Record the response (both correct and incorrect)
                        self.results.append({
                            "participant_id": self.participant_id,
                            "block": self.current_block + 1,
                            "block_type": "structured" if self.is_structured_block else "random",
                            "trial": self.current_trial + 1,
                            "position": self.current_position + 1,
                            "reaction_time": round(response_time, 2),
                            "correct": correct,
                            "attempt": incorrect_attempts + 1,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        if correct:
                            # If correct, end trial and proceed
                            self.correct_responses += 1
                            # Registrar timestamp do acerto para cálculo do tempo entre acertos
                            current_time = time.time()
                            self.correct_timestamps.append(current_time)
                            
                            # Show feedback briefly
                            pygame.display.flip()
                            pygame.time.delay(100)  # Brief delay between trials
                            waiting_for_response = False
                        else:
                            # For incorrect response, keep the same position but record the attempt
                            incorrect_attempts += 1
                            
                            # Flash the stimulus briefly to indicate incorrect response
                            pygame.display.flip()
                            pygame.time.delay(200)
                            pygame.display.flip()
            
            # If no response after 5 seconds, count as timeout but keep waiting for response
            if time.time() - self.start_time > 5.0 and incorrect_attempts == 0:
                # Record timeout as an incorrect attempt
                incorrect_attempts += 1
                self.total_responses += 1  # Também contar timeouts como respostas
                self.results.append({
                    "participant_id": self.participant_id,
                    "block": self.current_block + 1,
                    "block_type": "structured" if self.is_structured_block else "random",
                    "trial": self.current_trial + 1,
                    "position": self.current_position + 1,
                    "reaction_time": 5000,  # Set to maximum RT
                    "correct": False,
                    "attempt": incorrect_attempts,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Reset timer but keep waiting for response
                self.start_time = time.time()

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
                          "position", "reaction_time", "correct", "attempt", "timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
                
        print(f"Results saved to {filename}")
        return filename
    
    def calculate_inter_hit_times(self):
        """Calculate average time between consecutive correct responses"""
        if len(self.correct_timestamps) <= 1:
            return 0  # Não há intervalos se houver menos de 2 acertos
        
        total_time = 0
        intervals = 0
        
        for i in range(1, len(self.correct_timestamps)):
            interval = self.correct_timestamps[i] - self.correct_timestamps[i-1]
            total_time += interval
            intervals += 1
            
        return (total_time / intervals) if intervals > 0 else 0

    def show_completion_screen(self, filename):
        """Show experiment completion screen"""
        screen.fill(BACKGROUND_COLOR)
        
        # Calculate accuracy based on total responses
        accuracy = (self.correct_responses / self.total_responses * 100) if self.total_responses > 0 else 0
        
        # Calculate average time between correct responses (in seconds)
        avg_inter_hit_time = self.calculate_inter_hit_times()
        
        completion_text = [
            "Experimento concluído!",
            "",
            f"Precisão geral: {accuracy:.1f}%",
            "",
            f"Tempo médio entre acertos: {avg_inter_hit_time:.2f} segundos",
            "",
            f"Os resultados foram salvos em:",
            filename,
            "",
            "Obrigado pela sua participação!",
            "",
            "Pressione ESC para sair."
        ]
        
        # Começar o texto mais acima na tela e com margens adequadas
        margin = 40  # Margem horizontal para evitar corte nas bordas
        y_pos = 20  # Começar praticamente no topo
        
        for line in completion_text:
            text = font.render(line, True, (0, 0, 0))
            # Centraliza o texto mas garantindo margens mínimas
            x_pos = max(margin, SCREEN_WIDTH//2 - text.get_width()//2)
            screen.blit(text, (x_pos, y_pos))
            y_pos += 38
        
        pygame.display.flip()
        
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting_for_input = False
                        break
            
            pygame.time.delay(100)
        
        print("Encerrando programa após conclusão.")
    
    def calculate_block_statistics(self):
        """Calculate statistics for the current block"""
        if self.current_trial > 0:
            # Filter results for the current block
            block_results = [r for r in self.results if r["block"] == self.current_block + 1]
            
            # Calculate mean RT for correct responses only
            correct_rts = [r["reaction_time"] for r in block_results if r["correct"]]
            mean_rt = sum(correct_rts) / len(correct_rts) if correct_rts else 0
            
            # Calculate accuracy (acertos / total de respostas)
            total_block_responses = len(block_results)
            correct_responses = sum(1 for r in block_results if r["correct"])
            accuracy = (correct_responses / total_block_responses) * 100 if total_block_responses > 0 else 0
            
            block_type = "structured" if self.is_structured_block else "random"
            
            self.blocks_data.append({
                "block": self.current_block + 1,
                "type": block_type,
                "mean_rt": mean_rt,
                "accuracy": accuracy
            })
    
    def run(self):
        """Run the entire experiment"""
        try:
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
        except Exception as e:
            # Lidar com exceções para evitar travamentos inesperados
            print(f"Erro durante o experimento: {e}")
        finally:
            # Garantir que o pygame seja finalizado adequadamente
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    try:
        experiment = SRTTExperiment()
        experiment.run()
    except Exception as e:
        print(f"Erro ao iniciar o experimento: {e}")
        pygame.quit()
        sys.exit(1)
