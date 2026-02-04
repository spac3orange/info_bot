from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """FSM for admin broadcast: wait for message text."""

    wait_text = State()
