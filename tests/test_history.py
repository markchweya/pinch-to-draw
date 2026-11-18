from pinch_to_draw.history import History


class FakeCanvas:
    def __init__(self):
        self.state = {}
        self.deleted = set()

    def itemconfigure(self, item, state):
        self.state[item] = state

    def delete(self, item):
        self.deleted.add(item)


def test_undo_hides_drawn_items_and_redo_shows_them():
    c, h = FakeCanvas(), History()
    h.push("add", [(c, 1)])
    assert h.undo()
    assert c.state[1] == "hidden"
    assert h.redo()
    assert c.state[1] == "normal"


def test_undo_of_erase_brings_items_back():
    c, h = FakeCanvas(), History()
    h.push("hide", [(c, 7), (c, 8)])
    h.undo()
    assert c.state == {7: "normal", 8: "normal"}


def test_new_action_discards_redo_and_deletes_undone_drawings():
    c, h = FakeCanvas(), History()
    h.push("add", [(c, 1)])
    h.undo()
    h.push("add", [(c, 2)])
    assert c.deleted == {1}
    assert not h.redo()


def test_empty_pushes_are_ignored():
    h = History()
    h.push("hide", [])
    assert not h.undo()


def test_undo_on_empty_history():
    assert History().undo() is False
