# How it works

## Three windows

A drawing app that floats over everything has one problem to solve. Windows
lets mouse clicks pass through pixels that are fully transparent. That's what we
want in Mouse mode, but in Draw mode it means nothing can be drawn on the empty
parts of the screen. So the overlay is a stack of borderless, always-on-top
windows that cover every monitor:

| Window | Job |
|---|---|
| **catcher** | 1% opaque, so it's invisible but still catches the mouse in Draw mode. It also serves as the whiteboard or blackboard. It's hidden in Mouse mode. |
| **highlight** | Holds the highlighter strokes at 42% opacity, so text shows through. It always lets clicks through. |
| **ink** | Holds the solid strokes. One colour is set as see-through, so only the strokes show. Clicks pass through it in Mouse mode. |
| **toolbar** | The controls. It never steals focus from the app you're using. |

The click-through behaviour comes from the Win32 extended window styles
`WS_EX_LAYERED` and `WS_EX_TRANSPARENT`. They're set with `ctypes` in
`pinch_to_draw/win32.py`.

## From camera to pen

```
webcam (30 fps) -> MediaPipe hand landmarks -> pinch gap and pinch point
     -> 1-Euro filter -> 60 fps follower -> canvas stroke -> tail trim
```

1. **Camera** (`camera.py`): Media Foundation delivers about 30 fps on most
   laptops, while DirectShow often gives 10. Laptops usually have a dark
   infrared camera for Windows Hello as well, so each camera is checked for a
   real colour picture.
2. **Hand landmarks** (`tracker.py`): the MediaPipe Hand Landmarker finds 21
   points on your hand in each frame, in a background thread.
3. **Pinch** (`gestures.py`): the gap between the thumb and index fingertips is
   divided by the length of the palm, so it reads the same near or far from the
   camera. Hysteresis and a frame count keep the pinch from flickering.
4. **Smoothing** (`filters.py`): the 1-Euro filter smooths heavily when your
   hand is still and lightly when it moves fast. A follower moves the pen part
   of the way to its target every 16 ms, which fills the gaps between camera
   frames.
5. **Tail trim** (`air.py`): the last 120 ms of a stroke are dropped. Those
   points were drawn while your fingers were opening, and they leave a hook.
