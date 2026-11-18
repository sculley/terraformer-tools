// Terraformer Tools - entry point. Wires events to the size menu, area mining and the guide.

import { world, system } from "@minecraft/server";
import { toolFor } from "./tools.js";
import { registerAreaMining } from "./mining.js";
import { openSizeMenu, showCurrentSize } from "./size_menu.js";
import { openGuide, giveGuideOnFirstJoin } from "./guide.js";

registerAreaMining();

// "Use" can arrive as an item use (in the air) or a block interaction (aimed at a block).
// Both may fire for one press, so ignore repeats within a few ticks.
const lastUse = new Map();

function onUse(player, item) {
  if (!item) return;
  const now = system.currentTick;
  if (now - (lastUse.get(player.id) ?? -100) < 8) return;

  if (item.typeId === "terraformer:guide") {
    lastUse.set(player.id, now);
    openGuide(player);
    return;
  }
  if (!toolFor(item)) return;
  lastUse.set(player.id, now);
  if (player.isSneaking) openSizeMenu(player, item);
  else showCurrentSize(player, item);
}

world.afterEvents.itemUse.subscribe((e) => onUse(e.source, e.itemStack));

world.afterEvents.playerInteractWithBlock.subscribe((e) => {
  if (e.isFirstEvent) onUse(e.player, e.itemStack);
});

world.afterEvents.playerSpawn.subscribe((e) => {
  if (e.initialSpawn) giveGuideOnFirstJoin(e.player);
});

world.afterEvents.playerLeave.subscribe((e) => lastUse.delete(e.playerId));
