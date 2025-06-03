import streamlit as st
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

def snake_game():
    st.title("🐍 Snake Game")
    st.markdown("Use arrow keys to move the snake. Eat the red food to grow! Press **Space** to pause/resume, **R** to restart after game over.")
    
    # Initialize game state
    if 'game_state' not in st.session_state:
        reset_game()
    
    # Game parameters
    grid_size = 20
    cell_size = 0.9
    speed = st.sidebar.slider("Game Speed", 0.1, 1.0, 0.3)
    
    # Create layout
    game_placeholder = st.empty()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("New Game"):
            reset_game()
    with col2:
        st.markdown(f"**Score:** {st.session_state.game_state['score']}")
    with col3:
        if st.button("Pause/Resume"):
            st.session_state.game_state['paused'] = not st.session_state.game_state.get('paused', False)
            if st.session_state.game_state['paused']:
                st.info("Game Paused")
            else:
                st.success("Game Resumed")
    
    # Main game loop
    last_key_time = time.time()  # For debouncing
    key_debounce = 0.1  # Minimum time between keypresses (seconds)
    
    while True:
        # Handle keyboard input
        key = get_key_press()
        current_time = time.time()
        
        if key and (current_time - last_key_time >= key_debounce):
            last_key_time = current_time
            if key == " " and not st.session_state.game_state.get('game_over', False):  # Spacebar to pause/resume
                st.session_state.game_state['paused'] = not st.session_state.game_state.get('paused', False)
                if st.session_state.game_state['paused']:
                    st.info("Game Paused")
                else:
                    st.success("Game Resumed")
            elif key == "r" and st.session_state.game_state.get('game_over', False):  # R to restart
                reset_game()
                st.success("Game Restarted!")
            elif key in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"] and not st.session_state.game_state.get('game_over', False):
                new_direction = key.replace("Arrow", "").lower()
                # Prevent 180-degree turns
                opposite_dirs = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
                if new_direction != opposite_dirs.get(st.session_state.game_state['direction'], ''):
                    st.session_state.game_state['direction'] = new_direction
        
        if st.session_state.game_state.get('paused', False) or st.session_state.game_state.get('game_over', False):
            draw_game(game_placeholder, grid_size, cell_size)
            time.sleep(0.1)
            continue
        
        # Move snake
        move_snake()  # This now correctly references the function below
        
        # Check for collisions
        if check_collision():
            game_over()
            break
        
        # Check if snake ate food
        if (st.session_state.game_state['snake'][0][0] == st.session_state.game_state['food'][0] and 
            st.session_state.game_state['snake'][0][1] == st.session_state.game_state['food'][1]):
            st.session_state.game_state['score'] += 1
            st.session_state.game_state['snake'].append(st.session_state.game_state['snake'][-1])
            place_food()
        
        # Draw game
        draw_game(game_placeholder, grid_size, cell_size)
        
        # Control game speed
        time.sleep(speed)

def reset_game():
    st.session_state.game_state = {
        'snake': [[10, 10], [10, 9], [10, 8]],
        'direction': 'right',
        'food': [5, 5],
        'score': 0,
        'paused': False,
        'game_over': False
    }

def move_snake():  # Renamed from 'Vũ' to 'move_snake'
    head = st.session_state.game_state['snake'][0].copy()
    
    if st.session_state.game_state['direction'] == 'up':
        head[0] -= 1
    elif st.session_state.game_state['direction'] == 'down':
        head[0] += 1
    elif st.session_state.game_state['direction'] == 'left':
        head[1] -= 1
    elif st.session_state.game_state['direction'] == 'right':
        head[1] += 1
    
    st.session_state.game_state['snake'].insert(0, head)
    st.session_state.game_state['snake'].pop()

def check_collision():
    head = st.session_state.game_state['snake'][0]
    
    if (head[0] < 0 or head[0] >= 20 or 
        head[1] < 0 or head[1] >= 20):
        return True
    
    if head in st.session_state.game_state['snake'][1:]:
        return True
    
    return False

def place_food():
    while True:
        food = [np.random.randint(0, 20), np.random.randint(0, 20)]
        if food not in st.session_state.game_state['snake']:
            st.session_state.game_state['food'] = food
            break

def draw_game(placeholder, grid_size, cell_size):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)
    ax.set_xticks(np.arange(0, grid_size+1, 1))
    ax.set_yticks(np.arange(0, grid_size+1, 1))
    ax.grid(True)
    ax.set_facecolor('#f0f0f0')
    ax.tick_params(axis='both', which='both', length=0, labelsize=0)
    
    # Draw snake
    for segment in st.session_state.game_state['snake']:
        rect = Rectangle((segment[1], segment[0]), cell_size, cell_size, 
                        facecolor='#4CAF50', edgecolor='#388E3C', linewidth=2)
        ax.add_patch(rect)
    
    # Draw head
    head = st.session_state.game_state['snake'][0]
    head_rect = Rectangle((head[1], head[0]), cell_size, cell_size, 
                         facecolor='#2E7D32', edgecolor='#1B5E20', linewidth=2)
    ax.add_patch(head_rect)
    
    # Draw eyes on head
    eye_offset = 0.2
    if st.session_state.game_state['direction'] == 'right':
        eye1 = Circle((head[1] + 0.7, head[0] + 0.7), 0.1, color='white')
        eye2 = Circle((head[1] + 0.7, head[0] + 0.3), 0.1, color='white')
    elif st.session_state.game_state['direction'] == 'left':
        eye1 = Circle((head[1] + 0.3, head[0] + 0.7), 0.1, color='white')
        eye2 = Circle((head[1] + 0.3, head[0] + 0.3), 0.1, color='white')
    elif st.session_state.game_state['direction'] == 'up':
        eye1 = Circle((head[1] + 0.3, head[0] + 0.7), 0.1, color='white')
        eye2 = Circle((head[1] + 0.7, head[0] + 0.7), 0.1, color='white')
    else:  # down
        eye1 = Circle((head[1] + 0.3, head[0] + 0.3), 0.1, color='white')
        eye2 = Circle((head[1] + 0.7, head[0] + 0.3), 0.1, color='white')
    ax.add_patch(eye1)
    ax.add_patch(eye2)
    
    # Draw food
    food = st.session_state.game_state['food']
    food_circle = Circle((food[1] + 0.5, food[0] + 0.5), 0.4, 
                        facecolor='#FF5252', edgecolor='#D32F2F', linewidth=2)
    ax.add_patch(food_circle)
    
    # Display game over message on canvas if applicable
    if st.session_state.game_state.get('game_over', False):
        ax.text(grid_size/2, grid_size/2, f"Game Over!\nScore: {st.session_state.game_state['score']}\nPress R to Restart", 
                ha='center', va='center', fontsize=14, color='red', weight='bold')
    
    placeholder.pyplot(fig)
    plt.close(fig)

def game_over():
    st.session_state.game_state['game_over'] = True
    st.error(f"Game Over! Final Score: {st.session_state.game_state['score']}. Press R to restart.")
    st.balloons()

def get_key_press():
    key = st.session_state.get('key_pressed', None)
    st.session_state.key_pressed = None
    return key

# JavaScript for keypress detection
key_js = """
<script>
document.addEventListener('keydown', function(e) {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'r'].includes(e.key)) {
        Streamlit.setComponentValue(e.key);
        e.preventDefault(); // Prevent default browser behavior (e.g., scrolling)
    }
});
</script>
"""

# Create a component to capture keypresses
st.components.v1.html(key_js, height=0, width=0)

# Initialize the game
if __name__ == "__main__":
    snake_game()