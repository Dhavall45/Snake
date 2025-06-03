import streamlit as st
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

def snake_game():
    st.title("🐍 Snake Game")
    st.markdown("Use keyboard arrow keys or the buttons below to control the snake. Eat the food (red) to grow!")
    
    # Initialize game state
    if 'game_state' not in st.session_state:
        reset_game()
    
    # Game parameters
    grid_size = 20
    cell_size = 0.9
    speed = st.sidebar.slider("Game Speed", 0.1, 1.0, 0.3)
    
    # Create layout
    game_placeholder = st.empty()
    col1, col2, col3 = st.columns(3)  # Columns for New Game, Score, and Pause
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
    
    # Add arrow buttons for snake control with keyboard-like layout
    st.markdown("**Control Snake:**")
    
    # Custom CSS for arrow button alignment
    st.markdown("""
        <style>
        .arrow-buttons {
            display: grid;
            grid-template-columns: 50px 50px 50px;
            grid-template-rows: 50px 50px;
            gap: 5px;
            justify-content: center;
            margin-top: 10px;
        }
        .arrow-buttons .up {
            grid-column: 2;
            grid-row: 1;
        }
        .arrow-buttons .left {
            grid-column: 1;
            grid-row: 2;
        }
        .arrow-buttons .right {
            grid-column: 3;
            grid-row: 2;
        }
        .arrow-buttons .down {
            grid-column: 2;
            grid-row: 2;
        }
        .arrow-buttons button {
            padding: 10px;
            font-size: 16px;
            text-align: center;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Container for arrow buttons
    with st.container():
        st.markdown('<div class="arrow-buttons">', unsafe_allow_html=True)
        col_up, col_left, col_right, col_down = st.columns([1, 1, 1, 1])
        with col_up:
            if st.button("↑ Up", key="up_button"):
                handle_direction_change("down")
            st.markdown('<div class="up"></div>', unsafe_allow_html=True)
        with col_left:
            if st.button("← Left", key="left_button"):
                handle_direction_change("left")
            st.markdown('<div class="left"></div>', unsafe_allow_html=True)
        with col_right:
            if st.button("→ Right", key="right_button"):
                handle_direction_change("right")
            st.markdown('<div class="right"></div>', unsafe_allow_html=True)
        with col_down:
            if st.button("↓ Down", key="down_button"):
                handle_direction_change("up")
            st.markdown('<div class="down"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main game loop
    while True:
        # Handle keyboard input
        key = get_key_press()
        if key == " ":  # Spacebar to pause/resume
            st.session_state.game_state['paused'] = not st.session_state.game_state.get('paused', False)
            if st.session_state.game_state['paused']:
                st.info("Game Paused")
            else:
                st.success("Game Resumed")
        elif key in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"] and not st.session_state.game_state.get('game_over', False):
            new_direction = key.replace("Arrow", "").lower()
            handle_direction_change(new_direction)
        
        if st.session_state.game_state.get('paused', False) or st.session_state.game_state.get('game_over', False):
            draw_game(game_placeholder, grid_size, cell_size)  # Keep drawing the current state
            time.sleep(0.1)  # Small sleep to prevent busy-waiting
            continue  # Skip game logic if paused or game over
        
        # Move snake
        move_snake()
        
        # Check for collisions
        if check_collision():
            game_over()
            break
        
        # Check if snake ate food
        if (st.session_state.game_state['snake'][0][0] == st.session_state.game_state['food'][0] and 
            st.session_state.game_state['snake'][0][1] == st.session_state.game_state['food'][1]):
            st.session_state.game_state['score'] += 1
            st.session_state.game_state['snake'].append(st.session_state.game_state['snake'][-1])  # Grow snake
            place_food()
        
        # Draw game
        draw_game(game_placeholder, grid_size, cell_size)
        
        # Control game speed
        time.sleep(speed)

def reset_game():
    st.session_state.game_state = {
        'snake': [[10, 10], [10, 9], [10, 8]],  # Initial snake position
        'direction': 'right',  # Initial direction
        'food': [5, 5],  # Initial food position
        'score': 0,
        'paused': False,
        'game_over': False
    }

def handle_direction_change(new_direction):
    # Prevent 180-degree turns
    opposite_dirs = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
    if new_direction != opposite_dirs.get(st.session_state.game_state['direction'], ""):
        st.session_state.game_state['direction'] = new_direction

def move_snake():
    head = st.session_state.game_state['snake'][0].copy()
    
    # Move head based on direction
    if st.session_state.game_state['direction'] == 'up':
        head[0] -= 1
    elif st.session_state.game_state['direction'] == 'down':
        head[0] += 1
    elif st.session_state.game_state['direction'] == 'left':
        head[1] -= 1
    elif st.session_state.game_state['direction'] == 'right':
        head[1] += 1
    
    # Update snake position
    st.session_state.game_state['snake'].insert(0, head)
    st.session_state.game_state['snake'].pop()

def check_collision():
    head = st.session_state.game_state['snake'][0]
    
    # Check wall collision
    if (head[0] < 0 or head[0] >= 20 or 
        head[1] < 0 or head[1] >= 20):
        return True
    
    # Check self collision
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
    
    placeholder.pyplot(fig)
    plt.close(fig)

def game_over():
    st.session_state.game_state['game_over'] = True
    st.error(f"Game Over! Final Score: {st.session_state.game_state['score']}")
    st.balloons()

def get_key_press():
    key = st.session_state.get('key_pressed', None)
    st.session_state.key_pressed = None  # Reset after reading
    return key

# JavaScript for keypress detection
key_js = """
<script>
document.addEventListener('keydown', function(e) {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
        Streamlit.setComponentValue(e.key);
    }
});
</script>
"""

# Create a component to capture keypresses
st.components.v1.html(key_js, height=0, width=0)

# Initialize the game
if __name__ == "__main__":
    snake_game()