/**
 * ModularMenu — Editor Command & History Engine (ARC-08 §12.6).
 * Bounded undo/redo history for visual and settings editor.
 */

export type EditorCommandType =
  | "SET_THEME"
  | "SET_THEME_TOKEN"
  | "SET_LAYOUT"
  | "SET_LAYOUT_SETTING"
  | "ADD_COMPONENT"
  | "REMOVE_COMPONENT"
  | "MOVE_COMPONENT"
  | "UPDATE_COMPONENT_PROPS"
  | "SET_COMPONENT_VISIBILITY"
  | "RESET_COMPONENT";

export type EditorCommand<T = any> = {
  type: EditorCommandType;
  payload: T;
  timestamp: number;
};

export class EditorHistory<S> {
  private past: S[] = [];
  private present: S;
  private future: S[] = [];
  private readonly maxDepth: number;

  constructor(initialState: S, maxDepth: number = 50) {
    this.present = JSON.parse(JSON.stringify(initialState));
    this.maxDepth = maxDepth;
  }

  getCurrentState(): S {
    return JSON.parse(JSON.stringify(this.present));
  }

  execute(newState: S): void {
    this.past.push(this.present);
    if (this.past.length > this.maxDepth) {
      this.past.shift();
    }
    this.present = JSON.parse(JSON.stringify(newState));
    this.future = [];
  }

  canUndo(): boolean {
    return this.past.length > 0;
  }

  canRedo(): boolean {
    return this.future.length > 0;
  }

  undo(): S | null {
    if (!this.canUndo()) return null;
    const previous = this.past.pop()!;
    this.future.unshift(this.present);
    this.present = previous;
    return this.getCurrentState();
  }

  redo(): S | null {
    if (!this.canRedo()) return null;
    const next = this.future.shift()!;
    this.past.push(this.present);
    this.present = next;
    return this.getCurrentState();
  }
}
