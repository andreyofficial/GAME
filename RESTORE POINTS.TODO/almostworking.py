# Full Updated Game Code


import importlib
import json
import math
import os
import random
import re
import subprocess
import sys
import webbrowser
from array import array
from collections import Counter, deque
import importlib
import subprocess
import sys

def ensure_package(module_name, pip_name):
    try:
        importlib.import_module(module_name)

    except ModuleNotFoundError:
        print(f"Missing package: {pip_name}")
        print(f"Installing {pip_name} automatically...")

        try:
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                pip_name
            ])

            print(f"{pip_name} installed successfully.")

        except Exception as err:
            print(f"Failed to install {pip_name}: {err}")
            input("Press ENTER to exit...")
            sys.exit()

# Install packages if missing
ensure_package("pygame", "pygame")
ensure_package("PIL", "pillow")

# REAL imports
import pygame
from PIL import Image


pygame.init()

WIDTH, HEIGHT = 1280, 720
WINDOW_RESOLUTIONS = [
    (960, 540),
    (1280, 720),
    (1600, 900),
    (1920, 1080)
]
FPS_OPTIONS = [30, 60, 120, 144, 0]

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SW, SH = screen.get_size()
surf = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(BASE, "actually_usefull_textures")


def build_game_file_index():
    file_paths = []
    files_by_name = {}
    files_by_folder_and_name = {}

    if not os.path.isdir(BASE):
        return file_paths, files_by_name, files_by_folder_and_name

    for root, _, files in os.walk(BASE):
        files.sort()
        folder_name = os.path.basename(root).lower()

        for file_name in files:
            path = os.path.join(root, file_name)
            lowered_name = file_name.lower()
            file_paths.append(path)
            files_by_name.setdefault(lowered_name, []).append(path)
            files_by_folder_and_name.setdefault(
                (folder_name, lowered_name),
                []
            ).append(path)

    file_paths.sort()
    return file_paths, files_by_name, files_by_folder_and_name


def refresh_game_file_index():
    global GAME_FILE_PATHS
    global GAME_FILES_BY_NAME
    global GAME_FILES_BY_FOLDER_AND_NAME

    (
        GAME_FILE_PATHS,
        GAME_FILES_BY_NAME,
        GAME_FILES_BY_FOLDER_AND_NAME
    ) = build_game_file_index()


def find_game_file(filename):
    matches = GAME_FILES_BY_NAME.get(filename.lower(), [])

    if matches:
        return matches[0]

    return None


def find_game_file_by_suffix(suffix):
    lowered_suffix = suffix.lower()

    for path in GAME_FILE_PATHS:
        if os.path.basename(path).lower().endswith(lowered_suffix):
            return path

    return None


def find_game_files_matching(pattern):
    matcher = re.compile(pattern, re.IGNORECASE)
    return [
        path
        for path in GAME_FILE_PATHS
        if matcher.fullmatch(os.path.basename(path))
    ]


def find_game_file_in_folder(folder_name, filename):
    matches = GAME_FILES_BY_FOLDER_AND_NAME.get(
        (folder_name.lower(), filename.lower()),
        []
    )

    if matches:
        return matches[0]

    return None


refresh_game_file_index()
font = pygame.font.SysFont("Georgia", 18)
ui_font = pygame.font.SysFont("Georgia", 26, bold=True)
title_font = pygame.font.SysFont("Garamond", 44, bold=True)
small_font = pygame.font.SysFont("Georgia", 14)
hero_font = pygame.font.SysFont("Garamond", 82, bold=True)
section_font = pygame.font.SysFont("Garamond", 36, bold=True)

# =============================
# STATES
# =============================
game_state = "menu"
menu_state = "main"

seed_input = ""
code_input = ""
code_message = ""
world_seed = 0
current_world_name = ""
fullscreen = True
inventory_open = False
crafting_open = False
crafting_message = ""
map_open = False
show_controls = False
pause_menu_state = "main"
last_autosave_ms = 0
selected_resolution_index = 1
selected_fps_index = 1

# Day/Night cycle
game_time = 0  # in seconds
day_length = 900  # 15 minutes per full day/night cycle
night_start_ratio = 0.20  # short day (~3 min), long night (~12 min)
night_multiplier = 1.0  # for difficulty
disable_wall_breaking = False
selected_keybind_action = None
selected_upgrade = None
shop_message = ""
selected_load_world_name = None
load_world_message = ""
menu_notice_message = ""
menu_notice_until_ms = 0
game_over_snapshot = {}
kill_points = 0
total_kills = 0
upgrade_price_multiplier = 1.0
upgrade_levels = {
    "melee_damage": 0,
    "magic_damage": 0,
    "mob_wall_break_slow": 0,
    "max_health": 0,
    "max_mana": 0,
    "max_stamina": 0
}
upgrade_labels = {
    "melee_damage": "Melee Damage",
    "magic_damage": "All Magic Damage",
    "mob_wall_break_slow": "Mob Wall Break Slow",
    "max_health": "More Health",
    "max_mana": "More Mana",
    "max_stamina": "More Stamina"
}
upgrade_base_costs = {
    "melee_damage": 20,
    "magic_damage": 24,
    "mob_wall_break_slow": 18,
    "max_health": 22,
    "max_mana": 18,
    "max_stamina": 18
}
BASE_DAY_LENGTH = 900
BASE_NIGHT_START_RATIO = 0.20
CREATIVE_STAT_VALUE = 1_000_000_000
GAME_MODE_ORDER = ["easy", "hard", "creative"]
GAME_MODE_LABELS = {
    "easy": "Easy",
    "hard": "Hard",
    "creative": "Creative"
}
GAME_MODE_DESCRIPTIONS = {
    "easy": "Regular survival balance.",
    "hard": "Night is 2x longer, mobs are tougher.",
    "creative": "Infinite stats, no mob spawns."
}
WORLD_ICON_CHOICES = ["sword", "axe", "wall", "torch", "water_bucket", "steak"]
game_mode = "easy"
selected_game_mode = "easy"
enemy_health_multiplier = 1.0
enemy_damage_multiplier = 1.0
mobs_spawn_enabled = True
selected_world_icon_index = 0
current_world_icon = WORLD_ICON_CHOICES[0]
world_metadata_cache = {}
last_movement_log_tile = None
selected_player_image_path = ""
current_player_image_path = ""
custom_player_surface = None
game_over_close_at_ms = 0
camera_shake_strength = 0.0
camera_shake_x = 0
camera_shake_y = 0
impact_flash_alpha = 0.0
impact_flash_color = (255, 196, 132)
slash_effects = []
book_open = False
book_text = ""
book_cursor_blink_on = True
book_cursor_timer = 0.0
book_status_message = ""
book_status_until_ms = 0
master_volume = 0.8
audio_ready = False
sfx_sounds = {}
sfx_base_volumes = {}
menu_background_cache = None
menu_background_cache_tick = -99999

DEFAULT_KEYBINDS = {
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "sprint": pygame.K_LSHIFT,
    "inventory": pygame.K_e,
    "roll": pygame.K_SPACE,
    "pause": pygame.K_ESCAPE,
    "save_world": pygame.K_F5,
    "crafting": pygame.K_r,
    "map": pygame.K_m,
    "toggle_controls": pygame.K_TAB,
    "delete_waypoint": pygame.K_DELETE,
    "pick_player_image": pygame.K_F2,
    "clear_player_image": pygame.K_DELETE,
    "hotbar_1": pygame.K_1,
    "hotbar_2": pygame.K_2,
    "hotbar_3": pygame.K_3,
    "hotbar_4": pygame.K_4,
    "hotbar_5": pygame.K_5,
    "hotbar_6": pygame.K_6,
    "hotbar_7": pygame.K_7,
    "hotbar_8": pygame.K_8,
    "hotbar_9": pygame.K_9,
    "hotbar_10": pygame.K_0
}
KEYBIND_DISPLAY_ORDER = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "sprint",
    "roll",
    "inventory",
    "pause",
    "save_world",
    "crafting",
    "map",
    "toggle_controls",
    "delete_waypoint",
    "hotbar_1",
    "hotbar_2",
    "hotbar_3",
    "hotbar_4",
    "hotbar_5",
    "hotbar_6",
    "hotbar_7",
    "hotbar_8",
    "hotbar_9",
    "hotbar_10",
    "pick_player_image",
    "clear_player_image"
]
keybinds = dict(DEFAULT_KEYBINDS)
keybind_labels = {
    "move_up": "Move Up",
    "move_down": "Move Down",
    "move_left": "Move Left",
    "move_right": "Move Right",
    "sprint": "Sprint",
    "roll": "Roll",
    "inventory": "Inventory",
    "pause": "Pause / Back",
    "save_world": "Save World",
    "crafting": "Crafting",
    "map": "World Map",
    "toggle_controls": "Toggle Controls",
    "delete_waypoint": "Delete Waypoint",
    "pick_player_image": "Pick Player Image",
    "clear_player_image": "Clear Player Image",
    "hotbar_1": "Hotbar Slot 1",
    "hotbar_2": "Hotbar Slot 2",
    "hotbar_3": "Hotbar Slot 3",
    "hotbar_4": "Hotbar Slot 4",
    "hotbar_5": "Hotbar Slot 5",
    "hotbar_6": "Hotbar Slot 6",
    "hotbar_7": "Hotbar Slot 7",
    "hotbar_8": "Hotbar Slot 8",
    "hotbar_9": "Hotbar Slot 9",
    "hotbar_10": "Hotbar Slot 10"
}

SAVE_DIR = os.path.join(BASE, "saves")

# fix broken saves file
if os.path.exists(SAVE_DIR) and not os.path.isdir(SAVE_DIR):
    os.remove(SAVE_DIR)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# =============================
# PLAYER
# =============================
# 2 block tall player hitbox
player = pygame.Rect(0, 0, 48, 96)
player.center = (0, 0)
player_pos_x = float(player.x)
player_pos_y = float(player.y)

frame = 0
facing_left = False
state = "idle"
locked = False
tick_counter = 0

MAX_HP = 100
MAX_MANA = 100
MAX_STAM = 100
MANA_REGEN_PER_TICK = 0.20
STAMINA_REGEN_PER_TICK = 0.32
AUTOSAVE_INTERVAL_MS = 30000
GAME_OVER_CLOSE_DELAY_MS = 2400
DOOR_OPEN_DISTANCE = 112
MAX_SCREEN_SHAKE = 18.0
SCREEN_SHAKE_DECAY = 0.84
IMPACT_FLASH_DECAY = 6.0
MAX_SLASH_EFFECTS = 16
MAX_PARTICLES = 280
MAX_DAMAGE_TEXTS = 90
BOOK_MAX_CHARS = 2400
LAVA_DAMAGE_INTERVAL = 0.50
MENU_BG_CACHE_MS = 300
MENU_MIN_FPS = 240
SETTINGS_PATH = os.path.join(BASE, "settings.json")
GITHUB_URL = "https://github.com/andreyofficial"
ENABLE_SFX = False
ENABLE_FOG_EFFECTS = False

hp = 100
mana = 100
stam = 100
hp_limit = MAX_HP
mana_limit = MAX_MANA
stam_limit = MAX_STAM

PLAYER_SPEED = 4.5
SPRINT_SPEED = 7.0
INVENTORY_COLUMNS = 8
INVENTORY_ROWS = 6
INVENTORY_CAPACITY = INVENTORY_COLUMNS * INVENTORY_ROWS
INVENTORY_SLOT_SIZE = 60
INVENTORY_SLOT_GAP = 10
INVENTORY_PANEL_RECT = pygame.Rect(70, 52, 1140, 616)
INVENTORY_GRID_START_X = INVENTORY_PANEL_RECT.x + 30
INVENTORY_GRID_START_Y = INVENTORY_PANEL_RECT.y + 126

# =============================
# SYSTEMS
# =============================
world = {}
walls = set()
wall_types = {}  # tile_pos -> wall item id
doors = set()
open_doors = set()
placed_floors = set()
placed_water = set()
placed_lava = set()
drained_water = set()
forced_stone1_tiles = set()
torch_positions = set()
torch_mounts = {}  # tile_pos -> "ground" | "wall"
wall_break_timers = {}  # tile_pos -> time_started
wood_tiles = set()
bridge_tiles = set()
bushes = set()
inventory = [None] * INVENTORY_CAPACITY
TILE = 64
noise_cache = {}
shore_cache = {}
deco_cache = {}

# movement tracking
step_counter = 0
last_player_tile = (0, 0)

MAX_ENEMIES = 28
ENEMY_ACTIVE_DISTANCE = 1400
ENEMY_DESPAWN_DISTANCE = 2600
DOOR_UPDATE_INTERVAL = 2
door_update_counter = 0
WAYPOINT_COLORS = [
    (255, 92, 92),
    (86, 214, 255),
    (255, 210, 92),
    (142, 255, 122),
    (255, 126, 214),
    (186, 150, 255)
]
waypoints = []
selected_waypoint_id = None
waypoint_editing = False
waypoint_name_input = ""
next_waypoint_id = 1
inventory_selected_index = None
SPELL_HOTBAR_ENTRIES = [
    "spell_1",
    "spell_2",
    "spell_3",
    "spell_4",
    "spell_5",
    "spell_6"
]
HOTBAR_ITEM_SLOT_COUNT = 4
HOTBAR_FIRST_ITEM_SLOT = len(SPELL_HOTBAR_ENTRIES)
HOTBAR_TOTAL_SLOTS = HOTBAR_FIRST_ITEM_SLOT + HOTBAR_ITEM_SLOT_COUNT
DEFAULT_ACTIVE_HOTBAR_SLOT = HOTBAR_FIRST_ITEM_SLOT
active_hotbar_slot = DEFAULT_ACTIVE_HOTBAR_SLOT
WALL_ITEM_IDS = [
    "wall",
    "wall1",
    "wall2",
    "wall3",
    "wall4",
    "stone1_block",
    "stone2_block",
    "copper_block"
]
ITEM_IDS = [
    "sword",
    "axe",
    "steak",
    "door",
    "floor",
    "torch",
    "water_bucket",
    "lava_bucket",
    "book_and_quill",
    "snowball"
] + WALL_ITEM_IDS
MELEE_ITEM_IDS = {"sword", "axe"}
PLACEABLE_ITEM_IDS = set(WALL_ITEM_IDS + ["door", "floor", "torch", "water_bucket", "lava_bucket"])
DEFAULT_INVENTORY_ITEMS = [
    "sword",
    "axe",
    "steak",
    "book_and_quill",
    "wall",
    "wall1",
    "wall2",
    "wall3",
    "wall4",
    "stone1_block",
    "stone2_block",
    "copper_block",
    "door",
    "floor",
    "torch",
    "snowball",
    "water_bucket",
    "lava_bucket"
]
hotbar_slots = SPELL_HOTBAR_ENTRIES + [None] * HOTBAR_ITEM_SLOT_COUNT
MAX_ACTIVE_PROJECTILES = 90
player_lava_damage_timer = 0.0
WATERLIKE_TILE_IDS = {"water", "ocean"}
LIQUID_TILE_IDS = {"water", "ocean", "lava"}


def clear_world_runtime_cache():
    global door_update_counter

    world.clear()
    noise_cache.clear()
    shore_cache.clear()
    deco_cache.clear()
    door_update_counter = 0


def set_display_mode(use_fullscreen):
    global screen
    global SW
    global SH
    global fullscreen

    fullscreen = use_fullscreen

    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(
            WINDOW_RESOLUTIONS[selected_resolution_index]
        )

    SW, SH = screen.get_size()


def scale_mouse_pos(pos):
    if SW == 0 or SH == 0:
        return 0, 0

    return (
        int(pos[0] * WIDTH / SW),
        int(pos[1] * HEIGHT / SH)
    )


def is_night():
    time_in_day = game_time % day_length
    return time_in_day >= day_length * night_start_ratio


def get_current_day():
    return int(game_time // day_length) + 1


def get_night_multiplier():
    # Difficulty compounds by 1.5% per completed day/night cycle.
    return 1.015 ** (get_current_day() - 1)


def get_night_darkness_strength():
    time_in_day = game_time % day_length
    night_start = day_length * night_start_ratio
    transition = max(1.0, day_length * 0.08)

    if time_in_day < night_start - transition:
        return 0.0

    if night_start - transition <= time_in_day <= night_start + transition:
        return min(1.0, (time_in_day - (night_start - transition)) / (2 * transition))

    if time_in_day < day_length - transition:
        return 1.0

    return max(0.0, 1.0 - ((time_in_day - (day_length - transition)) / transition))


def log_player_action(action, details=""):
    timestamp = pygame.time.get_ticks() / 1000.0
    suffix = f" | {details}" if details else ""
    print(f"[PLAYER {timestamp:08.2f}s] {action}{suffix}")


def set_menu_notice(message, duration_ms=2600):
    global menu_notice_message
    global menu_notice_until_ms

    menu_notice_message = str(message)
    menu_notice_until_ms = pygame.time.get_ticks() + max(500, int(duration_ms))
    log_player_action("Menu notice", menu_notice_message)


def set_book_status(message, duration_ms=2200):
    global book_status_message
    global book_status_until_ms

    book_status_message = str(message)
    book_status_until_ms = pygame.time.get_ticks() + max(500, int(duration_ms))


def open_external_link(url):
    try:
        webbrowser.open(str(url), new=2)
        return True
    except Exception as err:
        set_menu_notice("Failed to open browser link.")
        log_player_action("Open URL failed", str(err))
        return False


def clamp_channel(value):
    return max(0, min(255, int(value)))


def clamp_color(color):
    if not isinstance(color, (list, tuple)) or len(color) < 3:
        return 255, 255, 255

    return (
        clamp_channel(color[0]),
        clamp_channel(color[1]),
        clamp_channel(color[2])
    )


def add_screen_shake(amount):
    global camera_shake_strength

    try:
        intensity = float(amount)
    except Exception:
        intensity = 0.0

    if intensity <= 0:
        return

    camera_shake_strength = min(MAX_SCREEN_SHAKE, camera_shake_strength + intensity)


def trigger_impact_flash(color=(255, 196, 132), alpha=60):
    global impact_flash_color
    global impact_flash_alpha

    impact_flash_color = clamp_color(color)
    impact_flash_alpha = max(impact_flash_alpha, float(alpha))


def spawn_slash_effect(center_pos, facing_left_value, heavy=False):
    if not isinstance(center_pos, (tuple, list)) or len(center_pos) != 2:
        return

    if len(slash_effects) >= MAX_SLASH_EFFECTS:
        slash_effects.pop(0)

    slash_effects.append(
        {
            "x": float(center_pos[0]),
            "y": float(center_pos[1] - 8),
            "base_angle": math.pi if facing_left_value else 0.0,
            "radius": 86 if heavy else 72,
            "life": 10 if heavy else 9,
            "max_life": 10 if heavy else 9,
            "spread": 1.20 if heavy else 1.03,
            "width": 8 if heavy else 6,
            "color": (255, 196, 130) if heavy else (255, 228, 172)
        }
    )


def update_visual_fx(gameplay_frozen):
    global camera_shake_strength
    global camera_shake_x
    global camera_shake_y
    global impact_flash_alpha

    if camera_shake_strength > 0.05:
        camera_shake_x = int(random.uniform(-camera_shake_strength, camera_shake_strength))
        camera_shake_y = int(random.uniform(-camera_shake_strength, camera_shake_strength))
        camera_shake_strength *= SCREEN_SHAKE_DECAY
    else:
        camera_shake_strength = 0.0
        camera_shake_x = 0
        camera_shake_y = 0

    if impact_flash_alpha > 0:
        decay = IMPACT_FLASH_DECAY * (0.45 if gameplay_frozen else 1.0)
        impact_flash_alpha = max(0.0, impact_flash_alpha - decay)

    if not gameplay_frozen:
        for slash_fx in slash_effects[:]:
            slash_fx["life"] -= 1
            if slash_fx["life"] <= 0:
                slash_effects.remove(slash_fx)


def draw_slash_effects(off):
    for slash_fx in slash_effects:
        life_ratio = slash_fx["life"] / max(1, slash_fx["max_life"])
        sweep = slash_fx["spread"] * (0.55 + life_ratio * 0.45)
        width = max(1, int(slash_fx["width"] * life_ratio))
        arc_rect = pygame.Rect(
            int(slash_fx["x"] + off[0] - slash_fx["radius"]),
            int(slash_fx["y"] + off[1] - slash_fx["radius"]),
            int(slash_fx["radius"] * 2),
            int(slash_fx["radius"] * 2)
        )
        base_color = slash_fx["color"]
        glow_color = (
            clamp_channel(base_color[0] * (0.55 + life_ratio * 0.7)),
            clamp_channel(base_color[1] * (0.55 + life_ratio * 0.7)),
            clamp_channel(base_color[2] * (0.55 + life_ratio * 0.7))
        )

        pygame.draw.arc(
            surf,
            glow_color,
            arc_rect,
            slash_fx["base_angle"] - sweep,
            slash_fx["base_angle"] + sweep,
            width
        )

        if width > 2:
            pygame.draw.arc(
                surf,
                (255, 246, 224),
                arc_rect.inflate(-10, -10),
                slash_fx["base_angle"] - sweep * 0.72,
                slash_fx["base_angle"] + sweep * 0.72,
                max(1, width - 2)
            )


def draw_knight_panel(
        rect,
        border_color=(176, 142, 92),
        fill_color=(26, 18, 12),
        inner_color=(42, 30, 20),
        border_radius=14,
        draw_rivets=True
):
    shadow_rect = rect.move(0, 6)
    pygame.draw.rect(surf, (8, 6, 4), shadow_rect, border_radius=border_radius)
    pygame.draw.rect(surf, fill_color, rect, border_radius=border_radius)

    inner_rect = rect.inflate(-8, -8)
    if inner_rect.width > 0 and inner_rect.height > 0:
        pygame.draw.rect(
            surf,
            inner_color,
            inner_rect,
            border_radius=max(6, border_radius - 4)
        )
        pygame.draw.line(
            surf,
            (206, 170, 112),
            (inner_rect.x + 10, inner_rect.y + 8),
            (inner_rect.right - 10, inner_rect.y + 8),
            1
        )

    pygame.draw.rect(surf, border_color, rect, 3, border_radius=border_radius)

    if draw_rivets and rect.width >= 64 and rect.height >= 44:
        rivet_color = (118, 104, 86)
        inset = 10
        rivet_points = [
            (rect.x + inset, rect.y + inset),
            (rect.right - inset, rect.y + inset),
            (rect.x + inset, rect.bottom - inset),
            (rect.right - inset, rect.bottom - inset)
        ]
        for point in rivet_points:
            pygame.draw.circle(surf, rivet_color, point, 2)


def draw_vignette_overlay():
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    step = 26
    for ring in range(8):
        margin = ring * step
        alpha = 8 + ring * 5
        pygame.draw.rect(
            vignette,
            (20, 8, 2, alpha),
            pygame.Rect(margin, margin, WIDTH - margin * 2, HEIGHT - margin * 2),
            width=max(2, step - 2)
        )

    surf.blit(vignette, (0, 0))


def get_hotbar_keybind_action(index):
    return f"hotbar_{index + 1}"


def get_hotbar_slot_index_for_key(key_value):
    for slot_index in range(HOTBAR_TOTAL_SLOTS):
        action = get_hotbar_keybind_action(slot_index)
        if keybinds.get(action) == key_value:
            return slot_index
    return None


def get_keybind_name(action):
    key_code = keybinds.get(action, DEFAULT_KEYBINDS.get(action, pygame.K_UNKNOWN))
    key_name = pygame.key.name(key_code)
    return key_name.upper() if key_name else "UNKNOWN"


def rebind_action_key(action, new_key):
    if action not in keybinds or not isinstance(new_key, int):
        return None

    previous_key = keybinds[action]
    swapped_action = None

    for other_action, key_code in keybinds.items():
        if other_action != action and key_code == new_key:
            keybinds[other_action] = previous_key
            swapped_action = other_action
            break

    keybinds[action] = new_key
    return swapped_action


def set_master_volume(value):
    global master_volume

    master_volume = max(0.0, min(1.0, float(value)))

    if audio_ready and ENABLE_SFX:
        for sound_obj in sfx_sounds.values():
            if sound_obj is None:
                continue
            base = sfx_base_volumes.get(sound_obj, 1.0)
            sound_obj.set_volume(base * master_volume)


def cycle_master_volume(step=0.1):
    if not ENABLE_SFX:
        return
    current_steps = int(round(master_volume * 10))
    current_steps = max(0, min(10, current_steps + int(round(step * 10))))
    set_master_volume(current_steps / 10.0)


def get_volume_label():
    if not ENABLE_SFX:
        return "OFF"
    return f"{int(round(master_volume * 100))}%"


def build_tone_sound(frequency_hz, duration_ms, amplitude=0.35):
    if not audio_ready:
        return None

    try:
        mixer_init = pygame.mixer.get_init()
        if not mixer_init:
            return None
        sample_rate, _, channels = mixer_init
        sample_count = max(1, int(sample_rate * (duration_ms / 1000.0)))
        tone_samples = array("h")
        max_amp = int(32767 * max(0.0, min(1.0, amplitude)))

        for index in range(sample_count):
            wave = math.sin(2.0 * math.pi * frequency_hz * index / sample_rate)
            tone_samples.append(int(max_amp * wave))

        raw_data = tone_samples.tobytes()
        if channels == 2:
            stereo_data = bytearray()
            for i in range(0, len(raw_data), 2):
                stereo_data.extend(raw_data[i:i + 2])
                stereo_data.extend(raw_data[i:i + 2])
            return pygame.mixer.Sound(buffer=bytes(stereo_data))

        return pygame.mixer.Sound(buffer=raw_data)
    except Exception:
        return None


def register_sfx(name, sound_obj, base_volume=1.0):
    if sound_obj is None:
        return
    sfx_sounds[name] = sound_obj
    sfx_base_volumes[sound_obj] = max(0.0, min(1.0, float(base_volume)))
    sound_obj.set_volume(sfx_base_volumes[sound_obj] * master_volume)


def init_audio():
    global audio_ready
    global sfx_sounds
    global sfx_base_volumes

    sfx_sounds = {}
    sfx_base_volumes = {}
    audio_ready = False

    if not ENABLE_SFX:
        return

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        audio_ready = True
    except Exception as err:
        print("audio init failed:", err)
        return

    # Prefer local assets if present; fallback to generated tones.
    local_sound_map = {
        "swing": "swing.wav",
        "spell": "spell.wav",
        "hit": "hit.wav",
        "enemy_die": "enemy_die.wav",
        "place": "place.wav",
        "break": "break.wav",
        "book_open": "book_open.wav",
        "book_close": "book_close.wav",
        "lava_burn": "lava_burn.wav",
        "player_hurt": "player_hurt.wav",
        "death": "death.wav"
    }
    tone_fallbacks = {
        "swing": (330, 90, 0.35),
        "spell": (620, 120, 0.30),
        "hit": (180, 80, 0.45),
        "enemy_die": (140, 160, 0.42),
        "place": (260, 80, 0.30),
        "break": (120, 110, 0.38),
        "book_open": (280, 90, 0.25),
        "book_close": (210, 90, 0.25),
        "lava_burn": (90, 120, 0.46),
        "player_hurt": (160, 110, 0.42),
        "death": (70, 240, 0.55)
    }
    base_volumes = {
        "swing": 0.65,
        "spell": 0.60,
        "hit": 0.70,
        "enemy_die": 0.58,
        "place": 0.45,
        "break": 0.50,
        "book_open": 0.45,
        "book_close": 0.45,
        "lava_burn": 0.62,
        "player_hurt": 0.72,
        "death": 0.78
    }

    for sfx_name, filename in local_sound_map.items():
        sound_obj = None
        file_path = find_game_file(filename)
        if file_path:
            try:
                sound_obj = pygame.mixer.Sound(file_path)
            except Exception:
                sound_obj = None

        if sound_obj is None:
            tone_def = tone_fallbacks.get(sfx_name)
            if tone_def is not None:
                sound_obj = build_tone_sound(tone_def[0], tone_def[1], tone_def[2])

        register_sfx(sfx_name, sound_obj, base_volumes.get(sfx_name, 0.6))

    set_master_volume(master_volume)


def play_sfx(name):
    if not ENABLE_SFX:
        return
    if not audio_ready:
        return
    sound_obj = sfx_sounds.get(name)
    if sound_obj is None:
        return
    try:
        sound_obj.play()
    except Exception:
        pass


def normalize_keybind_payload(payload):
    normalized = dict(DEFAULT_KEYBINDS)
    if isinstance(payload, dict):
        for action, default_key in DEFAULT_KEYBINDS.items():
            value = payload.get(action, default_key)
            if isinstance(value, int):
                normalized[action] = value
    return normalized


def load_global_settings():
    global selected_resolution_index
    global selected_fps_index
    global disable_wall_breaking
    global fullscreen
    global keybinds

    if not os.path.exists(SETTINGS_PATH):
        keybinds = dict(DEFAULT_KEYBINDS)
        return

    try:
        with open(SETTINGS_PATH, "r") as settings_file:
            settings_data = json.load(settings_file)
    except Exception:
        keybinds = dict(DEFAULT_KEYBINDS)
        return

    if not isinstance(settings_data, dict):
        keybinds = dict(DEFAULT_KEYBINDS)
        return

    keybinds = normalize_keybind_payload(settings_data.get("keybinds", {}))
    set_master_volume(settings_data.get("master_volume", master_volume))

    selected_resolution_index = int(settings_data.get("resolution_index", selected_resolution_index))
    selected_resolution_index = max(0, min(len(WINDOW_RESOLUTIONS) - 1, selected_resolution_index))

    selected_fps_index = int(settings_data.get("fps_index", selected_fps_index))
    selected_fps_index = max(0, min(len(FPS_OPTIONS) - 1, selected_fps_index))

    disable_wall_breaking = bool(settings_data.get("disable_wall_breaking", disable_wall_breaking))
    fullscreen = bool(settings_data.get("fullscreen", fullscreen))


def save_global_settings():
    settings_data = {
        "keybinds": {action: int(key_code) for action, key_code in keybinds.items()},
        "master_volume": float(master_volume),
        "resolution_index": int(selected_resolution_index),
        "fps_index": int(selected_fps_index),
        "disable_wall_breaking": bool(disable_wall_breaking),
        "fullscreen": bool(fullscreen)
    }

    try:
        with open(SETTINGS_PATH, "w") as settings_file:
            json.dump(settings_data, settings_file, indent=2)
    except Exception as err:
        print("settings save failed:", err)


def normalize_game_mode(mode):
    mode_value = str(mode).strip().lower()

    if mode_value in GAME_MODE_ORDER:
        return mode_value

    return "easy"


def normalize_world_icon(icon_id):
    icon_value = str(icon_id).strip().lower()

    if icon_value in WORLD_ICON_CHOICES:
        return icon_value

    return WORLD_ICON_CHOICES[0]


def normalize_player_image_path(path):
    if path is None:
        return ""

    candidate = str(path).strip()
    if not candidate:
        return ""

    return os.path.abspath(os.path.expanduser(candidate))


def compact_path_label(path, max_chars=54):
    text = str(path)
    if len(text) <= max_chars:
        return text

    keep_each_side = max(8, (max_chars - 3) // 2)
    return text[:keep_each_side] + "..." + text[-keep_each_side:]


def load_player_image_surface(image_path):
    normalized_path = normalize_player_image_path(image_path)
    if not normalized_path or not os.path.exists(normalized_path):
        return None

    try:
        source = pygame.image.load(normalized_path).convert_alpha()
    except Exception:
        return None

    source_width, source_height = source.get_size()
    if source_width <= 0 or source_height <= 0:
        return None

    target_width, target_height = 240, 160
    scale = min(target_width / source_width, target_height / source_height)
    scaled_size = (
        max(1, int(source_width * scale)),
        max(1, int(source_height * scale))
    )
    scaled = pygame.transform.smoothscale(source, scaled_size)
    framed_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
    framed_surface.blit(
        scaled,
        scaled.get_rect(center=(target_width // 2, target_height // 2))
    )
    return framed_surface


def apply_player_image(image_path):
    global current_player_image_path
    global custom_player_surface

    normalized_path = normalize_player_image_path(image_path)

    if not normalized_path:
        current_player_image_path = ""
        custom_player_surface = None
        return True

    loaded_surface = load_player_image_surface(normalized_path)
    if loaded_surface is None:
        current_player_image_path = ""
        custom_player_surface = None
        log_player_action("Player image load failed", normalized_path)
        return False

    current_player_image_path = normalized_path
    custom_player_surface = loaded_surface
    log_player_action("Player image selected", normalized_path)
    return True


def set_selected_player_image(image_path):
    global selected_player_image_path

    normalized_path = normalize_player_image_path(image_path)
    if not normalized_path:
        selected_player_image_path = ""
        return True

    if load_player_image_surface(normalized_path) is None:
        return False

    selected_player_image_path = normalized_path
    return True


def choose_player_image_from_computer():
    picker_errors = []

    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as err:
        picker_errors.append(f"tkinter unavailable: {err}")
        tk = None
        filedialog = None

    if tk is not None and filedialog is not None:
        root = None
        selected_path = ""
        tk_dialog_succeeded = False

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected_path = filedialog.askopenfilename(
                title="Choose Player Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                    ("All files", "*.*")
                ]
            )
            tk_dialog_succeeded = True
        except Exception as err:
            picker_errors.append(f"tkinter failed: {err}")
        finally:
            if root is not None:
                try:
                    root.destroy()
                except Exception:
                    pass

        if tk_dialog_succeeded:
            if selected_path:
                return normalize_player_image_path(selected_path)
            return ""

    try:
        dialog_result = subprocess.run(
            [
                "zenity",
                "--file-selection",
                "--title=Choose Player Image",
                "--file-filter=Images | *.png *.jpg *.jpeg *.bmp *.gif *.webp",
                "--file-filter=All Files | *"
            ],
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as err:
        picker_errors.append(f"zenity unavailable: {err}")
    else:
        if dialog_result.returncode == 0:
            selected_path = dialog_result.stdout.strip()
            if selected_path:
                return normalize_player_image_path(selected_path)
            return ""

        if dialog_result.returncode == 1:
            return ""

        stderr_line = dialog_result.stderr.strip() or f"exit code {dialog_result.returncode}"
        picker_errors.append(f"zenity failed: {stderr_line}")

    set_menu_notice("Image picker is unavailable on this system.")
    log_player_action("Player image picker unavailable", " | ".join(picker_errors))
    return None


def set_selected_world_icon(icon_id):
    global selected_world_icon_index

    normalized_icon = normalize_world_icon(icon_id)
    selected_world_icon_index = WORLD_ICON_CHOICES.index(normalized_icon)
    return normalized_icon


def get_selected_world_icon():
    return WORLD_ICON_CHOICES[selected_world_icon_index % len(WORLD_ICON_CHOICES)]


def cycle_selected_world_icon(step):
    global selected_world_icon_index

    selected_world_icon_index = (
        selected_world_icon_index + int(step)
    ) % len(WORLD_ICON_CHOICES)

    icon_id = get_selected_world_icon()
    log_player_action("World icon selected", icon_id)
    return icon_id


def get_world_icon_surface(icon_id, size=(32, 32)):
    normalized_icon = normalize_world_icon(icon_id)
    icon_surface = item_icons.get(normalized_icon)

    if icon_surface is None:
        icon_surface = item_icons.get("sword", make_sword_icon())

    return pygame.transform.smoothscale(icon_surface, size)


def set_game_mode(mode_value):
    global game_mode
    global selected_game_mode
    global day_length
    global night_start_ratio
    global enemy_health_multiplier
    global enemy_damage_multiplier
    global mobs_spawn_enabled

    normalized_mode = normalize_game_mode(mode_value)
    game_mode = normalized_mode
    selected_game_mode = normalized_mode

    day_length = BASE_DAY_LENGTH
    night_start_ratio = BASE_NIGHT_START_RATIO
    enemy_health_multiplier = 1.0
    enemy_damage_multiplier = 1.0
    mobs_spawn_enabled = True

    if normalized_mode == "hard":
        day_duration = BASE_DAY_LENGTH * BASE_NIGHT_START_RATIO
        hard_night_duration = (BASE_DAY_LENGTH - day_duration) * 2.0
        day_length = day_duration + hard_night_duration
        night_start_ratio = day_duration / day_length
        enemy_health_multiplier = 10.0
        enemy_damage_multiplier = 5.0
    elif normalized_mode == "creative":
        mobs_spawn_enabled = False


def apply_mode_player_stats(refill_stats):
    global hp
    global mana
    global stam
    global hp_limit
    global mana_limit
    global stam_limit

    if game_mode == "creative":
        hp_limit = CREATIVE_STAT_VALUE
        mana_limit = CREATIVE_STAT_VALUE
        stam_limit = CREATIVE_STAT_VALUE
        hp = hp_limit
        mana = mana_limit
        stam = stam_limit
        return

    apply_limit_upgrades()

    if refill_stats:
        hp = hp_limit
        mana = mana_limit
        stam = stam_limit
    else:
        hp = min(hp, hp_limit)
        mana = min(mana, mana_limit)
        stam = min(stam, stam_limit)


def make_centered_button(y, width=320, height=56):
    return pygame.Rect(
        WIDTH // 2 - width // 2,
        y,
        width,
        height
    )


def make_pause_button(y, width=620, height=64):
    return pygame.Rect(
        WIDTH // 2 - width // 2,
        y,
        width,
        height
    )


def get_pause_buttons():
    return {
        "resume": make_pause_button(178),
        "toggle_fullscreen": make_pause_button(248),
        "settings": make_pause_button(318),
        "upgrades": make_pause_button(388),
        "shop": make_pause_button(458),
        "codes": make_pause_button(528),
        "save_and_quit": make_pause_button(598)
    }


def get_main_menu_buttons():
    return {
        "new_world": make_centered_button(314, width=380, height=62),
        "load_world": make_centered_button(390, width=380, height=62),
        "multiplayer": make_centered_button(466, width=380, height=62),
        "quit": make_centered_button(542, width=380, height=62),
        "github": pygame.Rect(WIDTH - 252, 18, 228, 48)
    }


def get_new_world_buttons():
    buttons = {
        "create": make_centered_button(530, width=420, height=58),
        "back": make_centered_button(596, width=280, height=46),
        "icon_prev": pygame.Rect(312, 352, 54, 54),
        "icon_next": pygame.Rect(914, 352, 54, 54),
        "choose_image": pygame.Rect(290, 434, 330, 52),
        "clear_image": pygame.Rect(650, 434, 330, 52)
    }

    mode_start_x = 178
    mode_width = 300
    mode_gap = 22
    mode_y = 270
    mode_height = 56

    for index, mode_id in enumerate(GAME_MODE_ORDER):
        buttons[f"mode_{mode_id}"] = pygame.Rect(
            mode_start_x + index * (mode_width + mode_gap),
            mode_y,
            mode_width,
            mode_height
        )

    return buttons


def get_settings_buttons():
    return {
        "toggle_fullscreen": make_pause_button(260, width=700, height=62),
        "resolution": make_pause_button(328, width=700, height=62),
        "fps_lock": make_pause_button(396, width=700, height=62),
        "volume": make_pause_button(464, width=700, height=62),
        "disable_wall_breaking": make_pause_button(532, width=700, height=62),
        "keybinds": make_pause_button(600, width=700, height=62),
        "back": make_pause_button(668, width=700, height=54)
    }


def get_keybind_buttons():
    button_map = {}
    left_x = WIDTH // 2 - 470
    right_x = WIDTH // 2 + 20
    start_y = 226
    row_height = 44
    col_width = 450
    col_height = 38

    for index, action in enumerate(KEYBIND_DISPLAY_ORDER):
        row = index % 13
        col = index // 13
        slot_x = left_x if col == 0 else right_x
        slot_y = start_y + row * row_height
        button_map[action] = pygame.Rect(slot_x, slot_y, col_width, col_height)

    button_map["back"] = pygame.Rect(WIDTH // 2 - 240, 648, 480, 52)
    return button_map


def get_upgrade_buttons():
    button_map = {}
    y = 256
    for upgrade_id in upgrade_labels:
        button_map[upgrade_id] = make_pause_button(y, width=720, height=56)
        y += 66
    button_map["back"] = make_pause_button(644, width=520, height=52)
    return button_map


def get_shop_buttons():
    return {
        "buy_steak": make_pause_button(344, width=720, height=72),
        "back": make_pause_button(634, width=520, height=52)
    }


def get_load_world_entry_rect(index):
    return pygame.Rect(390, 214 + index * 38, 500, 34)


def get_load_world_buttons():
    return {
        "load": pygame.Rect(390, 574, 230, 48),
        "delete": pygame.Rect(650, 574, 240, 48),
        "back": pygame.Rect(490, 636, 300, 42)
    }


def get_game_over_buttons():
    return {
        "retry": make_centered_button(432, width=360, height=58),
        "menu": make_centered_button(504, width=300, height=52)
    }


def get_upgrade_cost(upgrade_id):
    base_cost = upgrade_base_costs.get(upgrade_id, 20)
    return max(1, int(round(base_cost * upgrade_price_multiplier)))


def get_melee_damage_multiplier():
    return 1.0 + upgrade_levels["melee_damage"] * 0.08


def get_magic_damage_multiplier():
    return 1.0 + upgrade_levels["magic_damage"] * 0.07


def get_enemy_wall_break_time():
    # Higher level means mobs need more time to break walls.
    return 15.0 * (1.0 + upgrade_levels["mob_wall_break_slow"] * 0.12)


def apply_limit_upgrades():
    global hp_limit
    global mana_limit
    global stam_limit
    global hp
    global mana
    global stam

    hp_limit = MAX_HP + upgrade_levels["max_health"] * 15
    mana_limit = MAX_MANA + upgrade_levels["max_mana"] * 15
    stam_limit = MAX_STAM + upgrade_levels["max_stamina"] * 15
    hp = min(hp, hp_limit)
    mana = min(mana, mana_limit)
    stam = min(stam, stam_limit)


def try_buy_upgrade(upgrade_id):
    global kill_points
    global upgrade_price_multiplier

    cost = get_upgrade_cost(upgrade_id)
    if kill_points < cost:
        return False

    kill_points -= cost
    upgrade_levels[upgrade_id] += 1
    upgrade_price_multiplier *= 1.015
    apply_mode_player_stats(refill_stats=False)
    log_player_action(
        "Upgrade purchased",
        f"{upgrade_labels.get(upgrade_id, upgrade_id)} | cost={cost} | points={kill_points}"
    )
    return True


def try_buy_steak():
    global kill_points
    global shop_message

    steak_cost = 8
    if kill_points < steak_cost:
        shop_message = "Not enough kills for steak."
        return False

    target_index = get_first_empty_inventory_slot()
    if target_index is None:
        shop_message = "Inventory full."
        return False

    kill_points -= steak_cost
    inventory[target_index] = "steak"
    shop_message = "Bought steak."
    log_player_action("Shop purchase", f"Steak | points={kill_points}")
    return True


def get_code_buttons():
    return {
        "apply": make_pause_button(514, width=320, height=56),
        "back": make_pause_button(580, width=320, height=56)
    }


def get_resolution_label():
    width, height = WINDOW_RESOLUTIONS[selected_resolution_index]
    return f"{width} x {height}"


def get_fps_label():
    fps_limit = FPS_OPTIONS[selected_fps_index]

    if fps_limit == 0:
        return "Unlimited"

    return f"{fps_limit} FPS"


def get_frame_limit():
    return FPS_OPTIONS[selected_fps_index]


def get_runtime_frame_limit():
    fps_limit = get_frame_limit()

    if game_state == "menu" and fps_limit != 0:
        return max(fps_limit, MENU_MIN_FPS)

    return fps_limit


def cycle_resolution():
    global selected_resolution_index
    global menu_background_cache
    global menu_background_cache_tick

    selected_resolution_index = (
        selected_resolution_index + 1
    ) % len(WINDOW_RESOLUTIONS)

    set_display_mode(fullscreen)
    menu_background_cache = None
    menu_background_cache_tick = -99999
    save_global_settings()


def cycle_fps_limit():
    global selected_fps_index

    selected_fps_index = (
        selected_fps_index + 1
    ) % len(FPS_OPTIONS)
    save_global_settings()


def reset_player_limits():
    global hp_limit
    global mana_limit
    global stam_limit

    hp_limit = MAX_HP
    mana_limit = MAX_MANA
    stam_limit = MAX_STAM


def apply_code(code):
    global hp
    global mana
    global stam
    global hp_limit
    global mana_limit
    global stam_limit
    global code_message

    normalized = code.strip().upper()

    if not normalized:
        code_message = "Enter a code first."
        return

    if normalized == "CODEGNG":
        hp_limit = max(hp_limit, 1_000_000)
        hp = 1_000_000
        code_message = "HP set to 1000000."

    elif normalized == "CODEGNG1":
        hp = 1
        hp_limit = max(hp_limit, 1)
        code_message = "HP set to 1."

    elif normalized == "CODEGNG2":
        mana_limit = max(mana_limit, 1_000_000)
        stam_limit = max(stam_limit, 1_000_000)
        mana = 1_000_000
        stam = 1_000_000
        code_message = "Mana and stamina set to 1000000."

    else:
        code_message = "Invalid code."


def get_world_pos_from_screen(screen_pos):
    return (
        player.centerx - WIDTH // 2 + screen_pos[0],
        player.centery - HEIGHT // 2 + screen_pos[1]
    )


def build_default_inventory():
    inventory_items = DEFAULT_INVENTORY_ITEMS[:INVENTORY_CAPACITY]

    if len(inventory_items) < INVENTORY_CAPACITY:
        inventory_items.extend([None] * (INVENTORY_CAPACITY - len(inventory_items)))

    return inventory_items


def build_default_hotbar():
    return SPELL_HOTBAR_ENTRIES + ["sword", "wall", "door", "floor"]


def get_hotbar_slot_key_label(index):
    action = get_hotbar_keybind_action(index)
    return pygame.key.name(keybinds.get(action, DEFAULT_KEYBINDS[action])).upper()


def get_item_label(item_id):
    labels = {
        "sword": "SWORD",
        "axe": "AXE",
        "steak": "STEAK",
        "wall": "WALL",
        "wall1": "WALL 1",
        "wall2": "WALL 2",
        "wall3": "WALL 3",
        "wall4": "WALL 4",
        "stone1_block": "STONE 1 BLOCK",
        "stone2_block": "STONE 2 BLOCK",
        "copper_block": "COPPER BLOCK",
        "door": "DOOR",
        "floor": "FLOOR",
        "torch": "TORCH",
        "snowball": "SNOWBALL",
        "water_bucket": "WATER BUCKET",
        "lava_bucket": "LAVA BUCKET",
        "book_and_quill": "BOOK & QUILL",
        "spell_1": "FIRE",
        "spell_2": "BOLT",
        "spell_3": "DARK",
        "spell_4": "SPARK",
        "spell_5": "BLAST",
        "spell_6": "STORM"
    }
    return labels.get(item_id, str(item_id).upper())


def get_compact_item_label(item_id):
    labels = {
        "sword": "SWORD",
        "axe": "AXE",
        "steak": "STEAK",
        "wall": "WALL",
        "wall1": "WALL1",
        "wall2": "WALL2",
        "wall3": "WALL3",
        "wall4": "WALL4",
        "stone1_block": "STONE1",
        "stone2_block": "STONE2",
        "copper_block": "COPPER",
        "door": "DOOR",
        "floor": "FLOOR",
        "torch": "TORCH",
        "snowball": "SNOW",
        "water_bucket": "WATER",
        "lava_bucket": "LAVA",
        "book_and_quill": "BOOK",
        "spell_1": "FIRE",
        "spell_2": "BOLT",
        "spell_3": "DARK",
        "spell_4": "SPARK",
        "spell_5": "BLAST",
        "spell_6": "STORM"
    }
    return labels.get(item_id, str(item_id).upper())


CRAFTING_RECIPES = [
    {
        "id": "craft_torch",
        "name": "Torch",
        "ingredients": {"floor": 1, "wall": 1},
        "output": {"item": "torch", "count": 1}
    },
    {
        "id": "craft_steak",
        "name": "Steak",
        "ingredients": {"floor": 1, "wall1": 1},
        "output": {"item": "steak", "count": 1}
    },
    {
        "id": "craft_wall_pack",
        "name": "Wall Pack",
        "ingredients": {"wall": 1},
        "output": {"item": "wall4", "count": 2}
    }
]


def get_inventory_item_count(item_id):
    return inventory.count(item_id)


def can_add_inventory_item(item_id, count):
    if count <= 0:
        return False
    return inventory.count(None) >= count


def get_first_empty_inventory_slot():
    try:
        return inventory.index(None)
    except ValueError:
        return None


def get_inventory_counts():
    return Counter(entry for entry in inventory if entry is not None)


def remove_inventory_item(item_id, count):
    removed = 0
    for index in range(len(inventory)):
        if inventory[index] == item_id:
            inventory[index] = None
            removed += 1
            if removed >= count:
                return True
    return False


def add_inventory_item(item_id, count):
    added = 0
    for index in range(len(inventory)):
        if inventory[index] is None:
            inventory[index] = item_id
            added += 1
            if added >= count:
                return True
    return False


def can_craft_recipe(recipe):
    ingredients = recipe.get("ingredients", {})
    output_count = int(recipe.get("output", {}).get("count", 1))
    if not can_add_inventory_item(recipe["output"]["item"], output_count):
        return False

    inventory_counts = get_inventory_counts()

    for item_id, needed in ingredients.items():
        if inventory_counts.get(item_id, 0) < needed:
            return False
    return True


def craft_recipe(recipe):
    global crafting_message

    if not can_craft_recipe(recipe):
        crafting_message = "Missing ingredients or no space."
        return False

    for item_id, needed in recipe["ingredients"].items():
        remove_inventory_item(item_id, needed)

    add_inventory_item(recipe["output"]["item"], recipe["output"]["count"])
    crafting_message = f"Crafted {recipe['output']['count']} {get_item_label(recipe['output']['item'])}."
    log_player_action(
        "Craft",
        f"{recipe['name']} -> {recipe['output']['item']} x{recipe['output']['count']}"
    )
    return True


def get_crafting_buttons():
    buttons = {}
    y = 220
    for recipe in CRAFTING_RECIPES:
        buttons[recipe["id"]] = make_centered_button(y, width=520, height=58)
        y += 74
    return buttons


def is_spell_entry(entry):
    return entry in SPELL_HOTBAR_ENTRIES


def is_inventory_item(entry):
    return entry in ITEM_IDS


def is_valid_hotbar_entry(entry):
    return entry is None or is_inventory_item(entry) or is_spell_entry(entry)


def get_active_hotbar_entry():
    if 0 <= active_hotbar_slot < len(hotbar_slots):
        return hotbar_slots[active_hotbar_slot]

    return None


def ensure_required_inventory_items():
    global inventory

    for required_item in ITEM_IDS:
        if required_item in inventory:
            continue

        empty_index = get_first_empty_inventory_slot()
        if empty_index is None:
            break
        inventory[empty_index] = required_item


def serialize_hotbar():
    return list(hotbar_slots)


def load_hotbar(data):
    global hotbar_slots
    global active_hotbar_slot

    hotbar_slots = build_default_hotbar()

    saved_hotbar = data.get("hotbar", [])

    if isinstance(saved_hotbar, list):
        for index in range(HOTBAR_TOTAL_SLOTS):
            if index >= len(saved_hotbar):
                continue

            entry = saved_hotbar[index]

            if is_valid_hotbar_entry(entry):
                hotbar_slots[index] = entry

    saved_active = data.get("active_hotbar_slot", DEFAULT_ACTIVE_HOTBAR_SLOT)

    if isinstance(saved_active, int) and 0 <= saved_active < len(hotbar_slots):
        active_hotbar_slot = saved_active
    else:
        active_hotbar_slot = DEFAULT_ACTIVE_HOTBAR_SLOT


def build_inventory_slot_rects():
    return [
        pygame.Rect(
            INVENTORY_GRID_START_X + (index % INVENTORY_COLUMNS) * (INVENTORY_SLOT_SIZE + INVENTORY_SLOT_GAP),
            INVENTORY_GRID_START_Y + (index // INVENTORY_COLUMNS) * (INVENTORY_SLOT_SIZE + INVENTORY_SLOT_GAP),
            INVENTORY_SLOT_SIZE,
            INVENTORY_SLOT_SIZE
        )
        for index in range(INVENTORY_CAPACITY)
    ]


def build_hotbar_slot_rects():
    slot_size = 58
    gap = 10
    total_width = HOTBAR_TOTAL_SLOTS * slot_size + (HOTBAR_TOTAL_SLOTS - 1) * gap
    start_x = WIDTH // 2 - total_width // 2
    start_y = HEIGHT - 74

    return [
        pygame.Rect(
            start_x + index * (slot_size + gap),
            start_y,
            slot_size,
            slot_size
        )
        for index in range(HOTBAR_TOTAL_SLOTS)
    ]


INVENTORY_SLOT_RECTS = build_inventory_slot_rects()
HOTBAR_SLOT_RECTS = build_hotbar_slot_rects()


def get_inventory_slot_rect(index):
    return INVENTORY_SLOT_RECTS[index]


def get_hotbar_slot_rects():
    return HOTBAR_SLOT_RECTS


def get_hotbar_slot_index_at(pos):
    for index, rect in enumerate(get_hotbar_slot_rects()):
        if rect.collidepoint(pos):
            return index

    return None


def get_inventory_slot_index_at(pos):
    for index in range(len(inventory)):
        if get_inventory_slot_rect(index).collidepoint(pos):
            return index

    return None


def get_icon_for_entry(entry):
    if entry in item_icons:
        return item_icons[entry]

    if entry in spell_icons:
        return spell_icons[entry]

    return None


def cast_spell_from_slot(spell_entry, target_pos):
    global mana

    try:
        spell_data = SPELL_SLOTS.get(spell_entry)

        if spell_data is None:
            return False

        if len(projectiles) >= MAX_ACTIVE_PROJECTILES:
            return False

        if (
            not isinstance(target_pos, (tuple, list))
            or len(target_pos) != 2
        ):
            return False

        spell_frames = spell_data.get("frames")
        if not isinstance(spell_frames, list):
            spell_frames = []

        base_damage = spell_data.get("damage", 0)
        if not isinstance(base_damage, (int, float)):
            base_damage = 0

        if mana < 70:
            return False

        mana -= 70
        boosted_damage = int(round(base_damage * get_magic_damage_multiplier()))

        projectiles.append(
            Projectile(
                player.center,
                target_pos,
                spell_frames,
                boosted_damage
            )
        )

        add_screen_shake(4.0)
        trigger_impact_flash((118, 162, 242), 46)
        play_sfx("spell")
        spawn_particles(
            player.center,
            (100, 150, 255),
            15
        )
        return True
    except Exception as err:
        print("spell cast failed:", err)
        return False


def throw_snowball(target_pos):
    if len(projectiles) >= MAX_ACTIVE_PROJECTILES:
        return False

    if (
            not isinstance(target_pos, (tuple, list))
            or len(target_pos) != 2
    ):
        return False

    snowball_projectile = Projectile(
        player.center,
        target_pos,
        snowball_projectile_frames,
        damage=1,
        speed=13
    )
    snowball_projectile.life = 90
    projectiles.append(snowball_projectile)
    spawn_particles(player.center, (228, 236, 252), 5)
    return True


def can_place_floor_at(tile_pos):
    return get_tile(tile_pos[0], tile_pos[1]) not in LIQUID_TILE_IDS


def place_equipped_item_at_mouse(mouse_pos):
    selected_entry = get_active_hotbar_entry()

    if selected_entry not in WALL_ITEM_IDS + ["door", "floor", "torch", "water_bucket", "lava_bucket"]:
        return False

    world_x, world_y = get_world_pos_from_screen(mouse_pos)
    tile_pos = (int(world_x // TILE), int(world_y // TILE))

    if selected_entry == "floor":
        if can_place_floor_at(tile_pos):
            placed_water.discard(tile_pos)
            placed_lava.discard(tile_pos)
            placed_floors.add(tile_pos)
            play_sfx("place")
            return True

        return False

    if selected_entry == "torch":
        if tile_pos in walls:
            torch_positions.add(tile_pos)
            torch_mounts[tile_pos] = "wall"
            play_sfx("place")
            return True

        if tile_pos in placed_floors or get_tile(tile_pos[0], tile_pos[1]) not in LIQUID_TILE_IDS:
            torch_positions.add(tile_pos)
            torch_mounts[tile_pos] = "ground"
            play_sfx("place")
            return True
        return False

    if selected_entry == "water_bucket":
        if tile_pos in walls or tile_pos in doors:
            return False
        placed_floors.discard(tile_pos)
        torch_positions.discard(tile_pos)
        torch_mounts.pop(tile_pos, None)
        placed_lava.discard(tile_pos)
        drained_water.discard(tile_pos)
        placed_water.add(tile_pos)
        invalidate_terrain_caches(tile_pos)
        play_sfx("place")
        return True

    if selected_entry == "lava_bucket":
        if tile_pos in walls or tile_pos in doors:
            return False
        placed_floors.discard(tile_pos)
        torch_positions.discard(tile_pos)
        torch_mounts.pop(tile_pos, None)
        placed_water.discard(tile_pos)
        drained_water.discard(tile_pos)
        placed_lava.add(tile_pos)
        add_stone1_ring_around_lava(tile_pos)
        invalidate_terrain_caches(tile_pos)
        play_sfx("place")
        return True

    if get_tile(tile_pos[0], tile_pos[1]) in LIQUID_TILE_IDS:
        return False

    if selected_entry in WALL_ITEM_IDS:
        doors.discard(tile_pos)
        if tile_pos in torch_positions:
            torch_mounts[tile_pos] = "wall"
        walls.add(tile_pos)
        wall_types[tile_pos] = selected_entry
        update_open_doors(force=True)
        play_sfx("place")
        return True

    if selected_entry == "door":
        walls.discard(tile_pos)
        wall_types.pop(tile_pos, None)
        if tile_pos in torch_positions and torch_mounts.get(tile_pos) == "wall":
            torch_positions.discard(tile_pos)
            torch_mounts.pop(tile_pos, None)
        doors.add(tile_pos)
        update_open_doors(force=True)
        play_sfx("place")
        return True

    return False


def break_equipped_item_at_mouse(mouse_pos):
    selected_entry = get_active_hotbar_entry()

    if selected_entry not in WALL_ITEM_IDS + ["door", "floor", "torch", "water_bucket", "lava_bucket"]:
        return False

    world_x, world_y = get_world_pos_from_screen(mouse_pos)
    tile_pos = (int(world_x // TILE), int(world_y // TILE))

    if selected_entry in WALL_ITEM_IDS and tile_pos in walls:
        walls.discard(tile_pos)
        wall_types.pop(tile_pos, None)
        if tile_pos in torch_positions and torch_mounts.get(tile_pos) == "wall":
            torch_positions.discard(tile_pos)
            torch_mounts.pop(tile_pos, None)
        play_sfx("break")
        return True

    if selected_entry == "door" and tile_pos in doors:
        doors.discard(tile_pos)
        update_open_doors(force=True)
        play_sfx("break")
        return True

    if selected_entry == "floor" and tile_pos in placed_floors:
        placed_floors.discard(tile_pos)
        play_sfx("break")
        return True

    if selected_entry == "torch" and tile_pos in torch_positions:
        torch_positions.discard(tile_pos)
        torch_mounts.pop(tile_pos, None)
        play_sfx("break")
        return True

    if selected_entry in ["water_bucket", "lava_bucket"]:
        removed = replace_water_with_sand(tile_pos)
        if not removed:
            removed = replace_lava_with_sand(tile_pos)
        if removed:
            play_sfx("break")
        return removed

    return False


def get_default_waypoint_name(waypoint_id):
    return f"Waypoint {waypoint_id}"


def get_waypoint_color_by_id(waypoint_id):
    return WAYPOINT_COLORS[(waypoint_id - 1) % len(WAYPOINT_COLORS)]


def get_waypoint_by_id(waypoint_id):
    for waypoint in waypoints:
        if waypoint["id"] == waypoint_id:
            return waypoint

    return None


def reset_waypoint_state():
    global selected_waypoint_id
    global waypoint_editing
    global waypoint_name_input
    global next_waypoint_id

    selected_waypoint_id = None
    waypoint_editing = False
    waypoint_name_input = ""
    next_waypoint_id = 1


def create_waypoint(world_x, world_y):
    global next_waypoint_id

    waypoint = {
        "id": next_waypoint_id,
        "x": int(world_x),
        "y": int(world_y),
        "name": get_default_waypoint_name(next_waypoint_id),
        "color": get_waypoint_color_by_id(next_waypoint_id)
    }

    waypoints.append(waypoint)
    next_waypoint_id += 1
    return waypoint


def start_waypoint_editing(waypoint):
    global selected_waypoint_id
    global waypoint_editing
    global waypoint_name_input

    if waypoint is None:
        return

    selected_waypoint_id = waypoint["id"]
    waypoint_name_input = str(waypoint.get("name", ""))
    waypoint_editing = True


def finish_waypoint_editing(apply_changes):
    global waypoint_editing
    global waypoint_name_input

    waypoint = get_waypoint_by_id(selected_waypoint_id)

    if waypoint and apply_changes:
        new_name = waypoint_name_input.strip()
        waypoint["name"] = new_name or get_default_waypoint_name(waypoint["id"])

    waypoint_editing = False
    waypoint_name_input = ""


def remove_waypoint_by_id(waypoint_id):
    global selected_waypoint_id
    global waypoint_editing
    global waypoint_name_input

    if waypoint_id is None:
        return

    for index, waypoint in enumerate(waypoints):
        if waypoint["id"] == waypoint_id:
            del waypoints[index]
            break

    if selected_waypoint_id == waypoint_id:
        selected_waypoint_id = None
        waypoint_editing = False
        waypoint_name_input = ""


def get_waypoint_screen_data(waypoint):
    screen_x = waypoint["x"] + WIDTH // 2 - player.centerx
    screen_y = waypoint["y"] + HEIGHT // 2 - player.centery
    margin = 44

    if margin <= screen_x <= WIDTH - margin and margin <= screen_y <= HEIGHT - margin:
        return {
            "offscreen": False,
            "anchor": (int(screen_x), int(screen_y))
        }

    center_x = WIDTH / 2
    center_y = HEIGHT / 2
    dx = screen_x - center_x
    dy = screen_y - center_y

    if dx == 0 and dy == 0:
        dx = 0.001

    scale_x = (WIDTH / 2 - margin) / abs(dx) if dx != 0 else 999999
    scale_y = (HEIGHT / 2 - margin) / abs(dy) if dy != 0 else 999999
    scale = min(scale_x, scale_y)

    arrow_x = center_x + dx * scale
    arrow_y = center_y + dy * scale
    angle = math.atan2(dy, dx)
    size = 16

    arrow_points = [
        (
            int(arrow_x + math.cos(angle) * size),
            int(arrow_y + math.sin(angle) * size)
        ),
        (
            int(arrow_x + math.cos(angle + 2.45) * size * 0.82),
            int(arrow_y + math.sin(angle + 2.45) * size * 0.82)
        ),
        (
            int(arrow_x + math.cos(angle - 2.45) * size * 0.82),
            int(arrow_y + math.sin(angle - 2.45) * size * 0.82)
        )
    ]

    return {
        "offscreen": True,
        "anchor": (int(arrow_x), int(arrow_y)),
        "arrow_points": arrow_points
    }


def find_waypoint_at_screen_pos(screen_pos, hit_radius=22):
    prioritized = []

    selected_waypoint = get_waypoint_by_id(selected_waypoint_id)

    if selected_waypoint is not None:
        prioritized.append(selected_waypoint)

    for waypoint in reversed(waypoints):
        if selected_waypoint is not None and waypoint["id"] == selected_waypoint["id"]:
            continue

        prioritized.append(waypoint)

    radius_sq = hit_radius * hit_radius

    for waypoint in prioritized:
        waypoint_data = get_waypoint_screen_data(waypoint)
        dx = screen_pos[0] - waypoint_data["anchor"][0]
        dy = screen_pos[1] - waypoint_data["anchor"][1]

        if dx * dx + dy * dy <= radius_sq:
            return waypoint

    return None


def serialize_waypoints():
    return [
        {
            "id": waypoint["id"],
            "x": waypoint["x"],
            "y": waypoint["y"],
            "name": waypoint["name"],
            "color": list(waypoint["color"])
        }
        for waypoint in waypoints
    ]


def load_waypoints(data):
    global next_waypoint_id

    waypoints.clear()
    reset_waypoint_state()

    loaded_waypoints = data.get("waypoints", [])

    if not isinstance(loaded_waypoints, list):
        loaded_waypoints = []

    max_id = 0

    for index, entry in enumerate(loaded_waypoints):
        if not isinstance(entry, dict):
            continue

        waypoint_id = int(entry.get("id", index + 1))
        color = entry.get("color", get_waypoint_color_by_id(waypoint_id))

        if (
            not isinstance(color, (list, tuple))
            or len(color) != 3
        ):
            color = get_waypoint_color_by_id(waypoint_id)

        waypoints.append(
            {
                "id": waypoint_id,
                "x": int(entry.get("x", 0)),
                "y": int(entry.get("y", 0)),
                "name": str(entry.get("name", get_default_waypoint_name(waypoint_id))),
                "color": (
                    int(color[0]),
                    int(color[1]),
                    int(color[2])
                )
            }
        )
        max_id = max(max_id, waypoint_id)

    next_waypoint_id = max_id + 1 if max_id else 1


def draw_button(rect, label, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    button_rect = rect.inflate(4, 4) if hovered else rect
    fill = (86, 60, 34) if hovered else (66, 46, 26)
    inner = (112, 82, 50) if hovered else (86, 62, 38)
    border = (238, 198, 126) if hovered else (182, 146, 92)

    draw_knight_panel(
        button_rect,
        border_color=border,
        fill_color=fill,
        inner_color=inner,
        border_radius=10,
        draw_rivets=False
    )

    txt = ui_font.render(label, True, (252, 236, 198))
    txt_rect = txt.get_rect(center=button_rect.center)
    surf.blit(txt, txt_rect)


def draw_labeled_bar(x, y, width, label, value, value_limit, fill_color):
    ratio = max(0.0, min(1.0, value / max(1, value_limit)))
    bar_rect = pygame.Rect(x, y, width, 20)
    pygame.draw.rect(surf, (20, 14, 10), bar_rect, border_radius=7)
    pygame.draw.rect(surf, (120, 94, 62), bar_rect, 2, border_radius=7)

    fill_width = int((width - 6) * ratio)
    if fill_width > 0:
        fill_rect = pygame.Rect(x + 3, y + 3, fill_width, 14)
        pygame.draw.rect(surf, fill_color, fill_rect, border_radius=6)
        highlight_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, 5)
        highlight_color = (
            clamp_channel(fill_color[0] + 42),
            clamp_channel(fill_color[1] + 42),
            clamp_channel(fill_color[2] + 42)
        )
        pygame.draw.rect(surf, highlight_color, highlight_rect, border_radius=4)

    label_img = small_font.render(
        f"{label}  {int(value)}/{int(value_limit)}",
        True,
        (244, 228, 196)
    )
    surf.blit(label_img, (x + 8, y + 3))


def draw_menu_button(rect, label, mouse_pos, accent_color):
    hovered = rect.collidepoint(mouse_pos)
    button_rect = rect.inflate(6, 6) if hovered else rect
    border_color = (
        clamp_channel(accent_color[0] + 36),
        clamp_channel(accent_color[1] + 36),
        clamp_channel(accent_color[2] + 28)
    ) if hovered else (
        clamp_channel(accent_color[0] - 16),
        clamp_channel(accent_color[1] - 16),
        clamp_channel(accent_color[2] - 16)
    )

    draw_knight_panel(
        button_rect,
        border_color=border_color,
        fill_color=(42, 28, 18),
        inner_color=(58, 40, 26),
        border_radius=12,
        draw_rivets=False
    )

    pygame.draw.rect(
        surf,
        accent_color,
        (button_rect.x + 12, button_rect.y + 12, 10, button_rect.height - 24),
        border_radius=5
    )

    txt = ui_font.render(label, True, (248, 236, 204))
    txt_rect = txt.get_rect(center=button_rect.center)
    txt_rect.x += 10
    surf.blit(txt, txt_rect)


def draw_menu_background():
    global menu_background_cache
    global menu_background_cache_tick

    tick = pygame.time.get_ticks()
    if (
            menu_background_cache is not None
            and tick - menu_background_cache_tick <= MENU_BG_CACHE_MS
    ):
        surf.blit(menu_background_cache, (0, 0))
        return

    background_surface = pygame.Surface((WIDTH, HEIGHT))
    water_frame = water_frames[(tick // 120) % len(water_frames)]
    scroll_x = (tick // 22) % TILE
    scroll_y = (tick // 34) % TILE
    cols = WIDTH // TILE + 3
    rows = HEIGHT // TILE + 3

    for col in range(cols):
        for row in range(rows):
            draw_x = col * TILE - scroll_x
            draw_y = row * TILE - scroll_y
            selector = (col * 7 + row * 11 + tick // 500) % 12

            if selector in [0, 1]:
                tile_surface = water_frame
            elif selector in [2, 3, 4]:
                tile_surface = sand_img
            else:
                tile_surface = grass_plain

            background_surface.blit(tile_surface, (draw_x, draw_y))

            if tile_surface is grass_plain and selector == 10:
                background_surface.blit(flower_tile, (draw_x, draw_y))
            elif tile_surface is grass_plain and selector == 11:
                background_surface.blit(bush_tile, (draw_x, draw_y))

            if selector == 8 and (col + row) % 3 == 0:
                background_surface.blit(bridge_img, (draw_x, draw_y))

    tint_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tint_overlay.fill((16, 11, 7, 132))
    pygame.draw.circle(tint_overlay, (255, 206, 132, 54), (WIDTH - 210, 142), 194)
    pygame.draw.circle(tint_overlay, (166, 114, 64, 42), (140, HEIGHT - 118), 230)
    background_surface.blit(tint_overlay, (0, 0))

    banner_rect = pygame.Rect(68, HEIGHT - 114, WIDTH - 136, 62)
    pygame.draw.rect(background_surface, (24, 18, 12), banner_rect, border_radius=16)
    pygame.draw.rect(background_surface, (64, 48, 30), banner_rect.inflate(-8, -8), border_radius=12)
    pygame.draw.rect(background_surface, (206, 166, 102), banner_rect, 2, border_radius=16)

    title_band = pygame.Rect(72, 66, 540, 122)
    title_shadow_band = title_band.move(0, 6)
    pygame.draw.rect(background_surface, (8, 6, 4), title_shadow_band, border_radius=18)
    pygame.draw.rect(background_surface, (26, 18, 12), title_band, border_radius=18)
    pygame.draw.rect(background_surface, (42, 28, 18), title_band.inflate(-8, -8), border_radius=14)
    pygame.draw.rect(background_surface, (226, 186, 108), title_band, 3, border_radius=18)

    title_shadow = hero_font.render("TERARIANTH", True, (0, 0, 0))
    background_surface.blit(title_shadow, (90, 86))
    title_img = hero_font.render("TERARIANTH", True, (250, 224, 168))
    background_surface.blit(title_img, (86, 82))

    subtitle = font.render(
        "Survive the night, build a fortress, and keep the world alive.",
        True,
        (228, 210, 176)
    )
    background_surface.blit(subtitle, (88, 150))

    preview_panel = pygame.Rect(824, 132, 340, 402)
    preview_shadow = preview_panel.move(0, 6)
    pygame.draw.rect(background_surface, (8, 6, 4), preview_shadow, border_radius=18)
    pygame.draw.rect(background_surface, (24, 16, 10), preview_panel, border_radius=18)
    pygame.draw.rect(background_surface, (42, 30, 20), preview_panel.inflate(-8, -8), border_radius=14)
    pygame.draw.rect(background_surface, (186, 148, 90), preview_panel, 3, border_radius=18)

    preview_ground = pygame.Rect(preview_panel.x + 18, preview_panel.bottom - 118, preview_panel.width - 36, 82)
    pygame.draw.rect(background_surface, (44, 58, 38), preview_ground, border_radius=14)
    pygame.draw.rect(background_surface, (114, 138, 88), preview_ground, 2, border_radius=14)

    player_preview = safe(idle_anim, tick * 0.01)
    background_surface.blit(player_preview, (preview_panel.x + 72, preview_panel.y + 126))

    enemy_preview = safe(monster_frames, tick * 0.02)
    background_surface.blit(enemy_preview, (preview_panel.x + 192, preview_panel.y + 204))

    sword_preview = pygame.transform.smoothscale(sword_img, (112, 112))
    background_surface.blit(sword_preview, (preview_panel.x + 210, preview_panel.y + 30))

    preview_label = section_font.render("WORLD READY", True, (244, 224, 176))
    background_surface.blit(preview_label, (preview_panel.x + 26, preview_panel.y + 28))

    preview_copy = font.render(
        "Use new world to start fresh or load an existing save.",
        True,
        (224, 210, 176)
    )
    background_surface.blit(preview_copy, (preview_panel.x + 28, preview_panel.y + 72))

    menu_background_cache = background_surface
    menu_background_cache_tick = tick
    surf.blit(menu_background_cache, (0, 0))


def draw_main_menu_screen():
    mouse_pos = scale_mouse_pos(pygame.mouse.get_pos())
    draw_menu_background()

    buttons = get_main_menu_buttons()
    draw_menu_button(buttons["new_world"], "New World", mouse_pos, (168, 136, 78))
    draw_menu_button(buttons["load_world"], "Load World", mouse_pos, (144, 124, 92))
    draw_menu_button(buttons["multiplayer"], "Multiplayer", mouse_pos, (196, 128, 74))
    draw_menu_button(buttons["quit"], "Quit", mouse_pos, (180, 86, 72))
    draw_menu_button(buttons["github"], "GitHub", mouse_pos, (106, 146, 204))

    save_count = len(get_worlds())
    footer = font.render(
        f"{save_count} save{'s' if save_count != 1 else ''} available   1/2/3/4/5 keyboard shortcuts",
        True,
        (232, 216, 182)
    )
    surf.blit(footer, (84, 620))

    prompt = font.render("Choose a world action to begin.", True, (244, 232, 204))
    surf.blit(prompt, (84, 646))
    github_line = small_font.render("GitHub: github.com/andreyofficial", True, (210, 228, 255))
    surf.blit(github_line, (WIDTH - 294, 72))

    if menu_notice_message and pygame.time.get_ticks() < menu_notice_until_ms:
        notice_rect = pygame.Rect(84, 672, 620, 34)
        draw_knight_panel(
            notice_rect,
            border_color=(194, 162, 106),
            fill_color=(30, 22, 14),
            inner_color=(48, 34, 22),
            border_radius=8,
            draw_rivets=False
        )
        notice_text = font.render(menu_notice_message, True, (240, 226, 196))
        surf.blit(notice_text, (notice_rect.x + 12, notice_rect.y + 8))


def draw_new_world_menu():
    mouse_pos = scale_mouse_pos(pygame.mouse.get_pos())
    draw_menu_background()

    panel = pygame.Rect(120, 72, 1040, 576)
    draw_knight_panel(
        panel,
        border_color=(208, 172, 106),
        fill_color=(22, 14, 8),
        inner_color=(40, 26, 16),
        border_radius=20,
        draw_rivets=True
    )

    title = section_font.render("NEW WORLD", True, (244, 228, 188))
    surf.blit(title, (panel.x + 34, panel.y + 30))

    subtitle = font.render(
        "Enter a world name or seed. The world is saved immediately after creation.",
        True,
        (228, 212, 178)
    )
    surf.blit(subtitle, (panel.x + 36, panel.y + 74))

    input_rect = pygame.Rect(panel.x + 36, panel.y + 112, panel.width - 72, 74)
    draw_knight_panel(
        input_rect,
        border_color=(214, 176, 106),
        fill_color=(26, 18, 10),
        inner_color=(44, 30, 18),
        border_radius=14,
        draw_rivets=False
    )

    shown_seed = seed_input if seed_input else "Type world name or seed"
    shown_color = (252, 240, 210) if seed_input else (168, 150, 126)
    seed_img = ui_font.render(shown_seed, True, shown_color)
    surf.blit(seed_img, (input_rect.x + 20, input_rect.y + 23))

    buttons = get_new_world_buttons()
    selected_icon = get_selected_world_icon()
    icon_preview_rect = pygame.Rect(380, 352, 520, 54)
    draw_knight_panel(
        icon_preview_rect,
        border_color=(196, 160, 102),
        fill_color=(24, 16, 10),
        inner_color=(40, 28, 18),
        border_radius=12,
        draw_rivets=False
    )

    draw_menu_button(buttons["icon_prev"], "<", mouse_pos, (170, 140, 92))
    draw_menu_button(buttons["icon_next"], ">", mouse_pos, (170, 140, 92))
    icon_surface = get_world_icon_surface(selected_icon, size=(36, 36))
    icon_rect = icon_surface.get_rect(midleft=(icon_preview_rect.x + 14, icon_preview_rect.centery))
    surf.blit(icon_surface, icon_rect)

    icon_label = ui_font.render(f"Icon: {get_compact_item_label(selected_icon)}", True, (244, 232, 198))
    surf.blit(icon_label, (icon_rect.right + 12, icon_preview_rect.y + 10))

    mode_title = font.render("Game Mode", True, (232, 218, 184))
    surf.blit(mode_title, (panel.x + 38, 236))

    for mode_id in GAME_MODE_ORDER:
        button_id = f"mode_{mode_id}"
        mode_rect = buttons[button_id]
        mode_hovered = mode_rect.collidepoint(mouse_pos)
        is_selected = selected_game_mode == mode_id
        fill_color = (44, 32, 22) if not is_selected else (70, 50, 32)
        if mode_hovered and not is_selected:
            fill_color = (58, 42, 30)
        border_color = (246, 210, 126) if is_selected else (182, 146, 92)
        pygame.draw.rect(surf, fill_color, mode_rect, border_radius=10)
        pygame.draw.rect(surf, border_color, mode_rect, 2, border_radius=10)
        mode_img = font.render(GAME_MODE_LABELS[mode_id], True, (244, 228, 188))
        surf.blit(mode_img, mode_img.get_rect(center=mode_rect.center))

    description = font.render(
        GAME_MODE_DESCRIPTIONS[selected_game_mode],
        True,
        (228, 212, 180)
    )
    surf.blit(description, (panel.x + 38, 332))

    image_title = font.render("Player Image", True, (232, 218, 184))
    surf.blit(image_title, (panel.x + 38, 392))

    if selected_player_image_path:
        player_image_line = compact_path_label(selected_player_image_path, max_chars=86)
        player_image_color = (236, 222, 190)
    else:
        player_image_line = "Default knight animation"
        player_image_color = (170, 154, 126)

    image_status = small_font.render(player_image_line, True, player_image_color)
    surf.blit(image_status, (panel.x + 38, 418))

    helper_line_1 = font.render("Press Enter or Create to generate the world.", True, (224, 206, 174))
    helper_line_2 = font.render(
        (
            f"{get_keybind_name('pick_player_image')} picks image, "
            f"{get_keybind_name('clear_player_image')} clears, "
            f"{get_keybind_name('pause')} or Back returns."
        ),
        True,
        (224, 206, 174)
    )
    surf.blit(helper_line_1, (panel.x + 38, panel.y + 410))
    surf.blit(helper_line_2, (panel.x + 38, panel.y + 432))

    draw_menu_button(buttons["choose_image"], "Choose Player Image", mouse_pos, (160, 130, 92))
    draw_menu_button(buttons["clear_image"], "Use Default Player", mouse_pos, (136, 118, 96))
    draw_menu_button(buttons["create"], "Create World", mouse_pos, (178, 148, 84))
    draw_menu_button(buttons["back"], "Back", mouse_pos, (148, 124, 92))


def draw_load_world_menu():
    mouse_pos = scale_mouse_pos(pygame.mouse.get_pos())
    draw_menu_background()

    panel = pygame.Rect(316, 96, 648, 604)
    draw_knight_panel(
        panel,
        border_color=(202, 166, 100),
        fill_color=(22, 14, 8),
        inner_color=(40, 26, 16),
        border_radius=20,
        draw_rivets=True
    )

    title = section_font.render("LOAD WORLD", True, (244, 228, 190))
    surf.blit(title, (panel.x + 30, panel.y + 24))

    subtitle = font.render(
        "Select a save, then load it or delete it from the list.",
        True,
        (228, 210, 176)
    )
    surf.blit(subtitle, (panel.x + 32, panel.y + 64))

    worlds = get_worlds()

    for i, world_name in enumerate(worlds[:9]):
        entry_rect = get_load_world_entry_rect(i)
        selected = selected_load_world_name == world_name
        bg_color = (78, 54, 34) if selected else (38, 26, 18)
        border_color = (246, 208, 124) if selected else (172, 140, 94)
        pygame.draw.rect(surf, bg_color, entry_rect, border_radius=8)
        pygame.draw.rect(surf, border_color, entry_rect, 2, border_radius=8)

        metadata = get_world_metadata(world_name)
        world_icon = get_world_icon_surface(metadata["icon"], size=(26, 26))
        world_icon_rect = world_icon.get_rect(midleft=(entry_rect.x + 10, entry_rect.centery))
        surf.blit(world_icon, world_icon_rect)

        label = font.render(
            f"{i + 1}  {world_name}   [{GAME_MODE_LABELS.get(metadata['mode'], 'Easy')}]",
            True,
            (252, 236, 194) if selected else (226, 212, 182)
        )
        surf.blit(label, (world_icon_rect.right + 10, entry_rect.y + 8))

    if not worlds:
        empty_msg = font.render("No saved worlds found yet.", True, (228, 210, 176))
        surf.blit(empty_msg, (panel.x + 32, panel.y + 124))

    buttons = get_load_world_buttons()
    draw_menu_button(buttons["load"], "Load Selected", mouse_pos, (176, 146, 84))
    draw_menu_button(buttons["delete"], "Delete Selected", mouse_pos, (186, 96, 82))
    draw_menu_button(buttons["back"], "Back", mouse_pos, (148, 124, 92))

    status_line = load_world_message or "Select a world, then choose Load or Delete."
    status = font.render(status_line, True, (234, 220, 190))
    surf.blit(status, (panel.x + 32, panel.y + 524))


def draw_game_over_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((12, 2, 0, 182))
    pygame.draw.circle(overlay, (210, 52, 34, 62), (WIDTH // 2, HEIGHT // 2 - 80), 280)
    surf.blit(overlay, (0, 0))

    panel = pygame.Rect(260, 142, 760, 430)
    draw_knight_panel(
        panel,
        border_color=(214, 102, 84),
        fill_color=(28, 12, 10),
        inner_color=(46, 20, 18),
        border_radius=20,
        draw_rivets=True
    )

    title = hero_font.render("YOU DIED", True, (255, 218, 206))
    surf.blit(title, title.get_rect(center=(WIDTH // 2, 228)))

    world_name = game_over_snapshot.get("world_name", "Unsaved World")
    deletion_status = game_over_snapshot.get("save_delete_status", "No save file to delete.")
    detail_lines = [
        f"World: {world_name}",
        f"Day Reached: {game_over_snapshot.get('day', 1)}",
        f"Total Kills: {game_over_snapshot.get('kills', 0)}",
        deletion_status
    ]

    for index, line in enumerate(detail_lines):
        text_img = font.render(line, True, (248, 214, 204))
        surf.blit(text_img, text_img.get_rect(center=(WIDTH // 2, 328 + index * 34)))

    remaining_ms = max(0, game_over_close_at_ms - pygame.time.get_ticks())
    remaining_seconds = max(0, int(math.ceil(remaining_ms / 1000)))
    closing_line = ui_font.render(
        f"Closing game in {remaining_seconds}s...",
        True,
        (255, 188, 172)
    )
    surf.blit(closing_line, closing_line.get_rect(center=(WIDTH // 2, 548)))


def draw_inventory_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surf.blit(overlay, (0, 0))

    panel = INVENTORY_PANEL_RECT
    draw_knight_panel(
        panel,
        border_color=(210, 172, 104),
        fill_color=(24, 16, 10),
        inner_color=(42, 28, 18),
        border_radius=16,
        draw_rivets=True
    )

    title = title_font.render("INVENTORY", True, (252, 232, 184))
    surf.blit(title, (panel.x + 32, panel.y + 22))

    subtitle = font.render("48 slots   Click an item, then click any hotbar slot to equip", True, (232, 214, 180))
    surf.blit(subtitle, (panel.x + 36, panel.y + 74))

    for index, item in enumerate(inventory):
        slot = get_inventory_slot_rect(index)
        is_selected = index == inventory_selected_index

        pygame.draw.rect(
            surf,
            (74, 56, 28) if is_selected else (56, 43, 24),
            slot,
            border_radius=10
        )
        pygame.draw.rect(
            surf,
            (255, 220, 120) if is_selected else (170, 146, 88),
            slot,
            3,
            border_radius=10
        )

        icon = get_icon_for_entry(item)

        if icon is not None:
            icon_rect = icon.get_rect(center=(slot.centerx, slot.centery - 6))
            surf.blit(icon, icon_rect)

        label = "EMPTY" if item is None else get_compact_item_label(item)
        txt = small_font.render(label, True, (255, 245, 220) if item is not None else (182, 172, 150))
        txt_rect = txt.get_rect(center=(slot.centerx, slot.bottom - 11))
        surf.blit(txt, txt_rect)

        slot_num = small_font.render(str(index + 1), True, (210, 180, 95))
        surf.blit(slot_num, (slot.x + 8, slot.y + 6))

    info_rect = pygame.Rect(panel.x + 620, panel.y + 116, 470, 446)
    draw_knight_panel(
        info_rect,
        border_color=(184, 150, 94),
        fill_color=(30, 22, 14),
        inner_color=(46, 34, 22),
        border_radius=14,
        draw_rivets=False
    )

    enemy_counts = Counter(en.enemy_type for en in enemies)
    used_slots = INVENTORY_CAPACITY - inventory.count(None)
    info_x = info_rect.x + 20
    start_y = info_rect.y + 16
    model_rect = pygame.Rect(info_rect.x + 292, info_rect.y + 16, 158, 206)
    draw_knight_panel(
        model_rect,
        border_color=(166, 138, 88),
        fill_color=(26, 18, 12),
        inner_color=(40, 28, 18),
        border_radius=10,
        draw_rivets=False
    )

    model_title = small_font.render("PLAYER MODEL", True, (236, 220, 186))
    surf.blit(model_title, model_title.get_rect(center=(model_rect.centerx, model_rect.y + 14)))

    model_preview = custom_player_surface if custom_player_surface is not None else safe(idle_anim, frame)
    if facing_left:
        model_preview = pygame.transform.flip(model_preview, True, False)
    if model_preview is not None:
        target_w = model_rect.width - 24
        target_h = model_rect.height - 44
        scale = min(
            target_w / max(1, model_preview.get_width()),
            target_h / max(1, model_preview.get_height())
        )
        preview_size = (
            max(1, int(model_preview.get_width() * scale)),
            max(1, int(model_preview.get_height() * scale))
        )
        preview_scaled = pygame.transform.smoothscale(model_preview, preview_size)
        preview_rect = preview_scaled.get_rect(center=(model_rect.centerx, model_rect.y + 118))
        surf.blit(preview_scaled, preview_rect)

    info_lines = [
        f"World: {current_world_name or 'Unsaved'}",
        f"Seed: {world_seed}",
        f"Slots Used: {used_slots}/{INVENTORY_CAPACITY}",
        f"Player X: {player.x}",
        f"Player Y: {player.y}",
        f"HP: {int(hp)}",
        f"Mana: {int(mana)}",
        f"Stamina: {int(stam)}",
        f"Walls: {len(walls)}",
        f"Doors: {len(doors)}",
        f"Floors: {len(placed_floors)}",
        f"Waypoints: {len(waypoints)}",
        f"Slimes: {enemy_counts.get('slime', 0)}",
        f"Rats: {enemy_counts.get('rat', 0)}",
        f"Bats: {enemy_counts.get('bat', 0)}",
        f"Monsters: {enemy_counts.get('monster', 0)}"
    ]

    info_title = ui_font.render("STATUS", True, (250, 232, 188))
    surf.blit(info_title, (info_x, start_y))

    for i, line in enumerate(info_lines):
        txt = small_font.render(line, True, (238, 220, 188))
        surf.blit(txt, (info_x, start_y + 48 + i * 26))


def draw_crafting_overlay():
    mouse_pos = scale_mouse_pos(pygame.mouse.get_pos())

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    surf.blit(overlay, (0, 0))

    panel = pygame.Rect(WIDTH // 2 - 320, 120, 640, 520)
    draw_knight_panel(
        panel,
        border_color=(198, 162, 102),
        fill_color=(22, 14, 8),
        inner_color=(40, 28, 18),
        border_radius=16,
        draw_rivets=True
    )

    title = title_font.render("CRAFTING", True, (246, 232, 194))
    surf.blit(title, title.get_rect(center=(WIDTH // 2, 165)))

    recipe_buttons = get_crafting_buttons()
    for recipe in CRAFTING_RECIPES:
        ingredients_text = ", ".join(
            f"{get_item_label(item_id)} x{count}"
            for item_id, count in recipe["ingredients"].items()
        )
        output = recipe["output"]
        label = f"{recipe['name']} -> {get_item_label(output['item'])} x{output['count']}  [{ingredients_text}]"
        draw_button(recipe_buttons[recipe["id"]], label, mouse_pos)

    status = font.render(
        crafting_message or "Press R or Esc to close.",
        True,
        (232, 216, 186)
    )
    surf.blit(status, status.get_rect(center=(WIDTH // 2, 608)))


def draw_pause_overlay():
    mouse_pos = scale_mouse_pos(pygame.mouse.get_pos())

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 8, 16, 170))
    surf.blit(overlay, (0, 0))

    if pause_menu_state == "main":
        panel_height = 690
    elif pause_menu_state == "settings":
        panel_height = 720
    elif pause_menu_state == "keybinds":
        panel_height = 720
    elif pause_menu_state == "upgrades":
        panel_height = 706
    elif pause_menu_state == "shop":
        panel_height = 706
    else:
        panel_height = 706

    panel = pygame.Rect(WIDTH // 2 - 510, 24, 1020, panel_height)
    draw_knight_panel(
        panel,
        border_color=(198, 162, 102),
        fill_color=(22, 14, 8),
        inner_color=(40, 28, 18),
        border_radius=18,
        draw_rivets=True
    )

    if pause_menu_state == "main":
        title = title_font.render("PAUSED", True, (248, 232, 194))
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 92)))

        buttons = get_pause_buttons()
        draw_button(buttons["resume"], "Resume", mouse_pos)

        fullscreen_label = "Go Windowed" if fullscreen else "Go Fullscreen"
        draw_button(buttons["toggle_fullscreen"], fullscreen_label, mouse_pos)
        draw_button(buttons["settings"], "Settings", mouse_pos)
        draw_button(buttons["upgrades"], "Upgrades", mouse_pos)
        draw_button(buttons["shop"], "Shop", mouse_pos)
        draw_button(buttons["codes"], "Codes", mouse_pos)
        draw_button(buttons["save_and_quit"], "Save and Quit", mouse_pos)

        pause_key = get_keybind_name("pause")
        hint = font.render(f"Press {pause_key} to resume", True, (232, 216, 186))
        surf.blit(hint, hint.get_rect(center=(WIDTH // 2, 678)))

    elif pause_menu_state == "settings":
        title = title_font.render("SETTINGS", True, (248, 232, 194))
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 90)))

        desc = font.render("Display, audio, gameplay and control settings", True, (232, 216, 186))
        surf.blit(desc, desc.get_rect(center=(WIDTH // 2, 132)))

        current = font.render(
            f"Window: {get_resolution_label()}   FPS Lock: {get_fps_label()}   Volume: {get_volume_label()}",
            True,
            (232, 216, 186)
        )
        surf.blit(current, current.get_rect(center=(WIDTH // 2, 164)))

        buttons = get_settings_buttons()
        fullscreen_label = "Go Windowed" if fullscreen else "Go Fullscreen"
        draw_button(buttons["toggle_fullscreen"], fullscreen_label, mouse_pos)
        draw_button(
            buttons["resolution"],
            f"Resolution: {get_resolution_label()}",
            mouse_pos
        )
        draw_button(
            buttons["fps_lock"],
            f"FPS Lock: {get_fps_label()}",
            mouse_pos
        )
        draw_button(
            buttons["volume"],
            f"Master Volume: {get_volume_label()}",
            mouse_pos
        )
        wall_breaking_label = "Disable Wall Breaking" if not disable_wall_breaking else "Enable Wall Breaking"
        draw_button(buttons["disable_wall_breaking"], wall_breaking_label, mouse_pos)
        draw_button(buttons["keybinds"], "Change Keybinds", mouse_pos)
        draw_button(buttons["back"], "Back", mouse_pos)

    elif pause_menu_state == "keybinds":
        title = title_font.render("KEYBINDS", True, (248, 232, 194))
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 86)))

        if selected_keybind_action is None:
            hint_text = "Click an action to rebind"
        else:
            hint_text = f"Press a key for {keybind_labels[selected_keybind_action]}"
        hint = font.render(hint_text, True, (232, 216, 186))
        surf.blit(hint, hint.get_rect(center=(WIDTH // 2, 126)))

        keybind_buttons = get_keybind_buttons()
        for action in KEYBIND_DISPLAY_ORDER:
            label = keybind_labels[action]
            key_name = pygame.key.name(keybinds[action]).upper()
            draw_button(keybind_buttons[action], f"{label}: {key_name}", mouse_pos)

        draw_button(keybind_buttons["back"], "Back", mouse_pos)

    elif pause_menu_state == "upgrades":
        title = title_font.render("UPGRADES", True, (248, 232, 194))
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 84)))

        points_text = font.render(
            f"Kills Currency: {kill_points}   Total Kills: {total_kills}",
            True,
            (232, 216, 186)
        )
        surf.blit(points_text, points_text.get_rect(center=(WIDTH // 2, 124)))

        price_text = font.render(
            f"Global Price Multiplier: x{upgrade_price_multiplier:.3f}",
            True,
            (232, 216, 186)
        )
        surf.blit(price_text, price_text.get_rect(center=(WIDTH // 2, 154)))

        upgrade_buttons = get_upgrade_buttons()
        for upgrade_id, label in upgrade_labels.items():
            level = upgrade_levels[upgrade_id]
            cost = get_upgrade_cost(upgrade_id)
            draw_button(
                upgrade_buttons[upgrade_id],
                f"{label}  Lv.{level}  Cost: {cost} kills",
                mouse_pos
            )

        if selected_upgrade is None:
            hint_msg = "Click an upgrade to buy"
        else:
            hint_msg = f"Tried buying: {upgrade_labels[selected_upgrade]}"
        hint = font.render(hint_msg, True, (220, 200, 170))
        surf.blit(hint, hint.get_rect(center=(WIDTH // 2, 620)))

        draw_button(upgrade_buttons["back"], "Back", mouse_pos)

    elif pause_menu_state == "shop":
        title = title_font.render("SHOP", True, (248, 232, 194))
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 92)))

        points_text = font.render(
            f"Kills Currency: {kill_points}",
            True,
            (232, 216, 186)
        )
        surf.blit(points_text, points_text.get_rect(center=(WIDTH // 2, 142)))

        buttons = get_shop_buttons()
        draw_button(buttons["buy_steak"], "Buy Steak (8 kills)", mouse_pos)
        draw_button(buttons["back"], "Back", mouse_pos)

        status = font.render(
            shop_message or "Steak heals when used from hotbar.",
            True,
            (232, 216, 186)
        )
        surf.blit(status, status.get_rect(center=(WIDTH // 2, 590)))

    else:
        title = title_font.render("CODES", True, (248, 232, 194))
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 92)))

        desc = font.render("Enter a code and press Enter or Apply.", True, (232, 216, 186))
        surf.blit(desc, desc.get_rect(center=(WIDTH // 2, 132)))

        input_rect = pygame.Rect(WIDTH // 2 - 360, 236, 720, 62)
        draw_knight_panel(
            input_rect,
            border_color=(194, 160, 102),
            fill_color=(24, 16, 10),
            inner_color=(42, 30, 20),
            border_radius=10,
            draw_rivets=False
        )

        shown_code = code_input if code_input else "Type code here"
        shown_color = (252, 240, 208) if code_input else (162, 146, 122)
        code_img = ui_font.render(shown_code, True, shown_color)
        surf.blit(code_img, (input_rect.x + 16, input_rect.y + 16))

        code_list = [
            "CODEGNG  -> 1000000 HP",
            "CODEGNG1 -> 1 HP",
            "CODEGNG2 -> 1000000 Mana/Stamina"
        ]

        for i, line in enumerate(code_list):
            txt = font.render(line, True, (232, 216, 186))
            surf.blit(txt, (WIDTH // 2 - 330, 332 + i * 24))

        message_color = (130, 255, 150) if code_message and "Invalid" not in code_message else (255, 180, 150)
        if not code_message:
            message_color = (232, 216, 186)

        msg = font.render(code_message or "Waiting for code input.", True, message_color)
        surf.blit(msg, msg.get_rect(center=(WIDTH // 2, 488)))

        buttons = get_code_buttons()
        draw_button(buttons["apply"], "Apply", mouse_pos)
        draw_button(buttons["back"], "Back", mouse_pos)


def draw_waypoints():
    for waypoint in waypoints:
        waypoint_data = get_waypoint_screen_data(waypoint)
        color = waypoint["color"]
        selected = waypoint["id"] == selected_waypoint_id
        anchor_x, anchor_y = waypoint_data["anchor"]

        if waypoint_data["offscreen"]:
            pygame.draw.polygon(
                surf,
                color,
                waypoint_data["arrow_points"]
            )
            pygame.draw.polygon(
                surf,
                (20, 20, 20),
                waypoint_data["arrow_points"],
                2
            )
        else:
            pygame.draw.line(
                surf,
                color,
                (anchor_x, anchor_y),
                (anchor_x, anchor_y + 18),
                2
            )
            pygame.draw.circle(
                surf,
                (16, 18, 24),
                (anchor_x, anchor_y),
                10 if selected else 8
            )
            pygame.draw.circle(
                surf,
                color,
                (anchor_x, anchor_y),
                6 if selected else 5
            )

        if selected:
            pygame.draw.circle(
                surf,
                color,
                (anchor_x, anchor_y),
                14 if waypoint_data["offscreen"] else 12,
                2
            )

        label = font.render(waypoint["name"], True, color)

        if waypoint_data["offscreen"]:
            label_rect = label.get_rect(midleft=(anchor_x + 18, anchor_y - 2))
        else:
            label_rect = label.get_rect(midbottom=(anchor_x, anchor_y - 12))

        label_rect.x = max(8, min(WIDTH - label_rect.width - 8, label_rect.x))
        label_rect.y = max(8, min(HEIGHT - label_rect.height - 8, label_rect.y))
        surf.blit(label, label_rect)


def draw_waypoint_editor():
    waypoint = get_waypoint_by_id(selected_waypoint_id)

    if waypoint is None:
        return

    panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT - 136, 500, 92)
    border_tint = (
        clamp_channel(waypoint["color"][0] * 0.8 + 80),
        clamp_channel(waypoint["color"][1] * 0.8 + 70),
        clamp_channel(waypoint["color"][2] * 0.8 + 60)
    )
    draw_knight_panel(
        panel,
        border_color=border_tint,
        fill_color=(20, 14, 8),
        inner_color=(36, 24, 16),
        border_radius=14,
        draw_rivets=False
    )

    title = font.render("WAYPOINT NAME", True, border_tint)
    surf.blit(title, (panel.x + 18, panel.y + 12))

    pygame.draw.rect(
        surf,
        (44, 30, 20),
        (panel.x + 18, panel.y + 36, 318, 34),
        border_radius=8
    )

    shown_name = waypoint_name_input if waypoint_name_input else "Type a name"
    shown_color = (252, 236, 200) if waypoint_name_input else (166, 148, 120)
    text_img = font.render(shown_name, True, shown_color)
    surf.blit(text_img, (panel.x + 28, panel.y + 45))

    instructions = font.render(
        "Enter confirm   Esc cancel   Delete remove",
        True,
        (230, 212, 178)
    )
    surf.blit(instructions, (panel.x + 18, panel.y + 72))


def get_wrapped_book_lines(text, max_chars=44, max_lines=22):
    text_value = str(text).replace("\r", "")
    wrapped_lines = []

    for raw_line in text_value.split("\n"):
        if raw_line == "":
            wrapped_lines.append("")
            continue

        words = raw_line.split(" ")
        current_line = ""

        for word in words:
            if not current_line:
                current_line = word
                continue

            candidate = current_line + " " + word
            if len(candidate) <= max_chars:
                current_line = candidate
            else:
                wrapped_lines.append(current_line)
                current_line = word

        wrapped_lines.append(current_line)

    if len(wrapped_lines) > max_lines:
        wrapped_lines = wrapped_lines[-max_lines:]

    return wrapped_lines


def draw_book_overlay():
    panel = pygame.Rect(170, 58, 940, 604)
    draw_knight_panel(
        panel,
        border_color=(206, 170, 104),
        fill_color=(28, 18, 12),
        inner_color=(44, 30, 20),
        border_radius=18,
        draw_rivets=True
    )

    left_page = pygame.Rect(panel.x + 34, panel.y + 54, 422, 520)
    right_page = pygame.Rect(panel.x + 486, panel.y + 54, 422, 520)

    for page_rect in [left_page, right_page]:
        pygame.draw.rect(surf, (236, 220, 182), page_rect, border_radius=10)
        pygame.draw.rect(surf, (188, 154, 104), page_rect, 2, border_radius=10)

    seam_rect = pygame.Rect(panel.centerx - 8, panel.y + 46, 16, 536)
    pygame.draw.rect(surf, (118, 84, 50), seam_rect, border_radius=7)
    pygame.draw.rect(surf, (84, 60, 36), seam_rect.inflate(-6, 0), border_radius=5)

    title = section_font.render("BOOK & QUILL", True, (246, 228, 188))
    surf.blit(title, title.get_rect(center=(panel.centerx, panel.y + 28)))

    if book_and_quill_img is not None:
        book_icon = pygame.transform.smoothscale(book_and_quill_img, (40, 40))
        surf.blit(book_icon, (panel.x + 16, panel.y + 10))
        surf.blit(book_icon, (panel.right - 56, panel.y + 10))

    wrapped_lines = get_wrapped_book_lines(book_text, max_chars=40, max_lines=22)
    line_height = 22
    left_start_x = left_page.x + 18
    right_start_x = right_page.x + 18
    start_y = left_page.y + 18

    for index, line in enumerate(wrapped_lines):
        page_side = 0 if index < 11 else 1
        page_index = index if page_side == 0 else index - 11
        draw_x = left_start_x if page_side == 0 else right_start_x
        draw_y = start_y + page_index * line_height
        line_img = font.render(line, True, (84, 62, 40))
        surf.blit(line_img, (draw_x, draw_y))

    if book_cursor_blink_on:
        cursor_page_side = 0 if len(wrapped_lines) < 12 else 1
        cursor_line_index = max(0, len(wrapped_lines) - (11 if cursor_page_side == 1 else 0))
        cursor_x = (left_start_x if cursor_page_side == 0 else right_start_x) + 6
        cursor_y = start_y + min(10, cursor_line_index) * line_height
        pygame.draw.line(
            surf,
            (74, 54, 34),
            (cursor_x, cursor_y),
            (cursor_x, cursor_y + 17),
            2
        )

    helper = small_font.render(
        (
            f"{get_keybind_name('pause')} close   "
            f"{get_keybind_name('save_world')} save world   "
            f"{len(book_text)} chars"
        ),
        True,
        (234, 220, 186)
    )
    surf.blit(helper, helper.get_rect(center=(panel.centerx, panel.bottom - 14)))

    if book_status_message and pygame.time.get_ticks() < book_status_until_ms:
        status_img = font.render(book_status_message, True, (246, 236, 206))
        surf.blit(status_img, status_img.get_rect(center=(panel.centerx, panel.y + 46)))


def draw_hotbar():
    mouse_pos = scale_mouse_pos(pygame.mouse.get_pos())

    for index, rect in enumerate(get_hotbar_slot_rects()):
        entry = hotbar_slots[index]
        is_spell = is_spell_entry(entry)
        is_selected = index == active_hotbar_slot
        hovered = rect.collidepoint(mouse_pos)

        fill_color = (52, 36, 24) if is_spell else (58, 40, 24)
        if hovered:
            fill_color = (
                min(255, fill_color[0] + 16),
                min(255, fill_color[1] + 16),
                min(255, fill_color[2] + 16)
            )

        border_color = (198, 156, 96) if is_spell else (182, 142, 88)

        draw_knight_panel(
            rect.inflate(4, 4) if hovered else rect,
            border_color=(250, 214, 132) if is_selected else border_color,
            fill_color=(30, 20, 14),
            inner_color=fill_color,
            border_radius=10,
            draw_rivets=False
        )

        key_label = font.render(get_hotbar_slot_key_label(index), True, (246, 228, 190))
        surf.blit(key_label, (rect.x + 6, rect.y + 4))

        icon = get_icon_for_entry(entry)

        if icon is not None:
            icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 3))
            surf.blit(icon, icon_rect)

        if entry is None:
            empty_label = small_font.render("EMPTY", True, (168, 154, 130))
            surf.blit(empty_label, empty_label.get_rect(center=(rect.centerx, rect.centery + 18)))
        else:
            label = small_font.render(get_compact_item_label(entry), True, (246, 230, 194))
            surf.blit(label, label.get_rect(center=(rect.centerx, rect.bottom - 10)))


# =============================
# TEXTURES
# =============================
def clamp_color_value(value):
    return max(0, min(255, int(value)))


def shift_color(color, amount):
    return tuple(clamp_color_value(channel + amount) for channel in color)


def make_generic_tile(base_color):
    tex = pygame.Surface((64, 64))
    tex.fill(base_color)

    accent = shift_color(base_color, 18)
    shade = shift_color(base_color, -26)

    for y in range(0, 64, 8):
        pygame.draw.line(tex, accent, (0, y), (64, y), 1)

    for x in range(4, 64, 12):
        pygame.draw.line(tex, shade, (x, 0), (x - 4, 64), 1)

    return tex


def make_grass_tile():
    tex = pygame.Surface((64, 64))
    tex.fill((52, 132, 62))

    for x in range(0, 64, 5):
        blade_height = 12 + (x * 7) % 16
        sway = ((x * 5) % 7) - 3
        pygame.draw.line(
            tex,
            (80, 175, 88),
            (x, 63),
            (x + sway, 63 - blade_height),
            2
        )

    for x in range(2, 64, 9):
        pygame.draw.line(
            tex,
            (38, 100, 48),
            (x, 63),
            (x + 1, 63 - 10 - (x % 11)),
            1
        )

    return tex


def make_sand_tile():
    tex = pygame.Surface((64, 64))
    tex.fill((214, 198, 118))

    for y in range(6, 64, 12):
        for x in range(4, 64, 14):
            pygame.draw.arc(
                tex,
                (240, 224, 146),
                (x, y, 16, 8),
                0,
                math.pi,
                1
            )

    for x in range(6, 64, 10):
        pygame.draw.circle(
            tex,
            (188, 171, 98),
            (x, 10 + (x * 3) % 44),
            1
        )

    return tex


def make_bridge_tile():
    tex = pygame.Surface((64, 64))
    tex.fill((92, 58, 30))

    for y in range(4, 64, 12):
        pygame.draw.rect(tex, (128, 82, 44), (0, y, 64, 8))
        pygame.draw.line(tex, (72, 44, 22), (0, y), (64, y), 2)

    for x in range(10, 64, 16):
        pygame.draw.rect(tex, (58, 35, 18), (x, 0, 4, 64))

    return tex


def make_floor_tile():
    tex = pygame.Surface((64, 64))
    tex.fill((106, 106, 116))

    for y in range(0, 64, 16):
        for x in range(0, 64, 16):
            inset = 2 if (x + y) % 32 == 0 else 3
            pygame.draw.rect(
                tex,
                (132, 132, 144),
                (x + inset, y + inset, 12, 12)
            )
            pygame.draw.rect(
                tex,
                (70, 70, 82),
                (x + inset, y + inset, 12, 12),
                1
            )

    return tex


def make_wall_tile():
    tex = pygame.Surface((64, 64))
    tex.fill((110, 70, 50))

    for yy in range(0, 64, 16):
        offset = 0 if (yy // 16) % 2 == 0 else 8

        for xx in range(-offset, 64, 16):
            pygame.draw.rect(
                tex,
                (140, 90, 60),
                (xx + 1, yy + 1, 14, 14)
            )
            pygame.draw.rect(
                tex,
                (70, 40, 30),
                (xx + 1, yy + 1, 14, 14),
                1
            )

    return tex


def make_door_tile():
    tex = pygame.Surface((64, 64))
    tex.fill((35, 35, 35))
    pygame.draw.rect(tex, (60, 60, 60), (6, 6, 52, 52), 3)
    pygame.draw.rect(tex, (80, 80, 80), (14, 10, 36, 44), 2)
    pygame.draw.circle(tex, (140, 140, 140), (44, 32), 3)
    return tex


def make_flower_tile():
    tex = pygame.Surface((64, 64), pygame.SRCALPHA)

    flower_specs = [
        (18, 40, (255, 230, 80)),
        (44, 24, (255, 110, 110)),
        (35, 48, (230, 245, 255)),
        (12, 20, (180, 120, 255))
    ]

    for x, y, petal_color in flower_specs:
        pygame.draw.line(tex, (62, 146, 74), (x, 63), (x, y + 4), 2)

        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            pygame.draw.circle(tex, petal_color, (x + dx, y + dy), 3)

        pygame.draw.circle(tex, (245, 210, 80), (x, y), 2)

    return tex


def make_bush_tile():
    tex = pygame.Surface((64, 64), pygame.SRCALPHA)

    for cx, cy, radius, color in [
        (20, 42, 12, (44, 124, 58)),
        (30, 34, 14, (58, 146, 70)),
        (44, 40, 13, (38, 108, 52)),
        (26, 48, 10, (72, 170, 82))
    ]:
        pygame.draw.circle(tex, color, (cx, cy), radius)

    for x in range(18, 48, 8):
        pygame.draw.line(tex, (66, 52, 34), (x, 63), (x + 1, 48), 2)

    return tex


def make_water_fallback_frames():
    frames = []

    for i in range(6):
        frame_surf = pygame.Surface((64, 64))
        frame_surf.fill((34, 88, 176))

        for y in range(8, 64, 12):
            offset = int(math.sin((i / 6) * math.tau + y * 0.16) * 6)
            pygame.draw.arc(
                frame_surf,
                (124, 188, 255),
                (offset - 10, y, 42, 14),
                0,
                math.pi,
                2
            )
            pygame.draw.arc(
                frame_surf,
                (48, 118, 206),
                (offset + 18, y + 4, 36, 12),
                0,
                math.pi,
                1
            )

        frames.append(frame_surf)

    return frames


def make_lava_fallback_frames():
    frames = []

    for i in range(6):
        frame_surf = pygame.Surface((64, 64))
        frame_surf.fill((168, 56, 12))

        for y in range(8, 64, 10):
            offset = int(math.sin((i / 6) * math.tau + y * 0.17) * 5)
            pygame.draw.arc(
                frame_surf,
                (255, 166, 56),
                (offset - 8, y, 36, 12),
                0,
                math.pi,
                2
            )
            pygame.draw.arc(
                frame_surf,
                (255, 232, 122),
                (offset + 14, y + 3, 22, 8),
                0,
                math.pi,
                1
            )

        frames.append(frame_surf)

    return frames


def make_ocean_frames(source_frames):
    oceanized = []

    for frame in source_frames:
        tinted = frame.copy()
        tint = pygame.Surface((64, 64), pygame.SRCALPHA)
        tint.fill((40, 78, 156, 92))
        tinted.blit(tint, (0, 0))
        oceanized.append(tinted)

    return oceanized


def generate_player_animation(anim_name):
    anim_name = anim_name.lower()
    frames = []
    frame_total = 6

    for i in range(frame_total):
        frame_surf = pygame.Surface((120, 80), pygame.SRCALPHA)
        swing = math.sin(i / frame_total * math.tau)
        bob = int(swing * 2)

        if "roll" in anim_name:
            roll_x = 58 + i * 2
            pygame.draw.ellipse(
                frame_surf,
                (42, 88, 170),
                (roll_x - 22, 26 + bob, 44, 28)
            )
            pygame.draw.ellipse(
                frame_surf,
                (228, 208, 116),
                (roll_x - 10, 30 + bob, 20, 12),
                2
            )
            pygame.draw.line(
                frame_surf,
                (190, 210, 240),
                (roll_x + 16, 34 + bob),
                (roll_x + 32, 28 + bob),
                3
            )

        else:
            torso_x = 58 + (6 if "attack" in anim_name and i >= 2 else 0)
            torso_y = 16 + bob
            leg_swing = int(swing * 7) if "run" in anim_name else 0
            sword_reach = 24 + i * 3 if "attack" in anim_name else 18

            pygame.draw.polygon(
                frame_surf,
                (114, 34, 34),
                [
                    (torso_x + 6, torso_y + 18),
                    (torso_x + 22, torso_y + 28),
                    (torso_x + 14, torso_y + 46),
                    (torso_x + 4, torso_y + 30)
                ]
            )

            pygame.draw.line(
                frame_surf,
                (44, 52, 74),
                (torso_x + 9, torso_y + 36),
                (torso_x + 4 + leg_swing, torso_y + 56),
                5
            )
            pygame.draw.line(
                frame_surf,
                (44, 52, 74),
                (torso_x + 15, torso_y + 36),
                (torso_x + 20 - leg_swing, torso_y + 58),
                5
            )

            pygame.draw.rect(
                frame_surf,
                (42, 88, 170),
                (torso_x, torso_y + 8, 20, 24),
                border_radius=6
            )
            pygame.draw.rect(
                frame_surf,
                (228, 208, 116),
                (torso_x + 6, torso_y + 10, 8, 20),
                2,
                border_radius=4
            )
            pygame.draw.circle(frame_surf, (220, 188, 152), (torso_x + 10, torso_y + 4), 8)

            shield_x = torso_x - 10 + (2 if "run" in anim_name else 0)
            pygame.draw.ellipse(frame_surf, (148, 112, 62), (shield_x, torso_y + 12, 12, 18))

            sword_start = (torso_x + 18, torso_y + 18)
            sword_end = (torso_x + 18 + sword_reach, torso_y + 10 - int(swing * 3))
            pygame.draw.line(frame_surf, (188, 210, 236), sword_start, sword_end, 3)
            pygame.draw.line(frame_surf, (110, 82, 40), sword_start, (torso_x + 14, torso_y + 22), 3)

        frames.append(pygame.transform.scale(frame_surf, (240, 160)))

    return frames


def generate_blob_frames(size=(96, 96), base_color=(66, 214, 108), eye_color=(24, 34, 24)):
    frames = []

    for i in range(8):
        frame_surf = pygame.Surface(size, pygame.SRCALPHA)
        phase = math.sin(i / 8 * math.tau)
        squish = int(phase * 6)
        body_rect = pygame.Rect(
            14,
            22 + max(0, squish),
            size[0] - 28,
            size[1] - 34 - abs(squish)
        )

        shadow_rect = body_rect.move(0, 6)
        pygame.draw.ellipse(frame_surf, shift_color(base_color, -48), shadow_rect)
        pygame.draw.ellipse(frame_surf, base_color, body_rect)
        pygame.draw.ellipse(frame_surf, shift_color(base_color, 26), body_rect.inflate(-22, -30))

        eye_y = body_rect.y + body_rect.height // 2 - 4
        pygame.draw.circle(frame_surf, eye_color, (body_rect.centerx - 10, eye_y), 3)
        pygame.draw.circle(frame_surf, eye_color, (body_rect.centerx + 10, eye_y), 3)
        pygame.draw.arc(
            frame_surf,
            eye_color,
            (body_rect.centerx - 12, eye_y + 2, 24, 12),
            0.2,
            math.pi - 0.2,
            2
        )

        frames.append(frame_surf)

    return frames


def generate_enemy_animation_set(kind, target_size):
    kind = kind.lower()
    animations = {}

    if kind == "rat":
        body_color = (138, 116, 84)
        detail_color = (88, 64, 46)
        eye_color = (232, 88, 72)

        def make_frame(state_name, frame_index):
            frame_surf = pygame.Surface(target_size, pygame.SRCALPHA)
            phase = math.sin(frame_index / 6 * math.tau)
            bob = int(phase * 3)
            leap = 6 if state_name == "attack" else 0
            leg_offset = int(phase * 5) if state_name == "run" else 0
            body = pygame.Rect(20 + leap, 34 + bob, target_size[0] - 40, target_size[1] - 46)

            pygame.draw.line(
                frame_surf,
                detail_color,
                (body.left + 4, body.centery + 2),
                (8, body.centery + 14 - bob),
                4
            )
            pygame.draw.ellipse(frame_surf, body_color, body)
            pygame.draw.ellipse(frame_surf, shift_color(body_color, 24), body.inflate(-18, -22))
            pygame.draw.circle(frame_surf, body_color, (body.right - 10, body.y + 18), 10)

            pygame.draw.polygon(
                frame_surf,
                detail_color,
                [(body.right - 18, body.y + 4), (body.right - 12, body.y - 10), (body.right - 6, body.y + 6)]
            )
            pygame.draw.polygon(
                frame_surf,
                detail_color,
                [(body.right - 6, body.y + 6), (body.right, body.y - 8), (body.right + 4, body.y + 8)]
            )
            pygame.draw.circle(frame_surf, eye_color, (body.right - 8, body.y + 18), 2)

            bite_open = 6 if state_name == "attack" else 2
            pygame.draw.line(
                frame_surf,
                detail_color,
                (body.right + 2, body.y + 24),
                (body.right + 10, body.y + 24 + bite_open),
                2
            )

            for foot_x in [body.left + 12, body.left + 30]:
                pygame.draw.line(
                    frame_surf,
                    detail_color,
                    (foot_x, body.bottom - 4),
                    (foot_x + leg_offset, body.bottom + 8),
                    3
                )

            return frame_surf

    elif kind == "bat":
        body_color = (112, 94, 150)
        detail_color = (58, 44, 86)
        eye_color = (246, 90, 90)

        def make_frame(state_name, frame_index):
            frame_surf = pygame.Surface(target_size, pygame.SRCALPHA)
            phase = math.sin(frame_index / 8 * math.tau)
            wing_lift = 10 + int((phase + 1) * 8)
            dive = 6 if state_name == "attack" else 0
            body_center = (target_size[0] // 2, target_size[1] // 2 + dive)

            left_wing = [
                (body_center[0] - 8, body_center[1] - 6),
                (body_center[0] - 34, body_center[1] - wing_lift),
                (body_center[0] - 46, body_center[1] + 6),
                (body_center[0] - 20, body_center[1] + 14)
            ]
            right_wing = [
                (body_center[0] + 8, body_center[1] - 6),
                (body_center[0] + 34, body_center[1] - wing_lift),
                (body_center[0] + 46, body_center[1] + 6),
                (body_center[0] + 20, body_center[1] + 14)
            ]

            pygame.draw.polygon(frame_surf, detail_color, left_wing)
            pygame.draw.polygon(frame_surf, detail_color, right_wing)
            pygame.draw.ellipse(frame_surf, body_color, (body_center[0] - 12, body_center[1] - 14, 24, 30))
            pygame.draw.circle(frame_surf, body_color, (body_center[0], body_center[1] - 16), 8)
            pygame.draw.polygon(frame_surf, detail_color, [(body_center[0] - 6, body_center[1] - 18), (body_center[0] - 2, body_center[1] - 30), (body_center[0], body_center[1] - 16)])
            pygame.draw.polygon(frame_surf, detail_color, [(body_center[0] + 6, body_center[1] - 18), (body_center[0] + 2, body_center[1] - 30), (body_center[0], body_center[1] - 16)])
            pygame.draw.circle(frame_surf, eye_color, (body_center[0] - 3, body_center[1] - 18), 2)
            pygame.draw.circle(frame_surf, eye_color, (body_center[0] + 3, body_center[1] - 18), 2)

            if state_name == "attack":
                pygame.draw.line(
                    frame_surf,
                    (255, 220, 220),
                    (body_center[0] - 4, body_center[1] - 6),
                    (body_center[0] - 7, body_center[1] + 2),
                    2
                )
                pygame.draw.line(
                    frame_surf,
                    (255, 220, 220),
                    (body_center[0] + 4, body_center[1] - 6),
                    (body_center[0] + 7, body_center[1] + 2),
                    2
                )

            return frame_surf

    else:
        base_color = (70, 180, 120)
        if kind == "monster":
            base_color = (94, 178, 210)

        idle_frames = generate_blob_frames(
            size=target_size,
            base_color=base_color,
            eye_color=(18, 28, 34)
        )
        return {
            "idle": idle_frames,
            "run": idle_frames,
            "attack": idle_frames
        }

    for state_name in ["idle", "run", "attack"]:
        frame_total = 6 if kind == "rat" else 8
        animations[state_name] = [
            make_frame(state_name, i)
            for i in range(frame_total)
        ]

    return animations


def generate_spell_frames(effect_name, size):
    effect_name = effect_name.lower()
    frames = []
    center = size // 2

    for i in range(6):
        frame_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pulse = 0.65 + 0.35 * math.sin(i / 6 * math.tau)

        if "fire-bomb" in effect_name:
            radius = int(size * (0.18 + i * 0.035))
            pygame.draw.circle(frame_surf, (255, 150, 40, 120), (center, center), radius + 8)
            pygame.draw.circle(frame_surf, (255, 210, 90), (center, center), radius)
            pygame.draw.circle(frame_surf, (255, 90, 30), (center, center), max(4, radius - 8))

        elif "lightning" in effect_name:
            points = [
                (center - 6, 6),
                (center + 8, center - 6),
                (center - 2, center + 4),
                (center + 10, size - 10)
            ]
            pygame.draw.lines(frame_surf, (190, 235, 255), False, points, 5)
            pygame.draw.lines(frame_surf, (255, 255, 255), False, points, 2)
            pygame.draw.line(frame_surf, (180, 220, 255), (center + 4, center - 2), (center + 18, center - 14), 2)

        elif "dark-bolt" in effect_name:
            radius = int(size * 0.24 + i * 2)
            pygame.draw.circle(frame_surf, (42, 54, 76, 140), (center, center), radius + 10)
            pygame.draw.circle(frame_surf, (18, 24, 36), (center, center), radius)
            pygame.draw.arc(frame_surf, (110, 138, 188), (center - radius, center - radius, radius * 2, radius * 2), 0.6, 3.5, 3)

        else:
            reach = int(size * (0.18 + 0.03 * i))
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                pygame.draw.line(
                    frame_surf,
                    (220, 245, 255),
                    (center, center),
                    (center + dx * reach, center + dy * reach),
                    2
                )
            pygame.draw.circle(frame_surf, (120, 225, 255), (center, center), max(3, int(6 * pulse)))

        frames.append(frame_surf)

    return frames


def load_tex(name, fallback_color):
    found_path = find_game_file(name)

    if found_path:

        try:
            return pygame.transform.scale(
                pygame.image.load(found_path).convert_alpha(),
                (64, 64)
            )

        except:
            pass

    lowered = name.lower()

    if lowered == "grass.png":
        return make_grass_tile()

    if lowered == "sand.png":
        return make_sand_tile()

    if lowered == "bridge.png":
        return make_bridge_tile()

    if lowered == "floor.png":
        return make_floor_tile()

    if lowered == "snowball.png":
        fallback = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(fallback, (236, 242, 255), (32, 32), 20)
        pygame.draw.circle(fallback, (200, 214, 238), (36, 28), 7)
        pygame.draw.circle(fallback, (196, 204, 222), (26, 39), 5)
        return fallback

    return make_generic_tile(fallback_color)


grass_img = load_tex("grass.png", (50, 180, 50))
sand_img = load_tex("sand.png", (220, 210, 120))

# =============================
# BIOME TILESET
# =============================
tileset_path = find_game_file("GRASS+.png")

# load tileset
tileset_loaded = False

if tileset_path:
    try:
        tileset = pygame.image.load(
            tileset_path
        ).convert_alpha()
        tileset_loaded = True

    except Exception as err:
        print("GRASS+.png FAILED:", err)
        tileset = pygame.Surface((512, 512))
        tileset.fill((0, 255, 0))

else:

    print("GRASS+.png NOT FOUND")

    # fallback
    tileset = pygame.Surface((512, 512))
    tileset.fill((0, 255, 0))

BIOME_TILE = 32


def get_tile_from_sheet(tx, ty):
    tile = pygame.Surface((BIOME_TILE, BIOME_TILE), pygame.SRCALPHA)

    tile.blit(
        tileset,
        (0, 0),
        (tx * BIOME_TILE, ty * BIOME_TILE, BIOME_TILE, BIOME_TILE)
    )

    return pygame.transform.scale(tile, (64, 64))


# biome textures
grass_plain = load_tex("grass.png", (50, 180, 50))

if tileset_loaded:
    flower_tile = get_tile_from_sheet(1, 7)
    bush_tile = get_tile_from_sheet(10, 7)
else:
    flower_tile = make_flower_tile()
    bush_tile = make_bush_tile()

desert_rock_tile = pygame.Surface((64, 64), pygame.SRCALPHA)
pygame.draw.ellipse(desert_rock_tile, (162, 140, 96), (12, 40, 16, 10))
pygame.draw.ellipse(desert_rock_tile, (146, 124, 82), (26, 28, 18, 12))
pygame.draw.ellipse(desert_rock_tile, (132, 112, 72), (42, 42, 10, 8))

# bridge texture auto find
bridge_img = load_tex("bridge.png", (120, 70, 20))
floor_img = load_tex("floor.png", (112, 112, 124))
torch_img = load_tex("torch.png", (64, 64, 255))
sword_img = load_tex("sword.png", (64, 64, 255))
axe_img = load_tex("axe.png", (64, 64, 255))
steak_img = load_tex("steak.png", (64, 64, 255))
water_bucket_img = load_tex("water_bucket.png", (64, 64, 255))
lava_bucket_img = load_tex("lava_bucket.png", (64, 64, 255))
lava_img = load_tex("lava.png", (255, 120, 42))
book_and_quill_img = load_tex("book_and_quill.png", (208, 188, 142))
stone1_img = load_tex("stone1.png", (124, 124, 132))
stone2_img = load_tex("stone2.png", (94, 94, 104))
copper_img = load_tex("copper.png", (172, 110, 76))
snowball_img = load_tex("snowball.png", (236, 242, 255))
pygame.display.set_caption("terarianth")
pygame.display.set_icon(sword_img)

# wall textures (separate wall objects)
wall_texture_files = {
    "wall": "wall.png",
    "wall1": "wall1.png",
    "wall2": "wall2.png",
    "wall3": "wall3.png",
    "wall4": "wall4.png",
    "stone1_block": "stone1.png",
    "stone2_block": "stone2.png",
    "copper_block": "copper.png"
}
wall_textures = {}

for wall_item_id, wall_filename in wall_texture_files.items():
    loaded_wall = None
    wall_path = find_game_file(wall_filename)

    if wall_path:
        try:
            loaded_wall = pygame.image.load(wall_path).convert_alpha()
            loaded_wall = pygame.transform.scale(loaded_wall, (64, 64))
            print("wall texture loaded:", wall_path)
        except Exception as err:
            print(f"{wall_filename} texture failed:", err)

    if loaded_wall is None:
        loaded_wall = pygame.transform.scale(make_wall_tile(), (64, 64))

    wall_textures[wall_item_id] = loaded_wall

wall_img = wall_textures["wall"]

# door texture auto find
door_img = None
door_path = find_game_file("door.png")

if door_path:
    try:
        door_img = pygame.image.load(door_path).convert_alpha()
        door_img = pygame.transform.scale(door_img, (64, 64))
        print("door texture loaded:", door_path)
    except Exception as err:
        print("door texture failed:", err)

if door_img is None:
    door_img = make_door_tile()


def make_open_door_variant(base_img):
    open_img = base_img.copy()
    shade = pygame.Surface((64, 64), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 110))
    open_img.blit(shade, (0, 0))
    pygame.draw.rect(open_img, (10, 10, 10, 180), (24, 0, 16, 64))
    return open_img


door_open_img = make_open_door_variant(door_img)

# =============================
# WATER GIF
# =============================
water_frames = []

gif_path = find_game_file("water.gif")

if gif_path:

    try:

        gif = Image.open(gif_path)

        while True:
            frame_img = gif.convert("RGBA")

            mode = frame_img.mode
            size = frame_img.size
            data = frame_img.tobytes()

            py_img = pygame.image.fromstring(data, size, mode)

            water_frames.append(
                pygame.transform.scale(py_img, (64, 64))
            )

            gif.seek(gif.tell() + 1)

    except EOFError:
        pass

    except Exception as err:
        print("water gif failed:", err)

if not water_frames:
    water_frames = make_water_fallback_frames()
ocean_frames = make_ocean_frames(water_frames)

lava_frames = []
lava_gif_path = find_game_file("lava.gif")

if lava_gif_path:
    try:
        lava_gif = Image.open(lava_gif_path)
        while True:
            frame_img = lava_gif.convert("RGBA")
            mode = frame_img.mode
            size = frame_img.size
            data = frame_img.tobytes()
            py_img = pygame.image.fromstring(data, size, mode)
            lava_frames.append(pygame.transform.scale(py_img, (64, 64)))
            lava_gif.seek(lava_gif.tell() + 1)
    except EOFError:
        pass
    except Exception as err:
        print("lava gif failed:", err)

if not lava_frames:
    if lava_img is not None:
        lava_frames = [pygame.transform.smoothscale(lava_img, (64, 64))]
    else:
        lava_frames = make_lava_fallback_frames()


# =============================
# KNIGHT
# =============================
def load_knight(name):
    path = find_game_file_by_suffix(name)

    if path:
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception:
            sheet = None

        if sheet is not None:
            frames = []

            for i in range(sheet.get_width() // 120):
                fr = pygame.Surface(
                    (120, 80),
                    pygame.SRCALPHA
                )

                fr.blit(
                    sheet,
                    (0, 0),
                    (i * 120, 0, 120, 80)
                )

                frames.append(
                    pygame.transform.scale(fr, (240, 160))
                )

            if frames:
                return frames

    return generate_player_animation(name)


idle_anim = load_knight("_Idle.png")
run_anim = load_knight("_Run.png")
attack_anim = load_knight("_Attack.png")
roll_anim = load_knight("_Roll.png")


def safe(anim, f):
    return anim[int(f) % len(anim)] if anim else pygame.Surface((1, 1), pygame.SRCALPHA)


# =============================
# BLOB
# =============================
def load_blob():
    blob_path = find_game_file("blob.png")

    if blob_path:
        try:
            sheet = pygame.image.load(blob_path).convert_alpha()
        except Exception:
            sheet = None

        if sheet is not None:
            frames = []

            fw = sheet.get_width() // 5
            fh = sheet.get_height() // 3

            if fw > 0 and fh > 0:
                for y in range(3):

                    for x in range(5):
                        fr = pygame.Surface(
                            (fw, fh),
                            pygame.SRCALPHA
                        )

                        fr.blit(
                            sheet,
                            (0, 0),
                            (x * fw, y * fh, fw, fh)
                        )

                        frames.append(
                            pygame.transform.scale(fr, (fw * 2, fh * 2))
                        )

                if frames:
                    return frames

    return generate_blob_frames()


blob_frames = load_blob()


def find_file_in_named_folder(folder_name, filename):
    return find_game_file_in_folder(folder_name, filename)


def load_strip_frames(path, target_size):
    if not path:
        return []

    try:
        sheet = pygame.image.load(path).convert_alpha()
    except Exception:
        return []

    frame_size = sheet.get_height()
    frame_count = max(1, sheet.get_width() // max(1, frame_size))
    frames = []

    for i in range(frame_count):
        frame = pygame.Surface(
            (frame_size, frame_size),
            pygame.SRCALPHA
        )

        frame.blit(
            sheet,
            (0, 0),
            (i * frame_size, 0, frame_size, frame_size)
        )

        frames.append(
            pygame.transform.scale(frame, target_size)
        )

    return frames


def load_enemy_animation_set(folder_name, filenames, target_size=(96, 96)):
    animations = {}
    fallback_animations = generate_enemy_animation_set(folder_name, target_size)

    for state_name, filename in filenames.items():
        path = find_file_in_named_folder(folder_name, filename)

        if path:
            animations[state_name] = load_strip_frames(path, target_size)

        if not animations.get(state_name):
            animations[state_name] = fallback_animations.get(state_name, [])

    if "idle" not in animations and "run" in animations:
        animations["idle"] = animations["run"]

    if "run" not in animations and "idle" in animations:
        animations["run"] = animations["idle"]

    if "attack" not in animations:
        animations["attack"] = animations.get(
            "run",
            animations.get("idle", [])
        )

    return animations


def load_monster_anim():
    slime_path = find_game_file("SlimeA.png")

    if slime_path:
        frames = load_strip_frames(
            slime_path,
            (112, 112)
        )

        if frames:
            return frames

    return generate_enemy_animation_set("monster", (112, 112))["idle"]


monster_frames = load_monster_anim()
rat_animations = load_enemy_animation_set(
    "Rat",
    {
        "idle": "idle.png",
        "run": "run.png",
        "attack": "attack_bite.png"
    }
)
bat_animations = load_enemy_animation_set(
    "Bat",
    {
        "idle": "fly.png",
        "run": "fly.png",
        "attack": "attack.png"
    }
)


# =============================
# TERRAIN
# =============================
def noise(x, y):
    key = (x, y)

    if key not in noise_cache:
        value = (
            x * 374761393
            + y * 668265263
            + world_seed * 982451653
        ) & 0xFFFFFFFF
        value ^= value >> 13
        value = (value * 1274126177) & 0xFFFFFFFF
        value ^= value >> 16
        noise_cache[key] = value / 0xFFFFFFFF

    return noise_cache[key]


def get_tile(x, y):
    if (x, y) in placed_lava:
        return "lava"

    if (x, y) in placed_water:
        return "water"

    if (x, y) in drained_water:
        return "sand"

    if (x, y) in forced_stone1_tiles:
        return "stone1"

    if (x, y) not in world:

        terrain_noise = noise(x // 6, y // 6)
        biome_noise = noise(x // 18 + 2500, y // 18 - 2500)
        stone_noise = noise(x // 14 - 1900, y // 14 + 2100)
        copper_noise = noise(x // 20 + 3800, y // 20 + 740)
        ocean_noise = noise(x // 26 - 840, y // 26 + 1260)

        if terrain_noise < 0.10 and ocean_noise > 0.42:
            tile = "ocean"
        elif terrain_noise < 0.21:
            tile = "water"
        elif copper_noise > 0.79 and terrain_noise > 0.36:
            tile = "copper"
        elif stone_noise > 0.73 and terrain_noise > 0.30:
            tile = "stone2"
        elif stone_noise > 0.58 and terrain_noise > 0.28:
            tile = "stone1"
        elif biome_noise > 0.67 and terrain_noise > 0.33:
            tile = "desert"
        else:
            tile = "grass"

        # Natural lava pockets in stone1 biome (about 1.5%).
        if tile == "stone1" and noise(x * 5 + 811, y * 5 - 293) < 0.015:
            tile = "lava"

        world[(x, y)] = tile

    return world[(x, y)]


def invalidate_terrain_caches(tile_pos, radius=1):
    tile_x, tile_y = tile_pos

    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            shore_cache.pop((tile_x + dx, tile_y + dy), None)


def add_stone1_ring_around_lava(tile_pos):
    tile_x, tile_y = tile_pos

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            neighbor = (tile_x + dx, tile_y + dy)
            if neighbor in placed_lava:
                continue

            forced_stone1_tiles.add(neighbor)
            placed_water.discard(neighbor)
            drained_water.discard(neighbor)
            world.pop(neighbor, None)

    invalidate_terrain_caches(tile_pos, radius=2)


def replace_water_with_sand(tile_pos):
    tile_x, tile_y = tile_pos

    if get_tile(tile_x, tile_y) not in WATERLIKE_TILE_IDS:
        return False

    placed_water.discard(tile_pos)
    placed_floors.discard(tile_pos)
    torch_positions.discard(tile_pos)
    torch_mounts.pop(tile_pos, None)
    drained_water.add(tile_pos)
    invalidate_terrain_caches(tile_pos)
    return True


def replace_lava_with_sand(tile_pos):
    tile_x, tile_y = tile_pos

    if get_tile(tile_x, tile_y) != "lava":
        return False

    placed_lava.discard(tile_pos)
    placed_floors.discard(tile_pos)
    torch_positions.discard(tile_pos)
    torch_mounts.pop(tile_pos, None)
    drained_water.add(tile_pos)
    invalidate_terrain_caches(tile_pos)
    return True


def is_shore(x, y):
    key = (x, y)

    if key in shore_cache:
        return shore_cache[key]

    if get_tile(x, y) in LIQUID_TILE_IDS:
        shore_cache[key] = False
        return False

    for dx in [-1, 0, 1]:

        for dy in [-1, 0, 1]:

            if get_tile(x + dx, y + dy) in LIQUID_TILE_IDS:
                shore_cache[key] = True
                return True

    shore_cache[key] = False
    return False


def get_tile_deco(tile_x, tile_y):
    key = (tile_x, tile_y)

    if key not in deco_cache:
        deco_cache[key] = noise(tile_x * 3, tile_y * 3)

    return deco_cache[key]


def is_water(px, py):
    return get_tile(
        int(px // TILE),
        int(py // TILE)
    ) in WATERLIKE_TILE_IDS


def is_lava(px, py):
    return get_tile(
        int(px // TILE),
        int(py // TILE)
    ) == "lava"


def find_spawn():
    return 0, 0


def get_wall_rect(tile_x, tile_y):
    return pygame.Rect(
        tile_x * TILE + 6,
        tile_y * TILE + 6,
        TILE - 12,
        TILE - 12
    )


def update_open_doors(force=False):
    global open_doors
    global door_update_counter

    if not doors:
        open_doors = set()
        return

    if not force:
        door_update_counter += 1

        if door_update_counter < DOOR_UPDATE_INTERVAL:
            return

    door_update_counter = 0
    new_open_doors = set()
    openers = [(player.centerx, player.centery)]
    open_distance_sq = DOOR_OPEN_DISTANCE * DOOR_OPEN_DISTANCE

    for enemy in enemies:
        if getattr(enemy, "opens_doors", False):
            openers.append((enemy.rect.centerx, enemy.rect.centery))

    for door_x, door_y in doors:
        center_x = door_x * TILE + TILE // 2
        center_y = door_y * TILE + TILE // 2

        for opener_x, opener_y in openers:
            dx = opener_x - center_x
            dy = opener_y - center_y

            if dx * dx + dy * dy <= open_distance_sq:
                new_open_doors.add((door_x, door_y))
                break

    open_doors = new_open_doors


def iter_rect_tiles(rect):
    tile_left = int(rect.left // TILE)
    tile_right = int((rect.right - 1) // TILE)
    tile_top = int(rect.top // TILE)
    tile_bottom = int((rect.bottom - 1) // TILE)

    for tx in range(tile_left, tile_right + 1):
        for ty in range(tile_top, tile_bottom + 1):
            yield tx, ty


def get_player_collision_rect(rect):
    return pygame.Rect(
        rect.x + 10,
        rect.bottom - 18,
        rect.width - 20,
        18
    )


def get_enemy_collision_rect(rect):
    return pygame.Rect(
        rect.x + 10,
        rect.bottom - 22,
        rect.width - 20,
        22
    )


def rect_collides_with_walls(collision_rect):
    for tx, ty in iter_rect_tiles(collision_rect):
        if (tx, ty) in walls and collision_rect.colliderect(get_wall_rect(tx, ty)):
            return True

    return False


def rect_collides_with_doors(collision_rect, block_open_doors):
    for tx, ty in iter_rect_tiles(collision_rect):
        if (tx, ty) not in doors:
            continue

        if not block_open_doors and (tx, ty) in open_doors:
            continue

        if collision_rect.colliderect(get_wall_rect(tx, ty)):
            return True

    return False


def rect_collides_with_water(collision_rect):
    for tx, ty in iter_rect_tiles(collision_rect):
        if get_tile(tx, ty) in WATERLIKE_TILE_IDS:
            return True

    return False


def can_occupy_rect(rect, collision_rect_builder, block_water=False, block_open_doors=False):
    collision_rect = collision_rect_builder(rect)

    if rect_collides_with_walls(collision_rect):
        return False

    if rect_collides_with_doors(collision_rect, block_open_doors):
        return False

    if block_water and rect_collides_with_water(collision_rect):
        return False

    return True


def move_rect_with_collisions(rect, dx, dy, collision_rect_builder, block_water=False, block_open_doors=False):
    moved = False

    if dx != 0:
        trial = rect.copy()
        trial.x += dx

        if can_occupy_rect(trial, collision_rect_builder, block_water, block_open_doors):
            rect.x = trial.x
            moved = True

    if dy != 0:
        trial = rect.copy()
        trial.y += dy

        if can_occupy_rect(trial, collision_rect_builder, block_water, block_open_doors):
            rect.y = trial.y
            moved = True

    return moved


def sync_player_rect():
    player.x = int(round(player_pos_x))
    player.y = int(round(player_pos_y))


def set_player_position(x, y):
    global player_pos_x
    global player_pos_y

    player_pos_x = float(x)
    player_pos_y = float(y)
    sync_player_rect()


def move_player_with_collisions(dx, dy):
    global player_pos_x
    global player_pos_y

    moved = False

    if dx != 0:
        trial = player.copy()
        trial.x = int(round(player_pos_x + dx))
        trial.y = int(round(player_pos_y))

        if can_occupy_rect(trial, get_player_collision_rect):
            player_pos_x += dx
            sync_player_rect()
            moved = True

    if dy != 0:
        trial = player.copy()
        trial.x = int(round(player_pos_x))
        trial.y = int(round(player_pos_y + dy))

        if can_occupy_rect(trial, get_player_collision_rect):
            player_pos_y += dy
            sync_player_rect()
            moved = True

    return moved


def get_player_look_direction():
    mouse_x, mouse_y = scale_mouse_pos(pygame.mouse.get_pos())
    dir_x = mouse_x - WIDTH // 2
    dir_y = mouse_y - HEIGHT // 2

    if dir_x == 0 and dir_y == 0:
        return (-1.0, 0.0) if facing_left else (1.0, 0.0)

    length = math.hypot(dir_x, dir_y)

    if length <= 0:
        return (-1.0, 0.0) if facing_left else (1.0, 0.0)

    return dir_x / length, dir_y / length


def get_map_reference_tiles():
    tiles = set(world.keys())
    tiles.update(walls)
    tiles.update(doors)
    tiles.update(placed_floors)
    tiles.update(placed_water)
    tiles.update(placed_lava)
    tiles.update(drained_water)
    tiles.update(forced_stone1_tiles)
    tiles.update(torch_positions)

    player_tile = (
        int(player.centerx // TILE),
        int(player.centery // TILE)
    )
    tiles.add(player_tile)

    for waypoint in waypoints:
        tiles.add(
            (
                int(waypoint["x"] // TILE),
                int(waypoint["y"] // TILE)
            )
        )

    for dx in range(-16, 17):
        for dy in range(-12, 13):
            tiles.add((player_tile[0] + dx, player_tile[1] + dy))

    return tiles


def get_world_map_layout():
    reference_tiles = list(get_map_reference_tiles())

    min_x = min(tile_x for tile_x, _ in reference_tiles) - 3
    max_x = max(tile_x for tile_x, _ in reference_tiles) + 3
    min_y = min(tile_y for _, tile_y in reference_tiles) - 3
    max_y = max(tile_y for _, tile_y in reference_tiles) + 3

    panel = pygame.Rect(34, 34, WIDTH - 68, HEIGHT - 68)
    inner = pygame.Rect(
        panel.x + 18,
        panel.y + 92,
        panel.width - 36,
        panel.height - 128
    )

    tile_count_x = max(1, max_x - min_x + 1)
    tile_count_y = max(1, max_y - min_y + 1)
    scale = min(
        inner.width / tile_count_x,
        inner.height / tile_count_y
    )

    map_width = tile_count_x * scale
    map_height = tile_count_y * scale
    origin_x = inner.x + (inner.width - map_width) / 2
    origin_y = inner.y + (inner.height - map_height) / 2

    return {
        "panel": panel,
        "inner": inner,
        "origin_x": origin_x,
        "origin_y": origin_y,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "scale": scale,
        "tiles": reference_tiles
    }


def get_world_map_tile_rect(tile_x, tile_y, layout):
    scale = layout["scale"]
    left = int(round(layout["origin_x"] + (tile_x - layout["min_x"]) * scale))
    top = int(round(layout["origin_y"] + (tile_y - layout["min_y"]) * scale))
    right = int(round(layout["origin_x"] + (tile_x - layout["min_x"] + 1) * scale))
    bottom = int(round(layout["origin_y"] + (tile_y - layout["min_y"] + 1) * scale))

    if right <= left:
        right = left + 1

    if bottom <= top:
        bottom = top + 1

    return pygame.Rect(left, top, right - left, bottom - top)


def inset_map_rect(rect, inset):
    inset_x = min(inset, max(0, (rect.width - 1) // 2))
    inset_y = min(inset, max(0, (rect.height - 1) // 2))
    return pygame.Rect(
        rect.x + inset_x,
        rect.y + inset_y,
        max(1, rect.width - inset_x * 2),
        max(1, rect.height - inset_y * 2)
    )


def world_point_to_map(world_x, world_y, layout):
    map_x = layout["origin_x"] + ((world_x / TILE) - layout["min_x"]) * layout["scale"]
    map_y = layout["origin_y"] + ((world_y / TILE) - layout["min_y"]) * layout["scale"]
    return int(round(map_x)), int(round(map_y))


def get_world_map_tile_color(tile_x, tile_y):
    tile = get_tile(tile_x, tile_y)

    if tile == "lava":
        return (206, 88, 28)

    if tile == "ocean":
        return (30, 68, 142)

    if tile == "water":
        return (46, 100, 196)

    if tile == "copper":
        return (176, 114, 72)

    if tile == "stone2":
        return (88, 94, 112)

    if tile == "stone1":
        return (118, 124, 138)

    if tile in ["desert", "sand"]:
        return (214, 198, 118)

    return (58, 132, 72)


def draw_map_waypoint_marker(waypoint, layout):
    center_x, center_y = world_point_to_map(
        waypoint["x"],
        waypoint["y"],
        layout
    )
    color = waypoint["color"]
    selected = waypoint["id"] == selected_waypoint_id
    size = max(7, min(16, int(round(layout["scale"] * 2.2))))

    arrow_points = [
        (center_x, center_y - size),
        (center_x + size, center_y + size // 2),
        (center_x, center_y + max(2, size // 4)),
        (center_x - size, center_y + size // 2)
    ]

    pygame.draw.polygon(surf, color, arrow_points)
    pygame.draw.polygon(surf, (18, 18, 18), arrow_points, 2)

    if selected:
        pygame.draw.circle(
            surf,
            color,
            (center_x, center_y),
            size + 6,
            2
        )

    label = font.render(waypoint["name"], True, color)
    label_rect = label.get_rect(midleft=(center_x + size + 8, center_y - 2))
    label_rect.x = min(layout["panel"].right - label_rect.width - 8, label_rect.x)
    label_rect.y = max(layout["panel"].y + 8, min(layout["panel"].bottom - label_rect.height - 8, label_rect.y))
    surf.blit(label, label_rect)


def draw_world_map_overlay():
    layout = get_world_map_layout()
    panel = layout["panel"]

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((4, 8, 14, 210))
    surf.blit(overlay, (0, 0))

    pygame.draw.rect(surf, (18, 24, 34), panel, border_radius=14)
    pygame.draw.rect(surf, (118, 176, 230), panel, 3, border_radius=14)

    title = title_font.render("WORLD MAP", True, (235, 245, 255))
    surf.blit(title, (panel.x + 18, panel.y + 14))

    subtitle = font.render(
        "M or Esc close   Waypoints stay visible here and in-world",
        True,
        (205, 220, 238)
    )
    surf.blit(subtitle, (panel.x + 22, panel.y + 58))

    for tile_x, tile_y in layout["tiles"]:
        tile_rect = get_world_map_tile_rect(tile_x, tile_y, layout)
        pygame.draw.rect(
            surf,
            get_world_map_tile_color(tile_x, tile_y),
            tile_rect
        )

    for tile_x, tile_y in placed_floors:
        pygame.draw.rect(
            surf,
            (118, 122, 136),
            inset_map_rect(
                get_world_map_tile_rect(tile_x, tile_y, layout),
                1
            )
        )

    for tile_x, tile_y in walls:
        pygame.draw.rect(
            surf,
            (112, 76, 48),
            get_world_map_tile_rect(tile_x, tile_y, layout)
        )

    for tile_x, tile_y in doors:
        pygame.draw.rect(
            surf,
            (174, 132, 72),
            inset_map_rect(
                get_world_map_tile_rect(tile_x, tile_y, layout),
                1
            )
        )

    for tile_x, tile_y in torch_positions:
        torch_rect = get_world_map_tile_rect(tile_x, tile_y, layout)
        pygame.draw.circle(
            surf,
            (255, 190, 72),
            torch_rect.center,
            max(2, min(5, torch_rect.width // 2))
        )

    for waypoint in waypoints:
        draw_map_waypoint_marker(waypoint, layout)

    player_x, player_y = world_point_to_map(
        player.centerx,
        player.centery,
        layout
    )
    look_x, look_y = get_player_look_direction()
    visor_length = max(18, min(56, layout["scale"] * 6.0))
    visor_width = max(7, visor_length * 0.42)
    normal_x = -look_y
    normal_y = look_x
    tip = (
        player_x + int(round(look_x * visor_length)),
        player_y + int(round(look_y * visor_length))
    )
    left_point = (
        player_x + int(round(look_x * visor_length * 0.34 + normal_x * visor_width)),
        player_y + int(round(look_y * visor_length * 0.34 + normal_y * visor_width))
    )
    right_point = (
        player_x + int(round(look_x * visor_length * 0.34 - normal_x * visor_width)),
        player_y + int(round(look_y * visor_length * 0.34 - normal_y * visor_width))
    )

    visor_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(
        visor_overlay,
        (230, 240, 255, 72),
        [(player_x, player_y), left_point, tip, right_point]
    )
    surf.blit(visor_overlay, (0, 0))

    pygame.draw.line(surf, (245, 248, 255), (player_x, player_y), tip, 2)
    pygame.draw.circle(surf, (24, 24, 28), (player_x, player_y), 7)
    pygame.draw.circle(surf, (255, 88, 88), (player_x, player_y), 4)


def can_spawn_enemy_at(tile_pos):
    return (
        get_tile(tile_pos[0], tile_pos[1]) not in LIQUID_TILE_IDS
        and tile_pos not in walls
        and tile_pos not in doors
    )


def is_enemy_path_tile_open(tile_pos, block_open_doors):
    if get_tile(tile_pos[0], tile_pos[1]) in LIQUID_TILE_IDS:
        return False

    if tile_pos in walls:
        return False

    if tile_pos in doors:
        if block_open_doors:
            return False

        if tile_pos not in open_doors:
            return False

    return True


def get_path_neighbors(tile_pos, goal_tile):
    x, y = tile_pos
    goal_x, goal_y = goal_tile

    step_x = 1 if goal_x > x else -1 if goal_x < x else 0
    step_y = 1 if goal_y > y else -1 if goal_y < y else 0

    neighbor_dirs = []

    for direction in [
        (step_x, 0),
        (0, step_y),
        (-step_x, 0),
        (0, -step_y),
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]:
        if direction == (0, 0) or direction in neighbor_dirs:
            continue

        neighbor_dirs.append(direction)

    return [
        (x + dx, y + dy)
        for dx, dy in neighbor_dirs
    ]


def find_enemy_path(start_tile, goal_tile, max_search_distance, block_open_doors):
    if start_tile == goal_tile:
        return []

    if max(
        abs(goal_tile[0] - start_tile[0]),
        abs(goal_tile[1] - start_tile[1])
    ) > max_search_distance:
        return []

    queue = deque([start_tile])
    parents = {start_tile: None}

    while queue:
        current_tile = queue.popleft()

        if current_tile == goal_tile:
            break

        for neighbor in get_path_neighbors(current_tile, goal_tile):
            if neighbor in parents:
                continue

            if max(
                abs(neighbor[0] - start_tile[0]),
                abs(neighbor[1] - start_tile[1])
            ) > max_search_distance:
                continue

            if neighbor != goal_tile and not is_enemy_path_tile_open(
                neighbor,
                block_open_doors
            ):
                continue

            parents[neighbor] = current_tile
            queue.append(neighbor)

    if goal_tile not in parents:
        return []

    path = []
    current_tile = goal_tile

    while current_tile and current_tile != start_tile:
        path.append(current_tile)
        current_tile = parents[current_tile]

    path.reverse()
    return path


def serialize_enemy(enemy):
    return {
        "x": enemy.rect.x,
        "y": enemy.rect.y,
        "hp": enemy.hp,
        "type": enemy.enemy_type
    }


def serialize_projectile(projectile):
    return {
        "x": projectile.x,
        "y": projectile.y,
        "vx": projectile.vx,
        "vy": projectile.vy,
        "frame": projectile.frame,
        "damage": projectile.damage,
        "life": projectile.life
    }


def serialize_particle(particle):
    return {
        "x": particle.x,
        "y": particle.y,
        "vx": particle.vx,
        "vy": particle.vy,
        "life": particle.life,
        "color": list(particle.color)
    }


def serialize_damage_text(damage_text):
    return {
        "x": damage_text.x,
        "y": damage_text.y,
        "val": damage_text.val,
        "life": damage_text.life
    }


def create_enemy_from_data(entry, default_type="slime"):
    enemy_type = default_type

    if isinstance(entry, dict):
        enemy_type = entry.get("type", default_type)
        x = entry["x"]
        y = entry["y"]
        hp_value = entry.get("hp")
    else:
        x = entry[0]
        y = entry[1]
        hp_value = entry[2] if len(entry) > 2 else None

    enemy_classes = {
        "monster": MushroomEnemy,
        "rat": RatEnemy,
        "bat": BatEnemy
    }
    enemy = enemy_classes.get(enemy_type, Enemy)(x, y)

    if hp_value is not None:
        enemy.hp = hp_value

    return enemy


def spawn_enemy_near_player(enemy_cls, chance):
    if not mobs_spawn_enabled:
        return

    if len(enemies) >= MAX_ENEMIES:
        return

    if random.random() >= chance:
        return

    sx = player.centerx + random.randint(-400, 400)
    sy = player.centery + random.randint(-400, 400)

    spawn_tile = (
        int(sx // TILE),
        int(sy // TILE)
    )

    if can_spawn_enemy_at(spawn_tile):
        enemies.append(enemy_cls(sx, sy))



# =============================
# SAVE / LOAD
# =============================
def get_worlds():

    worlds = []

    for file in os.listdir(SAVE_DIR):

        if file.endswith(".json"):
            worlds.append(file[:-5])

    return sorted(worlds)


def get_world_metadata(world_name):
    default_metadata = {
        "icon": WORLD_ICON_CHOICES[0],
        "mode": "easy"
    }
    path = os.path.join(SAVE_DIR, world_name + ".json")

    if not os.path.exists(path):
        return default_metadata

    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return default_metadata

    cached_entry = world_metadata_cache.get(world_name)

    if cached_entry and cached_entry.get("mtime") == mtime:
        return cached_entry["metadata"]

    metadata = dict(default_metadata)

    try:
        with open(path, "r") as file:
            payload = json.load(file)
            metadata["icon"] = normalize_world_icon(payload.get("world_icon", metadata["icon"]))
            metadata["mode"] = normalize_game_mode(payload.get("game_mode", metadata["mode"]))
    except Exception:
        pass

    world_metadata_cache[world_name] = {
        "mtime": mtime,
        "metadata": metadata
    }
    return metadata


def get_world_save_path(world_name):
    normalized_name = str(world_name).strip()
    if not normalized_name:
        return ""

    return os.path.join(SAVE_DIR, normalized_name + ".json")


def remove_world_save_file(world_name):
    normalized_name = str(world_name).strip()
    save_path = get_world_save_path(normalized_name)

    if not normalized_name or not save_path:
        return False, "No world selected."

    if not os.path.exists(save_path):
        return False, "World file not found."

    try:
        os.remove(save_path)
        world_metadata_cache.pop(normalized_name, None)
        return True, f"Deleted world: {normalized_name}"
    except Exception as err:
        return False, f"Delete failed: {err}"


def delete_world(name):
    global selected_load_world_name
    global load_world_message

    world_name = str(name).strip()
    if not world_name:
        load_world_message = "Select a world first."
        return False

    deleted, status_message = remove_world_save_file(world_name)
    load_world_message = status_message

    if deleted:
        if selected_load_world_name == world_name:
            selected_load_world_name = None
        log_player_action("World deleted", world_name)

    return deleted


def normalize_world_name(name=None):
    candidate = str(name).strip() if name is not None else ""

    if candidate:
        return candidate

    if current_world_name.strip():
        return current_world_name.strip()

    return str(world_seed)


def serialize_inventory():
    saved_inventory = []

    for item in inventory:
        if item is None or isinstance(item, (str, int, float, bool, list, dict)):
            saved_inventory.append(item)
        else:
            saved_inventory.append(str(item))

    return saved_inventory


def load_inventory(data):
    global inventory

    loaded_inventory = data.get("inventory", build_default_inventory())

    if not isinstance(loaded_inventory, list):
        loaded_inventory = build_default_inventory()

    inventory = loaded_inventory[:INVENTORY_CAPACITY]

    while len(inventory) < INVENTORY_CAPACITY:
        inventory.append(None)

    ensure_required_inventory_items()


def save_world(name=None, autosave=False):

    global current_world_name
    global last_autosave_ms

    world_name = normalize_world_name(name)
    current_world_name = world_name

    blob_data = [
        serialize_enemy(en)
        for en in enemies
        if en.enemy_type != "monster"
    ]
    monster_data = [
        serialize_enemy(en)
        for en in enemies
        if en.enemy_type == "monster"
    ]
    projectile_data = [
        serialize_projectile(p)
        for p in projectiles
    ]
    particle_data = [
        serialize_particle(particle)
        for particle in particles
    ]
    damage_text_data = [
        serialize_damage_text(damage_text)
        for damage_text in damage_texts
    ]

    data = {

        "world_name": world_name,
        "seed": world_seed,
        "world_icon": current_world_icon,
        "player_image_path": current_player_image_path,
        "game_mode": game_mode,
        "game_time": game_time,
        "disable_wall_breaking": disable_wall_breaking,
        "book_text": book_text,
        "kill_points": kill_points,
        "total_kills": total_kills,
        "upgrade_price_multiplier": upgrade_price_multiplier,
        "upgrade_levels": dict(upgrade_levels),

        "player": {
            "x": player.x,
            "y": player.y,
            "hp": hp,
            "mana": mana,
            "stamina": stam,
            "max_hp": hp_limit,
            "max_mana": mana_limit,
            "max_stamina": stam_limit
        },

        "inventory": serialize_inventory(),
        "hotbar": serialize_hotbar(),
        "active_hotbar_slot": active_hotbar_slot,
        "waypoints": serialize_waypoints(),

        "walls": [
            {
                "x": wx,
                "y": wy,
                "type": wall_types.get((wx, wy), "wall")
            }
            for wx, wy in sorted(walls)
        ],

        "doors": [
            {
                "x": dx,
                "y": dy
            }
            for dx, dy in sorted(doors)
        ],
        "floors": [
            {
                "x": fx,
                "y": fy
            }
            for fx, fy in sorted(placed_floors)
        ],
        "water_blocks": [
            {
                "x": wx,
                "y": wy
            }
            for wx, wy in sorted(placed_water)
        ],
        "lava_blocks": [
            {
                "x": lx,
                "y": ly
            }
            for lx, ly in sorted(placed_lava)
        ],
        "drained_water": [
            {
                "x": wx,
                "y": wy
            }
            for wx, wy in sorted(drained_water)
        ],
        "stone1_overrides": [
            {
                "x": sx,
                "y": sy
            }
            for sx, sy in sorted(forced_stone1_tiles)
        ],
        "torches": [
            {
                "x": tx,
                "y": ty,
                "mount": torch_mounts.get((tx, ty), "ground")
            }
            for tx, ty in sorted(torch_positions)
        ],

        "blobs": blob_data,
        "monsters": monster_data,
        "projectiles": projectile_data,
        "particles": particle_data,
        "damage_texts": damage_text_data
    }

    save_path = os.path.join(
        SAVE_DIR,
        world_name + ".json"
    )

    with open(save_path, "w") as f:
        json.dump(data, f, indent=4)

    try:
        world_metadata_cache[world_name] = {
            "mtime": os.path.getmtime(save_path),
            "metadata": {
                "icon": normalize_world_icon(current_world_icon),
                "mode": normalize_game_mode(game_mode)
            }
        }
    except OSError:
        pass

    last_autosave_ms = pygame.time.get_ticks()

    if autosave:
        print("WORLD AUTOSAVED:", save_path)
    else:
        print("WORLD SAVED:", save_path)


def load_world(name):

    global world_seed
    global current_world_name
    global enemies
    global hp
    global mana
    global stam
    global hp_limit
    global mana_limit
    global stam_limit
    global game_state
    global seed_input
    global last_autosave_ms
    global inventory_selected_index
    global game_time
    global disable_wall_breaking
    global kill_points
    global total_kills
    global upgrade_price_multiplier
    global map_open
    global projectiles
    global particles
    global damage_texts
    global current_world_icon
    global selected_world_icon_index
    global last_movement_log_tile
    global selected_player_image_path
    global game_over_close_at_ms
    global camera_shake_strength
    global camera_shake_x
    global camera_shake_y
    global impact_flash_alpha
    global book_text
    global player_lava_damage_timer

    path = os.path.join(
        SAVE_DIR,
        name + ".json"
    )

    if not os.path.exists(path):
        print("SAVE NOT FOUND")
        return

    with open(path, "r") as f:
        data = json.load(f)

    current_world_name = str(data.get("world_name", name)).strip() or name
    seed_input = current_world_name
    world_seed = data["seed"]
    current_world_icon = normalize_world_icon(data.get("world_icon", WORLD_ICON_CHOICES[0]))
    set_selected_world_icon(current_world_icon)
    set_game_mode(data.get("game_mode", "easy"))
    book_text = str(data.get("book_text", ""))
    loaded_image_path = data.get("player_image_path", "")
    if not loaded_image_path and isinstance(data.get("player"), dict):
        loaded_image_path = data["player"].get("image_path", "")
    selected_player_image_path = normalize_player_image_path(loaded_image_path)
    if not apply_player_image(selected_player_image_path):
        selected_player_image_path = ""
        log_player_action("World load image fallback", "default player animation")

    random.seed(world_seed)

    clear_world_runtime_cache()
    wall_break_timers.clear()

    # PLAYER
    if isinstance(data["player"], list):

        set_player_position(
            data["player"][0],
            data["player"][1]
        )

        reset_player_limits()
        hp = hp_limit
        mana = mana_limit
        stam = stam_limit

    else:

        player_data = data["player"]

        set_player_position(
            player_data["x"],
            player_data["y"]
        )

        hp_limit = max(
            MAX_HP,
            player_data.get("max_hp", player_data.get("hp", MAX_HP))
        )
        mana_limit = max(
            MAX_MANA,
            player_data.get("max_mana", player_data.get("mana", MAX_MANA))
        )
        stam_limit = max(
            MAX_STAM,
            player_data.get("max_stamina", player_data.get("stamina", player_data.get("stam", MAX_STAM)))
        )

        hp = player_data.get("hp", MAX_HP)
        mana = player_data.get("mana", MAX_MANA)
        stam = player_data.get("stamina", player_data.get("stam", MAX_STAM))

    game_time = data.get("game_time", 0)
    disable_wall_breaking = data.get("disable_wall_breaking", False)
    kill_points = int(data.get("kill_points", 0))
    total_kills = int(data.get("total_kills", 0))
    upgrade_price_multiplier = float(data.get("upgrade_price_multiplier", 1.0))
    loaded_upgrades = data.get("upgrade_levels", {})
    if isinstance(loaded_upgrades, dict):
        for key in upgrade_levels:
            upgrade_levels[key] = int(loaded_upgrades.get(key, 0))
    apply_mode_player_stats(refill_stats=False)

    load_inventory(data)
    load_hotbar(data)
    load_waypoints(data)
    inventory_selected_index = None

    # WALLS
    walls.clear()
    wall_types.clear()

    if "walls" in data:

        for w in data["walls"]:

            if isinstance(w, dict):
                tile_pos = (w["x"], w["y"])
                walls.add(tile_pos)
                saved_type = str(w.get("type", "wall")).lower()
                wall_types[tile_pos] = saved_type if saved_type in WALL_ITEM_IDS else "wall"

            else:
                tile_pos = (w[0], w[1])
                walls.add(tile_pos)
                wall_types[tile_pos] = "wall"

    # DOORS
    doors.clear()
    open_doors.clear()

    if "doors" in data:

        for d in data["doors"]:

            if isinstance(d, dict):

                doors.add(
                    (d["x"], d["y"])
                )

            else:

                doors.add(
                    (d[0], d[1])
                )

    placed_floors.clear()
    placed_water.clear()
    placed_lava.clear()
    drained_water.clear()
    forced_stone1_tiles.clear()

    if "floors" in data:

        for floor_entry in data["floors"]:

            if isinstance(floor_entry, dict):
                placed_floors.add(
                    (floor_entry["x"], floor_entry["y"])
                )

            else:
                placed_floors.add(
                    (floor_entry[0], floor_entry[1])
                )

    if "water_blocks" in data:
        for water_entry in data["water_blocks"]:
            if isinstance(water_entry, dict):
                placed_water.add(
                    (water_entry["x"], water_entry["y"])
                )
            else:
                placed_water.add(
                    (water_entry[0], water_entry[1])
                )

    if "lava_blocks" in data:
        for lava_entry in data["lava_blocks"]:
            if isinstance(lava_entry, dict):
                placed_lava.add(
                    (lava_entry["x"], lava_entry["y"])
                )
            else:
                placed_lava.add(
                    (lava_entry[0], lava_entry[1])
                )

    if "drained_water" in data:
        for sand_entry in data["drained_water"]:
            if isinstance(sand_entry, dict):
                drained_water.add(
                    (sand_entry["x"], sand_entry["y"])
                )
            else:
                drained_water.add(
                    (sand_entry[0], sand_entry[1])
                )

    if "stone1_overrides" in data:
        for stone_entry in data["stone1_overrides"]:
            if isinstance(stone_entry, dict):
                forced_stone1_tiles.add(
                    (stone_entry["x"], stone_entry["y"])
                )
            else:
                forced_stone1_tiles.add(
                    (stone_entry[0], stone_entry[1])
                )

    torch_positions.clear()
    torch_mounts.clear()

    if "torches" in data:

        for torch_entry in data["torches"]:

            if isinstance(torch_entry, dict):
                tile_pos = (torch_entry["x"], torch_entry["y"])
                torch_positions.add(tile_pos)
                mount_value = str(torch_entry.get("mount", "ground")).lower()
                torch_mounts[tile_pos] = "wall" if mount_value == "wall" else "ground"

            else:
                tile_pos = (torch_entry[0], torch_entry[1])
                torch_positions.add(tile_pos)
                torch_mounts[tile_pos] = "ground"

    # BLOBS / ENEMIES
    enemies = []

    blob_entries = data.get("blobs", data.get("enemies", []))

    if blob_entries:

        for e in blob_entries:
            enemies.append(
                create_enemy_from_data(e, default_type="slime")
            )

    monster_entries = data.get("monsters", [])

    if monster_entries:

        for e in monster_entries:
            enemies.append(
                create_enemy_from_data(e, default_type="monster")
            )

    if not mobs_spawn_enabled:
        enemies = []

    projectiles = []
    for proj_entry in data.get("projectiles", []):
        if not isinstance(proj_entry, dict):
            continue
        proj = Projectile(
            (proj_entry.get("x", player.centerx), proj_entry.get("y", player.centery)),
            (
                proj_entry.get("x", player.centerx) + proj_entry.get("vx", 0),
                proj_entry.get("y", player.centery) + proj_entry.get("vy", 0)
            ),
            [],
            proj_entry.get("damage", 0),
            1
        )
        proj.x = float(proj_entry.get("x", proj.x))
        proj.y = float(proj_entry.get("y", proj.y))
        proj.vx = float(proj_entry.get("vx", proj.vx))
        proj.vy = float(proj_entry.get("vy", proj.vy))
        proj.frame = float(proj_entry.get("frame", 0))
        proj.life = int(proj_entry.get("life", 1))
        if proj.life > 0:
            projectiles.append(proj)

    particles = []
    for particle_entry in data.get("particles", []):
        if not isinstance(particle_entry, dict):
            continue
        color = particle_entry.get("color", [255, 255, 255])
        if not isinstance(color, list) or len(color) != 3:
            color = [255, 255, 255]
        particle = Particle(
            particle_entry.get("x", player.centerx),
            particle_entry.get("y", player.centery),
            (int(color[0]), int(color[1]), int(color[2]))
        )
        particle.vx = float(particle_entry.get("vx", particle.vx))
        particle.vy = float(particle_entry.get("vy", particle.vy))
        particle.life = int(particle_entry.get("life", particle.life))
        if particle.life > 0:
            particles.append(particle)

    damage_texts = []
    for damage_text_entry in data.get("damage_texts", []):
        if not isinstance(damage_text_entry, dict):
            continue
        damage_text = DamageText(
            damage_text_entry.get("x", player.centerx),
            damage_text_entry.get("y", player.centery),
            damage_text_entry.get("val", 0)
        )
        damage_text.life = int(damage_text_entry.get("life", damage_text.life))
        if damage_text.life > 0:
            damage_texts.append(damage_text)

    if len(particles) > MAX_PARTICLES:
        particles = particles[-MAX_PARTICLES:]
    if len(damage_texts) > MAX_DAMAGE_TEXTS:
        damage_texts = damage_texts[-MAX_DAMAGE_TEXTS:]

    update_open_doors(force=True)
    last_autosave_ms = pygame.time.get_ticks()
    map_open = False
    game_over_close_at_ms = 0
    camera_shake_strength = 0.0
    camera_shake_x = 0
    camera_shake_y = 0
    impact_flash_alpha = 0.0
    player_lava_damage_timer = 0.0
    slash_effects.clear()
    game_state = "game"
    last_movement_log_tile = None
    log_player_action(
        "World loaded",
        f"{current_world_name} | mode={GAME_MODE_LABELS[game_mode]} | icon={current_world_icon}"
    )


def close_runtime_overlays():
    global inventory_open
    global crafting_open
    global crafting_message
    global map_open
    global show_controls
    global pause_menu_state
    global selected_keybind_action
    global selected_upgrade
    global code_input
    global code_message
    global shop_message
    global inventory_selected_index
    global waypoint_editing
    global waypoint_name_input
    global book_open
    global book_status_message
    global book_status_until_ms

    inventory_open = False
    crafting_open = False
    crafting_message = ""
    map_open = False
    show_controls = False
    pause_menu_state = "main"
    selected_keybind_action = None
    selected_upgrade = None
    code_input = ""
    code_message = ""
    shop_message = ""
    inventory_selected_index = None
    waypoint_editing = False
    waypoint_name_input = ""
    book_open = False
    book_status_message = ""
    book_status_until_ms = 0


def start_new_world_from_seed(seed_text, mode_value=None, world_icon_id=None, player_image_path=None):
    global world_seed
    global current_world_name
    global seed_input
    global inventory
    global hotbar_slots
    global active_hotbar_slot
    global inventory_selected_index
    global hp
    global mana
    global stam
    global kill_points
    global total_kills
    global upgrade_price_multiplier
    global selected_upgrade
    global game_state
    global game_time
    global state
    global frame
    global locked
    global step_counter
    global facing_left
    global current_world_icon
    global last_movement_log_tile
    global selected_player_image_path
    global game_over_close_at_ms
    global camera_shake_strength
    global camera_shake_x
    global camera_shake_y
    global impact_flash_alpha
    global player_lava_damage_timer
    global book_text

    world_seed = sum(ord(c) for c in seed_text)
    current_world_name = str(seed_text).strip() or str(world_seed)
    seed_input = current_world_name
    current_world_icon = normalize_world_icon(
        world_icon_id if world_icon_id is not None else get_selected_world_icon()
    )
    set_selected_world_icon(current_world_icon)
    set_game_mode(mode_value if mode_value is not None else selected_game_mode)
    selected_player_image_path = normalize_player_image_path(
        player_image_path if player_image_path is not None else selected_player_image_path
    )
    if not apply_player_image(selected_player_image_path):
        selected_player_image_path = ""
        log_player_action("Player image fallback", "default player animation")

    random.seed(world_seed)

    clear_world_runtime_cache()
    walls.clear()
    wall_types.clear()
    doors.clear()
    open_doors.clear()
    placed_floors.clear()
    placed_water.clear()
    placed_lava.clear()
    drained_water.clear()
    forced_stone1_tiles.clear()
    torch_positions.clear()
    torch_mounts.clear()
    wall_break_timers.clear()
    waypoints.clear()
    reset_waypoint_state()
    enemies.clear()
    projectiles.clear()
    particles.clear()
    damage_texts.clear()
    kill_points = 0
    total_kills = 0
    upgrade_price_multiplier = 1.0
    book_text = ""

    for upg_key in upgrade_levels:
        upgrade_levels[upg_key] = 0

    selected_upgrade = None
    inventory = build_default_inventory()
    hotbar_slots = build_default_hotbar()
    active_hotbar_slot = DEFAULT_ACTIVE_HOTBAR_SLOT
    inventory_selected_index = None
    game_time = 0
    state = "idle"
    frame = 0
    locked = False
    step_counter = 0
    facing_left = False
    last_movement_log_tile = None
    close_runtime_overlays()
    reset_player_limits()

    player.center = find_spawn()
    set_player_position(player.x, player.y)
    apply_mode_player_stats(refill_stats=True)

    save_world(current_world_name)
    game_over_close_at_ms = 0
    camera_shake_strength = 0.0
    camera_shake_x = 0
    camera_shake_y = 0
    impact_flash_alpha = 0.0
    player_lava_damage_timer = 0.0
    slash_effects.clear()
    game_state = "game"
    log_player_action(
        "World created",
        f"{current_world_name} | mode={GAME_MODE_LABELS[game_mode]} | icon={current_world_icon}"
    )


def retry_current_world():
    world_name = current_world_name.strip() or seed_input.strip()
    save_path = get_world_save_path(world_name)

    if save_path and os.path.exists(save_path):
        log_player_action("Retry world", world_name)
        load_world(world_name)
        return True

    if world_name:
        log_player_action("Retry fallback create", world_name)
        start_new_world_from_seed(world_name, player_image_path=current_player_image_path)
        return True

    return False


def return_to_main_menu():
    global game_state
    global menu_state
    global load_world_message
    global selected_load_world_name
    global game_over_close_at_ms
    global camera_shake_strength
    global camera_shake_x
    global camera_shake_y
    global impact_flash_alpha
    global menu_background_cache
    global menu_background_cache_tick

    close_runtime_overlays()
    menu_state = "main"
    load_world_message = ""
    selected_load_world_name = None
    game_over_close_at_ms = 0
    camera_shake_strength = 0.0
    camera_shake_x = 0
    camera_shake_y = 0
    impact_flash_alpha = 0.0
    menu_background_cache = None
    menu_background_cache_tick = -99999
    slash_effects.clear()
    game_state = "menu"
    log_player_action("Return to main menu")


def trigger_game_over():
    global game_state
    global hp
    global game_over_snapshot
    global game_over_close_at_ms

    if game_state == "game_over":
        return

    hp = max(0, hp)
    close_runtime_overlays()

    world_name_for_save = current_world_name.strip() or seed_input.strip()
    save_delete_status = "No save file to delete."
    if world_name_for_save:
        deleted, delete_message = remove_world_save_file(world_name_for_save)
        if deleted:
            save_delete_status = f"Save deleted: {world_name_for_save}"
        else:
            save_delete_status = delete_message

    game_over_snapshot = {
        "world_name": current_world_name or "Unsaved World",
        "day": get_current_day(),
        "kills": total_kills,
        "seed": world_seed,
        "save_delete_status": save_delete_status
    }
    add_screen_shake(12.0)
    trigger_impact_flash((232, 64, 52), 132)
    spawn_particles(player.center, (255, 124, 92), 36)
    play_sfx("death")
    game_over_close_at_ms = pygame.time.get_ticks() + GAME_OVER_CLOSE_DELAY_MS
    game_state = "game_over"
    log_player_action(
        "Game over",
        (
            f"world={game_over_snapshot['world_name']} | day={game_over_snapshot['day']} "
            f"| kills={game_over_snapshot['kills']} | {save_delete_status}"
        )
    )

# =============================
# ENEMY
# =============================
class Enemy:

    enemy_type = "slime"
    max_hp = 100
    damage = 5
    speed = 2
    attack_range = 33
    blocks_open_doors = True
    opens_doors = False
    anim_speed = 0.15

    def __init__(self, x, y):

        multiplier = get_night_multiplier()
        self.max_hp = int(self.max_hp * multiplier * enemy_health_multiplier)
        self.damage = int(self.damage * multiplier * enemy_damage_multiplier)

        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect = pygame.Rect(x, y, 80, 80)

        self.hp = self.max_hp
        self.frame = 0
        self.attack_cd = 0
        self.anim_state = "idle"
        self.facing_left = False

    def sync_rect(self):
        self.rect.x = int(round(self.pos_x))
        self.rect.y = int(round(self.pos_y))

    def try_move(self, dx, dy):
        trial = self.rect.copy()

        if dx != 0:
            trial.x = int(round(self.pos_x + dx))

        if dy != 0:
            trial.y = int(round(self.pos_y + dy))

        if can_occupy_rect(
                trial,
                get_enemy_collision_rect,
                block_water=True,
                block_open_doors=self.blocks_open_doors
        ):
            if dx != 0:
                self.pos_x += dx

            if dy != 0:
                self.pos_y += dy

            self.sync_rect()
            return True

        return False

    def get_target_point(self):
        return player.centerx, player.centery

    def move_toward_target(self, target_x, target_y):
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist == 0:
            return False, False

        step_x = dx / dist * self.speed
        step_y = dy / dist * self.speed

        if step_x < 0:
            self.facing_left = True
        elif step_x > 0:
            self.facing_left = False

        moved_x = self.try_move(step_x, 0)
        moved_y = self.try_move(0, step_y)
        return moved_x, moved_y

    def draw_health_bar(self, off, fill_color=(255, 0, 0)):
        pygame.draw.rect(
            surf,
            (60, 0, 0),
            (
                self.rect.x + off[0],
                self.rect.y + off[1] - 15,
                80,
                8
            )
        )

        pygame.draw.rect(
            surf,
            fill_color,
            (
                self.rect.x + off[0],
                self.rect.y + off[1] - 15,
                80 * (self.hp / max(1, self.max_hp)),
                8
            )
        )

    def update(self):

        global hp

        player_dx = player.centerx - self.rect.centerx
        player_dy = player.centery - self.rect.centery
        player_dist = math.hypot(player_dx, player_dy)
        target_x, target_y = self.get_target_point()

        # move toward player
        if player_dist > self.attack_range:

            moved_x, moved_y = self.move_toward_target(
                target_x,
                target_y
            )

            self.anim_state = "run" if moved_x or moved_y else "idle"

        # attack player
        else:

            self.anim_state = "attack"

            if self.attack_cd <= 0:
                if game_mode != "creative":
                    hp -= self.damage
                    add_screen_shake(2.2 + self.damage * 0.15)
                    trigger_impact_flash((210, 52, 42), 82)
                    spawn_particles(player.center, (255, 92, 62), 12)
                    play_sfx("player_hurt")
                    log_player_action(
                        "Damage taken",
                        f"-{self.damage} HP from {self.enemy_type} | hp={max(0, int(hp))}/{int(hp_limit)}"
                    )
                self.attack_cd = 60

        if self.attack_cd > 0:
            self.attack_cd -= 1

        self.frame += self.anim_speed

        # Wall breaking at night
        if is_night() and not disable_wall_breaking:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                wall_tile = (int(self.rect.centerx // TILE) + dx, int(self.rect.centery // TILE) + dy)
                if wall_tile in walls and wall_tile not in wall_break_timers:
                    wall_break_timers[wall_tile] = game_time

    def get_draw_frames(self):
        return blob_frames

    def draw(self, off):

        frames = self.get_draw_frames()

        if frames:

            img = frames[int(self.frame) % len(frames)]

            surf.blit(
                img,
                (
                    self.rect.x + off[0] - 20,
                    self.rect.y + off[1] - 20
                )
            )

        else:

            pygame.draw.rect(
                surf,
                (0, 255, 0),
                (
                    self.rect.x + off[0],
                    self.rect.y + off[1],
                    80,
                    80
                )
            )

        self.draw_health_bar(off)


class SmartEnemy(Enemy):

    path_refresh_frames = 28
    path_search_distance = 14
    animation_set = {}
    health_bar_color = (255, 0, 0)
    fallback_color = (190, 190, 190)

    def __init__(self, x, y):
        super().__init__(x, y)
        self.path_tiles = []
        self.path_refresh = 0
        self.last_goal_tile = None

    def refresh_path(self, start_tile, goal_tile):
        self.path_tiles = find_enemy_path(
            start_tile,
            goal_tile,
            self.path_search_distance,
            self.blocks_open_doors
        )
        self.path_refresh = self.path_refresh_frames
        self.last_goal_tile = goal_tile

    def get_target_point(self):
        start_tile = (
            int(self.rect.centerx // TILE),
            int(self.rect.centery // TILE)
        )
        goal_tile = (
            int(player.centerx // TILE),
            int(player.centery // TILE)
        )

        player_tile_distance = abs(start_tile[0] - goal_tile[0]) + abs(start_tile[1] - goal_tile[1])
        dynamic_refresh = max(12, min(48, int(14 + player_tile_distance * 1.2)))
        self.path_refresh_frames = dynamic_refresh
        self.path_refresh -= 1

        if goal_tile != self.last_goal_tile:
            self.path_refresh = 0

        if self.path_refresh <= 0 or not self.path_tiles:
            self.refresh_path(start_tile, goal_tile)

        while self.path_tiles and self.path_tiles[0] == start_tile:
            self.path_tiles.pop(0)

        if self.path_tiles:
            next_tile = self.path_tiles[0]
            next_target = (
                next_tile[0] * TILE + TILE // 2,
                next_tile[1] * TILE + TILE // 2
            )

            if math.hypot(
                self.rect.centerx - next_target[0],
                self.rect.centery - next_target[1]
            ) <= max(8, self.speed + 4):
                self.path_tiles.pop(0)

                if self.path_tiles:
                    next_tile = self.path_tiles[0]
                    next_target = (
                        next_tile[0] * TILE + TILE // 2,
                        next_tile[1] * TILE + TILE // 2
                    )

            if self.path_tiles:
                return next_target

        return player.centerx, player.centery

    def get_draw_frames(self):
        if self.anim_state == "attack" and self.animation_set.get("attack"):
            return self.animation_set["attack"]

        if self.anim_state == "run" and self.animation_set.get("run"):
            return self.animation_set["run"]

        return self.animation_set.get(
            "idle",
            self.animation_set.get("run", [])
        )

    def draw(self, off):
        frames = self.get_draw_frames()

        if not frames:
            pygame.draw.rect(
                surf,
                self.fallback_color,
                (
                    self.rect.x + off[0],
                    self.rect.y + off[1],
                    80,
                    80
                )
            )
            self.draw_health_bar(off, self.health_bar_color)
            return

        img = frames[int(self.frame) % len(frames)]

        if self.facing_left:
            img = pygame.transform.flip(img, True, False)

        img_rect = img.get_rect(center=(
            self.rect.centerx + off[0],
            self.rect.centery + off[1]
        ))
        surf.blit(img, img_rect)
        self.draw_health_bar(off, self.health_bar_color)


class MushroomEnemy(Enemy):

    enemy_type = "monster"
    max_hp = 50
    damage = 10
    blocks_open_doors = False
    opens_doors = True
    anim_speed = 0.18

    def get_draw_frames(self):
        return monster_frames

    def draw(self, off):
        frames = self.get_draw_frames()

        if frames:
            img = frames[int(self.frame) % len(frames)]

            surf.blit(
                img,
                (
                    self.rect.x + off[0] - 16,
                    self.rect.y + off[1] - 20
                )
            )

        else:
            pygame.draw.rect(
                surf,
                (210, 80, 120),
                (
                    self.rect.x + off[0],
                    self.rect.y + off[1],
                    80,
                    80
                )
            )

        self.draw_health_bar(off, (255, 70, 120))


class RatEnemy(SmartEnemy):

    enemy_type = "rat"
    animation_set = rat_animations
    anim_speed = 0.18
    fallback_color = (145, 120, 85)


class BatEnemy(SmartEnemy):

    enemy_type = "bat"
    animation_set = bat_animations
    anim_speed = 0.22
    fallback_color = (110, 90, 150)


enemies = [
    Enemy(400, 400)
]

# =============================
# FX
# =============================
particles = []
damage_texts = []


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 30
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, off):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x + off[0]), int(self.y + off[1])), 2)


class DamageText:
    def __init__(self, x, y, val):
        self.x = x
        self.y = y
        self.val = val
        self.life = 40

    def update(self):
        self.y -= 1
        self.life -= 1

    def draw(self, off):
        img = font.render(str(self.val), True, (255, 200, 50))
        surf.blit(img, (self.x + off[0], self.y + off[1]))


def spawn_particles(pos, color, count=10):
    for _ in range(count):
        particles.append(Particle(pos[0], pos[1], color))
    if len(particles) > MAX_PARTICLES:
        del particles[:-MAX_PARTICLES]


# =============================
# MAGIC EFFECTS
# =============================
def load_anim(pattern, size):
    out = find_game_files_matching(pattern)

    frames = []

    for path in sorted(out):
        try:
            frames.append(
                pygame.transform.scale(
                    pygame.image.load(path).convert_alpha(),
                    (size, size)
                )
            )
        except Exception:
            continue

    if frames:
        return frames

    return generate_spell_frames(pattern, size)


fireball = load_anim(r"Fire-bomb\d+\.png", 64)
lightning = load_anim(r"Lightning\d+\.png", 96)
dark = load_anim(r"Dark-Bolt\d+\.png", 64)
spark = load_anim(r"spark\d+\.png", 48)


def make_sword_icon(size=(42, 42)):
    icon = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.line(icon, (212, 222, 236), (11, 31), (30, 12), 5)
    pygame.draw.line(icon, (154, 166, 184), (10, 32), (32, 10), 2)
    pygame.draw.line(icon, (132, 88, 40), (8, 34), (14, 28), 5)
    pygame.draw.line(icon, (236, 194, 84), (12, 27), (20, 35), 4)
    pygame.draw.circle(icon, (236, 194, 84), (20, 35), 3)
    return icon


def build_icon_from_surface(surface, size=(42, 42)):
    if surface is None:
        return pygame.Surface(size, pygame.SRCALPHA)

    return pygame.transform.smoothscale(surface, size)


SPELL_SLOTS = {
    "spell_1": {"frames": fireball, "damage": 15},
    "spell_2": {"frames": lightning, "damage": 20},
    "spell_3": {"frames": dark, "damage": 18},
    "spell_4": {"frames": spark, "damage": 10},
    "spell_5": {"frames": fireball, "damage": 25},
    "spell_6": {"frames": lightning, "damage": 30}
}
snowball_projectile_frames = [pygame.transform.smoothscale(snowball_img, (22, 22))]
item_icons = {
    "sword": build_icon_from_surface(sword_img) if sword_img else make_sword_icon(),
    "axe": build_icon_from_surface(axe_img),
    "steak": build_icon_from_surface(steak_img),
    "wall": build_icon_from_surface(wall_textures["wall"]),
    "wall1": build_icon_from_surface(wall_textures["wall1"]),
    "wall2": build_icon_from_surface(wall_textures["wall2"]),
    "wall3": build_icon_from_surface(wall_textures["wall3"]),
    "wall4": build_icon_from_surface(wall_textures["wall4"]),
    "stone1_block": build_icon_from_surface(wall_textures["stone1_block"]),
    "stone2_block": build_icon_from_surface(wall_textures["stone2_block"]),
    "copper_block": build_icon_from_surface(wall_textures["copper_block"]),
    "door": build_icon_from_surface(door_img),
    "floor": build_icon_from_surface(floor_img),
    "torch": build_icon_from_surface(torch_img),
    "snowball": build_icon_from_surface(snowball_img),
    "water_bucket": build_icon_from_surface(water_bucket_img),
    "lava_bucket": build_icon_from_surface(lava_bucket_img),
    "book_and_quill": build_icon_from_surface(book_and_quill_img)
}
spell_icons = {
    spell_id: build_icon_from_surface(data["frames"][0] if data["frames"] else None)
    for spell_id, data in SPELL_SLOTS.items()
}


# =============================
# PROJECTILE
# =============================
class Projectile:

    def __init__(self, pos, target, frames=None, damage=25, speed=10):

        self.x, self.y = pos

        dx, dy = target[0] - pos[0], target[1] - pos[1]

        d = max(1, math.hypot(dx, dy))

        self.vx, self.vy = dx / d * speed, dy / d * speed

        self.frames = frames if frames else []
        self.frame = 0
        self.damage = damage
        self.hit = False
        self.life = 180

    def update(self):

        self.x += self.vx
        self.y += self.vy
        self.frame += 0.4
        self.life -= 1

    def draw(self, off):

        if self.frames:

            img = safe(self.frames, self.frame)

            surf.blit(
                img,
                img.get_rect(center=(
                    self.x + off[0],
                    self.y + off[1]
                ))
            )

        else:

            pygame.draw.circle(
                surf,
                (255, 200, 50),
                (
                    int(self.x + off[0]),
                    int(self.y + off[1])
                ),
                6
            )

    def rect(self):

        return pygame.Rect(
            self.x - 10,
            self.y - 10,
            20,
            20
        )


projectiles = []

# magic projectile visuals enabled

# Initialize global settings and audio once all helpers are available.
load_global_settings()
set_display_mode(fullscreen)
init_audio()

# =============================
# MAIN LOOP
# =============================
while True:
    delta_time = clock.tick(get_runtime_frame_limit()) / 1000.0

    for e in pygame.event.get():

        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "menu":

            if e.type == pygame.KEYDOWN:

                if menu_state == "main":

                    if e.key == pygame.K_1:
                        menu_state = "new_world"
                        log_player_action("Menu", "Open new world screen")

                    if e.key == pygame.K_2:
                        menu_state = "load_world"
                        load_world_message = ""
                        log_player_action("Menu", "Open load world screen")

                    if e.key == pygame.K_3:
                        set_menu_notice("Multiplayer available soon")

                    if e.key == pygame.K_4:
                        log_player_action("Quit requested")
                        pygame.quit()
                        sys.exit()

                    if e.key == pygame.K_5:
                        if open_external_link(GITHUB_URL):
                            log_player_action("Open URL", GITHUB_URL)

                    if e.key == pygame.K_ESCAPE:
                        log_player_action("Quit requested")
                        pygame.quit()
                        sys.exit()

                elif menu_state == "new_world":

                    if e.key == pygame.K_RETURN:
                        start_new_world_from_seed(
                            seed_input,
                            selected_game_mode,
                            get_selected_world_icon(),
                            selected_player_image_path
                        )

                    elif e.key == pygame.K_ESCAPE or (
                            e.key == keybinds["pause"]
                            and not (e.unicode and e.unicode.isprintable())
                    ):
                        menu_state = "main"
                        log_player_action("Menu", "Back to main menu")

                    elif e.key == pygame.K_BACKSPACE:
                        seed_input = seed_input[:-1]

                    elif e.key == pygame.K_LEFT:
                        cycle_selected_world_icon(-1)

                    elif e.key == pygame.K_RIGHT:
                        cycle_selected_world_icon(1)

                    elif e.key == pygame.K_1:
                        set_game_mode("easy")
                        log_player_action("Game mode selected", "Easy")

                    elif e.key == pygame.K_2:
                        set_game_mode("hard")
                        log_player_action("Game mode selected", "Hard")

                    elif e.key == pygame.K_3:
                        set_game_mode("creative")
                        log_player_action("Game mode selected", "Creative")

                    elif e.key == keybinds["pick_player_image"] and not (
                            e.unicode and e.unicode.isprintable()
                    ):
                        chosen_image_path = choose_player_image_from_computer()
                        if chosen_image_path is None:
                            pass
                        elif not chosen_image_path:
                            set_menu_notice("Image selection canceled.")
                        elif set_selected_player_image(chosen_image_path):
                            set_menu_notice("Player image selected.")
                            log_player_action("Player image chosen", chosen_image_path)
                        else:
                            set_menu_notice("Could not load that image.")

                    elif e.key == keybinds["clear_player_image"] and not (
                            e.unicode and e.unicode.isprintable()
                    ):
                        selected_player_image_path = ""
                        set_menu_notice("Player image reset to default.")

                    elif e.unicode and e.unicode.isprintable() and len(seed_input) < 28:
                        seed_input += e.unicode

                elif menu_state == "load_world":

                    worlds = get_worlds()

                    if e.key == pygame.K_1 and len(worlds) > 0:
                        load_world(worlds[0])

                    if e.key == pygame.K_2 and len(worlds) > 1:
                        load_world(worlds[1])

                    if e.key == pygame.K_3 and len(worlds) > 2:
                        load_world(worlds[2])

                    if e.key == keybinds["pause"]:
                        menu_state = "main"
                        load_world_message = ""
                        selected_load_world_name = None
                        log_player_action("Menu", "Back to main menu")

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_pos = scale_mouse_pos(e.pos)

                if menu_state == "main":
                    buttons = get_main_menu_buttons()

                    if buttons["new_world"].collidepoint(mouse_pos):
                        menu_state = "new_world"
                        log_player_action("Menu", "Open new world screen")
                    elif buttons["load_world"].collidepoint(mouse_pos):
                        menu_state = "load_world"
                        load_world_message = ""
                        log_player_action("Menu", "Open load world screen")
                    elif buttons["multiplayer"].collidepoint(mouse_pos):
                        set_menu_notice("Multiplayer available soon")
                    elif buttons["github"].collidepoint(mouse_pos):
                        if open_external_link(GITHUB_URL):
                            log_player_action("Open URL", GITHUB_URL)
                    elif buttons["quit"].collidepoint(mouse_pos):
                        log_player_action("Quit requested")
                        pygame.quit()
                        sys.exit()

                elif menu_state == "new_world":
                    buttons = get_new_world_buttons()

                    if buttons["create"].collidepoint(mouse_pos):
                        start_new_world_from_seed(
                            seed_input,
                            selected_game_mode,
                            get_selected_world_icon(),
                            selected_player_image_path
                        )
                    elif buttons["back"].collidepoint(mouse_pos):
                        menu_state = "main"
                        log_player_action("Menu", "Back to main menu")
                    elif buttons["icon_prev"].collidepoint(mouse_pos):
                        cycle_selected_world_icon(-1)
                    elif buttons["icon_next"].collidepoint(mouse_pos):
                        cycle_selected_world_icon(1)
                    elif buttons["choose_image"].collidepoint(mouse_pos):
                        chosen_image_path = choose_player_image_from_computer()
                        if chosen_image_path is None:
                            pass
                        elif not chosen_image_path:
                            set_menu_notice("Image selection canceled.")
                        elif set_selected_player_image(chosen_image_path):
                            set_menu_notice("Player image selected.")
                            log_player_action("Player image chosen", chosen_image_path)
                        else:
                            set_menu_notice("Could not load that image.")
                    elif buttons["clear_image"].collidepoint(mouse_pos):
                        selected_player_image_path = ""
                        set_menu_notice("Player image reset to default.")
                    else:
                        for mode_id in GAME_MODE_ORDER:
                            button_id = f"mode_{mode_id}"
                            if buttons[button_id].collidepoint(mouse_pos):
                                set_game_mode(mode_id)
                                log_player_action(
                                    "Game mode selected",
                                    GAME_MODE_LABELS[mode_id]
                                )
                                break

                elif menu_state == "load_world":
                    worlds = get_worlds()
                    for i, world_name in enumerate(worlds[:9]):
                        if get_load_world_entry_rect(i).collidepoint(mouse_pos):
                            selected_load_world_name = world_name
                            load_world_message = f"Selected: {world_name}"
                            metadata = get_world_metadata(world_name)
                            log_player_action(
                                "World selected",
                                f"{world_name} | mode={GAME_MODE_LABELS[metadata['mode']]}"
                            )
                            break

                    buttons = get_load_world_buttons()
                    if buttons["load"].collidepoint(mouse_pos):
                        if selected_load_world_name:
                            load_world(selected_load_world_name)
                        else:
                            load_world_message = "Select a world to load."
                    elif buttons["delete"].collidepoint(mouse_pos):
                        delete_world(selected_load_world_name)
                    elif buttons["back"].collidepoint(mouse_pos):
                        menu_state = "main"
                        load_world_message = ""
                        selected_load_world_name = None
                        log_player_action("Menu", "Back to main menu")

            continue

        if game_state == "game_over":
            continue

        if game_state == "pause":

            if e.type == pygame.KEYDOWN:

                if pause_menu_state == "keybinds" and selected_keybind_action is not None:
                    swapped_action = rebind_action_key(selected_keybind_action, e.key)
                    save_global_settings()
                    log_player_action(
                        "Keybind changed",
                        f"{selected_keybind_action} -> {pygame.key.name(e.key)}"
                    )
                    if swapped_action is not None:
                        log_player_action(
                            "Keybind swapped",
                            (
                                f"{swapped_action} -> "
                                f"{pygame.key.name(keybinds[swapped_action])}"
                            )
                        )
                    selected_keybind_action = None

                elif (
                        e.key == keybinds["pause"]
                        and not (
                            pause_menu_state == "codes"
                            and e.unicode
                            and e.unicode.isprintable()
                        )
                ):

                    if pause_menu_state in ["settings", "codes", "keybinds", "upgrades", "shop"]:
                        if pause_menu_state == "keybinds":
                            selected_keybind_action = None
                        if pause_menu_state == "upgrades":
                            selected_upgrade = None
                        if pause_menu_state == "shop":
                            shop_message = ""
                        pause_menu_state = "main"
                        log_player_action("Pause menu", "Back to pause root")
                    else:
                        game_state = "game"
                        log_player_action("Pause menu", "Resume game")

                elif pause_menu_state == "codes":

                    if e.key == pygame.K_RETURN:
                        apply_code(code_input)

                    elif e.key == pygame.K_BACKSPACE:
                        code_input = code_input[:-1]

                    elif e.unicode and e.unicode.isprintable():
                        code_input += e.unicode.upper()

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:

                mouse_pos = scale_mouse_pos(e.pos)

                if pause_menu_state == "main":
                    buttons = get_pause_buttons()

                    if buttons["resume"].collidepoint(mouse_pos):
                        game_state = "game"
                        log_player_action("Pause menu", "Resume game")

                    elif buttons["toggle_fullscreen"].collidepoint(mouse_pos):
                        set_display_mode(not fullscreen)
                        save_global_settings()
                        log_player_action("Display mode", "Fullscreen" if fullscreen else "Windowed")

                    elif buttons["settings"].collidepoint(mouse_pos):
                        pause_menu_state = "settings"
                        log_player_action("Pause menu", "Open settings")

                    elif buttons["upgrades"].collidepoint(mouse_pos):
                        pause_menu_state = "upgrades"
                        selected_upgrade = None
                        log_player_action("Pause menu", "Open upgrades")

                    elif buttons["shop"].collidepoint(mouse_pos):
                        pause_menu_state = "shop"
                        shop_message = ""
                        log_player_action("Pause menu", "Open shop")

                    elif buttons["codes"].collidepoint(mouse_pos):
                        code_input = ""
                        code_message = ""
                        pause_menu_state = "codes"
                        log_player_action("Pause menu", "Open codes")

                    elif buttons["save_and_quit"].collidepoint(mouse_pos):
                        save_world()
                        log_player_action("Save and quit")
                        pygame.quit()
                        sys.exit()

                elif pause_menu_state == "settings":
                    buttons = get_settings_buttons()

                    if buttons["toggle_fullscreen"].collidepoint(mouse_pos):
                        set_display_mode(not fullscreen)
                        save_global_settings()
                        log_player_action("Display mode", "Fullscreen" if fullscreen else "Windowed")

                    elif buttons["resolution"].collidepoint(mouse_pos):
                        cycle_resolution()
                        log_player_action("Resolution changed", get_resolution_label())

                    elif buttons["fps_lock"].collidepoint(mouse_pos):
                        cycle_fps_limit()
                        log_player_action("FPS lock changed", get_fps_label())

                    elif buttons["volume"].collidepoint(mouse_pos):
                        cycle_master_volume()
                        save_global_settings()
                        log_player_action("Volume changed", get_volume_label())

                    elif buttons["disable_wall_breaking"].collidepoint(mouse_pos):
                        disable_wall_breaking = not disable_wall_breaking
                        save_global_settings()
                        log_player_action(
                            "Wall breaking setting",
                            "Disabled" if disable_wall_breaking else "Enabled"
                        )

                    elif buttons["keybinds"].collidepoint(mouse_pos):
                        pause_menu_state = "keybinds"
                        selected_keybind_action = None
                        log_player_action("Pause menu", "Open keybinds")

                    elif buttons["back"].collidepoint(mouse_pos):
                        pause_menu_state = "main"
                        log_player_action("Pause menu", "Back")

                elif pause_menu_state == "keybinds":
                    buttons = get_keybind_buttons()

                    if buttons["back"].collidepoint(mouse_pos):
                        pause_menu_state = "settings"
                        selected_keybind_action = None
                        log_player_action("Keybinds", "Back to settings")
                    else:
                        for action in KEYBIND_DISPLAY_ORDER:
                            if buttons[action].collidepoint(mouse_pos):
                                selected_keybind_action = action
                                log_player_action("Keybinds", f"Waiting input for {action}")
                                break

                elif pause_menu_state == "upgrades":
                    buttons = get_upgrade_buttons()

                    if buttons["back"].collidepoint(mouse_pos):
                        pause_menu_state = "main"
                        selected_upgrade = None
                        log_player_action("Upgrades", "Back")
                    else:
                        for upgrade_id in upgrade_labels:
                            if buttons[upgrade_id].collidepoint(mouse_pos):
                                selected_upgrade = upgrade_id
                                try_buy_upgrade(upgrade_id)
                                break

                elif pause_menu_state == "shop":
                    buttons = get_shop_buttons()

                    if buttons["buy_steak"].collidepoint(mouse_pos):
                        try_buy_steak()

                    elif buttons["back"].collidepoint(mouse_pos):
                        pause_menu_state = "main"
                        shop_message = ""
                        log_player_action("Shop", "Back")

                else:
                    buttons = get_code_buttons()

                    if buttons["apply"].collidepoint(mouse_pos):
                        apply_code(code_input)
                        log_player_action("Code applied", code_input.strip().upper() or "<empty>")

                    elif buttons["back"].collidepoint(mouse_pos):
                        pause_menu_state = "main"
                        log_player_action("Codes", "Back")

            continue

        if book_open:

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_BACKSPACE:
                    if book_text:
                        book_text = book_text[:-1]

                elif e.key == pygame.K_RETURN:
                    if len(book_text) < BOOK_MAX_CHARS:
                        book_text += "\n"

                elif e.unicode and e.unicode.isprintable():
                    if len(book_text) < BOOK_MAX_CHARS:
                        book_text += e.unicode

                elif e.key == keybinds["save_world"]:
                    save_world()
                    set_book_status("Book saved with world.")
                    log_player_action("Book", "Manual save")

                elif e.key == pygame.K_ESCAPE or e.key == keybinds["pause"]:
                    book_open = False
                    play_sfx("book_close")
                    if current_world_name.strip():
                        save_world(autosave=True)
                    set_book_status("Book closed and saved.")
                    log_player_action("Book", "Close")

            continue

        if inventory_open:

            if e.type == pygame.KEYDOWN:

                if e.key == keybinds["inventory"]:
                    inventory_open = False
                    inventory_selected_index = None
                    log_player_action("Inventory", "Close")

                elif e.key == keybinds["pause"]:
                    inventory_open = False
                    inventory_selected_index = None
                    code_input = ""
                    code_message = ""
                    pause_menu_state = "main"
                    game_state = "pause"
                    log_player_action("Inventory", "Close and pause")

            elif e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = scale_mouse_pos(e.pos)

                if e.button == 1:
                    inventory_index = get_inventory_slot_index_at(mouse_pos)

                    if inventory_index is not None:
                        if inventory[inventory_index] is None:
                            inventory_selected_index = None
                            log_player_action("Inventory", f"Slot {inventory_index + 1} empty")
                        elif inventory_selected_index == inventory_index:
                            inventory_selected_index = None
                            log_player_action("Inventory", "Clear selected slot")
                        else:
                            inventory_selected_index = inventory_index
                            log_player_action(
                                "Inventory",
                                f"Select slot {inventory_index + 1} ({inventory[inventory_index]})"
                            )

                        continue

                    hotbar_index = get_hotbar_slot_index_at(mouse_pos)

                    if hotbar_index is not None:
                        if inventory_selected_index is not None:
                            hotbar_slots[hotbar_index] = inventory[inventory_selected_index]
                            active_hotbar_slot = hotbar_index
                            inventory_selected_index = None
                            log_player_action(
                                "Hotbar assign",
                                f"slot={hotbar_index + 1} item={hotbar_slots[hotbar_index]}"
                            )
                        else:
                            active_hotbar_slot = hotbar_index
                            log_player_action("Hotbar select", f"slot={hotbar_index + 1}")

                        continue

                elif e.button == 3:
                    hotbar_index = get_hotbar_slot_index_at(mouse_pos)

                    if hotbar_index is not None:
                        hotbar_slots[hotbar_index] = None
                        log_player_action("Hotbar clear", f"slot={hotbar_index + 1}")

                        if active_hotbar_slot == hotbar_index:
                            active_hotbar_slot = DEFAULT_ACTIVE_HOTBAR_SLOT

                        continue

            continue

        if crafting_open:

            if e.type == pygame.KEYDOWN:
                if e.key in [keybinds["crafting"], keybinds["pause"]]:
                    crafting_open = False
                    crafting_message = ""
                    log_player_action("Crafting", "Close")

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_pos = scale_mouse_pos(e.pos)
                recipe_buttons = get_crafting_buttons()
                for recipe in CRAFTING_RECIPES:
                    if recipe_buttons[recipe["id"]].collidepoint(mouse_pos):
                        craft_recipe(recipe)
                        break

            continue

        if map_open:

            if e.type == pygame.KEYDOWN and e.key in [keybinds["map"], keybinds["pause"]]:
                map_open = False
                log_player_action("Map", "Close")

            continue

        if waypoint_editing:

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_RETURN:
                    finish_waypoint_editing(True)
                    log_player_action("Waypoint", "Save name")

                elif e.key == pygame.K_BACKSPACE:
                    waypoint_name_input = waypoint_name_input[:-1]

                elif e.unicode and e.unicode.isprintable() and len(waypoint_name_input) < 28:
                    waypoint_name_input += e.unicode

                elif e.key == pygame.K_ESCAPE or e.key == keybinds["pause"]:
                    finish_waypoint_editing(False)
                    log_player_action("Waypoint", "Cancel edit")

                elif e.key == keybinds["delete_waypoint"]:
                    remove_waypoint_by_id(selected_waypoint_id)
                    log_player_action("Waypoint", "Delete selected")

            continue

        if e.type == pygame.KEYDOWN:

            if e.key == keybinds["pause"]:
                inventory_open = False
                code_input = ""
                code_message = ""
                pause_menu_state = "main"
                game_state = "pause"
                log_player_action("Pause", "Open")
                continue

            if e.key == keybinds["save_world"]:
                save_world()
                log_player_action("Manual save", current_world_name or str(world_seed))

            if e.key == keybinds["inventory"]:
                inventory_open = not inventory_open
                inventory_selected_index = None
                log_player_action("Inventory", "Open" if inventory_open else "Close")

            if e.key == keybinds["crafting"]:
                crafting_open = not crafting_open
                crafting_message = ""
                if crafting_open:
                    inventory_open = False
                    inventory_selected_index = None
                log_player_action("Crafting", "Open" if crafting_open else "Close")

            if e.key == keybinds["map"]:
                map_open = not map_open
                if map_open:
                    inventory_open = False
                    crafting_open = False
                    inventory_selected_index = None
                log_player_action("Map", "Open" if map_open else "Close")
                continue

            if e.key == keybinds["toggle_controls"]:
                show_controls = not show_controls
                log_player_action("Controls panel", "Show" if show_controls else "Hide")

            if e.key == keybinds["delete_waypoint"]:
                remove_waypoint_by_id(selected_waypoint_id)
                log_player_action("Waypoint", "Delete selected")

            if e.key == keybinds["roll"] and not locked and stam >= 50:
                stam -= 50
                state = "roll"
                frame = 0
                locked = True
                add_screen_shake(1.4)
                spawn_particles(player.center, (210, 192, 162), 8)
                log_player_action("Roll", f"stamina={int(stam)}")

            hotbar_key_slot = get_hotbar_slot_index_for_key(e.key)
            if hotbar_key_slot is not None:
                active_hotbar_slot = hotbar_key_slot
                log_player_action("Hotbar select", f"slot={active_hotbar_slot + 1}")

                spell_entry = hotbar_slots[hotbar_key_slot]
                if is_spell_entry(spell_entry):
                    mx, my = scale_mouse_pos(pygame.mouse.get_pos())
                    world_mouse = (
                        mx - WIDTH // 2 + player.centerx,
                        my - HEIGHT // 2 + player.centery
                    )
                    spell_cast = cast_spell_from_slot(spell_entry, world_mouse)
                    log_player_action(
                        "Cast spell",
                        f"{spell_entry} | {'ok' if spell_cast else 'blocked'}"
                    )

        if e.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = scale_mouse_pos(e.pos)
            hotbar_index = get_hotbar_slot_index_at(mouse_pos)

            if e.button == 2:
                clicked_waypoint = find_waypoint_at_screen_pos(mouse_pos)

                if clicked_waypoint is None:
                    world_x, world_y = get_world_pos_from_screen(mouse_pos)
                    clicked_waypoint = create_waypoint(world_x, world_y)
                    log_player_action("Waypoint", f"Create at {int(world_x)}, {int(world_y)}")
                else:
                    log_player_action("Waypoint", f"Edit {clicked_waypoint['name']}")

                start_waypoint_editing(clicked_waypoint)
                continue

            if hotbar_index is not None:
                active_hotbar_slot = hotbar_index
                log_player_action("Hotbar select", f"slot={hotbar_index + 1}")

                continue

            if e.button == 3:
                world_x, world_y = get_world_pos_from_screen(mouse_pos)
                placed = place_equipped_item_at_mouse(mouse_pos)
                log_player_action(
                    "Place item",
                    f"{get_active_hotbar_entry()} at {int(world_x // TILE)},{int(world_y // TILE)} | {'ok' if placed else 'blocked'}"
                )
                continue

            if e.button == 1:
                active_entry = get_active_hotbar_entry()

                if active_entry == "book_and_quill":
                    book_open = True
                    book_cursor_blink_on = True
                    book_cursor_timer = 0.0
                    play_sfx("book_open")
                    set_book_status("Book opened.")
                    log_player_action("Book", "Open")
                    continue

                if active_entry == "snowball":
                    world_x, world_y = get_world_pos_from_screen(mouse_pos)
                    thrown = throw_snowball((world_x, world_y))
                    log_player_action(
                        "Throw snowball",
                        f"{int(world_x // TILE)},{int(world_y // TILE)} | {'ok' if thrown else 'blocked'}"
                    )
                    continue

                if active_entry in PLACEABLE_ITEM_IDS:
                    world_x, world_y = get_world_pos_from_screen(mouse_pos)
                    broken = break_equipped_item_at_mouse(mouse_pos)
                    log_player_action(
                        "Break item",
                        f"{active_entry} at {int(world_x // TILE)},{int(world_y // TILE)} | {'ok' if broken else 'none'}"
                    )
                    continue

                if active_entry in MELEE_ITEM_IDS and not locked and stam >= 10:

                    stam -= 10
                    state = "attack"
                    frame = 0
                    locked = True
                    heavy_strike = active_entry == "axe"
                    attack_size = 110 if active_entry == "axe" else 90
                    base_damage = 32 if active_entry == "axe" else 20
                    melee_damage = int(round(base_damage * get_melee_damage_multiplier()))
                    attack_box = pygame.Rect(
                        player.centerx - attack_size // 2,
                        player.centery - attack_size // 2,
                        attack_size,
                        attack_size
                    )

                    hits_landed = 0
                    for en in enemies:
                        if attack_box.colliderect(en.rect):
                            en.hp -= melee_damage
                            hits_landed += 1
                            spawn_particles(en.rect.center, (255, 206, 132), 8 if heavy_strike else 6)

                    spawn_slash_effect(player.center, facing_left, heavy=heavy_strike)
                    add_screen_shake(2.8 if heavy_strike else 1.8)
                    trigger_impact_flash((198, 140, 88), 34 if hits_landed > 0 else 20)
                    play_sfx("swing")
                    log_player_action("Melee attack", f"{active_entry} dmg={melee_damage}")

                if active_entry == "steak":
                    hp = min(hp_limit, hp + 40)
                    try:
                        steak_idx = inventory.index("steak")
                        inventory[steak_idx] = None
                    except ValueError:
                        pass
                    for idx in range(len(hotbar_slots)):
                        if hotbar_slots[idx] == "steak":
                            hotbar_slots[idx] = None
                    log_player_action("Consume", f"steak hp={int(hp)}/{int(hp_limit)}")

    # ================= MENU
    if game_state == "menu":
        if menu_state == "main":
            draw_main_menu_screen()
        elif menu_state == "new_world":
            draw_new_world_menu()
        elif menu_state == "load_world":
            draw_load_world_menu()

        screen.blit(
            pygame.transform.scale(surf, (SW, SH)),
            (0,0)
        )

        pygame.display.update()

        continue

    if (
            game_state == "game_over"
            and game_over_close_at_ms
            and pygame.time.get_ticks() >= game_over_close_at_ms
    ):
        log_player_action("Game closed", "death screen timeout")
        pygame.quit()
        sys.exit()

    # ================= UPDATE
    gameplay_frozen = (
        game_state in ["pause", "game_over"]
        or inventory_open
        or crafting_open
        or waypoint_editing
        or map_open
        or book_open
    )
    tick_counter += 1

    if book_open:
        book_cursor_timer += delta_time
        if book_cursor_timer >= 0.45:
            book_cursor_timer = 0.0
            book_cursor_blink_on = not book_cursor_blink_on
    else:
        book_cursor_timer = 0.0
        book_cursor_blink_on = True

    # Update game time
    game_time += delta_time

    if not gameplay_frozen:

        if game_mode == "creative":
            hp = hp_limit
            mana = mana_limit
            stam = stam_limit

        hp = min(hp_limit, hp + 0.01)
        mana = min(mana_limit, mana + MANA_REGEN_PER_TICK)
        stam = min(stam_limit, stam + STAMINA_REGEN_PER_TICK)
        update_open_doors()

        if game_mode != "creative":
            player_lava_damage_timer -= delta_time
            if is_lava(player.centerx, player.bottom - 6) and player_lava_damage_timer <= 0:
                hp -= 8
                player_lava_damage_timer = LAVA_DAMAGE_INTERVAL
                add_screen_shake(2.0)
                trigger_impact_flash((255, 102, 36), 56)
                spawn_particles(player.center, (255, 142, 62), 11)
                play_sfx("lava_burn")
                log_player_action(
                    "Lava damage",
                    f"-8 HP | hp={max(0, int(hp))}/{int(hp_limit)}"
                )
        else:
            player_lava_damage_timer = 0.0

        current_tile = (
            int(player.centerx // TILE),
            int(player.centery // TILE)
        )

        moving = False

        if current_tile != last_player_tile:

            step_counter += 1
            last_player_tile = current_tile
            if last_movement_log_tile != current_tile:
                last_movement_log_tile = current_tile
                log_player_action("Move", f"tile={current_tile[0]}, {current_tile[1]}")

            if step_counter >= 10:

                step_counter = 0

                spawn_multiplier = 5.0 if is_night() else 1.0

                if mobs_spawn_enabled:
                    for _ in range(5 if is_night() else 1):
                        spawn_enemy_near_player(
                            random.choice([Enemy, RatEnemy, BatEnemy]),
                            min(1.0, 0.6 * spawn_multiplier)
                        )
                        spawn_enemy_near_player(
                            MushroomEnemy,
                            min(1.0, 0.8 * spawn_multiplier)
                        )

        if not locked:

            keys = pygame.key.get_pressed()

            move_x = 0
            move_y = 0

            speed = SPRINT_SPEED if keys[keybinds["sprint"]] else PLAYER_SPEED

            if keys[keybinds["move_left"]]:
                move_x -= speed
                facing_left = True

            if keys[keybinds["move_right"]]:
                move_x += speed
                facing_left = False

            if keys[keybinds["move_up"]]:
                move_y -= speed

            if keys[keybinds["move_down"]]:
                move_y += speed

            moved_x = move_player_with_collisions(move_x, 0)
            moved_y = move_player_with_collisions(0, move_y)

            if moved_x or moved_y:
                moving = True

            state = "run" if moving else "idle"

        # ================= ANIMATION
        if state == "roll":

            frame += 0.5

            move_player_with_collisions(
                -12 if facing_left else 12,
                0
            )

            if frame >= len(roll_anim):
                state = "idle"
                locked = False
                frame = 0

        elif state == "attack":

            frame += 0.4

            if frame >= len(attack_anim):
                state = "idle"
                locked = False
                frame = 0

        else:
            frame += 0.2

        # ================= ENEMIES
        active_distance_sq = ENEMY_ACTIVE_DISTANCE * ENEMY_ACTIVE_DISTANCE
        despawn_distance_sq = ENEMY_DESPAWN_DISTANCE * ENEMY_DESPAWN_DISTANCE

        if not mobs_spawn_enabled and enemies:
            enemies.clear()
            wall_break_timers.clear()

        for en in enemies[:]:
            dx = en.rect.centerx - player.centerx
            dy = en.rect.centery - player.centery
            dist_sq = dx * dx + dy * dy

            if dist_sq > despawn_distance_sq:
                enemies.remove(en)
                continue

            if dist_sq <= active_distance_sq:
                if dist_sq > (ENEMY_ACTIVE_DISTANCE * 0.75) ** 2 and tick_counter % 2 == 0:
                    continue
                en.update()

                en_lava_timer = getattr(en, "lava_timer", 0.0) - delta_time
                if is_lava(en.rect.centerx, en.rect.bottom - 6):
                    if en_lava_timer <= 0:
                        en.hp -= 9
                        en_lava_timer = LAVA_DAMAGE_INTERVAL
                        if tick_counter % 3 == 0:
                            spawn_particles(en.rect.center, (255, 132, 44), 8)
                    setattr(en, "lava_timer", en_lava_timer)
                else:
                    setattr(en, "lava_timer", 0.0)

        # ================= PROJECTILES (single pass: move + collide + despawn)
        for p in projectiles[:]:
            p.update()

            if p.life <= 0:
                projectiles.remove(p)
                continue

            proj_tile_x = int(p.x // TILE)
            proj_tile_y = int(p.y // TILE)
            if (
                    (proj_tile_x, proj_tile_y) in walls
                    or (
                        (proj_tile_x, proj_tile_y) in doors
                        and (proj_tile_x, proj_tile_y) not in open_doors
                    )
            ):
                projectiles.remove(p)
                continue

            projectile_rect = p.rect()
            hit_enemy = False

            for en in enemies:

                if projectile_rect.colliderect(en.rect):

                    en.hp -= p.damage

                    damage_texts.append(
                        DamageText(
                            en.rect.centerx + random.randint(-10, 10),
                            en.rect.y - 10,
                            p.damage
                        )
                    )
                    if len(damage_texts) > MAX_DAMAGE_TEXTS:
                        del damage_texts[:-MAX_DAMAGE_TEXTS]

                    spawn_particles(
                        en.rect.center,
                        (255, 180, 50),
                        20
                    )
                    add_screen_shake(2.2)
                    trigger_impact_flash((255, 184, 96), 44)
                    play_sfx("hit")

                    if p in projectiles:
                        projectiles.remove(p)

                    hit_enemy = True
                    break

            if hit_enemy:
                continue

        # remove dead enemies
        for en in enemies[:]:

            if en.hp <= 0:
                spawn_particles(en.rect.center, (255, 224, 146), 14)
                add_screen_shake(1.1)
                play_sfx("enemy_die")
                enemies.remove(en)
                total_kills += 1
                kill_points += 1

        # Check wall breaking timers
        if is_night() and not disable_wall_breaking:
            for wall_tile, start_time in list(wall_break_timers.items()):
                if game_time - start_time >= get_enemy_wall_break_time():
                    if wall_tile in walls:
                        walls.discard(wall_tile)
                        wall_types.pop(wall_tile, None)
                        if wall_tile in torch_positions and torch_mounts.get(wall_tile) == "wall":
                            torch_positions.discard(wall_tile)
                            torch_mounts.pop(wall_tile, None)
                        spawn_particles(
                            (wall_tile[0] * TILE + TILE // 2, wall_tile[1] * TILE + TILE // 2),
                            (100, 100, 100),
                            10
                        )
                        add_screen_shake(1.2)
                    del wall_break_timers[wall_tile]
        else:
            wall_break_timers.clear()

        if (
                current_world_name.strip()
                and pygame.time.get_ticks() - last_autosave_ms >= AUTOSAVE_INTERVAL_MS
        ):
            save_world(autosave=True)

        if hp <= 0:
            trigger_game_over()
            gameplay_frozen = True

    update_visual_fx(gameplay_frozen)

    # ================= DRAW
    surf.fill((20, 20, 20))

    ox = WIDTH // 2 - player.centerx + camera_shake_x
    oy = HEIGHT // 2 - player.centery + camera_shake_y
    center_tile_x = int(player.centerx // TILE)
    center_tile_y = int(player.centery // TILE)
    player_tile_x = center_tile_x
    player_tile_y = int((player.bottom + 32) // TILE)
    water_frame = water_frames[
        (pygame.time.get_ticks() // 120)
        %
        len(water_frames)
    ]
    ocean_frame = ocean_frames[
        (pygame.time.get_ticks() // 120)
        %
        len(ocean_frames)
    ]
    lava_frame = lava_frames[
        (pygame.time.get_ticks() // 100)
        %
        len(lava_frames)
    ]
    visible_tiles_x = WIDTH // TILE + 2
    visible_tiles_y = HEIGHT // TILE + 2
    half_tiles_x = visible_tiles_x // 2
    half_tiles_y = visible_tiles_y // 2

    for tx in range(-half_tiles_x, half_tiles_x + 1):

        for ty in range(-half_tiles_y, half_tiles_y + 1):

            wx = center_tile_x + tx
            wy = center_tile_y + ty

            x = wx * TILE + ox
            y = wy * TILE + oy

            t = get_tile(wx, wy)

            if t == "water":
                surf.blit(water_frame, (x, y))
            elif t == "ocean":
                surf.blit(ocean_frame, (x, y))
            elif t == "lava":
                surf.blit(lava_frame, (x, y))

            else:

                if is_shore(wx, wy):

                    surf.blit(sand_img, (x, y))

                else:

                    if t == "grass":
                        surf.blit(grass_plain, (x, y))

                    elif t in ["desert", "sand"]:
                        surf.blit(sand_img, (x, y))

                    elif t == "stone1":
                        surf.blit(stone1_img, (x, y))

                    elif t == "stone2":
                        surf.blit(stone2_img, (x, y))

                    elif t == "copper":
                        surf.blit(copper_img, (x, y))

                # decorations
                deco = get_tile_deco(wx, wy)

                if t == "grass" and deco > 0.93:
                    surf.blit(flower_tile, (x, y))

                elif t == "grass" and deco < 0.05:
                    surf.blit(bush_tile, (x, y))

                elif t == "desert" and deco > 0.9:
                    surf.blit(desert_rock_tile, (x, y))

            if (wx, wy) in placed_floors:
                surf.blit(floor_img, (x, y))

            if (wx, wy) in torch_positions:
                torch_mount = torch_mounts.get((wx, wy), "ground")
                if torch_mount == "wall":
                    surf.blit(torch_img, (x, y - 20))
                else:
                    surf.blit(torch_img, (x, y))

            if (
                    t in WATERLIKE_TILE_IDS
                    and wx == player_tile_x
                    and wy == player_tile_y
            ):
                surf.blit(bridge_img, (x, y))

            if (wx, wy) in walls:
                wall_item_id = wall_types.get((wx, wy), "wall")
                wall_surface = wall_textures.get(wall_item_id, wall_textures["wall"])
                if wall_surface:
                    surf.blit(wall_surface, (x, y))

                else:
                    pygame.draw.rect(
                        surf,
                        (120, 120, 120),
                        (x, y, TILE, TILE)
                    )

            if (wx, wy) in doors:

                if (wx, wy) in open_doors:
                    surf.blit(door_open_img, (x, y))

                else:
                    surf.blit(door_img, (x, y))

    # ================= ENEMY DRAW
    view_rect = pygame.Rect(-160, -160, WIDTH + 320, HEIGHT + 320)

    for en in enemies:
        draw_rect = en.rect.move(ox, oy)

        if draw_rect.colliderect(view_rect):
            en.draw((ox, oy))

    # ================= PLAYER DRAW
    if custom_player_surface is not None:
        img = custom_player_surface
    elif state == "attack":
        img = safe(attack_anim, frame)
    elif state == "roll":
        img = safe(roll_anim, frame)
    elif state == "run":
        img = safe(run_anim, frame)
    else:
        img = safe(idle_anim, frame)

    if facing_left:
        img = pygame.transform.flip(img, True, False)

    surf.blit(
        img,
        (WIDTH // 2 - 120 + camera_shake_x, HEIGHT // 2 - 80 + camera_shake_y)
    )

    draw_slash_effects((ox, oy))

    # ================= PROJECTILE DRAW
    for p in projectiles:
        p.draw((ox, oy))

    # ================= PARTICLES
    for particle in particles[:]:

        if not gameplay_frozen:
            particle.update()

        particle.draw((ox, oy))

        if particle.life <= 0:
            particles.remove(particle)

    # ================= DAMAGE TEXT
    for damage_text in damage_texts[:]:

        if not gameplay_frozen:
            damage_text.update()

        damage_text.draw((ox, oy))

        if damage_text.life <= 0:
            damage_texts.remove(damage_text)

    draw_waypoints()

    # ================= UI
    hud_panel = pygame.Rect(16, 14, 336, 156)
    draw_knight_panel(
        hud_panel,
        border_color=(196, 160, 102),
        fill_color=(22, 14, 8),
        inner_color=(38, 26, 16),
        border_radius=12,
        draw_rivets=True
    )

    world_line = small_font.render(
        f"{current_world_name or 'Unsaved'}  |  {GAME_MODE_LABELS.get(game_mode, 'Easy')}",
        True,
        (232, 216, 184)
    )
    surf.blit(world_line, (hud_panel.x + 10, hud_panel.y + 8))

    day_phase = "Night" if is_night() else "Day"
    day_line = small_font.render(
        f"Day {get_current_day()}  |  {day_phase}  |  Kills {total_kills}  |  Points {kill_points}",
        True,
        (232, 216, 184)
    )
    surf.blit(day_line, (hud_panel.x + 10, hud_panel.y + 26))

    draw_labeled_bar(hud_panel.x + 10, hud_panel.y + 50, 314, "HP", hp, hp_limit, (205, 64, 64))
    draw_labeled_bar(hud_panel.x + 10, hud_panel.y + 75, 314, "Mana", mana, mana_limit, (88, 156, 244))
    draw_labeled_bar(hud_panel.x + 10, hud_panel.y + 100, 314, "Stamina", stam, stam_limit, (96, 198, 118))

    active_item = get_active_hotbar_entry()
    active_item_label = get_item_label(active_item) if active_item else "EMPTY"
    action_line = small_font.render(
        f"Active: {active_item_label}   |   RMB place   |   LMB use",
        True,
        (242, 226, 190)
    )
    surf.blit(action_line, (hud_panel.x + 10, hud_panel.y + 126))

    mode_icon = get_world_icon_surface(current_world_icon, size=(36, 36))
    surf.blit(mode_icon, (hud_panel.right - 46, hud_panel.y + 6))


    # ================= CONTROLS UI
    if show_controls:
        controls_rect = pygame.Rect(20, 140, 420, 476)
        draw_knight_panel(
            controls_rect,
            border_color=(188, 150, 96),
            fill_color=(20, 14, 8),
            inner_color=(36, 24, 16),
            border_radius=14,
            draw_rivets=True
        )

        hotbar_key_labels = [get_hotbar_slot_key_label(i) for i in range(HOTBAR_TOTAL_SLOTS)]
        controls = [
            f"{get_keybind_name('toggle_controls')} - Toggle Controls",
            (
                f"{get_keybind_name('move_up')}/{get_keybind_name('move_left')}/"
                f"{get_keybind_name('move_down')}/{get_keybind_name('move_right')} - Move"
            ),
            f"{get_keybind_name('sprint')} - Sprint",
            f"{get_keybind_name('roll')} - Roll",
            f"{get_keybind_name('map')} - World Map",
            f"{'/'.join(hotbar_key_labels[:5])} - Hotbar 1-5",
            f"{'/'.join(hotbar_key_labels[5:])} - Hotbar 6-10",
            "LEFT CLICK - Attack/Use item",
            "RIGHT CLICK - Place item",
            f"{get_keybind_name('inventory')} - Inventory",
            "MIDDLE CLICK - Waypoint/Edit",
            f"{get_keybind_name('delete_waypoint')} - Delete Waypoint",
            f"{get_keybind_name('save_world')} - Save World",
            f"{get_keybind_name('pause')} - Pause"
        ]

        title = font.render(
            "CONTROLS",
            True,
            (248, 226, 160)
        )

        surf.blit(title,(150,155))

        for i, line in enumerate(controls):

            txt = small_font.render(
                line,
                True,
                (234, 218, 188)
            )

            surf.blit(
                txt,
                (40, 200 + i * 24)
            )

    if inventory_open:
        draw_inventory_overlay()

    if crafting_open:
        draw_crafting_overlay()

    draw_hotbar()

    if book_open:
        draw_book_overlay()

    if waypoint_editing:
        draw_waypoint_editor()

    if game_state == "pause":
        draw_pause_overlay()

    if game_state == "game_over":
        draw_game_over_overlay()

    # ================= FINAL DRAW
    if ENABLE_FOG_EFFECTS:
        darkness = get_night_darkness_strength()
        if darkness > 0:
            darkness_value = int(255 * (1.0 - 0.88 * darkness))
            dark_overlay = pygame.Surface((WIDTH, HEIGHT))
            dark_overlay.fill((darkness_value, darkness_value, darkness_value))

            t = pygame.time.get_ticks() * 0.0025
            for tx, ty in torch_positions:
                light_x = tx * TILE + ox + TILE // 2
                light_y = ty * TILE + oy + (
                    TILE // 2 - 20
                    if torch_mounts.get((tx, ty), "ground") == "wall"
                    else TILE // 2
                )
                radius = int(
                    145
                    + math.sin(t + tx * 0.73 + ty * 0.41) * 6
                    + math.sin(t * 0.6 + tx * 0.21) * 4
                )
                pygame.draw.circle(
                    dark_overlay,
                    (220, 220, 220),
                    (light_x, light_y),
                    max(110, radius)
                )

            surf.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

    if map_open:
        draw_world_map_overlay()

    if ENABLE_FOG_EFFECTS:
        draw_vignette_overlay()

    if impact_flash_alpha > 0:
        flash_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_overlay.fill(
            (
                impact_flash_color[0],
                impact_flash_color[1],
                impact_flash_color[2],
                clamp_channel(impact_flash_alpha)
            )
        )
        surf.blit(flash_overlay, (0, 0))

    screen.blit(
        pygame.transform.scale(surf, (SW, SH)),
        (0, 0)
    )

    pygame.display.update()


# The main loop is included above. If your editor cut it off because the file is very large,

# scroll further down in the document or collapse fewer code sections.