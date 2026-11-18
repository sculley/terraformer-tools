// The size picker: sneak + use a Terraformer tool to choose 1×1, 2×2 or 3×3.

import { EquipmentSlot } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { SIZES, toolFor, getSize, setSize } from "./tools.js";

export function showCurrentSize(player, item) {
  const tool = toolFor(item);
  const size = getSize(item);
  player.onScreenDisplay.setActionBar(`§a${tool.name}: ${size} × ${size}  §7(sneak + use to change)`);
}

export async function openSizeMenu(player, item) {
  const tool = toolFor(item);
  const current = getSize(item);

  const form = new ActionFormData()
    .title(tool.name)
    .body(`Choose how many blocks this tool breaks at once.\n\nCurrent size: §a${current} × ${current}§r`);
  for (const n of SIZES) {
    form.button(`${n} × ${n}${n === current ? "  §2(current)" : ""}`, `textures/ui/terraformer_size_${n}`);
  }

  const response = await form.show(player);
  if (response.canceled || response.selection === undefined) return;
  const size = SIZES[response.selection];

  // Re-read the held item: the player may have switched slots while the menu was open.
  const equipment = player.getComponent("minecraft:equippable");
  const held = equipment?.getEquipment(EquipmentSlot.Mainhand);
  if (!held || held.typeId !== item.typeId) {
    player.sendMessage("§cKeep holding the tool while you pick a size.");
    return;
  }
  setSize(held, size);
  equipment.setEquipment(EquipmentSlot.Mainhand, held);
  player.onScreenDisplay.setActionBar(`§a${tool.name}: ${size} × ${size}`);
  player.playSound("random.orb", { pitch: 0.7 + size * 0.2 });
}
