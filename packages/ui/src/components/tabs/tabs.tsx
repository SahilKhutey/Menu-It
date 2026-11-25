'use client';

import React, {
  createContext,
  useContext,
  useId,
  useState,
  type HTMLAttributes,
  type ReactNode,
} from 'react';
import './tabs.css';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (id: string) => void;
  baseId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

export interface TabsProps extends HTMLAttributes<HTMLDivElement> {
  defaultValue: string;
  value?: string;
  onValueChange?: (val: string) => void;
  children: ReactNode;
}

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  children,
  className,
  ...props
}: TabsProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const baseId = useId();

  const activeTab = value !== undefined ? value : internalValue;

  const setActiveTab = (nextVal: string) => {
    if (value === undefined) {
      setInternalValue(nextVal);
    }
    onValueChange?.(nextVal);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab, baseId }}>
      <div className={['ui-tabs', className].filter(Boolean).join(' ')} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
}

export function TabList({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role="tablist"
      className={['ui-tablist', className].filter(Boolean).join(' ')}
      {...props}
    />
  );
}

export interface TabTriggerProps extends HTMLAttributes<HTMLButtonElement> {
  value: string;
  disabled?: boolean;
}

export function TabTrigger({ value, disabled, children, className, ...props }: TabTriggerProps) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('TabTrigger must be used inside Tabs');

  const isSelected = ctx.activeTab === value;
  const tabId = `${ctx.baseId}-tab-${value}`;
  const panelId = `${ctx.baseId}-panel-${value}`;

  return (
    <button
      {...props}
      type="button"
      role="tab"
      id={tabId}
      aria-selected={isSelected}
      aria-controls={panelId}
      tabIndex={isSelected ? 0 : -1}
      disabled={disabled}
      className={['ui-tab', isSelected ? 'ui-tab--active' : '', className]
        .filter(Boolean)
        .join(' ')}
      onClick={() => ctx.setActiveTab(value)}
    >
      {children}
    </button>
  );
}

export interface TabPanelProps extends HTMLAttributes<HTMLDivElement> {
  value: string;
}

export function TabPanel({ value, children, className, ...props }: TabPanelProps) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('TabPanel must be used inside Tabs');

  if (ctx.activeTab !== value) return null;

  const tabId = `${ctx.baseId}-tab-${value}`;
  const panelId = `${ctx.baseId}-panel-${value}`;

  return (
    <div
      {...props}
      role="tabpanel"
      id={panelId}
      aria-labelledby={tabId}
      tabIndex={0}
      className={['ui-tabpanel', className].filter(Boolean).join(' ')}
    >
      {children}
    </div>
  );
}
