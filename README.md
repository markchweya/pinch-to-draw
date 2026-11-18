# Pinch to Draw

Draw on top of anything on your Windows screen, with no touchscreen needed.
Use the mouse, the touchpad, or **pinch your thumb and index finger in front of
the webcam** and draw in the air.

It works over any app, video, slide deck or browser tab, so it's handy for
presenting, teaching, screen recording or just pointing things out.

## Features

- **Pinch to draw with the webcam.** Google's MediaPipe tracks your hand, and a
  ring follows the point between your thumb and index finger. Pinch to draw,
  open your fingers to stop.
- **Smooth strokes.** The camera runs at 30 fps, a 1-Euro filter removes
  jitter, and the pen glides at 60 fps between camera frames.
- **Draw and Mouse modes.** In Draw mode the mouse draws. In Mouse mode clicks
  go straight through to your apps and your drawings stay on screen.
- **Tools:** pen, translucent highlighter, line, arrow, rectangle, ellipse,
  text and eraser. There are 8 colours and 4 thicknesses.
- **Undo and redo** for everything, including clear and erase.
- **Whiteboard and blackboard** backgrounds.
- **Screenshots** of your screen with the drawings, saved to `Pictures\PinchToDraw`.
- **Global hotkeys** that work from any app.
- Covers every monitor and handles display scaling (DPI aware).

## Install

You need Windows 10 or 11 and Python 3.10 or newer.

```bash
git clone https://github.com/markchweya/pinch-to-draw.git
cd pinch-to-draw
pip install -r requirements.txt
```

The first time you turn on pinch drawing, the app downloads Google's hand model
(about 8 MB) to `%LOCALAPPDATA%\PinchToDraw`.

## Run

Double-click `PinchToDraw.pyw`, or run:

```bash
python -m pinch_to_draw
```

## Pinch drawing

1. Click the camera button on the toolbar, or press **Ctrl+Alt+A**.
2. Hold your hand up in front of the camera. A preview appears in the
   bottom-right corner.
3. Move your hand inside the grey box in the preview. That box covers your
   whole screen.
4. **Pinch** to draw and **open** your fingers to stop.

More tips are in [docs/gestures.md](docs/gestures.md).

## Shortcuts

| Keys | Action |
|---|---|
| Ctrl+Alt+D | Switch Draw / Mouse mode |
| Ctrl+Alt+A | Pinch drawing on / off |
| Ctrl+Alt+Z | Undo |
| Ctrl+Alt+C | Clear all |
| Ctrl+Alt+H | Hide / show drawings |
| Ctrl+Alt+W | Whiteboard |
| Ctrl+Alt+Q | Quit |

The keys that work while you're in Draw mode are listed in
[docs/shortcuts.md](docs/shortcuts.md).

## How it works

The overlay is three see-through, always-on-top windows stacked over all your
monitors, with a toolbar on top. You can read how they fit together, and how the
hand tracking is smoothed, in [docs/how-it-works.md](docs/how-it-works.md).

## Troubleshooting

If the camera preview is black, the hotkeys don't respond, or the lines lag,
see [docs/troubleshooting.md](docs/troubleshooting.md).

## Development

```bash
pip install pytest
python -m pytest
```

The tests cover the logic that doesn't need a screen or a camera: filters,
gestures, geometry and undo history.

## License

MIT. See [LICENSE](LICENSE). The hand model is Google's MediaPipe Hand
Landmarker, released under the Apache 2.0 license.
