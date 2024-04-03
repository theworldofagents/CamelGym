from .moderator_actions import InstructSpeak
from .common_actions import Speak, NighttimeWhispers, Reflect
from .werewolf_actions import Hunt, Impersonate
from .guard_actions import Protect
from .seer_actions import Verify
from .witch_actions import Save, Poison

ACTIONS = {
    "Speak": Speak,
    "Hunt": Hunt,
    "Protect": Protect,
    "Verify": Verify,
    "Save": Save,
    "Poison": Poison,
    "Impersonate": Impersonate,
}
