import time

class AnimationEngine:
    spinner_frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    def __init__(self):
        self.frame = 0
    def next_spinner(self):
        self.frame = (self.frame + 1) % len(self.spinner_frames)
        return self.spinner_frames[self.frame]
    def glow(self, text, color):
        # Simulate glow by alternating bold
        return color + ('\033[1m' if self.frame % 2 == 0 else '') + text + '\033[0m'
    def sleep(self, seconds):
        time.sleep(seconds)






