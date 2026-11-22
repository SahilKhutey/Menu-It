import type { ItemAvailability } from "@modularmenu/contracts";

export interface AvailabilityPresentation {
  label: string;
  isOrderable: boolean;
  badgeClass: string;
}

export function formatAvailability(
  state: ItemAvailability,
  locale: string = "en-IN"
): AvailabilityPresentation {
  switch (state) {
    case "available":
      return { label: "Available", isOrderable: true, badgeClass: "badge-available" };
    case "sold_out":
      return { label: "Sold out", isOrderable: false, badgeClass: "badge-sold-out" };
    case "unavailable":
      return { label: "Currently unavailable", isOrderable: false, badgeClass: "badge-unavailable" };
    default:
      throw new Error(`UNSUPPORTED_AVAILABILITY_STATE: ${state}`);
  }
}
