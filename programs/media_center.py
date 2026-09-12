"""
Media center placeholder program - lightweight scaffold.

This file provides a minimal entrypoint for the media center so
developers can continue work while a full media backend is restored.
"""
import importlib


def run_media_center():
    try:
        mh = importlib.import_module("tools.media_hub")
        if hasattr(mh, "main"):
            mh.main()
        else:
            print("tools.media_hub loaded but no main(); using placeholder.")
            placeholder()
    except Exception as e:
        print("MediaHub import error:", e)
        placeholder()


def placeholder():
    print("MediaCenter placeholder: no media backend available.")


if __name__ == "__main__":
    run_media_center()
