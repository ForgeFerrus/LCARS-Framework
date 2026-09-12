"""
MediaHub runner wrapper (scaffold).

Simple wrapper that imports `tools.media_hub` and calls `main()` if available.
"""


def main():
    try:
        import tools.media_hub as mh
        if hasattr(mh, "main"):
            mh.main()
        else:
            print("tools.media_hub present but no main()")
    except Exception as e:
        print("Failed to import tools.media_hub:", e)


if __name__ == "__main__":
    main()
