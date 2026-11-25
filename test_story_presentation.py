#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import unittest


STORY_PATH = Path(__file__).with_name("殖民地.json")


class StoryPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.story = json.loads(STORY_PATH.read_text(encoding="utf-8"))

    def test_choice_nodes_always_offer_at_least_two_defined_options(self) -> None:
        single_option_nodes = {
            node_id: [choice.get("text", "") for choice in node.get("choices", [])]
            for node_id, node in self.story["nodes"].items()
            if "choices" in node and len(node["choices"]) < 2
        }
        self.assertEqual({}, single_option_nodes)

    def test_choice_nodes_have_two_options_without_unlock_requirements(self) -> None:
        insufficient_choice_nodes = {
            node_id: [choice.get("text", "") for choice in node.get("choices", [])]
            for node_id, node in self.story["nodes"].items()
            if "choices" in node
            and len([
                choice for choice in node["choices"]
                if choice.get("condition") in (None, "default")
            ]) < 2
        }
        self.assertEqual({}, insufficient_choice_nodes)

    def test_narrative_pages_have_higher_information_density(self) -> None:
        narrative_pages = {
            node_id: len(node.get("segments", []))
            for node_id, node in self.story["nodes"].items()
            if node.get("segments") and not node.get("isEnding")
        }
        average_segments = sum(narrative_pages.values()) / len(narrative_pages)
        single_paragraph_pages = [
            node_id for node_id, segment_count in narrative_pages.items()
            if segment_count == 1
        ]
        self.assertGreaterEqual(average_segments, 3.0)
        self.assertLessEqual(set(single_paragraph_pages), {"ch6_final_decision", "ch6_wait_route"})

    def test_key_story_events_use_their_matching_scene_art(self) -> None:
        expected_images = {
            "ch3_command_01": "概念图/05-两双手套.jpg",
            "ch5_evac_02": "概念图/10-无物撤离.jpg",
        }
        actual_images = {
            node_id: self.story["nodes"][node_id]["scene"]["image"]
            for node_id in expected_images
        }
        self.assertEqual(expected_images, actual_images)


if __name__ == "__main__":
    unittest.main()
