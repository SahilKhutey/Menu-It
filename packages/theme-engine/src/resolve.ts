/**
 * ModularMenu — Deterministic Customization & Theme Resolver (ARC-08 §11).
 * Resolves normalized presentation configuration from theme presets, layout defaults,
 * component registry, and restaurant overrides without mutating inputs.
 */

function isPlainObject(value: unknown): value is Record<string, any> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Deterministically merges override object into base object based on allowed keys.
 * Does not mutate inputs.
 */
export function deepMerge(
  base: Record<string, any>,
  override: Record<string, any>
): Record<string, any> {
  const result: Record<string, any> = { ...base };

  for (const [key, value] of Object.entries(override || {})) {
    if (value === undefined) {
      continue;
    }
    if (value === null) {
      // null means reset property if supported
      delete result[key];
      continue;
    }
    if (isPlainObject(value) && isPlainObject(result[key])) {
      result[key] = deepMerge(result[key], value);
    } else {
      result[key] = value;
    }
  }

  return result;
}

export type ResolveParams = {
  themePreset: { id: string; version: string; tokens: Record<string, any> };
  themeOverrides?: Record<string, any>;
  layoutDefinition: { id: string; version: string; default_settings: Record<string, any>; responsive: Record<string, any> };
  layoutOverrides?: { settings?: Record<string, any>; responsive?: Record<string, any> };
  componentDefinitions: Map<string, { id: string; version: string; default_props: Record<string, any> }>;
  components: Array<{
    instance_id: string;
    component_id: string;
    component_version: string;
    slot: string;
    position: number;
    visible: boolean;
    props: Record<string, any>;
  }>;
};

export function resolveCustomization(params: ResolveParams) {
  // 1. Resolve Tokens: Theme Preset + Restaurant Overrides
  const resolvedTokens = deepMerge(params.themePreset.tokens, params.themeOverrides || {});

  // 2. Resolve Layout: Layout Defaults + Restaurant Overrides
  const layoutSettings = deepMerge(
    params.layoutDefinition.default_settings,
    params.layoutOverrides?.settings || {}
  );
  const layoutResponsive = deepMerge(
    params.layoutDefinition.responsive,
    params.layoutOverrides?.responsive || {}
  );

  // 3. Resolve Components: Definition default_props + Instance props
  const resolvedComponents = (params.components || []).map((instance) => {
    const def = params.componentDefinitions.get(instance.component_id);
    const defaultProps = def ? def.default_props : {};
    const mergedProps = deepMerge(defaultProps, instance.props || {});

    return {
      instanceId: instance.instance_id,
      componentId: instance.component_id,
      componentVersion: instance.component_version,
      slot: instance.slot,
      position: instance.position,
      visible: instance.visible !== false,
      props: mergedProps,
    };
  });

  // Sort components by position deterministically
  resolvedComponents.sort((a, b) => a.position - b.position);

  return {
    configurationVersion: "1.0.0",
    theme: {
      themeId: params.themePreset.id,
      themeVersion: params.themePreset.version,
      tokens: resolvedTokens,
    },
    layout: {
      id: params.layoutDefinition.id,
      version: params.layoutDefinition.version,
      settings: layoutSettings,
      responsive: layoutResponsive,
    },
    components: resolvedComponents,
  };
}
