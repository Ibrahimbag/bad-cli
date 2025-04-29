import argparse
import curses
import cv2
from sys import exit
from time import sleep
from ffpyplayer.player import MediaPlayer

FILE_NAME = "bad-apple.mp4"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--curses-clear",
        help="Uses the clear method comes with curses instead of escape sequence. "
        "This option prevents flickering in some terminals (But causes more in most.)",
        action="store_true",
    )
    return parser.parse_args()


def init_curses():
    stdscr = curses.initscr()
    stdscr.nodelay(1)
    curses.cbreak()
    curses.noecho()
    curses.curs_set(False)

    curses.start_color()
    if curses.has_colors() == False:
        print("Terminal can't display color")
        exit(2)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    return stdscr


def play_video(stdscr, args):
    cap = cv2.VideoCapture(FILE_NAME)
    player = MediaPlayer(FILE_NAME)

    if not cap.isOpened():
        print("Error: Could not open video.")
        exit(3)

    key = 0
    while cap.isOpened() and key != 27:  # ESC key
        success, image = cap.read()
        height, width = stdscr.getmaxyx()

        if success:
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            for y in range(height):
                for x in range(width):
                    pixel_color = image[y, x]
                    try:
                        if pixel_color > 127:
                            stdscr.addstr(y, x, " ", curses.color_pair(1))
                        else:
                            stdscr.addstr(y, x, " ", curses.color_pair(2))
                    except curses.error:
                        pass
        else:
            break

        stdscr.refresh()
        key = stdscr.getch()

        frame_delay = 1 / cap.get(cv2.CAP_PROP_FPS)
        audio_frame, val = player.get_frame()
        if val != "eof" and audio_frame is not None:
            _, pts = audio_frame
            sleep(max(0, frame_delay - (player.get_pts() - pts)))
        else:
            sleep(frame_delay)

        if args.curses_clear:
            stdscr.clear()
        else:
            print("\033c", end="")

    cap.release()


def end_curses():
    curses.nocbreak()
    curses.echo()
    curses.endwin()


def main():
    args = parse_args()
    stdscr = init_curses()
    play_video(stdscr, args)
    end_curses()


if __name__ == "__main__":
    main()
