# Modified Snake Game

This is a classic "Snake" game enhanced with new features:
- **Bonuses** (acceleration and slowdown)
- **Mines (bombs)** with a timer and explosion animation
- **Obstacles** on the field

## Main Changes

### 1. Bonuses

There are two types of bonuses:

1. **Acceleration (ACCELERATION)**  
   When eaten, the snake temporarily moves faster (FPS is increased).  
   - Displayed as a **yellow** cube on the field.  
   - The duration of the effect is controlled by the `BONUS_DURATION` parameter.

2. **Slowdown (SLOWDOWN)**  
   When eaten, the snake temporarily moves slower (FPS is decreased).  
   - Displayed as a **cyan** cube on the field.  
   - The duration of the effect is the same `BONUS_DURATION`.
### 2. Mines (Bombs)

After the snake eats a regular snack (green food), there is a certain chance (**`MINE_APPEAR_CHANCE`**) that a mine will spawn (up to **`MINE_MAX_COUNT = 3`** mines).
- The mine is placed on a free cell at least **`MINE_REQUIRED_DISTANCE`** away from the snake’s head.  
- Each mine has a lifespan (**`MINE_LIFETIME_TICKS`** = 120 ticks, ~12 seconds at 10 FPS). When its time runs out, it explodes.
- When the mine explodes, an animation is displayed (expanding circle). If the snake’s head is within 1-cell radius of the explosion, the snake loses (game over).
- If the snake steps on the mine before it explodes, that also results in a game over.

### 3. Obstacles

Several (by default **`OBSTACLE_COUNT = 10`**) gray "cubes" are placed randomly on the field. If the snake collides with any obstacle, it’s game over:
- The final score (snake length) is displayed.
- The snake is reset to its starting state.

