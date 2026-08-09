# MathQuest 0.11.1 hotfix

Fixes a frontend load/freeze regression caused by legacy enhancement scripts observing the entire DOM while also mutating version labels and visual content. Older release layers no longer fight over the displayed version, observer callbacks are coalesced, async enhancement fetches are guarded against duplication, and visual question content is no longer continuously removed and recreated.

The Home Assistant statistics API introduced in 0.11.0 is unchanged.
