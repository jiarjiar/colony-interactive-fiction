#!/usr/bin/env python3
"""对《殖民地》执行带条件的状态遍历，而不只检查静态引用。"""
from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import re

SOURCE = Path(__file__).with_name("殖民地.json")
FLAG_RE = re.compile(r"^hasFlag '([^']+)'$")


def matches(condition, flags: frozenset[str]) -> bool:
    if condition is None or condition == "default":
        return True
    if isinstance(condition, str):
        match = FLAG_RE.match(condition)
        if not match:
            raise ValueError(f"不支持的字符串条件：{condition!r}")
        return match.group(1) in flags
    if isinstance(condition, dict) and set(condition) == {"all"}:
        return all(isinstance(item, dict) and set(item) == {"flag"} and item["flag"] in flags
                   for item in condition["all"])
    raise ValueError(f"不支持的条件：{condition!r}")


def apply_changes(choice: dict, flags: frozenset[str], achievements: frozenset[str]):
    changes = choice.get("changes", {})
    next_flags = set(flags)
    next_flags.update(changes.get("addFlags", []))
    if changes.get("addFlag"):
        next_flags.add(changes["addFlag"])
    important = changes.get("importantFlag")
    if important:
        next_flags.add(important["flag"] if isinstance(important, dict) else important)
    next_achievements = set(achievements)
    unlocked = changes.get("unlockAchievement")
    if unlocked:
        next_achievements.add(unlocked)
    return frozenset(next_flags), frozenset(next_achievements)


def main() -> None:
    story = json.loads(SOURCE.read_text(encoding="utf-8"))
    nodes = story["nodes"]
    defined_achievements = set(story.get("achievements", {}))
    start = story["startNodeId"]
    queue = deque([(start, frozenset(), frozenset(), [])])
    visited = set()
    ending_paths: dict[str, list[str]] = {}
    unlocked_anywhere: set[str] = set()

    while queue:
        node_id, flags, achievements, path = queue.popleft()
        state = (node_id, flags, achievements)
        if state in visited:
            continue
        visited.add(state)
        node = nodes[node_id]
        current_achievements = set(achievements)
        if node.get("achievement"):
            current_achievements.add(node["achievement"])
        achievements = frozenset(current_achievements)
        unlocked_anywhere.update(achievements)
        if node.get("isEnding"):
            ending_paths.setdefault(node_id, path)
            continue
        if node.get("next"):
            queue.append((node["next"], flags, achievements, path))
            continue
        if node.get("routes"):
            for route in node["routes"]:
                if matches(route.get("condition"), flags):
                    queue.append((route["next"], flags, achievements, path + [f"{node_id} → {route['next']}"]))
                    break
            else:
                raise AssertionError(f"路由无匹配项：{node_id}")
            continue
        for choice in node.get("choices", []):
            if not matches(choice.get("condition"), flags):
                continue
            next_flags, next_achievements = apply_changes(choice, flags, achievements)
            queue.append((choice["next"], next_flags, next_achievements,
                          path + [f"{node_id}: {choice['text']}"]))

    expected_endings = {node_id for node_id, node in nodes.items() if node.get("isEnding")}
    missing_endings = expected_endings - set(ending_paths)
    missing_achievements = defined_achievements - unlocked_anywhere
    unknown_achievements = unlocked_anywhere - defined_achievements
    if missing_endings:
        raise AssertionError(f"真实条件下不可达结局：{sorted(missing_endings)}")
    if missing_achievements:
        raise AssertionError(f"无法解锁的成就：{sorted(missing_achievements)}")
    if unknown_achievements:
        raise AssertionError(f"引用了未定义成就：{sorted(unknown_achievements)}")

    print(f"条件状态遍历通过：{len(visited)} 个状态")
    print(f"真实可达结局：{len(ending_paths)} / {len(expected_endings)}")
    print(f"真实可解锁成就：{len(unlocked_anywhere)} / {len(defined_achievements)}")
    for ending_id in sorted(ending_paths):
        decisions = ending_paths[ending_id]
        print(f"- {ending_id}: {len(decisions)} 个显式选择/路由步骤")


if __name__ == "__main__":
    main()
