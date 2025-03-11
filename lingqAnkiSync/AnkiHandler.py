import os
from aqt import mw
from anki.notes import Note
from anki.cards import Card
from typing import List
from .Models.AnkiCard import AnkiCard


def create_notes_from_cards(cards: List[AnkiCard], deck_name: str) -> int:
    return sum(create_note(card, deck_name) == True for card in cards)


def create_note(card: AnkiCard, deck_name: str) -> bool:
    if does_duplicate_card_exist_in_deck(card.primary_key, deck_name):
        return False
    model_name = "lingqAnkiSync"
    note_fields = [
        "Front",
        "Back",
        "LingqPK",
        "LingqStatus",
        "Sentence",
        "LingqImportance",
        "FrontAudio",
        "SentenceAudio",
    ]
    create_note_type_if_not_exist(model_name, note_fields)

    model = mw.col.models.by_name(model_name)
    note = Note(mw.col, model)

    note["Front"] = card.word
    note["Back"] = "<br>".join(f"{i+1}. {item}" for i, item in enumerate(card.translations))
    note["LingqPK"] = str(card.primary_key)
    note["LingqStatus"] = str(card.status)
    note.tags = card.tags
    note["Sentence"] = card.sentence
    note["LingqImportance"] = str(card.importance)

    deck_id = mw.col.decks.id(deck_name)
    note.note_type()["did"] = deck_id
    mw.col.add_note(note, deck_id)
    if card.interval > 0:
        mw.col.sched.set_due_date([note.id], str(card.interval))
    return True


def does_duplicate_card_exist_in_deck(lingq_pk, deck_name):
    return len(mw.col.find_cards(f'deck:"{deck_name}" LingqPK:"{lingq_pk}"')) > 0


def create_note_type(name: str, fields: List):
    model = mw.col.models.new(name)

    for field in fields:
        mw.col.models.addField(model, mw.col.models.newField(field))

    template = mw.col.models.new_template("lingqAnkiSync")
    resource_folder = os.path.dirname(__file__) + "/resources"

    with open(resource_folder + "/style.css", "r") as f:
        model["css"] = f.read()

    with open(resource_folder + "/front.html", "r") as f:
        template["qfmt"] = f.read()

    with open(resource_folder + "/back.html", "r") as f:
        template["afmt"] = f.read()

    mw.col.models.add_template(model, template)
    mw.col.models.add(model)
    mw.col.models.set_current(model)
    mw.col.models.save(model)
    return model


def create_note_type_if_not_exist(note_type_name: str, note_fields: List):
    if not mw.col.models.by_name(note_type_name):
        create_note_type(note_type_name, note_fields)


def update_card_status(deck_name: str, lingq_pk: int, status: str):
    card_id = mw.col.find_cards(f'deck:"{deck_name}" LingqPK:"{lingq_pk}"')[0]
    card = mw.col.get_card(card_id)
    card.note()["LingqStatus"] = status
    mw.col.update_note(card.note())


def get_all_cards_in_deck(deck_name: str) -> List[AnkiCard]:
    cards = []
    card_ids = mw.col.find_cards(f'deck:"{deck_name}"')
    for card_id in card_ids:
        card = mw.col.get_card(card_id)
        card = _create_anki_card_object(card, card_id)
        cards.append(card)
    return cards


def get_all_deck_names() -> List[str]:
    return [x.name for x in mw.col.decks.all_names_and_ids()]


def get_interval_from_card(card_id: int) -> int:
    interval = mw.col.db.scalar("select ivl from cards where id = ?", card_id)
    return 0 if interval is None else interval


def _create_anki_card_object(card: Card, card_id: int) -> AnkiCard:
    return AnkiCard(
        int(card.note()["LingqPK"]),
        card.note()["Front"],
        card.note()["Back"],
        get_interval_from_card(card_id),
        card.note()["LingqStatus"],
        card.note().tags,
        card.note()["Sentence"],
        card.note()["LingqImportance"],
    )
