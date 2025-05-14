import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tkinter import Tk, filedialog

def select_result_file():
    """Open a file dialog to select a result file"""
    root = Tk()
    root.withdraw()  # Hide the main window
    
    # Ask the user to select a file
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo de resultados SRTT",
        filetypes=[("CSV Files", "*.csv")],
        initialdir="./results" if os.path.exists("./results") else "."
    )
    
    root.destroy()
    return file_path

def load_data(file_path):
    """Load data from CSV file"""
    data = []
    
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numeric values
            row['reaction_time'] = float(row['reaction_time'])
            row['block'] = int(row['block'])
            row['trial'] = int(row['trial'])
            row['position'] = int(row['position'])
            row['correct'] = row['correct'].lower() == 'true'
            
            data.append(row)
    
    return data

def analyze_data(data):
    """Analyze SRTT data"""
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Ensure attempts field exists (for backward compatibility)
    if 'attempts' not in df.columns:
        df['attempts'] = 1
    
    # Calculate mean RT by block and block type (only correct responses)
    rt_by_block = df[df['correct']].groupby(['block', 'block_type'])['reaction_time'].mean().reset_index()
    
    # Calculate accuracy by block
    accuracy_by_block = df.groupby(['block', 'block_type'])['correct'].mean().reset_index()
    accuracy_by_block['accuracy'] = accuracy_by_block['correct'] * 100
    
    # Calculate mean attempts by block
    attempts_by_block = df.groupby(['block', 'block_type'])['attempts'].mean().reset_index()
    
    # Calculate learning effect (difference between random and structured blocks)
    structured_rt = df[(df['block_type'] == 'structured') & df['correct']]['reaction_time'].mean()
    random_rt = df[(df['block_type'] == 'random') & df['correct']]['reaction_time'].mean()
    learning_effect = random_rt - structured_rt
    
    # Calculate mean attempts for structured vs random
    structured_attempts = df[df['block_type'] == 'structured']['attempts'].mean()
    random_attempts = df[df['block_type'] == 'random']['attempts'].mean()
    
    # Get participant ID
    participant_id = data[0]['participant_id'] if data else "Unknown"
    
    return {
        'rt_by_block': rt_by_block,
        'accuracy_by_block': accuracy_by_block,
        'attempts_by_block': attempts_by_block,
        'structured_rt': structured_rt,
        'random_rt': random_rt,
        'structured_attempts': structured_attempts,
        'random_attempts': random_attempts,
        'learning_effect': learning_effect,
        'participant_id': participant_id
    }

def generate_visualizations(results):
    """Generate visualizations of SRTT results"""
    rt_by_block = results['rt_by_block']
    accuracy_by_block = results['accuracy_by_block']
    participant_id = results['participant_id']
    
    # Set up the figure with three subplots if attempts data is available
    has_attempts = 'attempts_by_block' in results
    num_plots = 3 if has_attempts else 2
    
    plt.figure(figsize=(12, 5 * num_plots))
    
    # Plot 1: Mean reaction time by block and block type
    plt.subplot(num_plots, 1, 1)
    
    # Get unique block types
    block_types = rt_by_block['block_type'].unique()
    
    for block_type in block_types:
        data = rt_by_block[rt_by_block['block_type'] == block_type]
        plt.plot(data['block'], data['reaction_time'], 
                marker='o', 
                linestyle='-' if block_type == 'structured' else '--',
                label=block_type.capitalize())
    
    plt.xlabel('Bloco')
    plt.ylabel('Tempo de Reação Médio (ms)')
    plt.title(f'Tempo de Reação por Bloco - Participante {participant_id}')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Plot 2: Accuracy by block and block type
    plt.subplot(num_plots, 1, 2)
    
    for block_type in block_types:
        data = accuracy_by_block[accuracy_by_block['block_type'] == block_type]
        plt.plot(data['block'], data['accuracy'], 
                marker='o', 
                linestyle='-' if block_type == 'structured' else '--',
                label=block_type.capitalize())
    
    plt.xlabel('Bloco')
    plt.ylabel('Precisão (%)')
    plt.title(f'Precisão por Bloco - Participante {participant_id}')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Plot 3: Attempts by block and block type (if data is available)
    if has_attempts:
        attempts_by_block = results['attempts_by_block']
        plt.subplot(num_plots, 1, 3)
        
        for block_type in block_types:
            data = attempts_by_block[attempts_by_block['block_type'] == block_type]
            plt.plot(data['block'], data['attempts'], 
                    marker='o', 
                    linestyle='-' if block_type == 'structured' else '--',
                    label=block_type.capitalize())
        
        plt.xlabel('Bloco')
        plt.ylabel('Número Médio de Tentativas')
        plt.title(f'Tentativas por Bloco - Participante {participant_id}')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
    
    # Adjust layout and save figure
    plt.tight_layout()
    
    # Create results directory if it doesn't exist
    if not os.path.exists('analysis'):
        os.makedirs('analysis')
    
    # Save figure
    plt.savefig(f'analysis/srtt_analysis_participant_{participant_id}.png', dpi=300)
    
    plt.show()
    
    # Generate a bar chart comparing structured vs random reaction times and attempts
    if has_attempts:
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        
        # First subplot: Reaction times
        ax1 = axs[0]
        rt_means = [results['structured_rt'], results['random_rt']]
        ax1.bar(['Estruturado', 'Aleatório'], rt_means, color=['blue', 'red'])
        ax1.set_ylabel('Tempo de Reação Médio (ms)')
        ax1.set_title('Tempo de Reação por Tipo de Bloco')
        
        # Second subplot: Attempts
        ax2 = axs[1]
        attempt_means = [results['structured_attempts'], results['random_attempts']]
        ax2.bar(['Estruturado', 'Aleatório'], attempt_means, color=['green', 'orange'])
        ax2.set_ylabel('Número Médio de Tentativas')
        ax2.set_title('Tentativas por Tipo de Bloco')
        
        fig.suptitle(f'Comparação entre Blocos - Participante {participant_id}', fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.9])  # Make room for the suptitle
        
        # Add learning effect text
        fig.text(0.5, 0.95, f'Efeito de aprendizagem: {results["learning_effect"]:.2f} ms', 
                ha='center', fontsize=12)
    else:
        # Original single plot for reaction times only
        plt.figure(figsize=(8, 6))
        
        rt_means = [results['structured_rt'], results['random_rt']]
        plt.bar(['Estruturado', 'Aleatório'], rt_means, color=['blue', 'red'])
        
        plt.ylabel('Tempo de Reação Médio (ms)')
        plt.title(f'Comparação entre Blocos - Participante {participant_id}')
        
        # Add learning effect text
        plt.annotate(f'Efeito de aprendizagem: {results["learning_effect"]:.2f} ms', 
                    xy=(0.5, 0.9), 
                    xycoords='figure fraction', 
                    ha='center')
    
    plt.savefig(f'analysis/srtt_learning_effect_participant_{participant_id}.png', dpi=300)
    plt.show()

def print_summary(results):
    """Print a summary of the analysis results"""
    print("\n" + "=" * 50)
    print(f"SRTT Analysis - Participant: {results['participant_id']}")
    print("=" * 50)
    
    print(f"\nMean Reaction Time:")
    print(f"  Structured blocks: {results['structured_rt']:.2f} ms")
    print(f"  Random blocks: {results['random_rt']:.2f} ms")
    print(f"  Learning effect: {results['learning_effect']:.2f} ms")
    
    print(f"\nMean Number of Attempts:")
    print(f"  Structured blocks: {results['structured_attempts']:.2f}")
    print(f"  Random blocks: {results['random_attempts']:.2f}")
    
    if results['learning_effect'] > 0:
        print("\nA positive learning effect indicates implicit learning of the sequence pattern.")
    else:
        print("\nNo significant learning effect detected.")
    
    print("\nDetailed results by block:")
    print(results['rt_by_block'])
    
    print("\nAccuracy by block:")
    print(results['accuracy_by_block'][['block', 'block_type', 'accuracy']])
    
    print("\nMean attempts by block:")
    print(results['attempts_by_block'])
    
    print("\n" + "=" * 50)
    print("Analysis complete. Visualizations have been saved to the 'analysis' folder.")
    print("=" * 50)

def export_summary(results, original_file_path):
    """Export a summary of the analysis results to a CSV file"""
    # Create analysis directory if it doesn't exist
    if not os.path.exists('analysis'):
        os.makedirs('analysis')
    
    # Get base filename without extension and directory
    base_filename = os.path.splitext(os.path.basename(original_file_path))[0]
    
    # Create summary filename
    summary_file = f"analysis/{base_filename}_summary.csv"
    
    # Prepare summary data
    summary_data = {
        'participant_id': [results['participant_id']],
        'structured_rt_mean': [results['structured_rt']],
        'random_rt_mean': [results['random_rt']],
        'learning_effect': [results['learning_effect']],
        'structured_attempts_mean': [results.get('structured_attempts', 1)],
        'random_attempts_mean': [results.get('random_attempts', 1)]
    }
    
    # Add block-specific data
    block_data = results['rt_by_block']
    for index, row in block_data.iterrows():
        block_num = row['block']
        block_type = row['block_type']
        rt = row['reaction_time']
        
        summary_data[f'block_{block_num}_{block_type}_rt'] = [rt]
    
    # Add accuracy data
    acc_data = results['accuracy_by_block']
    for index, row in acc_data.iterrows():
        block_num = row['block']
        block_type = row['block_type']
        acc = row['accuracy']
        
        summary_data[f'block_{block_num}_{block_type}_accuracy'] = [acc]
    
    # Add attempts data if available
    if 'attempts_by_block' in results:
        att_data = results['attempts_by_block']
        for index, row in att_data.iterrows():
            block_num = row['block']
            block_type = row['block_type']
            attempts = row['attempts']
            
            summary_data[f'block_{block_num}_{block_type}_attempts'] = [attempts]
    
    # Write to CSV
    pd.DataFrame(summary_data).to_csv(summary_file, index=False)
    
    print(f"\nSummary exported to: {summary_file}")

def main():
    print("SRTT Analysis Tool")
    print("=================")
    
    # Select result file
    file_path = select_result_file()
    
    if not file_path:
        print("No file selected. Exiting.")
        return
    
    print(f"Loading data from: {file_path}")
    
    # Load and analyze data
    data = load_data(file_path)
    
    if not data:
        print("No data found or file format invalid.")
        return
    
    print(f"Loaded {len(data)} trials. Analyzing...")
    
    # Analyze data
    results = analyze_data(data)
    
    # Print summary
    print_summary(results)
    
    # Export summary
    export_summary(results, file_path)
    
    # Generate visualizations
    generate_visualizations(results)

if __name__ == "__main__":
    main()
