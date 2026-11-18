// What each Terraformer tool is allowed to dig, and the size setting stored on the item.

export const SIZES = [1, 2, 3];
export const DEFAULT_SIZE = 3;
const SIZE_PROPERTY = "terraformer:size";

export const TOOLS = {
  "terraformer:pickaxe": {
    name: "Terraformer Pickaxe",
    // Area mining only takes blocks a pickaxe would take, so chests, logs, dirt etc. are left alone.
    blockTags: [
      "minecraft:is_pickaxe_item_destructible",
      "stone",
      "metal",
      "rail",
      "diamond_pick_diggable",
      "iron_pick_diggable",
      "stone_pick_diggable",
    ],
  },
  "terraformer:spade": {
    name: "Terraformer Spade",
    blockTags: ["minecraft:is_shovel_item_destructible", "dirt", "sand", "gravel", "grass", "snow"],
  },
};

/** Blocks the area never touches, even if they carry a matching tag. */
export const NEVER_BREAK = new Set([
  "minecraft:bedrock",
  "minecraft:barrier",
  "minecraft:border_block",
  "minecraft:allow",
  "minecraft:deny",
  "minecraft:command_block",
  "minecraft:chain_command_block",
  "minecraft:repeating_command_block",
  "minecraft:structure_block",
  "minecraft:structure_void",
  "minecraft:jigsaw",
  "minecraft:light_block",
  "minecraft:end_portal",
  "minecraft:end_portal_frame",
  "minecraft:end_gateway",
  "minecraft:portal",
  "minecraft:reinforced_deepslate",
]);

export function toolFor(item) {
  return item ? TOOLS[item.typeId] : undefined;
}

export function getSize(item) {
  const value = item.getDynamicProperty(SIZE_PROPERTY);
  return SIZES.includes(value) ? value : DEFAULT_SIZE;
}

export function setSize(item, size) {
  item.setDynamicProperty(SIZE_PROPERTY, size);
  item.setLore([`§r§7Mining area: §a${size} × ${size}`, "§r§8Sneak + use to change"]);
}

export function canDig(tool, block) {
  if (!block || block.isAir || block.isLiquid || NEVER_BREAK.has(block.typeId)) return false;
  return tool.blockTags.some((tag) => block.hasTag(tag));
}
