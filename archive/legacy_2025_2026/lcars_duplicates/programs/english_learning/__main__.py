"""Entry point for the English Learning package.

The launcher simply invokes :func:`main` from ``main.py`` so that the
package can be executed with ``python -m lcars.programs.english_learning``
without importing any of the broken ``apps`` helpers.
"""

# entry point imports the launcher implementation
def main():
    # dynamically import to avoid circulars
    from .launcher import main as _launch
    return _launch()


if __name__ == "__main__":
    main()
