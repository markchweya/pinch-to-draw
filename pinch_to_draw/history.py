"""Undo / redo for canvas items.

Every action is a kind plus a list of (canvas, item_id) pairs:
  "add"  - items were drawn (undo hides them)
  "hide" - items were erased or cleared (undo shows them again)
Nothing is deleted until it can no longer be redone.
"""


class History:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, kind, items):
        if not items:
            return
        self.undo_stack.append((kind, list(items)))
        for old_kind, old_items in self.redo_stack:
            if old_kind == "add":  # undone drawings can never come back now
                for canvas, item in old_items:
                    canvas.delete(item)
        self.redo_stack.clear()

    @staticmethod
    def _show(action, reverse):
        kind, items = action
        visible = (kind == "add") != reverse
        for canvas, item in items:
            canvas.itemconfigure(item, state="normal" if visible else "hidden")

    def undo(self):
        if not self.undo_stack:
            return False
        action = self.undo_stack.pop()
        self._show(action, reverse=True)
        self.redo_stack.append(action)
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        action = self.redo_stack.pop()
        self._show(action, reverse=False)
        self.undo_stack.append(action)
        return True
