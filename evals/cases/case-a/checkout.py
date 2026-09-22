"""Two independent mechanisms. Provider records are the external ledger."""
from uuid import uuid4


class Provider:
    def __init__(self):
        self.charges = {}

    def capture(self, purchase_id, key):
        # The provider deduplicates by supplied key, not by purchase_id.
        if key not in self.charges:
            self.charges[key] = purchase_id
        raise TimeoutError("response lost after commit")


def checkout(provider, local_paid, purchase_id):
    attempt_key = str(uuid4())
    provider.capture(purchase_id, attempt_key)
    local_paid[purchase_id] = "paid"


def reconcile(provider, local_paid):
    return {purchase_id: purchase_id in provider.charges.values()
            for purchase_id in local_paid}


def project_seen(seen_events, event_id):
    # An unrelated in-memory projection; no external effect.
    seen_events.add(event_id)
