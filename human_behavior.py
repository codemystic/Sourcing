"""
Human Behavior Simulation Module
Provides realistic human-like interactions for web scraping
"""

import random
import time
from playwright.sync_api import Page

class HumanBehavior:
    """Simulates realistic human browsing behavior"""
    
    @staticmethod
    def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay between actions (human-like pauses)"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def human_type(element, text, min_delay=100, max_delay=300):
        """Type text with random delays like a human"""
        for char in text:
            element.type(char, delay=random.randint(min_delay, max_delay))
            # Occasionally pause longer (thinking)
            if random.random() < 0.1:  # 10% chance of longer pause
                time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def human_scroll(page: Page, target_position: int, viewport_height: int = 1080):
        """Scroll like a human - variable speed, occasional pauses, micro-adjustments"""
        current_position = page.evaluate("window.pageYOffset")
        distance = target_position - current_position
        
        # Determine scroll direction
        direction = 1 if distance > 0 else -1
        distance = abs(distance)
        
        # Human-like scroll: variable chunks, random pauses
        scrolled = 0
        while scrolled < distance:
            # Variable scroll amount (humans don't scroll uniformly)
            chunk = random.randint(80, 250)
            if distance - scrolled < chunk:
                chunk = distance - scrolled
            
            scroll_to = current_position + (direction * (scrolled + chunk))
            page.evaluate(f"window.scrollTo(0, {scroll_to})")
            
            scrolled += chunk
            
            # Variable delay between scrolls
            time.sleep(random.uniform(0.1, 0.4))
            
            # Occasionally pause to "read" content (10% chance)
            if random.random() < 0.1:
                time.sleep(random.uniform(1.0, 2.5))
            
            # Micro-adjustments (5% chance) - humans sometimes scroll back slightly
            if random.random() < 0.05:
                micro_adjust = random.randint(-30, 30)
                page.evaluate(f"window.scrollBy(0, {micro_adjust})")
                time.sleep(random.uniform(0.1, 0.3))
    
    @staticmethod
    def move_mouse_naturally(page: Page, target_x: float, target_y: float, duration: float = 3.0):
        """Move mouse cursor naturally to target position over specified duration"""
        try:
            print(f"  👁️  Moving mouse naturally to position ({target_x}, {target_y})...")
            
            # Get current mouse position (start from center of screen)
            start_x, start_y = 640, 360  # Approximate center
            
            # Calculate number of steps based on duration (30 steps per second)
            steps = int(duration * 30)
            
            for i in range(steps):
                # Calculate progress (0 to 1)
                progress = i / steps
                
                # Use easing function for natural movement (ease-in-out)
                eased_progress = progress * progress * (3 - 2 * progress)
                
                # Calculate current position with slight randomness
                current_x = start_x + (target_x - start_x) * eased_progress
                current_y = start_y + (target_y - start_y) * eased_progress
                
                # Add small random jitter for human-like movement
                jitter_x = random.uniform(-2, 2)
                jitter_y = random.uniform(-2, 2)
                
                # Move mouse
                page.mouse.move(current_x + jitter_x, current_y + jitter_y)
                
                # Small delay between movements
                time.sleep(duration / steps)
            
            # Final precise movement to target
            page.mouse.move(target_x, target_y)
            print(f"  ✓ Mouse moved to target position")
            time.sleep(random.uniform(0.05, 0.15))
            return True
            
        except Exception as e:
            print(f"  ⚠️  Error moving mouse: {e}")
            return False
    
    @staticmethod
    def random_page_actions(page: Page):
        """Perform random human-like actions: slight scrolls, mouse movements, pauses"""
        actions = [
            lambda: page.evaluate(f"window.scrollBy(0, {random.randint(-50, 50)})"),
            lambda: page.mouse.move(random.randint(100, 1000), random.randint(100, 800)),
            lambda: time.sleep(random.uniform(0.5, 2.0))
        ]
        
        # Perform 1-3 random actions
        for _ in range(random.randint(1, 3)):
            random.choice(actions)()
            time.sleep(random.uniform(0.2, 0.5))
    
    @staticmethod
    def human_click(element, pre_click_delay=(0.5, 1.5), post_click_delay=(0.5, 2.0)):
        """Click with human-like delays before and after"""
        if pre_click_delay:
            time.sleep(random.uniform(*pre_click_delay))
        
        element.click()
        
        if post_click_delay:
            time.sleep(random.uniform(*post_click_delay))
    
    @staticmethod
    def human_hover(element, hover_duration=(1.0, 3.0)):
        """Hover over element with human-like duration"""
        element.hover()
        time.sleep(random.uniform(*hover_duration))
    
    @staticmethod
    def simulate_reading(time_per_line=0.2, lines=5):
        """Simulate reading content"""
        reading_time = random.uniform(time_per_line * lines, time_per_line * lines * 2)
        time.sleep(reading_time)
    
    @staticmethod
    def simulate_thinking(think_time=(2.0, 5.0)):
        """Simulate thinking/pause"""
        time.sleep(random.uniform(*think_time))

# Export the function for direct use
move_mouse_naturally = HumanBehavior.move_mouse_naturally