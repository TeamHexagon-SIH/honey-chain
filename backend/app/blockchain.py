import hashlib
import json


GENESIS_HASH = "GENESIS"


def calculate_event_hash(
    batch_id,
    event_type,
    location,
    description,
    previous_hash,
    created_at
):
    payload = {
        "batch_id": batch_id,
        "event_type": event_type,
        "location": location,
        "description": description,
        "previous_hash": previous_hash,
        "created_at": created_at.isoformat()
    }

    encoded_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    return hashlib.sha256(encoded_payload).hexdigest()


def verify_chain(events):
    if not events:
        return {
            "valid": False,
            "message": "No traceability events found."
        }

    previous_hash = GENESIS_HASH

    for event in events:

        # Check connection with previous event
        if event.previous_hash != previous_hash:
            return {
                "valid": False,
                "message": f"Chain broken at event {event.id}.",
                "failure_at_event": event.id
            }

        # Recalculate hash
        calculated_hash = calculate_event_hash(
            event.batch_id,
            event.event_type,
            event.location,
            event.description,
            event.previous_hash,
            event.created_at
        )

        # Compare calculated hash with stored hash
        if calculated_hash != event.current_hash:
            return {
                "valid": False,
                "message": f"Tampering detected at event {event.id}.",
                "failure_at_event": event.id
            }

        previous_hash = event.current_hash

    return {
        "valid": True,
        "message": "Traceability chain is valid.",
        "checked_events": len(events)
    }


def simulate_tampering(event):
    """
    Demo-only helper.
    Changes the event description without updating its stored hash.
    This should make chain verification fail.
    """
    event.description = event.description + " [TAMPERED FOR DEMO]"
    return event


def restore_demo_chain(events):
    """
    Restore a demo-tampered traceability chain.

    Recalculates every event hash in sequence while preserving
    the original event data and timestamps.
    """

    if not events:
        return {
            "valid": False,
            "message": "No traceability events found."
        }

    previous_hash = GENESIS_HASH

    for event in events:

        # Remove the demo tampering marker if present
        if event.description.endswith(" [TAMPERED FOR DEMO]"):
            event.description = event.description[
                :-len(" [TAMPERED FOR DEMO]")
            ]

        event.previous_hash = previous_hash

        event.current_hash = calculate_event_hash(
            event.batch_id,
            event.event_type,
            event.location,
            event.description,
            event.previous_hash,
            event.created_at
        )

        previous_hash = event.current_hash

    return verify_chain(events)