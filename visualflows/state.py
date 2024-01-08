shared_state = {"objects": {}}


def read_state(key):
    return shared_state.get(key)


def write_state(key, value):
    shared_state[key] = value


def get_state():
    return shared_state
