"""Internal browser stub (wraps lcars_web_browser)
"""
from programs.lcars_web_browser import launch as launch_browser

if __name__ == "__main__":
    # simply delegate to existing web browser program
    launch_browser()