// Area mining: when a Terraformer tool breaks a block, break the rest of the 2×2 or 3×3 face around it.

import { world, system, GameMode } from "@minecraft/server";
import { toolFor, getSize, canDig } from "./tools.js";

const sign = (n) => (n < 0 ? -1 : 1);

/** Nearest horizontal axis to a vector, as a unit step. */
function snapHorizontal(v) {
  return Math.abs(v.x) >= Math.abs(v.z) ? { x: sign(v.x), y: 0, z: 0 } : { x: 0, y: 0, z: sign(v.z) };
}

/** Which face of the block the player is looking at, worked out from their view if the ray missed. */
function faceFromView(view) {
  const ax = Math.abs(view.x);
  const ay = Math.abs(view.y);
  const az = Math.abs(view.z);
  if (ay >= ax && ay >= az) return view.y < 0 ? "Up" : "Down";
  if (ax >= az) return view.x > 0 ? "West" : "East";
  return view.z > 0 ? "North" : "South";
}

/**
 * The two directions that span the mined face.
 * `across` points to the player's right; `along` points up on walls, or away from the player on floors and ceilings.
 * A 2×2 therefore grows up and to the right of the block you hit; a 3×3 is centred on it.
 */
function planeAxes(face, view) {
  const right = snapHorizontal({ x: -view.z, z: view.x });
  switch (face) {
    case "Up":
    case "Down":
      return [right, snapHorizontal(view)];
    case "North":
    case "South":
      return [{ x: sign(right.x || 1), y: 0, z: 0 }, { x: 0, y: 1, z: 0 }];
    default: // East / West
      return [{ x: 0, y: 0, z: sign(right.z || 1) }, { x: 0, y: 1, z: 0 }];
  }
}

function mineArea(player, dimension, origin, face, view, size, tool) {
  if (!player.isValid) return;
  const [across, along] = planeAxes(face ?? faceFromView(view), view);
  const start = -Math.floor((size - 1) / 2);
  const mode = player.getGameMode() === GameMode.Creative ? "replace" : "destroy";

  for (let i = start; i < start + size; i++) {
    for (let j = start; j < start + size; j++) {
      if (i === 0 && j === 0) continue; // the game breaks this one itself
      const x = origin.x + across.x * i + along.x * j;
      const y = origin.y + across.y * i + along.y * j;
      const z = origin.z + across.z * i + along.z * j;
      let block;
      try {
        block = dimension.getBlock({ x, y, z });
      } catch {
        continue; // outside the world or not loaded
      }
      if (!canDig(tool, block)) continue;
      // "destroy" drops the block's items and plays the break effect, just like mining it.
      dimension.runCommand(`setblock ${x} ${y} ${z} air ${mode}`);
    }
  }
}

export function registerAreaMining() {
  world.beforeEvents.playerBreakBlock.subscribe((event) => {
    const tool = toolFor(event.itemStack);
    if (!tool) return;
    const size = getSize(event.itemStack);
    const { player, block, dimension } = event;
    // Only spread when the block you hit is one this tool is meant for.
    if (size <= 1 || !canDig(tool, block)) return;

    const origin = { x: block.x, y: block.y, z: block.z };
    const view = player.getViewDirection();
    let face;
    try {
      const hit = player.getBlockFromViewDirection({ maxDistance: 12 });
      const b = hit?.block;
      if (b && b.x === origin.x && b.y === origin.y && b.z === origin.z) face = hit.face;
    } catch {
      // fall back to the view direction
    }
    // Before-events are read-only, so do the breaking on the next tick.
    system.run(() => mineArea(player, dimension, origin, face, view, size, tool));
  });
}
