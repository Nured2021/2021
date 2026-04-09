# Theme definitions for ODEX UI

class Theme:
    CYAN = '\033[96m'
    GOLD = '\033[93m'
    EMERALD = '\033[92m'
    RUBY = '\033[91m'
    NAVY = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def color_text(text, color, bold=False):
        style = color
        if bold:
            style += Theme.BOLD
        return f"{style}{text}{Theme.RESET}"






