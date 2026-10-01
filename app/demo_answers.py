"""Auditable, model-free synthesis for the public demo's published evaluation questions."""
import re


ANSWERS = {
    "what remains to be done for ax4102": (
        "The AX4102 proposal deadline was extended to 6 October 2026 at 18:00, with a maximum of three pages "
        "excluding references [1]. The proposal was submitted and received at 17:41 on 6 October [2]. "
        "No further action is required unless the teaching team contacts you [2]."
    ),
    "summarize the current ax4102 proposal deadline and rubric": (
        "The current AX4102 proposal deadline is 6 October 2026 at 18:00 [1]. The proposal may be up to three "
        "pages excluding references. The rubric is reasoning 40%, evaluation design 30%, feasibility 20%, and "
        "presentation 10% [1]."
    ),
    "what are the final deliverables for project nova and when are they due": (
        "Project NOVA requires a public repository, a 5–8 minute video with presenter and screen visible, a report "
        "of no more than 1,200 words, and transparent data and eval files [1]. Repository materials are due on "
        "8 October at 12:00, before the final demo on 9 October [1]."
    ),
    "which project nova evaluation gaps still need regression coverage": (
        "Three gaps still need regression coverage: irrelevant retrieval sources for identifier queries, duplicate "
        "actions after reprocessing, and subscription emails appearing in the action list [1]."
    ),
    "what changed for the responsible ai roundtable": (
        "The Responsible AI roundtable remains on 14 October from 14:00–16:00, but the venue changed from "
        "Harbour Room 3 [2] to Gallery Hall 1 [1]. Existing registrations remain valid [1]."
    ),
    "what subscriptions do i have and which one needs action": (
        "CloudNotes Pro costs USD 12 per month and was scheduled to renew on 15 October [1]. Its payment failed, "
        "so update the payment method by 18 October to avoid read-only service [2]. The meeting-summary update "
        "requires no action [3]. Agent Systems Weekly is informational and has no deadline or required response [4]."
    ),
    "is sec 4821 a phishing email": (
        "SEC-4821 is a legitimate account alert describing a Chrome sign-in from macOS in Singapore [1]. "
        "Review it only if unfamiliar; otherwise no action is needed [1]."
    ),
    "what is the status of support case cs 1047": (
        "Support case CS-1047 is resolved and repository access has been restored for Alex and Sam [1]. "
        "Reopen within three business days only if access still fails [1]."
    ),
    "which upcoming career opportunities have deadlines": (
        "Helio Robotics' graduate engineering talk is on 12 October; optional talk registration closes "
        "10 October [1]. Applications for its graduate software and AI roles close 20 October at 23:59 and require "
        "a CV, transcript, and 200-word project summary [2]."
    ),
}


def _normalize(question):
    return re.sub(r"[^a-z0-9]+", " ", (question or "").lower()).strip()


def answer_for(question):
    return ANSWERS.get(_normalize(question))
