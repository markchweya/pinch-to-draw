# Troubleshooting

## The camera preview is black

- Open the privacy shutter over the lens, if your laptop has one.
- Close other apps that use the camera, such as Teams, Zoom or the Camera app.
- Check **Settings > Privacy & security > Camera** and make sure desktop apps
  are allowed to use it.
- Laptops with Windows Hello have a second, infrared camera that shows a dark
  picture. The app skips it, but if you have several cameras, unplug the one you
  don't want.

## The lines are jumpy or lag behind

- Add light in front of you. In a dark room the camera slows down to let in more
  light.
- Keep your hand inside the grey box in the preview.
- Close other heavy programs. Hand tracking takes about 15 ms per frame on the
  processor.

## A drawing starts when I don't pinch, or stops while I pinch

Change the thresholds in `pinch_to_draw/gestures.py` (`PinchDetector`):

- `close_below`: raise it if pinching is hard to trigger.
- `open_above`: raise it if strokes break while you pinch.

## Hotkeys don't work

Another program may own the same keys. The app lists any hotkeys it couldn't
register when it starts. The toolbar buttons always work.

## I can't click anything

You're in Draw mode. Press **Esc** or **Ctrl+Alt+D**, or click the blue **Draw**
button, to switch to Mouse mode.

## Antivirus warnings

The app registers global hotkeys and draws over the screen, so some security
tools may flag it. The code is in this repository and nothing is sent over the
network. The only download is the hand model from Google's servers.
