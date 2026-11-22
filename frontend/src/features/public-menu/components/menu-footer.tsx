import React from "react";
import type { RenderRestaurant } from "@modularmenu/contracts";

interface MenuFooterProps {
  restaurant: RenderRestaurant;
}

export function MenuFooter({ restaurant }: MenuFooterProps) {
  const contact = restaurant.contact_information || {};

  return (
    <footer className="menu-footer border-t border-[var(--mm-color-border-subtle,#F4F4F5)] bg-zinc-50 py-8 px-4 mt-12 text-center text-xs text-zinc-500">
      <div className="max-w-4xl mx-auto space-y-2">
        <p className="font-semibold text-zinc-700">{restaurant.name}</p>
        {contact.address && <p>{contact.address}</p>}
        {contact.phone && <p>Tel: {contact.phone}</p>}
        <div className="pt-4 text-[10px] text-zinc-400">
          <p>Powered by ModularMenu™ · FSSAI & GST Compliant</p>
        </div>
      </div>
    </footer>
  );
}
