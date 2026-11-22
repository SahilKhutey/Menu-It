import type { MenuRenderInput, MenuRenderPlan, RenderNode } from "@modularmenu/contracts";

export interface ComponentDefinitionLookup {
  allowedSlots: string[];
  validateProps?: (props: Record<string, any>) => boolean;
}

export interface LayoutDefinitionLookup {
  slots: string[];
  maxColumns?: number;
}

export interface PlatformCatalogueRegistry {
  getComponent(id: string, version?: string): ComponentDefinitionLookup | undefined;
  getLayout(id: string, version?: string): LayoutDefinitionLookup | undefined;
}

export function resolveRenderPlan(
  input: MenuRenderInput,
  registry: PlatformCatalogueRegistry
): MenuRenderPlan {
  if (!input || !input.metadata || !input.resolved_configuration) {
    throw new Error("RENDER_INPUT_INVALID");
  }

  const { theme, layout, components } = input.resolved_configuration;

  // 1. Layout Resolution
  const layoutDef = registry.getLayout(layout.id, layout.version);
  if (!layoutDef) {
    throw new Error(`RENDER_LAYOUT_NOT_FOUND: ${layout.id}@${layout.version}`);
  }

  // 2. Component Resolution & Slot Compatibility
  const rootNodes: RenderNode[] = [];
  const warnings: Array<{ code: string; message: string }> = [];

  const seenInstanceIds = new Set<string>();

  const componentList = Array.isArray(components) ? components : [];
  for (let idx = 0; idx < componentList.length; idx++) {
    const comp = componentList[idx];

    if (seenInstanceIds.has(comp.instance_id)) {
      throw new Error(`DUPLICATE_INSTANCE_ID: ${comp.instance_id}`);
    }
    seenInstanceIds.add(comp.instance_id);

    const compDef = registry.getComponent(comp.component_id, comp.component_version);
    if (!compDef) {
      throw new Error(`RENDER_COMPONENT_NOT_FOUND: ${comp.component_id}@${comp.component_version}`);
    }

    if (!compDef.allowedSlots.includes(comp.slot)) {
      throw new Error(`RENDER_COMPONENT_SLOT_INVALID: ${comp.component_id} cannot be placed in ${comp.slot}`);
    }

    if (!layoutDef.slots.includes(comp.slot)) {
      throw new Error(`RENDER_LAYOUT_SLOT_INVALID: Slot ${comp.slot} not supported by layout ${layout.id}`);
    }

    if (compDef.validateProps && !compDef.validateProps(comp.props)) {
      throw new Error(`RENDER_COMPONENT_PROPS_INVALID: Props invalid for ${comp.component_id}`);
    }

    rootNodes.push({
      id: comp.instance_id,
      componentId: comp.component_id,
      componentVersion: comp.component_version,
      slot: comp.slot,
      order: comp.position ?? idx,
      props: comp.props || {},
      children: [],
    });
  }

  // Stable ordering
  rootNodes.sort((a, b) => a.order - b.order);

  return {
    schemaVersion: input.metadata.schema_version,
    theme: {
      id: theme.id,
      version: theme.version,
      tokens: theme.tokens,
    },
    layout: {
      id: layout.id,
      version: layout.version,
      slots: layoutDef.slots,
    },
    root: rootNodes,
    warnings,
  };
}
