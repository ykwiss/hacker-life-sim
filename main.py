"""Entry point for Hacker Life Sandbox."""
from hacker_sim.ui import HackerApp


def main() -> None:
    app = HackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
