/**
 * ModularMenu — Component Registry Engine (ARC-08 §8, §16.4).
 */

export type RegisteredComponentMeta = {
  id: string;
  version: string;
  schema_version: string;
  name: string;
  category: "structure" | "content" | "metadata" | "navigation";
  description: string;
  default_props: Record<string, any>;
  props_schema: Record<string, any>;
  supported_slots: string[];
  supported_layouts: string[];
  status: "active" | "deprecated" | "retired";
};

export class ComponentRegistry {
  private readonly components = new Map<string, RegisteredComponentMeta>();

  constructor(initialCatalogue?: RegisteredComponentMeta[]) {
    if (initialCatalogue) {
      for (const comp of initialCatalogue) {
        this.register(comp);
      }
    }
  }

  register(definition: RegisteredComponentMeta): void {
    const key = `${definition.id}@${definition.version}`;
    if (this.components.has(key)) {
      throw new Error(`Duplicate component registration: ${key}`);
    }
    this.components.set(key, definition);
    // Also index by bare ID for default latest version lookup
    this.components.set(definition.id, definition);
  }

  get(componentId: string, version?: string): RegisteredComponentMeta | undefined {
    if (version) {
      return this.components.get(`${componentId}@${version}`);
    }
    return this.components.get(componentId);
  }

  has(componentId: string, version?: string): boolean {
    return this.get(componentId, version) !== undefined;
  }

  isSlotSupported(componentId: string, slot: string, version?: string): boolean {
    const comp = this.get(componentId, version);
    if (!comp) return false;
    return comp.supported_slots.includes(slot);
  }

  listActive(): RegisteredComponentMeta[] {
    const unique = new Map<string, RegisteredComponentMeta>();
    this.components.forEach((comp) => {
      if (comp.status === "active") {
        unique.set(comp.id, comp);
      }
    });
    const result: RegisteredComponentMeta[] = [];
    unique.forEach((comp) => result.push(comp));
    return result;
  }
}
