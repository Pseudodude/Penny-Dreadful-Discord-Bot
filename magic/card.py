import copy
import unicodedata

from munch import Munch

# Properties of the various aspects of cards with information about how to store and retrieve them from the database.

BOOLEAN = 'INTEGER'
DATE = 'INTEGER'
INTEGER = 'INTEGER'
REAL = 'REAL'
TEXT = 'TEXT'

FALSE = 0

BASE = {
    'type': TEXT,
    'nullable': True,
    'primary_key': False,
    'select': '`{table}`.`{column}`',
    'mtgjson': True,
    'foreign_key': None,
    'default': None,
    'unique': False
}

def card_properties():
    props = {}
    for k in ['id', 'layout']:
        props[k] = copy.deepcopy(BASE)
    props['id']['type'] = INTEGER
    props['id']['nullable'] = False
    props['id']['primary_key'] = True
    props['id']['mtgjson'] = False
    props['layout']['nullable'] = False
    return props

def face_properties():
    props = {}
    base = copy.deepcopy(BASE)
    base['select'] = "GROUP_CONCAT(CASE WHEN `{table}`.position = 1 THEN `{table}`.`{column}` ELSE '' END, '') AS `{column}`"
    for k in ['id', 'name', 'mana_cost', 'cmc', 'power', 'toughness', 'power', 'toughness', 'loyalty', 'type', 'text', 'image_name', 'hand', 'life', 'starter', 'position', 'name_ascii', 'card_id']:
        props[k] = copy.deepcopy(base)
    for k in ['id', 'position', 'name_ascii', 'card_id']:
        props[k]['mtgjson'] = False
    for k in ['id', 'name', 'type', 'text']:
        props[k]['nullable'] = False
    for k in ['id', 'card_id', 'hand', 'life', 'starter']:
        props[k]['type'] = INTEGER
    props['id']['primary_key'] = True
    props['cmc']['type'] = REAL
    props['name']['select'] = """{name_select} AS name""".format(name_select=name_select())
    props['name_ascii']['select'] = """{name_select} AS name_ascii""".format(name_select=name_select('name_ascii'))
    props['mana_cost']['select'] = """CASE
            WHEN layout IN ('split') AND `{table}`.`text` LIKE '%Fuse (You may cast one or both halves of this card from your hand.)%' THEN
                GROUP_CONCAT(`{table}`.`{column}`, '')
            WHEN layout IN ('split') THEN
                NULL
            ELSE
                GROUP_CONCAT(CASE WHEN position = 1 THEN `{table}`.`{column}` ELSE '' END, '')
        END AS `{column}`"""
    props['cmc']['select'] = "GROUP_CONCAT(`{table}`.`{column}`, '|') AS `{column}`"
    props['text']['select'] = "GROUP_CONCAT(`{table}`.`{column}`, '\n-----\n') AS `{column}`"
    props['card_id']['foreign_key'] = ('card', 'id')
    return props

def set_properties():
    props = {}
    for k in ['id', 'name', 'code', 'gatherer_code', 'old_code', 'magiccardsinfo_code', 'release_date', 'border', 'type', 'online_only']:
        props[k] = copy.deepcopy(BASE)
    for k in ['id', 'name', 'code', 'release_date', 'border', 'type']:
        props[k]['nullable'] = False
    props['id']['primary_key'] = True
    props['id']['type'] = INTEGER
    props['id']['mtgjson'] = False
    props['release_date']['type'] = DATE
    props['online_only']['type'] = BOOLEAN
    props['name']['unique'] = True
    props['code']['unique'] = True
    props['gatherer_code']['unique'] = True
    props['old_code']['unique'] = True
    props['magiccardsinfo_code']['unique'] = True
    return props

def printing_properties():
    props = {}
    for k in ['id', 'system_id', 'rarity', 'flavor', 'artist', 'number', 'multiverseid', 'watermark', 'border', 'timeshifted', 'reserved', 'mci_number', 'card_id', 'set_id', 'rarity_id']:
        props[k] = copy.deepcopy(BASE)
    for k in ['id', 'system_id', 'rarity', 'artist', 'card_id', 'set_id']:
        props[k]['nullable'] = False
    for k in ['id', 'card_id', 'set_id', 'rarity_id']:
        props[k]['type'] = INTEGER
        props[k]['mtgjson'] = False
    props['id']['primary_key'] = True
    props['id']['nullable'] = False
    props['timeshifted']['type'] = BOOLEAN
    props['reserved']['type'] = BOOLEAN
    props['card_id']['foreign_key'] = ('card', 'id')
    props['set_id']['foreign_key'] = ('set', 'id')
    props['rarity_id']['foreign_key'] = ('rarity', 'id')
    return props

def name_select(column='face_name'):
    return """
        CASE
        WHEN layout = 'double-faced' THEN
            GROUP_CONCAT(CASE WHEN `{table}`.position = 1 THEN {column} ELSE '' END, '')
        WHEN layout = 'meld' THEN
            GROUP_CONCAT(CASE WHEN `{table}`.position = 1 OR `{table}`.position = 2 THEN {column} ELSE '' END, '')
        ELSE
            GROUP_CONCAT({column}, ' // ' )
        END
    """.format(column=column, table='{table}')

def unaccent(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def canonicalize(name):
    return unaccent(name.strip().lower())

class Card(Munch):
    def __init__(self, params):
        super().__init__()
        for k in params.keys():
            v = params[k]
            if k == 'names' or k == 'cmc':
                if v is not None:
                    v = v.split('|')
            setattr(self, k, v)
        if not self.names:
            setattr(self, 'names', [self.name])

    def is_creature(self):
        return 'Creature' in self.type

    def is_land(self):
        return 'Land' in self.type

    def is_spell(self):
        return not self.is_creature() and not self.is_land()

class Printing(Munch):
    def __init__(self, params):
        super().__init__()
        for k in params.keys():
            setattr(self, k, params[k])