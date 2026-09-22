"""Current projection; input and output shapes are defined in task.md."""
def apply(state, event):
    state[event["subject"]] = {"revision": event["revision"], "status": event["status"]}
