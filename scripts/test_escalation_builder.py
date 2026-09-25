from app.triage.query_triage import (
    LegalQueryTriage
)

from app.triage.escalation_builder import (
    EscalationBuilder
)


# ==============================================
# Components
# ==============================================

triage = (
    LegalQueryTriage()
)


builder = (
    EscalationBuilder()
)


# ==============================================
# Test urgent query
# ==============================================

query = (
    "Someone is threatening to kill me "
    "right now. What should I do?"
)


decision = triage.classify(
    query,
    retrieval_results=None
)


payload = builder.build(

    query=query,

    stage="pre_triage",

    triage=decision,

    retrieval_results=[]
)


# ==============================================
# Output
# ==============================================

print(
    "\n===================================="
)

print(
    "HUMAN ESCALATION PAYLOAD"
)

print(
    "===================================="
)


print(
    "Type:",
    payload[
        "type"
    ]
)


print(
    "Status:",
    payload[
        "status"
    ]
)


print(
    "Priority:",
    payload[
        "priority"
    ]
)


print(
    "Category:",
    payload[
        "category"
    ]
)


print(
    "Routing stage:",
    payload[
        "routing_stage"
    ]
)


print(
    "Urgent:",
    payload[
        "triage"
    ][
        "urgent"
    ]
)


print(
    "Retrieved provisions:",
    len(
        payload[
            "retrieved_provisions"
        ]
    )
)


print(
    "Assigned to:",
    payload[
        "assignment"
    ][
        "assigned_to"
    ]
)


print(
    "Resolved:",
    payload[
        "resolution"
    ][
        "resolved"
    ]
)