// The Terraformer Tools Guide: a chaptered book opened by using it.

import { ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const GOT_GUIDE = "terraformer:got_guide";

const CHAPTERS = [
  {
    title: "The tools",
    icon: "textures/items/terraformer_pickaxe",
    body: [
      "§lTerraformer Pickaxe§r digs stone, ores, deepslate, metal blocks and anything else a pickaxe can mine.",
      "",
      "§lTerraformer Spade§r digs dirt, grass, sand, gravel, clay, snow and anything else a shovel can mine.",
      "",
      "Both tools:",
      "• mine §ainstantly§r",
      "• §anever break§r - they have no durability",
      "• can dig a §a1 × 1§r, §a2 × 2§r or §a3 × 3§r area with each block you break",
      "",
      "New tools start at §a3 × 3§r.",
    ],
  },
  {
    title: "Changing the size",
    icon: "textures/ui/terraformer_size_2",
    body: [
      "1. Hold the pickaxe or spade.",
      "2. §lSneak§r and press §lUse§r.",
      "   PS5 / controller: hold sneak (R3 by default) and press L2.",
      "   PC: hold Shift and right-click.",
      "   Touch: tap sneak, then tap and hold the screen.",
      "3. Pick §a1 × 1§r, §a2 × 2§r or §a3 × 3§r from the menu.",
      "",
      "Each tool remembers its own size, and it is shown in the tool's description. Use the tool without sneaking to see its size on screen.",
      "",
      "Tip: carry two pickaxes - one on 3 × 3 for clearing, one on 1 × 1 for detail work.",
    ],
  },
  {
    title: "Where the area goes",
    icon: "textures/ui/terraformer_size_3",
    body: [
      "The area is a flat square on the face of the block you hit.",
      "",
      "§l3 × 3§r - centred on the block you hit.",
      "§l2 × 2§r - the block you hit plus the blocks above it and to your right. On floors and ceilings it spreads to your right and away from you.",
      "§l1 × 1§r - just the block you hit, like a normal tool.",
      "",
      "Dig into a wall to make a tunnel, dig down for a shaft, or dig the floor to flatten land.",
      "",
      "The pickaxe only takes pickaxe blocks and the spade only takes spade blocks, so chests, logs and builds next to your work stay put. If you hit a block the tool isn't meant for, only that block breaks.",
    ],
  },
  {
    title: "Crafting recipes",
    icon: "textures/items/terraformer_spade",
    body: [
      "Use a crafting table. Top row first:",
      "",
      "§lTerraformer Pickaxe§r",
      "§a Emerald  ·  Emerald  ·  Emerald§r",
      "§7    -      ·§f Iron Ingot§7 ·     -",
      "§7    -      ·§f Iron Ingot§7 ·     -§r",
      "",
      "§lTerraformer Spade§r",
      "§7    -      ·§a  Emerald  §7 ·     -",
      "§7    -      ·§f Iron Ingot§7 ·     -",
      "§7    -      ·§f Iron Ingot§7 ·     -§r",
      "",
      "§lTerraformer Tools Guide§r",
      "Book + Emerald, in any slots.",
      "",
      "Everything is also in the creative inventory.",
    ],
  },
  {
    title: "Good to know",
    icon: "textures/items/terraformer_guide",
    body: [
      "• Blocks broken by the area drop their items, just like mining them. In Creative they don't drop.",
      "• Bedrock, portals, barriers, command blocks and other unbreakable blocks are never touched.",
      "• Water and lava are left in place - watch out when you open a cave!",
      "• The tools can't be enchanted. They don't need to be.",
      "• Lost this book? Craft another from a Book and an Emerald.",
    ],
  },
];

export async function openGuide(player, page) {
  if (page === undefined) {
    const menu = new ActionFormData()
      .title("Terraformer Tools")
      .body("Instant, unbreakable tools for clearing land fast.\nPick a chapter:");
    for (const c of CHAPTERS) menu.button(c.title, c.icon);
    const r = await menu.show(player);
    if (r.canceled || r.selection === undefined) return;
    return openGuide(player, r.selection);
  }

  const chapter = CHAPTERS[page];
  const form = new ActionFormData().title(chapter.title).body(chapter.body.join("\n"));
  const hasNext = page + 1 < CHAPTERS.length;
  form.button("< Contents");
  if (hasNext) form.button(`Next: ${CHAPTERS[page + 1].title} >`);
  const r = await form.show(player);
  if (r.canceled || r.selection === undefined) return;
  return openGuide(player, r.selection === 0 ? undefined : page + 1);
}

/** Every player gets one guide the first time they join a world with the add-on. */
export function giveGuideOnFirstJoin(player) {
  if (player.getDynamicProperty(GOT_GUIDE)) return;
  const inventory = player.getComponent("minecraft:inventory")?.container;
  if (!inventory) return;
  const leftover = inventory.addItem(new ItemStack("terraformer:guide", 1));
  if (leftover) player.dimension.spawnItem(leftover, player.location);
  player.setDynamicProperty(GOT_GUIDE, true);
  player.sendMessage("§aTerraformer Tools:§r you've been given a guide book. Use it to learn the tools and recipes.");
}
