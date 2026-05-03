#!/usr/bin/env python3
"""
批次生成 Kirby 創意小短劇 / Batch Kirby Story Generator

不需要呼叫 Claude API。
每個「Episode」會生成一段連續故事，依模式輸出圖片輪播、混合圖影，或全影片片段，存入獨立子資料夾。
透過 kirby_themes.json（概念庫）+ story_arcs.json（敘事弧線）+ library.json（元件庫）
自動組合出有前後脈絡的 Kirby 視覺故事。

用法 / Usage:
  # 乾跑：預覽 5 個 episode 的 prompt（不打 API）
  python scripts/batch_kirby_generate.py --episodes 5 --dry-run

  # 生成 10 個純圖片故事（每個 3 張連續圖）
  python scripts/batch_kirby_generate.py --episodes 10 --type image

  # 輪播模式：每個 episode 自動隨機 3~5 張連續圖
  python scripts/batch_kirby_generate.py --episodes 10 --type carousel

  # 混合模式：1 張 anchor 圖 + 1 支濃縮影片
  python scripts/batch_kirby_generate.py --episodes 5 --type mixed

  # 全影片短劇（每幕各生 ref 圖再轉影片）
  python scripts/batch_kirby_generate.py --episodes 3 --type video

  # 指定叢集 + 趨勢關鍵字 + 指定 batch-id（可重現）
  python scripts/batch_kirby_generate.py --episodes 5 --cluster cosmos_drift
      --trend-keywords "母親節,溫情" --batch-id session-01

  # 4 幕故事（加入結局）
  python scripts/batch_kirby_generate.py --episodes 5 --beats 4

  # 斷點續跑（需指定相同 batch-id 找到舊目錄）
  python scripts/batch_kirby_generate.py --episodes 10 --batch-id session-01 --resume
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_PATH = PROJECT_ROOT / "template_components" / "library.json"
THEMES_PATH  = PROJECT_ROOT / "data" / "kirby_themes.json"
ARCS_PATH    = PROJECT_ROOT / "data" / "story_arcs.json"

KIRBY_CHARACTER = (
    "Kirby (the iconic pink round Nintendo character with stubby arms, "
    "rosy cheeks, and expressive blue eyes)"
)

# Beat 4 模板（若 --beats 4，在高潮後加一幕結局）
BEAT_4_TEMPLATE = {
    "index": 4,
    "label": "Aftermath",
    "narrative": (
        "Quiet resolution or unexpected twist ending. "
        "The dust settles. Kirby occupies the space differently than at the start. "
        "One final image that reframes the whole episode."
    ),
    "tone_guidance": "Tone: gentle irony, warmth, or a silent punchline. The story feels complete.",
    "shot_bias": ["cinematic_medium_wide", "overhead_tableau"],
    "motion_bias": ["reveal_then_hold"],
}

BEAT_5_TEMPLATE = {
    "index": 5,
    "label": "Echo Ending",
    "narrative": (
        "One final visual echo that proves the story changed the space. "
        "End with a tiny callback, emotional afterglow, or playful lingering detail."
    ),
    "tone_guidance": "Tone: complete, charming, and quietly memorable. End like the last card in a shareable carousel.",
    "shot_bias": ["overhead_tableau", "cinematic_medium_wide"],
    "motion_bias": ["reveal_then_hold"],
}


# ──────────────────────────────────────────────
# 載入資源
# ──────────────────────────────────────────────

def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_api_key() -> str:
    import os
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    config = PROJECT_ROOT / "config" / "gemini_config.json"
    if config.exists():
        data = json.loads(config.read_text(encoding="utf-8"))
        return data.get("api_key", "").strip()
    return ""


def _import_generators():
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        import generate_media_gemini as gmg
        return gmg.generate_image, gmg.generate_video
    except ImportError as e:
        raise SystemExit(f"無法匯入 generate_media_gemini: {e}")


# ──────────────────────────────────────────────
# 元件選擇
# ──────────────────────────────────────────────

def pick(rng: random.Random, pool: list) -> dict:
    return rng.choice(pool)


def pick_by_bias(rng: random.Random, pool: list, bias_ids: list[str]) -> dict:
    """優先從 bias_ids 裡挑，無法對應時 fallback 到全池。"""
    biased = [item for item in pool if item["id"] in bias_ids]
    return rng.choice(biased) if biased else rng.choice(pool)


def pick_by_id(pool: list[dict], item_id: str) -> dict | None:
    for item in pool:
        if item["id"] == item_id:
            return item
    return None


def pick_component_lock(
    rng: random.Random,
    pool: list[dict],
    *,
    preferred_ids: list[str] | None = None,
    forced_id: str | None = None,
) -> dict:
    if forced_id:
        forced = pick_by_id(pool, forced_id)
        if forced:
            return forced
    if preferred_ids:
        weighted_preferred = [pick_by_id(pool, item_id) for item_id in preferred_ids]
        weighted_preferred = [item for item in weighted_preferred if item is not None]
        if weighted_preferred:
            return rng.choice(weighted_preferred)
    return rng.choice(pool)


def get_seasonal_keyword(rng: random.Random, themes: dict) -> str:
    month = str(date.today().month)
    keywords: list[str] = themes.get("seasonal_keywords", {}).get(month, [])
    return rng.choice(keywords) if keywords else ""


CLUSTER_VISUAL_BIASES: dict[str, dict[str, list[str]]] = {
    "garden_buddies": {
        "scene": ["garden_secret_pocket", "wilderness_solitude", "dreamlike_storybook_land"],
        "color": ["muted_earth_organic", "sun_bleached_pastel", "tonal_harmony_serene"],
        "hook": ["quiet_emotional_reveal", "satisfying_completion", "mystery_object_or_action"],
        "rewatch_layer": ["background_easter_egg", "expression_micro_beat", "foreshadow_payoff_in_frame"],
        "narrative_structure": ["single_unbroken_moment", "setup_payoff_classic"],
    },
    "cozy_home": {
        "scene": ["domestic_emotional_corner", "studio_seamless_pop", "tiny_epic_workspace"],
        "color": ["warm_ember_glow", "tonal_harmony_serene", "sun_bleached_pastel"],
        "hook": ["quiet_emotional_reveal", "relatable_mirror", "satisfying_completion"],
        "rewatch_layer": ["expression_micro_beat", "background_easter_egg", "second_meaning_caption"],
        "narrative_structure": ["single_unbroken_moment", "question_then_answer", "setup_payoff_classic"],
    },
    "snack_happiness": {
        "scene": ["kitchen_choreography", "studio_seamless_pop", "marketplace_density"],
        "color": ["candy_saturated_pop", "warm_ember_glow", "high_contrast_primary"],
        "hook": ["satisfying_completion", "unexpected_role", "pattern_break"],
        "rewatch_layer": ["background_easter_egg", "foreshadow_payoff_in_frame", "expression_micro_beat"],
        "narrative_structure": ["setup_payoff_classic", "before_during_after", "question_then_answer"],
    },
    "tiny_errands": {
        "scene": ["tiny_epic_workspace", "cluttered_workshop", "marketplace_density", "transit_in_between"],
        "color": ["sun_bleached_pastel", "muted_earth_organic", "warm_ember_glow"],
        "hook": ["promise_of_payoff", "before_after_implied", "satisfying_completion"],
        "rewatch_layer": ["foreshadow_payoff_in_frame", "background_easter_egg", "expression_micro_beat"],
        "narrative_structure": ["before_during_after", "setup_payoff_classic", "list_format_count"],
    },
    "weather_softness": {
        "scene": ["weather_extreme_moment", "rooftop_horizon", "wilderness_solitude", "underwater_silence"],
        "color": ["cool_subzero_palette", "tonal_harmony_serene", "sun_bleached_pastel"],
        "hook": ["quiet_emotional_reveal", "mystery_object_or_action", "relatable_mirror"],
        "rewatch_layer": ["unusual_perspective_invite", "expression_micro_beat", "background_easter_egg"],
        "narrative_structure": ["single_unbroken_moment", "question_then_answer", "setup_payoff_classic"],
    },
    "animal_friends": {
        "scene": ["wilderness_solitude", "garden_secret_pocket", "domestic_emotional_corner"],
        "color": ["muted_earth_organic", "tonal_harmony_serene", "warm_ember_glow"],
        "hook": ["quiet_emotional_reveal", "promise_of_payoff", "relatable_mirror"],
        "rewatch_layer": ["expression_micro_beat", "background_easter_egg", "foreshadow_payoff_in_frame"],
        "narrative_structure": ["setup_payoff_classic", "single_unbroken_moment", "question_then_answer"],
    },
    "sleepy_healing": {
        "scene": ["domestic_emotional_corner", "garden_secret_pocket", "underwater_silence", "dreamlike_storybook_land"],
        "color": ["tonal_harmony_serene", "warm_ember_glow", "cool_subzero_palette"],
        "hook": ["quiet_emotional_reveal", "relatable_mirror", "before_after_implied"],
        "rewatch_layer": ["expression_micro_beat", "background_easter_egg", "second_meaning_caption"],
        "narrative_structure": ["single_unbroken_moment", "loop_returns_to_start", "setup_payoff_classic"],
    },
    "tiny_celebrations": {
        "scene": ["studio_seamless_pop", "rooftop_horizon", "marketplace_density", "retro_arcade_glow"],
        "color": ["candy_saturated_pop", "high_contrast_primary", "gradient_synthwave"],
        "hook": ["pattern_break", "satisfying_completion", "promise_of_payoff"],
        "rewatch_layer": ["background_easter_egg", "subliminal_recurring_motif", "expression_micro_beat"],
        "narrative_structure": ["setup_payoff_classic", "before_during_after", "list_format_count"],
    },
    "seasonal_cute": {
        "scene": ["garden_secret_pocket", "weather_extreme_moment", "wilderness_solitude", "domestic_emotional_corner"],
        "color": ["sun_bleached_pastel", "muted_earth_organic", "warm_ember_glow", "cool_subzero_palette"],
        "hook": ["quiet_emotional_reveal", "before_after_implied", "mystery_object_or_action"],
        "rewatch_layer": ["background_easter_egg", "foreshadow_payoff_in_frame", "expression_micro_beat"],
        "narrative_structure": ["before_during_after", "setup_payoff_classic", "single_unbroken_moment"],
    },
    "friendly_pairs": {
        "scene": ["domestic_emotional_corner", "transit_in_between", "rooftop_horizon", "garden_secret_pocket"],
        "color": ["warm_ember_glow", "tonal_harmony_serene", "sun_bleached_pastel"],
        "hook": ["relatable_mirror", "quiet_emotional_reveal", "promise_of_payoff"],
        "rewatch_layer": ["expression_micro_beat", "second_meaning_caption", "background_easter_egg"],
        "narrative_structure": ["setup_payoff_classic", "single_unbroken_moment", "question_then_answer"],
    },
    "simple_magic": {
        "scene": ["dreamlike_storybook_land", "underwater_silence", "garden_secret_pocket", "liminal_corridor"],
        "color": ["gradient_synthwave", "tonal_harmony_serene", "cool_subzero_palette"],
        "hook": ["mystery_object_or_action", "quiet_emotional_reveal", "pattern_break"],
        "rewatch_layer": ["subliminal_recurring_motif", "unusual_perspective_invite", "foreshadow_payoff_in_frame"],
        "narrative_structure": ["question_then_answer", "single_unbroken_moment", "subverted_expectation"],
    },
    "urban_mini_adventures": {
        "scene": ["neon_night_market", "transit_in_between", "rooftop_horizon", "marketplace_density"],
        "color": ["neon_against_concrete", "gradient_synthwave", "teal_orange_blockbuster"],
        "hook": ["pattern_break", "mystery_object_or_action", "promise_of_payoff"],
        "rewatch_layer": ["background_easter_egg", "second_meaning_caption", "unusual_perspective_invite"],
        "narrative_structure": ["cold_open_drop_in", "setup_payoff_classic", "question_then_answer"],
    },
    "festival_wonder": {
        "scene": ["neon_night_market", "studio_seamless_pop", "marketplace_density", "rooftop_horizon"],
        "color": ["candy_saturated_pop", "gradient_synthwave", "high_contrast_primary"],
        "hook": ["pattern_break", "promise_of_payoff", "satisfying_completion"],
        "rewatch_layer": ["background_easter_egg", "subliminal_recurring_motif", "expression_micro_beat"],
        "narrative_structure": ["setup_payoff_classic", "list_format_count", "before_during_after"],
    },
    "dream_quests": {
        "scene": ["dreamlike_storybook_land", "wilderness_solitude", "underwater_silence", "abandoned_grandeur"],
        "color": ["gradient_synthwave", "cool_subzero_palette", "teal_orange_blockbuster"],
        "hook": ["promise_of_payoff", "mystery_object_or_action", "unexpected_role"],
        "rewatch_layer": ["foreshadow_payoff_in_frame", "unusual_perspective_invite", "subliminal_recurring_motif"],
        "narrative_structure": ["before_during_after", "question_then_answer", "setup_payoff_classic"],
    },
    "tiny_professions": {
        "scene": ["tiny_epic_workspace", "cluttered_workshop", "kitchen_choreography", "tech_clean_lab"],
        "color": ["high_contrast_primary", "warm_ember_glow", "duo_tone_disciplined"],
        "hook": ["unexpected_role", "promise_of_payoff", "pattern_break"],
        "rewatch_layer": ["background_easter_egg", "foreshadow_payoff_in_frame", "expression_micro_beat"],
        "narrative_structure": ["before_during_after", "setup_payoff_classic", "cold_open_drop_in"],
    },
    "retro_playroom": {
        "scene": ["retro_arcade_glow", "studio_seamless_pop", "liminal_corridor", "tiny_epic_workspace"],
        "color": ["gradient_synthwave", "high_contrast_primary", "neon_against_concrete"],
        "hook": ["pattern_break", "wtf_first_frame", "unexpected_role"],
        "rewatch_layer": ["subliminal_recurring_motif", "background_easter_egg", "second_meaning_caption"],
        "narrative_structure": ["subverted_expectation", "cold_open_drop_in", "loop_returns_to_start"],
    },
}


CLUSTER_PRESET_BIASES: dict[str, list[str]] = {
    "tiny_errands": ["tiny_office_warmth"],
    "cozy_home": ["tiny_office_warmth"],
    "urban_mini_adventures": ["neon_solitude_loop"],
    "festival_wonder": ["absurd_pattern_break", "neon_solitude_loop"],
    "retro_playroom": ["absurd_pattern_break", "liminal_uncanny_dwell"],
    "dream_quests": ["stadium_grit_triumph", "liminal_uncanny_dwell"],
}


NOVELTY_SPARKS: list[dict[str, str]] = [
    {
        "id": "genre_flip_documentary",
        "prompt": (
            "Novelty spark: treat the cute premise like a tiny prestige documentary scene, "
            "with one observational real-world detail that makes the fantasy feel freshly discovered."
        ),
    },
    {
        "id": "unexpected_public_scale",
        "prompt": (
            "Novelty spark: move the emotional beat into a public-scale environment where the small action "
            "quietly affects the whole space, not just the character."
        ),
    },
    {
        "id": "object_pov",
        "prompt": (
            "Novelty spark: frame the story as if an important prop is the silent witness, "
            "so the camera angle and composition feel less predictable."
        ),
    },
    {
        "id": "weather_interrupt",
        "prompt": (
            "Novelty spark: add a sudden gentle weather interruption that changes the plan and creates "
            "a new visual payoff instead of merely decorating the scene."
        ),
    },
    {
        "id": "micro_job_absurdity",
        "prompt": (
            "Novelty spark: give the character a tiny overly serious job with charmingly ridiculous stakes, "
            "then make the final image prove the job mattered."
        ),
    },
    {
        "id": "material_transformation",
        "prompt": (
            "Novelty spark: let one material in the scene transform visually during the beat "
            "such as paper, steam, light, crumbs, leaves, or reflection becoming the payoff."
        ),
    },
    {
        "id": "wrong_place_right_mood",
        "prompt": (
            "Novelty spark: place the soft emotion in a location that normally feels too large, busy, "
            "technical, or cinematic, then make the contrast feel intentional."
        ),
    },
    {
        "id": "second_character_misdirect",
        "prompt": (
            "Novelty spark: include one secondary presence that appears to be the gag at first, "
            "but becomes the emotional support or visual reveal by the end."
        ),
    },
    {
        "id": "miniature_epic_quest",
        "prompt": (
            "Novelty spark: turn the simple action into a miniature epic quest with one obstacle, "
            "one clever workaround, and one clean final emblem of success."
        ),
    },
    {
        "id": "surreal_rule",
        "prompt": (
            "Novelty spark: add one clear surreal rule to the world, then keep everything else grounded "
            "so the image feels surprising rather than random."
        ),
    },
]


def pick_novelty_spark(rng: random.Random, diversity_level: str) -> dict[str, str] | None:
    if diversity_level == "low":
        return None
    if diversity_level == "normal" and rng.random() >= 0.45:
        return None
    return rng.choice(NOVELTY_SPARKS)


def infer_concept_visual_biases(concept: dict) -> dict[str, list[str]]:
    text = " ".join([
        concept.get("id", ""),
        concept.get("en", ""),
        concept.get("zh", ""),
        concept.get("visual_core", ""),
        concept.get("act2_twist", ""),
    ]).lower()

    scene_bias: list[str] = []
    color_bias: list[str] = []
    hook_bias: list[str] = []

    def add_unique(bucket: list[str], values: list[str]) -> None:
        for value in values:
            if value not in bucket:
                bucket.append(value)

    if any(keyword in text for keyword in ["store", "neon", "night market", "festival", "parade"]):
        add_unique(scene_bias, ["neon_night_market", "marketplace_density"])
        add_unique(color_bias, ["gradient_synthwave", "neon_against_concrete", "candy_saturated_pop"])
        add_unique(hook_bias, ["pattern_break", "promise_of_payoff"])
    if any(keyword in text for keyword in ["train", "transit", "subway", "station", "car"]):
        add_unique(scene_bias, ["transit_in_between"])
        add_unique(color_bias, ["cool_subzero_palette", "teal_orange_blockbuster"])
    if any(keyword in text for keyword in ["rooftop", "bridge", "skyline"]):
        add_unique(scene_bias, ["rooftop_horizon"])
        add_unique(hook_bias, ["promise_of_payoff"])
    if any(keyword in text for keyword in ["rain", "snow", "mist", "wind", "cloud", "firework"]):
        add_unique(scene_bias, ["weather_extreme_moment", "wilderness_solitude"])
        add_unique(color_bias, ["cool_subzero_palette", "sun_bleached_pastel"])
    if any(keyword in text for keyword in ["workshop", "repair", "helmet", "tool", "lamp"]):
        add_unique(scene_bias, ["cluttered_workshop", "tiny_epic_workspace"])
        add_unique(color_bias, ["warm_ember_glow", "duo_tone_disciplined"])
    if any(keyword in text for keyword in ["cake", "cookie", "pastry", "chef", "kitchen", "soup", "snack"]):
        add_unique(scene_bias, ["kitchen_choreography", "studio_seamless_pop"])
        add_unique(color_bias, ["candy_saturated_pop", "warm_ember_glow"])
        add_unique(hook_bias, ["satisfying_completion"])
    if any(keyword in text for keyword in ["library", "book", "desk", "pencil", "reading"]):
        add_unique(scene_bias, ["tiny_epic_workspace", "domestic_emotional_corner"])
        add_unique(color_bias, ["sun_bleached_pastel", "warm_ember_glow"])
    if any(keyword in text for keyword in ["device", "wire", "lab", "tech"]):
        add_unique(scene_bias, ["tech_clean_lab"])
        add_unique(color_bias, ["duo_tone_disciplined", "cool_subzero_palette"])
    if any(keyword in text for keyword in ["garden", "flower", "plant", "bouquet", "leaf"]):
        add_unique(scene_bias, ["garden_secret_pocket", "wilderness_solitude"])
        add_unique(color_bias, ["muted_earth_organic", "sun_bleached_pastel"])
    if any(keyword in text for keyword in ["dream", "tower", "forest", "map", "moon", "star", "water"]):
        add_unique(scene_bias, ["dreamlike_storybook_land", "underwater_silence"])
        add_unique(color_bias, ["gradient_synthwave", "tonal_harmony_serene"])
        add_unique(hook_bias, ["mystery_object_or_action"])
    if any(keyword in text for keyword in ["arcade", "television", "pinball", "claw machine", "toy", "sticker"]):
        add_unique(scene_bias, ["retro_arcade_glow", "studio_seamless_pop"])
        add_unique(color_bias, ["high_contrast_primary", "gradient_synthwave"])
        add_unique(hook_bias, ["pattern_break", "unexpected_role"])
    if any(keyword in text for keyword in ["sleep", "nap", "blanket", "pillow", "dozing"]):
        add_unique(scene_bias, ["domestic_emotional_corner", "garden_secret_pocket"])
        add_unique(color_bias, ["tonal_harmony_serene", "warm_ember_glow"])

    return {
        "scene": scene_bias,
        "color": color_bias,
        "hook": hook_bias,
    }


def pick_episode_recipe(
    rng: random.Random,
    library: dict,
    cluster: dict,
    concept: dict,
    diversity_level: str = "high",
) -> dict:
    comps = library["components"]
    cluster_bias = CLUSTER_VISUAL_BIASES.get(cluster["id"], {})
    concept_bias = infer_concept_visual_biases(concept)
    preset = None

    preset_ids = CLUSTER_PRESET_BIASES.get(cluster["id"], [])
    preset_chance = {
        "low": 0.55,
        "normal": 0.35,
        "high": 0.22,
        "wild": 0.08,
    }.get(diversity_level, 0.22)
    if preset_ids and rng.random() < preset_chance:
        candidates = [p for p in library.get("preset_combos", []) if p["id"] in preset_ids]
        if candidates:
            preset = rng.choice(candidates)

    preset_ingredients = preset["ingredients"] if preset else {}
    novelty = pick_novelty_spark(rng, diversity_level)

    return {
        "preset": preset,
        "novelty": novelty,
        "scene": pick_component_lock(
            rng, comps["scene"],
            preferred_ids=(concept_bias.get("scene", []) * 3) + cluster_bias.get("scene", []),
            forced_id=preset_ingredients.get("scene"),
        ),
        "style": pick_component_lock(
            rng, comps["style"],
            forced_id=preset_ingredients.get("style"),
        ),
        "lighting": pick_component_lock(
            rng, comps["lighting"],
            forced_id=preset_ingredients.get("lighting"),
        ),
        "color": pick_component_lock(
            rng, comps["color"],
            preferred_ids=(concept_bias.get("color", []) * 3) + cluster_bias.get("color", []),
            forced_id=preset_ingredients.get("color"),
        ),
        "hook": pick_component_lock(
            rng, comps["hook"],
            preferred_ids=(concept_bias.get("hook", []) * 3) + cluster_bias.get("hook", []),
            forced_id=preset_ingredients.get("hook"),
        ),
        "emotion": pick_component_lock(
            rng, comps["emotion"],
            forced_id=preset_ingredients.get("emotion"),
        ),
        "rewatch_layer": pick_component_lock(
            rng, comps["rewatch_layer"],
            preferred_ids=cluster_bias.get("rewatch_layer"),
            forced_id=preset_ingredients.get("rewatch_layer"),
        ),
        "narrative_structure": pick_component_lock(
            rng, comps["narrative_structure"],
            preferred_ids=cluster_bias.get("narrative_structure"),
            forced_id=preset_ingredients.get("narrative_structure"),
        ),
        "sound_design_cue": pick_component_lock(
            rng, comps["sound_design_cue"],
            forced_id=preset_ingredients.get("sound_design_cue"),
        ),
        "text_overlay_strategy": pick_component_lock(
            rng, comps["text_overlay_strategy"],
            forced_id=preset_ingredients.get("text_overlay_strategy"),
        ),
        "subject_archetype": pick_component_lock(
            rng, comps["subject_archetype"],
            forced_id=preset_ingredients.get("subject_archetype"),
        ),
    }


# ──────────────────────────────────────────────
# 概念序列產生（打亂後循環，確保同批次不重複）
# ──────────────────────────────────────────────

def build_concept_queue(
    rng: random.Random,
    themes: dict,
    cluster_id: str | None,
) -> list[tuple[dict, dict]]:
    """
    回傳 [(cluster, concept), ...] 的多樣化列表。
    未指定 cluster 時改用跨叢集輪抽，避免同批次連續落在同一種題材。
    """
    clusters = themes["clusters"]
    if cluster_id:
        target = [c for c in clusters if c["id"] == cluster_id]
        if not target:
            raise SystemExit(f"找不到叢集: {cluster_id}")
    else:
        target = list(clusters)

    grouped: dict[str, list[tuple[dict, dict]]] = {}
    for cl in target:
        pairs = [(cl, concept) for concept in cl["concepts"]]
        rng.shuffle(pairs)
        grouped[cl["id"]] = pairs

    queue: list[tuple[dict, dict]] = []
    cluster_ids = list(grouped)
    last_cluster_id: str | None = None

    while any(grouped.values()):
        available = [cid for cid in cluster_ids if grouped[cid]]
        if len(available) > 1 and last_cluster_id in available:
            available.remove(last_cluster_id)
        cid = rng.choice(available)
        queue.append(grouped[cid].pop(0))
        last_cluster_id = cid

    return queue


class ConceptCycler:
    """無限循環概念佇列，每輪耗盡後重新打亂。"""
    def __init__(self, rng: random.Random, pool: list[tuple[dict, dict]]) -> None:
        self._rng = rng
        self._pool = pool
        self._queue: list[tuple[dict, dict]] = []
        self._last_cluster_id: str | None = None

    def next(self) -> tuple[dict, dict]:
        if not self._queue:
            shuffled = list(self._pool)
            self._rng.shuffle(shuffled)
            self._queue = shuffled
        if len(self._queue) > 1 and self._last_cluster_id:
            for idx, (cluster, _) in enumerate(self._queue):
                if cluster["id"] != self._last_cluster_id:
                    self._queue.insert(0, self._queue.pop(idx))
                    break
        cluster, concept = self._queue.pop(0)
        self._last_cluster_id = cluster["id"]
        return cluster, concept


# ──────────────────────────────────────────────
# Prompt 組裝
# ──────────────────────────────────────────────

def build_beat_prompt(
    beat_def: dict,
    beat_num: int,
    total_beats: int,
    concept: dict,
    cluster: dict,
    arc: dict,
    episode_recipe: dict,
    rng: random.Random,
    library: dict,
    themes: dict,
    trend_keywords: list[str],
    is_video: bool,
) -> str:
    comps = library["components"]
    scene_lock = episode_recipe["scene"]
    style_lock = episode_recipe["style"]
    lighting_lock = episode_recipe["lighting"]
    color_lock = episode_recipe["color"]
    hook_lock = episode_recipe["hook"]
    emotion_lock = episode_recipe["emotion"]
    rewatch_lock = episode_recipe["rewatch_layer"]
    narrative_lock = episode_recipe["narrative_structure"]
    sound_lock = episode_recipe["sound_design_cue"]
    text_overlay_lock = episode_recipe["text_overlay_strategy"]
    subject_archetype_lock = episode_recipe["subject_archetype"]
    preset = episode_recipe.get("preset")
    novelty = episode_recipe.get("novelty")

    # Shot：依 beat 位置偏好不同角度
    shot = pick_by_bias(rng, comps["shot"], beat_def.get("shot_bias", []))

    # Hook：只有 beat 1 用 hook 破題，後續 beat 用敘事銜接代替
    hook_text = ""
    if beat_num == 1:
        hook_text = hook_lock["prompt"]

    # 決定視覺焦點
    # Beat 1 使用英文 en 欄位（visual_core 是中文設計筆記，會導致 Gemini 圖片 API 不生圖）
    if beat_num == 1:
        scene_focus = concept["en"]
        continuity = ""
    elif beat_num == 2:
        scene_focus = concept.get("act2_twist", concept["visual_core"])
        continuity = (
            f"This is beat {beat_num} of {total_beats} in a continuous story. "
            f"Continuing directly from: {concept['en']}. "
        )
    else:
        scene_focus = beat_def["narrative"]
        continuity = (
            f"This is beat {beat_num} of {total_beats} — the climax/resolution. "
            f"Continuing from the arc of: {concept['en']}. "
        )

    # Motion（僅影片）
    motion_text = ""
    if is_video:
        motion = pick_by_bias(rng, comps["motion"], beat_def.get("motion_bias", []))
        motion_text = motion["prompt"]

    # 趨勢/季節
    seasonal = get_seasonal_keyword(rng, themes)
    trend_injections = []
    if trend_keywords:
        trend_injections.append(rng.choice(trend_keywords))
    if seasonal:
        trend_injections.append(seasonal)
    trend_text = f"Thematic note: {', '.join(trend_injections)}." if trend_injections else ""

    # 組合
    parts = [p for p in [
        hook_text,
        f"Episode arc: {arc['description_en']}.",
        f"Narrative rhythm: {narrative_lock['prompt']}",
        continuity,
        f"Scene concept: {concept['en']}.",
        f"Cluster mood: {cluster['label_en']}.",
        f"Character behavior note: {cluster.get('kirby_trait', '')}",
        f"Visual focus this beat: {scene_focus}.",
        f"Core image logic: {concept.get('visual_core', concept['en'])}",
        beat_def["tone_guidance"],
        f"Main subject: {KIRBY_CHARACTER}.",
        subject_archetype_lock["prompt"],
        scene_lock["prompt"],
        shot["prompt"],
        lighting_lock["prompt"],
        color_lock["prompt"],
        emotion_lock["prompt"],
        style_lock["prompt"],
        rewatch_lock["prompt"],
        novelty["prompt"] if novelty else "",
        text_overlay_lock["prompt"],
        sound_lock["prompt"] if is_video else "",
        motion_text,
        f"Optional preset flavor: {preset['id']}." if preset else "",
        "Keep Kirby's round silhouette expressive and readable throughout the episode.",
        trend_text,
    ] if p]

    return " ".join(parts)


def build_carousel_image_prompt(
    *,
    beat_def: dict,
    beat_num: int,
    total_beats: int,
    concept: dict,
    cluster: dict,
    arc: dict,
    episode_recipe: dict,
    rng: random.Random,
    library: dict,
    themes: dict,
    trend_keywords: list[str],
) -> str:
    base_prompt = build_beat_prompt(
        beat_def=beat_def,
        beat_num=beat_num,
        total_beats=total_beats,
        concept=concept,
        cluster=cluster,
        arc=arc,
        episode_recipe=episode_recipe,
        rng=rng,
        library=library,
        themes=themes,
        trend_keywords=trend_keywords,
        is_video=False,
    )

    carousel_note = (
        f" This is panel {beat_num} of a {total_beats}-panel carousel story."
        " Keep the same character design, same art direction, same lighting family, and the same scene logic across all panels."
        " Only advance the story one clear step from the previous panel."
        " Preserve recognizable props, camera logic, and emotional continuity so the set reads as one connected sequence."
    )
    if beat_num == 1:
        carousel_note += " Panel 1 must establish the setting cleanly so later panels can build on it."
    elif beat_num == total_beats:
        carousel_note += " Final panel must feel like a payoff, not a reset."
    return f"{base_prompt}{carousel_note}"


def build_mixed_video_prompt(
    beats: list[dict],
    concept: dict,
    cluster: dict,
    arc: dict,
    episode_recipe: dict,
    rng: random.Random,
    library: dict,
    themes: dict,
    trend_keywords: list[str],
    gag_template: dict,
) -> str:
    """
    mixed 模式只輸出 1 張圖 + 1 支影片。
    影片會承接 beat 1 的 anchor 圖，並把後段 beats 濃縮成一支更完整的短片，
    避免先多生一張單純拿來當 reference 的圖片。
    """
    primary_beat_num = 2 if len(beats) >= 2 else 1
    primary_beat = beats[primary_beat_num - 1]
    prompt = build_beat_prompt(
        beat_def=primary_beat,
        beat_num=primary_beat_num,
        total_beats=len(beats),
        concept=concept,
        cluster=cluster,
        arc=arc,
        episode_recipe=episode_recipe,
        rng=rng,
        library=library,
        themes=themes,
        trend_keywords=trend_keywords,
        is_video=True,
    )

    later_steps = [beat["narrative"] for beat in beats[1:]]
    later_summary = " Then progress through: " + " ".join(later_steps) if later_steps else ""
    ending_note = (
        " Keep this as one concise continuous shot from the opening reference image."
        " Build visible progression quickly, then land on the most satisfying final frame."
        " Avoid padded motion and do not stretch the action longer than the idea can support."
    )
    pacing_note = f" Gag pacing template: {gag_template['instruction']}"
    return f"{prompt}{later_summary}{ending_note}{pacing_note}"


def pick_gag_template(
    *,
    args: argparse.Namespace,
    concept: dict,
    cluster: dict,
    arc: dict,
    beat_def: dict,
    beat_num: int,
    total_beats: int,
) -> dict:
    """
    先決定 gag 節奏模板，再由模板帶出秒數與 prompt 節奏。
    避免只靠 cluster 粗略判斷，導致簡單動作被錯拉成 8 秒。
    """
    gag_templates = {
        "micro_reaction": {
            "name": "micro_reaction",
            "duration": 4,
            "instruction": (
                "0-1s setup pose, 1-3s one clear emotional change, 3-4s short hold on the payoff."
            ),
        },
        "reveal_then_hold": {
            "name": "reveal_then_hold",
            "duration": 4,
            "instruction": (
                "0-1.5s establish, 1.5-3s tiny reveal, 3-4s hold on the cute payoff without extra business."
            ),
        },
        "soft_progression": {
            "name": "soft_progression",
            "duration": 6,
            "instruction": (
                "0-2s establish, 2-4.5s gentle progression, 4.5-6s satisfying settle into the final pose."
            ),
        },
        "escalate_and_land": {
            "name": "escalate_and_land",
            "duration": 6,
            "instruction": (
                "0-2s setup, 2-4s visible escalation, 4-6s clean payoff and brief landing beat."
            ),
        },
        "mini_story_arc": {
            "name": "mini_story_arc",
            "duration": 8,
            "instruction": (
                "0-2s establish, 2-5s progression through multiple readable actions, 5-8s payoff and aftermath."
            ),
        },
    }

    concept_text = " ".join(
        [
            concept.get("zh", ""),
            concept.get("en", ""),
            concept.get("act2_twist", ""),
            beat_def.get("label", ""),
            beat_def.get("narrative", ""),
            arc.get("label_en", ""),
        ]
    ).lower()

    short_action_cues = (
        "card", "heart", "hug", "hugs", "gratitude", "smile", "confetti",
        "cookie", "flower", "pillow", "blanket", "rest", "nap", "calm",
        "quiet", "together", "warm", "plush", "steam", "bubble", "hat",
    )
    reveal_cues = (
        "reveal", "opens slightly", "flickers softly", "lands neatly",
        "drifts up slowly", "tiny reveal", "shared gesture",
    )
    multi_step_cues = (
        "collecting", "deliver", "carrying", "lining up", "sweep", "mission",
        "watering", "arranging", "doodling", "puzzle", "rainbow line",
    )

    if args.type == "mixed":
        if total_beats >= 4 and cluster["id"] in {"tiny_errands", "weather_softness"}:
            return gag_templates["mini_story_arc"]
        if any(cue in concept_text for cue in short_action_cues):
            if any(cue in concept_text for cue in reveal_cues):
                return gag_templates["reveal_then_hold"]
            return gag_templates["micro_reaction"]
        if any(cue in concept_text for cue in multi_step_cues):
            return gag_templates["escalate_and_land"]
        if arc.get("label_en") in {"Peaceful Rest", "Cozy Companionship"}:
            return gag_templates["micro_reaction"]
        return gag_templates["soft_progression"]

    label_text = f"{beat_def.get('label', '')} {beat_def.get('narrative', '')}".lower()
    short_cues = (
        "simple", "calm", "quiet", "rest", "resting", "together", "warm",
        "settled", "full calm", "comforting", "aftermath",
    )
    medium_cues = (
        "change", "reveal", "gesture", "deeper", "enchantment",
        "discover", "shared", "little", "tiny",
    )

    if total_beats >= 4 and beat_num in {2, 3}:
        return gag_templates["soft_progression"]
    if any(cue in label_text for cue in short_cues):
        return gag_templates["micro_reaction"]
    if any(cue in label_text for cue in medium_cues):
        return gag_templates["soft_progression"]
    return gag_templates["soft_progression"] if beat_num < total_beats else gag_templates["micro_reaction"]


def resolve_episode_beats(
    *,
    args: argparse.Namespace,
    rng: random.Random,
    arc: dict,
) -> list[dict]:
    beats = list(arc["beats"])

    if args.beats is None:
        target_beats = rng.randint(3, 5) if args.type == "carousel" else 3
    else:
        target_beats = args.beats

    if target_beats >= 4:
        beats.append(BEAT_4_TEMPLATE)
    if target_beats >= 5:
        beats.append(BEAT_5_TEMPLATE)
    return beats


def resolve_arc_for_concept(
    rng: random.Random,
    concept: dict,
    arcs: dict,
) -> tuple[str, dict]:
    arc_candidates = concept.get("arc_candidates") or []
    if arc_candidates:
        valid_ids = [arc_id for arc_id in arc_candidates if arc_id in arcs]
        if valid_ids:
            chosen_id = rng.choice(valid_ids)
            return chosen_id, arcs[chosen_id]

    arc_type = concept.get("arc_type", "comedy_escalation")
    return arc_type, arcs.get(arc_type, list(arcs.values())[0])


# ──────────────────────────────────────────────
# Episode 生成
# ──────────────────────────────────────────────

def generate_episode(
    ep_num: int,
    concept: dict,
    cluster: dict,
    arc: dict,
    beats: list[dict],
    rng: random.Random,
    library: dict,
    themes: dict,
    out_dir: Path,
    api_key: str,
    gen_img,
    gen_vid,
    args: argparse.Namespace,
    dry_run: bool = False,
) -> list[dict]:
    """
    生成一個 episode（3-5 beat）。
    回傳 beat-level 結果清單。
    """
    ep_dir = out_dir / f"ep{ep_num:02d}"
    ep_dir.mkdir(parents=True, exist_ok=True)

    total_beats = len(beats)
    episode_recipe = pick_episode_recipe(
        rng,
        library,
        cluster,
        concept,
        diversity_level=args.diversity_level,
    )

    results: list[dict] = []
    anchor_image: Path | None = None  # beat 1 圖，用於影片的 character anchor
    prev_image:   Path | None = None  # 前一幕圖，用於影片的 reference image

    print(f"\n  📖 Story: {concept['zh']}")
    print(f"     Arc: {arc['label_zh']}（{arc['label_en']}）")
    print(
        "     Visual Recipe: "
        f"{episode_recipe['scene']['label_en']} | "
        f"{episode_recipe['style']['label_en']} | "
        f"{episode_recipe['lighting']['label_en']} | "
        f"{episode_recipe['color']['label_en']}"
    )
    if episode_recipe.get("preset"):
        print(f"     Preset Combo: {episode_recipe['preset']['id']}")
    if episode_recipe.get("novelty"):
        print(f"     Novelty Spark: {episode_recipe['novelty']['id']}")

    media_plan: list[dict] = []
    if args.type in {"image", "carousel"}:
        media_plan = [
            {"output_index": beat_num, "source_beat": beat_num, "is_video": False}
            for beat_num in range(1, total_beats + 1)
        ]
    elif args.type == "video":
        media_plan = [
            {"output_index": beat_num, "source_beat": beat_num, "is_video": True}
            for beat_num in range(1, total_beats + 1)
        ]
    else:
        media_plan = [
            {"output_index": 1, "source_beat": 1, "is_video": False},
            {"output_index": 2, "source_beat": 2, "is_video": True, "is_condensed_mixed_video": True},
        ]

    for plan_idx, item in enumerate(media_plan, 1):
        beat_num = item["source_beat"]
        beat_def = beats[beat_num - 1]
        is_video = item["is_video"]
        gag_template = pick_gag_template(
            args=args,
            concept=concept,
            cluster=cluster,
            arc=arc,
            beat_def=beat_def,
            beat_num=beat_num,
            total_beats=total_beats,
        )

        if item.get("is_condensed_mixed_video"):
            prompt = build_mixed_video_prompt(
                beats=beats,
                concept=concept,
                cluster=cluster,
                arc=arc,
                episode_recipe=episode_recipe,
                rng=rng,
                library=library,
                themes=themes,
                trend_keywords=args.trend_keywords_list,
                gag_template=gag_template,
            )
        elif args.type == "carousel":
            prompt = build_carousel_image_prompt(
                beat_def=beat_def,
                beat_num=beat_num,
                total_beats=total_beats,
                concept=concept,
                cluster=cluster,
                arc=arc,
                episode_recipe=episode_recipe,
                rng=rng,
                library=library,
                themes=themes,
                trend_keywords=args.trend_keywords_list,
            )
        else:
            prompt = build_beat_prompt(
                beat_def=beat_def,
                beat_num=beat_num,
                total_beats=total_beats,
                concept=concept,
                cluster=cluster,
                arc=arc,
                episode_recipe=episode_recipe,
                rng=rng,
                library=library,
                themes=themes,
                trend_keywords=args.trend_keywords_list,
                is_video=is_video,
            )

        media_label = "🎬 VIDEO" if is_video else "🖼️  IMAGE"
        beat_desc = f"Beat {beat_num}/{total_beats}"
        if item.get("is_condensed_mixed_video"):
            beat_desc = f"Mixed Video {plan_idx}/{len(media_plan)}"
        print(f"\n  {beat_desc} [{beat_def['label']}] {media_label}")
        if is_video:
            print(f"  Gag template: {gag_template['name']} | Duration: {gag_template['duration']}s")
        print(f"  Prompt: {prompt[:110]}...")

        if dry_run:
            ext = ".mp4" if is_video else ".png"
            print(f"  → (dry-run) {ep_dir.relative_to(PROJECT_ROOT)}/{item['output_index']:02d}{ext}")
            results.append({"beat": beat_num, "type": "video" if is_video else "image", "success": True, "dry_run": True})
            continue

        # ── 真實生成 ──
        if is_video:
            duration_seconds = gag_template["duration"]
            # Step 1: 若沒有 prev_image，先生 ref 圖
            if prev_image is None or not prev_image.exists():
                ref_path = ep_dir / f"{item['output_index']:02d}_ref.png"
                ref_prompt = build_beat_prompt(
                    beat_def=beat_def, beat_num=beat_num, total_beats=total_beats,
                    concept=concept, cluster=cluster, arc=arc,
                    episode_recipe=episode_recipe,
                    rng=rng, library=library, themes=themes,
                    trend_keywords=args.trend_keywords_list, is_video=False,
                )
                print(f"    📸 先生成 reference 圖 → {ref_path.name}")
                ref_ok = gen_img(ref_prompt, ref_path, api_key)
                if not ref_ok:
                    print("    ⚠️  reference 圖失敗，跳過此影片幕")
                    results.append({"beat": beat_num, "type": "video", "success": False, "reason": "ref_failed"})
                    if args.delay > 0:
                        time.sleep(args.delay)
                    continue
                prev_image = ref_path
                if anchor_image is None:
                    anchor_image = ref_path

            # Step 2: 圖轉影片
            video_path = ep_dir / f"{item['output_index']:02d}.mp4"
            print(f"    🎬 生成影片 → {video_path.name}（{duration_seconds}s）")
            ok = gen_vid(
                prompt=prompt,
                output_path=video_path,
                api_key=api_key,
                reference_image_path=prev_image,
                # character_anchor_path 不傳：
                # veo-3.1-lite/fast 不支援 reference_images[asset]，只有 veo-3.1-generate-preview 才有。
                duration_seconds=duration_seconds,
                aspect_ratio=args.aspect_ratio,
            )
        else:
            img_path = ep_dir / f"{item['output_index']:02d}.png"
            print(f"    🖼️  生成圖片 → {img_path.name}")
            ok = gen_img(prompt, img_path, api_key)
            if ok:
                prev_image = img_path
                if anchor_image is None:
                    anchor_image = img_path

        results.append({
            "beat": beat_num,
            "type": "video" if is_video else "image",
            "success": ok,
            "path": str((ep_dir / (f"{item['output_index']:02d}.mp4" if is_video else f"{item['output_index']:02d}.png")).relative_to(PROJECT_ROOT)),
        })

        if plan_idx < len(media_plan) and args.delay > 0:
            time.sleep(args.delay)

    return results


# ──────────────────────────────────────────────
# 進度 log
# ──────────────────────────────────────────────

def load_progress(log_path: Path) -> dict:
    if log_path.exists():
        try:
            return json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"episodes": {}}


def save_progress(log_path: Path, progress: dict) -> None:
    log_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def run_batch(args: argparse.Namespace) -> None:
    library = load_json(LIBRARY_PATH)
    themes  = load_json(THEMES_PATH)
    arcs    = load_json(ARCS_PATH)

    # ── 隨機種子 ──
    # 指定 batch-id 時保留可重現性；未指定時每次執行都用新的時間戳，避免同一天重跑拿到同一批題材。
    seed_str = args.batch_id or datetime.now().isoformat(timespec="microseconds")
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    print(f"🎲 Batch ID: {seed_str}  |  Seed: {seed}")

    # ── 輸出資料夾命名 ──
    # 有 batch-id → 確定性（方便 resume），無 batch-id → 加時間戳避免覆蓋
    if args.batch_id:
        folder_name = f"Kirby-Stories-{date.today()}-{args.batch_id}"
    else:
        ts = datetime.now().strftime("%H%M")
        folder_name = f"Kirby-Stories-{date.today()}-{ts}"
    out_dir = PROJECT_ROOT / "Local_Media" / folder_name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 輸出目錄: {out_dir.relative_to(PROJECT_ROOT)}")

    # ── 進度追蹤 ──
    log_path = out_dir / "batch_log.json"
    progress = load_progress(log_path) if args.resume else {"episodes": {}}
    done_eps = set(progress["episodes"].keys())

    # ── 概念循環器 ──
    pool  = build_concept_queue(rng, themes, args.cluster)
    cycler = ConceptCycler(rng, pool)
    pool_cluster_count = len({cluster["id"] for cluster, _ in pool})
    print(f"🧪 Diversity: {args.diversity_level}  |  Concept pool: {len(pool)} concepts / {pool_cluster_count} clusters")

    # ── 故事弧線 beats ──
    # 每個 episode 動態選 arc（由 concept 的 arc_type 決定）

    # ── 趨勢關鍵字預處理 ──
    args.trend_keywords_list = (
        [k.strip() for k in args.trend_keywords.split(",") if k.strip()]
        if args.trend_keywords else []
    )

    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN — 預覽 {args.episodes} 個 episode（不打 API）")
        print(f"{'='*60}")
    else:
        api_key = load_api_key()
        if not api_key:
            raise SystemExit("❌ 找不到 Gemini API Key。請設定 GEMINI_API_KEY 環境變數。")
        gen_img, gen_vid = _import_generators()

    success_eps = 0
    fail_eps    = 0

    for ep_idx in range(1, args.episodes + 1):
        ep_key = f"ep{ep_idx:02d}"

        if ep_key in done_eps:
            print(f"\n⏭️  [{ep_idx:02d}/{args.episodes}] {ep_key} 已完成，跳過")
            success_eps += 1
            continue

        cluster, concept = cycler.next()
        arc_type, arc = resolve_arc_for_concept(rng, concept, arcs)

        beats = resolve_episode_beats(args=args, rng=rng, arc=arc)

        print(f"\n{'─'*60}")
        print(f"[{ep_idx:02d}/{args.episodes}] Episode {ep_key}")
        print(f"叢集: {cluster['label_zh']}  |  Arc: {arc['label_zh']}  |  Beats: {len(beats)}")

        ep_results = generate_episode(
            ep_num=ep_idx,
            concept=concept,
            cluster=cluster,
            arc=arc,
            beats=beats,
            rng=rng,
            library=library,
            themes=themes,
            out_dir=out_dir,
            api_key=None if args.dry_run else api_key,
            gen_img=None if args.dry_run else gen_img,
            gen_vid=None if args.dry_run else gen_vid,
            args=args,
            dry_run=args.dry_run,
        )

        beat_success = sum(1 for r in ep_results if r.get("success"))
        beat_total   = len(ep_results)

        if not args.dry_run:
            progress["episodes"][ep_key] = {
                "concept": concept["zh"],
                "cluster": cluster["id"],
                "arc": arc_type,
                "diversity_level": args.diversity_level,
                "beats_ok": beat_success,
                "beats_total": beat_total,
                "results": ep_results,
                "timestamp": datetime.now().isoformat(),
            }
            save_progress(log_path, progress)

        if beat_success == beat_total or args.dry_run:
            success_eps += 1
        else:
            fail_eps += 1

        if ep_idx < args.episodes and args.delay > 0 and not args.dry_run:
            time.sleep(args.delay)

    # ── 最終報告 ──
    print(f"\n{'='*60}")
    print(f"✅ 完成  |  Episodes 成功: {success_eps}  |  失敗: {fail_eps}  |  共: {args.episodes}")
    print(f"📁 輸出: {out_dir.relative_to(PROJECT_ROOT)}")
    if args.type == "mixed":
        print(f"   結構: {out_dir.name}/ep01/01.png + 02.mp4")
    elif args.type == "video":
        print(f"   結構: {out_dir.name}/ep01/01.mp4 + 02.mp4 + 03.mp4 ...")
    elif args.type == "carousel":
        print(f"   結構: {out_dir.name}/ep01/01.png + 02.png + 03.png (+ 04/05.png 視 episode 而定)")
    else:
        print(f"   結構: {out_dir.name}/ep01/01.png + 02.png + 03.png ...")
    if not args.dry_run:
        print(f"📝 詳細 log: {log_path.relative_to(PROJECT_ROOT)}")
    print(f"{'='*60}")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="批次生成 Kirby 連續小短劇（不需呼叫 Claude API）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
輸出結構:
  Local_Media/Kirby-Stories-2026-04-25-session01/
    ep01/
      01.png   ← Carousel / Image / Mixed anchor
      02.png   ← Carousel / Image
      03.png   ← Carousel / Image
      04.png   ← Carousel 額外 panel（可選）
      05.png   ← Carousel 額外 panel（可選）
      02.mp4   ← Mixed 模式：濃縮後段影片
    ep02/
      01.png
      02.png / 02.mp4
    batch_log.json

範例:
  # 預覽 5 個故事的 prompt（不花額度）
  python scripts/batch_kirby_generate.py --episodes 5 --dry-run

  # 10 個純圖片故事（每個 3 張）
  python scripts/batch_kirby_generate.py --episodes 10 --type image

  # 10 個輪播故事（每個 episode 隨機 3~5 張）
  python scripts/batch_kirby_generate.py --episodes 10 --type carousel

  # 5 個混合故事（1 圖 + 1 影片）
  python scripts/batch_kirby_generate.py --episodes 5 --type mixed

  # 指定叢集（可選: workplace_absurd, food_odyssey, cosmos_drift,
  #   cozy_intimate, power_awakening, tiny_vs_epic,
  #   emotional_warrior, art_crossover, future_glitch, nature_ritual）
  python scripts/batch_kirby_generate.py --episodes 5 --cluster cosmos_drift

  # 加節日趨勢 + batch-id（方便 resume）
  python scripts/batch_kirby_generate.py --episodes 10 --trend-keywords "母親節,溫情"
      --batch-id mothers-day

  # 斷點續跑
  python scripts/batch_kirby_generate.py --episodes 10 --batch-id mothers-day --resume

  # 指定 5 張輪播圖
  python scripts/batch_kirby_generate.py --episodes 5 --type carousel --beats 5

  # 4 幕故事（有結局）+ 9:16 豎版影片（Reels 格式）
  python scripts/batch_kirby_generate.py --episodes 5 --beats 4 --aspect-ratio 9:16
        """,
    )
    parser.add_argument("--episodes", "-n", type=int, default=5, help="生成幾個故事 episode（預設 5）")
    parser.add_argument(
        "--beats", type=int, default=None, choices=[3, 4, 5],
        help="每個 episode 幾幕；carousel 未指定時會每集隨機 3~5，其他模式未指定時預設 3",
    )
    parser.add_argument(
        "--type", choices=["image", "video", "mixed", "carousel"], default="mixed",
        help="媒體類型：image=全圖片 / video=全影片 / mixed=1張 anchor 圖 + 1支濃縮影片 / carousel=3~5張連續輪播圖（預設 mixed）",
    )
    parser.add_argument(
        "--batch-id", default=None,
        help="批次識別碼，決定隨機種子（相同 id 可重現；指定 id 時 --resume 才有效）。不指定則用時間戳命名資料夾。",
    )
    parser.add_argument("--cluster", default=None, help="強制使用特定叢集 ID")
    parser.add_argument(
        "--trend-keywords", default=None,
        help="額外趨勢關鍵字（逗號分隔），例如 '母親節,溫情,感謝'",
    )
    parser.add_argument(
        "--diversity-level",
        choices=["low", "normal", "high", "wild"],
        default="high",
        help="題材與視覺隨機強度；high 會降低固定 preset 並注入新意，wild 會更跳脫（預設 high）",
    )
    parser.add_argument("--delay", type=float, default=5.0, help="每次 API 呼叫間隔秒數（預設 5）")
    parser.add_argument(
        "--aspect-ratio", default="16:9", choices=["16:9", "9:16"],
        help="影片畫面比例（預設 16:9；9:16 適合 Reels）",
    )
    parser.add_argument("--resume", action="store_true", help="跳過已完成的 episode（需指定 --batch-id）")
    parser.add_argument("--dry-run", action="store_true", help="只印 prompt，不呼叫 API")

    args = parser.parse_args()
    run_batch(args)


if __name__ == "__main__":
    main()
