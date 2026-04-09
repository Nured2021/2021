import os
import sys
import time
from ui.theme import Theme
from ui.animation import AnimationEngine

class UIRenderer:
    def __init__(self, live_state):
        self.state = live_state
        self.anim = AnimationEngine()
        self.theme = Theme()
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    def render_spinner(self):
        spinner = self.anim.next_spinner()
        return self.theme.color_text(f" {spinner} ", Theme.CYAN, bold=True)
    def render_pipeline(self):
        out = []
        for idx, stage in enumerate(self.state.stages):
            status = self.state.stage_status[idx]
            color = Theme.NAVY
            if status == 'active':
                color = Theme.CYAN if stage != 'DEPLOY' else Theme.GOLD
            elif status == 'done':
                color = Theme.EMERALD
            elif status == 'error':
                color = Theme.RUBY
            txt = self.theme.color_text(stage, color, bold=(status=='active'))
            out.append(txt)
        return ' → '.join(out)
    def render_logs(self):
        out = []
        for log in self.state.logs:
            color = Theme.CYAN
            if 'error' in log.lower():
                color = Theme.RUBY
            elif 'deploy' in log.lower():
                color = Theme.GOLD
            elif 'complete' in log.lower() or 'success' in log.lower():
                color = Theme.EMERALD
            out.append(self.theme.color_text(log, color))
        return '\n'.join(out)
    def render(self):
        self.clear()
        print(self.render_spinner(), end=' ')
        print(self.render_pipeline())
        print('-'*60)
        print(self.render_logs())
    def run_loop(self):
        while True:
            self.render()
            self.anim.sleep(0.2)






