/**
 * ModularMenu — Component Definition & Instance Contracts (ARC-08 §8).
 * Generated from component-definition.schema.json & component-instance.schema.json.
 */

export type ComponentCategory = "structure" | "content" | "metadata" | "navigation";
export type ComponentSlot = "header" | "navigation" | "content" | "category.header" | "category.items" | "footer";

export type ComponentDefinition = {
  id: string;
  version: string;
  schema_version: "1.0.0";
  name: string;
  category: ComponentCategory;
  description: string;
  default_props: Record<string, unknown>;
  props_schema: Record<string, unknown>;
  supported_slots: ComponentSlot[];
  supported_layouts: string[];
  accessibility?: {
    requirements: string[];
  };
  status: "active" | "deprecated" | "retired";
};

export type ComponentInstance = {
  instance_id: string;
  component_id: string;
  component_version: string;
  schema_version: "1.0.0";
  slot: ComponentSlot;
  position: number;
  visible: boolean;
  props: Record<string, unknown>;
};
